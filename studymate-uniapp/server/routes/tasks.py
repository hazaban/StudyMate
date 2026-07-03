"""Daily task routes."""

from uuid import UUID
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from jose import jwt

from database import get_db, DailyTask, StudyPlan
from config import SECRET_KEY, ALGORITHM
from schemas.task import TaskCreate, TaskUpdate, TaskResponse, AITaskGenerateRequest
from services.ai_service import generate_daily_tasks

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _get_user_id(authorization: str = Header(None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期")


def _should_repeat(repeat_type: str, target_date: date) -> bool:
    """判断循环任务在目标日期是否应该出现。

    - daily: 每天都出现
    - weekday: 周一至周五出现
    - holiday: 周六、周日出现
    - none / 其他: 不循环
    """
    if repeat_type == "daily":
        return True
    if repeat_type == "weekday":
        # weekday(): Monday=0 ... Sunday=6
        return target_date.weekday() < 5
    if repeat_type == "holiday":
        return target_date.weekday() >= 5
    return False


def _task_to_response(task: DailyTask, target_date: date) -> TaskResponse:
    """将任务转为响应对象，循环任务根据目标日期动态计算状态。"""
    repeat_type = task.repeat_type or "none"
    completed_dates = task.completed_dates or []

    if repeat_type != "none":
        date_str = target_date.isoformat()
        if date_str in completed_dates:
            status = "completed"
            completed_at = None
            # 尝试保留原始 completed_at（仅作展示参考）
            if task.completed_at:
                completed_at = task.completed_at
        else:
            status = "pending"
            completed_at = None
    else:
        status = task.status
        completed_at = task.completed_at

    return TaskResponse(
        id=task.id,
        plan_id=task.plan_id,
        date=task.date,
        type=task.type,
        subject=task.subject,
        content=task.content,
        duration=task.duration,
        status=status,
        completed_at=completed_at,
        proof_image_url=task.proof_image_url or "",
        repeat_type=repeat_type,
        completed_dates=completed_dates,
        created_at=task.created_at,
    )


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plan = db.query(StudyPlan).filter(StudyPlan.id == data.plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    task = DailyTask(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_to_response(task, task.date)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    plan_id: UUID = Query(...),
    task_date: date = Query(None, alias="date"),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    target_date = task_date or date.today()

    # 1. 非循环任务：按日期精确查询
    normal_query = db.query(DailyTask).filter(
        DailyTask.plan_id == plan_id,
        DailyTask.date == target_date,
    )
    # 兼容旧数据：repeat_type 为 NULL 或 'none'
    normal_tasks = [
        t for t in normal_query.order_by(DailyTask.created_at.asc()).all()
        if (t.repeat_type or "none") == "none"
    ]

    # 2. 循环任务：查询所有 repeat_type != 'none' 的任务，按规则判断是否出现
    repeat_query = db.query(DailyTask).filter(DailyTask.plan_id == plan_id)
    repeat_tasks = [
        t for t in repeat_query.order_by(DailyTask.created_at.asc()).all()
        if (t.repeat_type or "none") != "none" and _should_repeat(t.repeat_type, target_date)
    ]

    # 合并并按创建时间排序
    all_tasks = normal_tasks + repeat_tasks
    all_tasks.sort(key=lambda t: t.created_at)
    return [_task_to_response(t, target_date) for t in all_tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    task = db.query(DailyTask).join(StudyPlan).filter(
        DailyTask.id == task_id,
        StudyPlan.user_id == user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return _task_to_response(task, task.date)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: UUID, data: TaskUpdate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    task = db.query(DailyTask).join(StudyPlan).filter(
        DailyTask.id == task_id,
        StudyPlan.user_id == user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return _task_to_response(task, task.date)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    task = db.query(DailyTask).join(StudyPlan).filter(
        DailyTask.id == task_id,
        StudyPlan.user_id == user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(task)
    db.commit()


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: UUID,
    task_date: date = Query(None, alias="date"),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    task = db.query(DailyTask).join(StudyPlan).filter(
        DailyTask.id == task_id,
        StudyPlan.user_id == user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    repeat_type = task.repeat_type or "none"
    target_date = task_date or date.today()

    if repeat_type != "none":
        # 循环任务：把日期加入 completed_dates
        completed_dates = task.completed_dates or []
        date_str = target_date.isoformat()
        if date_str not in completed_dates:
            completed_dates.append(date_str)
            task.completed_dates = completed_dates
    else:
        # 非循环任务：直接更新 status
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)
    return _task_to_response(task, target_date)


@router.post("/ai/generate")
async def ai_generate_tasks(data: AITaskGenerateRequest, user_id: UUID = Depends(_get_user_id)):
    result = await generate_daily_tasks(data.model_dump())
    return result
