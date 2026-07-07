"""Daily task routes with repeat task support."""
from uuid import UUID
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from jose import jwt

from database import get_db, DailyTask, StudyPlan
from config import SECRET_KEY, ALGORITHM
from schemas.task import TaskCreate, TaskUpdate, TaskResponse, AITaskGenerateRequest
from services.ai_service import generate_daily_tasks, parse_task_text
from routes.farm import add_fertilize_count

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _get_user_id(authorization: str = Header(None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期")


def _should_repeat(task: DailyTask, task_date: date) -> bool:
    """判断循环任务在指定日期是否应该出现。"""
    if task.repeat_type == "none" or not task.repeat_type:
        return task.date == task_date
    if task.repeat_type == "daily":
        return task.date <= task_date
    if task.repeat_type == "weekday":
        return task.date <= task_date and task_date.weekday() < 5
    if task.repeat_type == "holiday":
        return task.date <= task_date and task_date.weekday() >= 5
    return False


def _is_completed_on(task: DailyTask, task_date: date) -> bool:
    """判断循环任务在指定日期是否已完成。"""
    if task.repeat_type == "none" or not task.repeat_type:
        return task.status == "completed"
    date_str = task_date.isoformat()
    return date_str in (task.completed_dates or [])


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plan = db.query(StudyPlan).filter(StudyPlan.id == data.plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    task_data = data.model_dump()
    task = DailyTask()
    for key, value in task_data.items():
        if hasattr(task, key):
            setattr(task, key, value)
    db.add(task)
    try:
        db.commit()
    except Exception:
        db.rollback()
        task_data.pop('start_minute', None)
        task = DailyTask()
        for key, value in task_data.items():
            if hasattr(task, key):
                setattr(task, key, value)
        db.add(task)
        db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)


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

    query = db.query(DailyTask).filter(DailyTask.plan_id == plan_id)
    if task_date:
        query = query.filter(DailyTask.date <= task_date)
        tasks = query.order_by(DailyTask.created_at.asc()).all()

        result = []
        for t in tasks:
            if _should_repeat(t, task_date):
                completed = _is_completed_on(t, task_date)
                resp = TaskResponse.model_validate(t)
                resp = resp.model_copy(update={
                    "status": "completed" if completed else "pending",
                    "date": task_date,
                })
                result.append(resp)
        return result
    else:
        tasks = query.order_by(DailyTask.created_at.asc()).all()
        return [TaskResponse.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    task = db.query(DailyTask).join(StudyPlan).filter(DailyTask.id == task_id, StudyPlan.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: UUID, data: TaskUpdate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    task = db.query(DailyTask).join(StudyPlan).filter(DailyTask.id == task_id, StudyPlan.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    task = db.query(DailyTask).join(StudyPlan).filter(DailyTask.id == task_id, StudyPlan.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(task)
    db.commit()


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: UUID, task_date: date = Query(None), user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    task = db.query(DailyTask).join(StudyPlan).filter(DailyTask.id == task_id, StudyPlan.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    now = datetime.now(timezone.utc)

    if task.repeat_type == "none" or not task.repeat_type:
        task.status = "completed"
        task.completed_at = now
    else:
        the_date = task_date or date.today()
        date_str = the_date.isoformat()
        if not task.completed_dates:
            task.completed_dates = []
        if date_str not in task.completed_dates:
            task.completed_dates = list(task.completed_dates) + [date_str]

    db.commit()
    db.refresh(task)

    add_fertilize_count(task.plan_id, task.subject, db)

    resp = TaskResponse.model_validate(task)
    if task.repeat_type and task.repeat_type != "none" and task_date:
        resp = resp.model_copy(update={"status": "completed", "date": task_date})
    return resp


@router.post("/{task_id}/uncomplete", response_model=TaskResponse)
def uncomplete_task(task_id: UUID, task_date: date = Query(None), user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    task = db.query(DailyTask).join(StudyPlan).filter(DailyTask.id == task_id, StudyPlan.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.repeat_type == "none" or not task.repeat_type:
        task.status = "pending"
        task.completed_at = None
    else:
        the_date = task_date or date.today()
        date_str = the_date.isoformat()
        if task.completed_dates and date_str in task.completed_dates:
            task.completed_dates = [d for d in task.completed_dates if d != date_str]

    db.commit()
    db.refresh(task)

    resp = TaskResponse.model_validate(task)
    if task.repeat_type and task.repeat_type != "none" and task_date:
        resp = resp.model_copy(update={"status": "pending", "date": task_date})
    return resp


@router.post("/ai/generate")
async def ai_generate_tasks(data: AITaskGenerateRequest, user_id: UUID = Depends(_get_user_id)):
    result = await generate_daily_tasks(data.model_dump())
    return result


@router.post("/ai/parse-plan")
async def ai_parse_plan(data: dict, user_id: UUID = Depends(_get_user_id)):
    """AI解析用户输入的文字计划，提取科目/章节/任务/时长等信息"""
    text = data.get("text", "")
    plan_id = data.get("plan_id", "")
    result = await parse_task_text(text, plan_id)
    return result
