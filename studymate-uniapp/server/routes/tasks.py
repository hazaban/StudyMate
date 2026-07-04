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


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plan = db.query(StudyPlan).filter(StudyPlan.id == data.plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    task = DailyTask(**data.model_dump())
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
        query = query.filter(DailyTask.date == task_date)
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
    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    add_fertilize_count(task.plan_id, task.subject, db)
    return TaskResponse.model_validate(task)


@router.post("/{task_id}/uncomplete", response_model=TaskResponse)
def uncomplete_task(task_id: UUID, task_date: date = Query(None), user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    task = db.query(DailyTask).join(StudyPlan).filter(DailyTask.id == task_id, StudyPlan.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    task.status = "pending"
    task.completed_at = None
    db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)


@router.post("/ai/generate")
async def ai_generate_tasks(data: AITaskGenerateRequest, user_id: UUID = Depends(_get_user_id)):
    result = await generate_daily_tasks(data.model_dump())
    return result
