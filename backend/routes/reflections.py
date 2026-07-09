"""Task reflection routes (任务反思记录)."""

from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session

from database import get_db, TaskReflection, StudyPlan, DailyTask
from config import SECRET_KEY, ALGORITHM
from schemas.reflection import TaskReflectionCreate, TaskReflectionUpdate, TaskReflectionResponse

router = APIRouter(prefix="/api/reflections", tags=["reflections"])


def _get_user_id(authorization: str = Header(None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        from jose import jwt
        payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期")


@router.post("", response_model=TaskReflectionResponse, status_code=201)
def create_reflection(data: TaskReflectionCreate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plan = db.query(StudyPlan).filter(StudyPlan.id == data.plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    task = db.query(DailyTask).filter(DailyTask.id == data.task_id, DailyTask.plan_id == data.plan_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    existing = db.query(TaskReflection).filter(
        TaskReflection.task_id == data.task_id,
        TaskReflection.task_date == data.task_date
    ).first()
    if existing:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return TaskReflectionResponse.model_validate(existing)

    record = TaskReflection(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return TaskReflectionResponse.model_validate(record)


@router.get("", response_model=list[TaskReflectionResponse])
def list_reflections(
    plan_id: UUID = Query(...),
    task_date: date = Query(None),
    task_id: UUID = Query(None),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    query = db.query(TaskReflection).filter(TaskReflection.plan_id == plan_id)
    if task_date:
        query = query.filter(TaskReflection.task_date == task_date)
    if task_id:
        query = query.filter(TaskReflection.task_id == task_id)
    query = query.order_by(TaskReflection.task_date.desc(), TaskReflection.created_at.desc())
    records = query.all()
    return [TaskReflectionResponse.model_validate(r) for r in records]


@router.get("/{record_id}", response_model=TaskReflectionResponse)
def get_reflection(record_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    record = db.query(TaskReflection).filter(TaskReflection.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    plan = db.query(StudyPlan).filter(StudyPlan.id == record.plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=403, detail="无权限")
    return TaskReflectionResponse.model_validate(record)


@router.put("/{record_id}", response_model=TaskReflectionResponse)
def update_reflection(record_id: UUID, data: TaskReflectionUpdate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    record = db.query(TaskReflection).filter(TaskReflection.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    plan = db.query(StudyPlan).filter(StudyPlan.id == record.plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=403, detail="无权限")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return TaskReflectionResponse.model_validate(record)


@router.delete("/{record_id}", status_code=204)
def delete_reflection(record_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    record = db.query(TaskReflection).filter(TaskReflection.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    plan = db.query(StudyPlan).filter(StudyPlan.id == record.plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=403, detail="无权限")

    db.delete(record)
    db.commit()
    return None
