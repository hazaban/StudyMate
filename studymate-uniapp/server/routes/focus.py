"""Focus record routes (番茄钟记录)."""

from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from jose import jwt

from database import get_db, FocusRecord, StudyPlan
from config import SECRET_KEY, ALGORITHM
from schemas.focus import FocusRecordCreate, FocusRecordUpdate, FocusRecordResponse

router = APIRouter(prefix="/api/focus", tags=["focus"])


def _get_user_id(authorization: str = Header(None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期")


@router.post("", response_model=FocusRecordResponse, status_code=201)
def create_record(data: FocusRecordCreate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plan = db.query(StudyPlan).filter(StudyPlan.id == data.plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    record = FocusRecord(**data.model_dump(), user_id=user_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return FocusRecordResponse.model_validate(record)


@router.get("", response_model=list[FocusRecordResponse])
def list_records(
    plan_id: UUID = Query(...),
    start_date: date = Query(None),
    end_date: date = Query(None),
    subject: str = Query(None),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    query = db.query(FocusRecord).filter(FocusRecord.plan_id == plan_id)
    if start_date:
        query = query.filter(FocusRecord.date >= start_date)
    if end_date:
        query = query.filter(FocusRecord.date <= end_date)
    if subject:
        query = query.filter(FocusRecord.subject == subject)
    query = query.order_by(FocusRecord.date.desc(), FocusRecord.created_at.desc())
    records = query.all()
    return [FocusRecordResponse.model_validate(r) for r in records]


@router.get("/stats")
def get_stats(
    plan_id: UUID = Query(...),
    start_date: date = Query(None),
    end_date: date = Query(None),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    query = db.query(FocusRecord).filter(FocusRecord.plan_id == plan_id, FocusRecord.type == "focus")
    if start_date:
        query = query.filter(FocusRecord.date >= start_date)
    if end_date:
        query = query.filter(FocusRecord.date <= end_date)

    total = query.with_entities(
        func.coalesce(func.sum(FocusRecord.duration), 0).label("total_minutes"),
        func.count(FocusRecord.id).label("total_sessions")
    ).first()

    days = 1
    if start_date and end_date:
        days = (end_date - start_date).days + 1
    elif end_date:
        days = 30
    else:
        days = 30

    total_minutes = int(total.total_minutes or 0)
    total_sessions = int(total.total_sessions or 0)
    avg_minutes = round(total_minutes / max(days, 1), 1)

    return {
        "total_minutes": total_minutes,
        "total_sessions": total_sessions,
        "avg_minutes": avg_minutes
    }


@router.get("/stats/subject")
def get_subject_stats(
    plan_id: UUID = Query(...),
    start_date: date = Query(None),
    end_date: date = Query(None),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    query = db.query(FocusRecord).filter(FocusRecord.plan_id == plan_id, FocusRecord.type == "focus")
    if start_date:
        query = query.filter(FocusRecord.date >= start_date)
    if end_date:
        query = query.filter(FocusRecord.date <= end_date)

    results = query.with_entities(
        FocusRecord.subject,
        func.coalesce(func.sum(FocusRecord.duration), 0).label("minutes"),
        func.count(FocusRecord.id).label("sessions")
    ).group_by(FocusRecord.subject).all()

    return [
        {
            "subject": r.subject or "未分类",
            "minutes": int(r.minutes or 0),
            "sessions": int(r.sessions or 0)
        }
        for r in results
    ]


@router.get("/stats/daily")
def get_daily_stats(
    plan_id: UUID = Query(...),
    start_date: date = Query(None),
    end_date: date = Query(None),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    query = db.query(FocusRecord).filter(FocusRecord.plan_id == plan_id, FocusRecord.type == "focus")
    if start_date:
        query = query.filter(FocusRecord.date >= start_date)
    if end_date:
        query = query.filter(FocusRecord.date <= end_date)

    results = query.with_entities(
        FocusRecord.date,
        func.coalesce(func.sum(FocusRecord.duration), 0).label("minutes"),
        func.count(FocusRecord.id).label("sessions")
    ).group_by(FocusRecord.date).order_by(FocusRecord.date.asc()).all()

    return [
        {
            "date": r.date.isoformat(),
            "minutes": int(r.minutes or 0),
            "sessions": int(r.sessions or 0)
        }
        for r in results
    ]


@router.put("/{record_id}", response_model=FocusRecordResponse)
def update_record(record_id: UUID, data: FocusRecordUpdate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    record = db.query(FocusRecord).filter(FocusRecord.id == record_id).first()
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
    return FocusRecordResponse.model_validate(record)


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    record = db.query(FocusRecord).filter(FocusRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    plan = db.query(StudyPlan).filter(StudyPlan.id == record.plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=403, detail="无权限")

    db.delete(record)
    db.commit()
    return None
