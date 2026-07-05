"""Mistake book routes."""

from uuid import UUID
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from jose import jwt

from database import get_db, Mistake, StudyPlan
from config import SECRET_KEY, ALGORITHM
from schemas.mistake import MistakeCreate, MistakeUpdate, MistakeResponse, MistakeListResponse

router = APIRouter(prefix="/api/mistakes", tags=["mistakes"])


def _get_user_id(authorization: str = Header(None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期")


@router.post("", response_model=MistakeResponse, status_code=201)
def create_mistake(data: MistakeCreate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    """手动添加错题，支持文字和图片。"""
    plan = db.query(StudyPlan).filter(StudyPlan.id == data.plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    create_data = data.model_dump()
    # Set default next_review_date to today so it appears in today's review
    if not create_data.get("next_review_date"):
        create_data["next_review_date"] = date.today()

    mistake = Mistake(**create_data)
    db.add(mistake)
    db.commit()
    db.refresh(mistake)
    return MistakeResponse.model_validate(mistake)


@router.get("", response_model=MistakeListResponse)
def list_mistakes(
    plan_id: UUID = Query(...),
    subject: str = Query(None),
    difficulty: str = Query(None),
    mastered: str = Query(None),
    tag: str = Query(None),
    pending: str = Query(None),  # "1" = only show due today
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    query = db.query(Mistake).filter(Mistake.plan_id == plan_id)
    if subject:
        query = query.filter(Mistake.subject == subject)
    if difficulty:
        query = query.filter(Mistake.difficulty == difficulty)
    if mastered is not None:
        query = query.filter(Mistake.mastered == mastered)
    if pending == "1":
        today = date.today()
        query = query.filter(Mistake.next_review_date <= today, Mistake.mastered == "0")

    mistakes = query.order_by(Mistake.next_review_date.asc()).all()

    # Filter by tag on the Python side (JSON array matching)
    if tag:
        mistakes = [m for m in mistakes if m.tags and tag in (m.tags or [])]

    return MistakeListResponse(
        mistakes=[MistakeResponse.model_validate(m) for m in mistakes],
        total=len(mistakes)
    )


@router.get("/subjects")
def get_mistake_subjects(
    plan_id: UUID = Query(...),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    """Get distinct subjects for mistakes under a plan."""
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    subjects = db.query(Mistake.subject).filter(Mistake.plan_id == plan_id).distinct().all()
    return {"subjects": [s[0] for s in subjects]}


@router.get("/tags/by-subject")
def get_mistake_tags_by_subject(
    plan_id: UUID = Query(...),
    subject: str = Query(None),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    """Get tags for mistakes, optionally filtered by subject."""
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    query = db.query(Mistake.tags).filter(Mistake.plan_id == plan_id)
    if subject:
        query = query.filter(Mistake.subject == subject)
    rows = query.all()
    tag_set = set()
    for r in rows:
        if r[0]:
            for t in r[0]:
                tag_set.add(t)
    return {"tags": sorted(tag_set)}


@router.get("/export")
def export_mistakes(
    plan_id: UUID = Query(...),
    subject: str = Query(None),
    tag: str = Query(None),
    difficulty: str = Query(None),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    """Export mistakes data (returns full list for client-side export)."""
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    query = db.query(Mistake).filter(Mistake.plan_id == plan_id)
    if subject:
        query = query.filter(Mistake.subject == subject)
    if difficulty:
        query = query.filter(Mistake.difficulty == difficulty)
    if tag:
        mistakes = query.order_by(Mistake.created_at.desc()).all()
        mistakes = [m for m in mistakes if m.tags and tag in (m.tags or [])]
    else:
        mistakes = query.order_by(Mistake.created_at.desc()).all()
    return {
        "mistakes": [MistakeResponse.model_validate(m).model_dump(mode='json') for m in mistakes],
        "total": len(mistakes)
    }


@router.get("/{mistake_id}", response_model=MistakeResponse)
def get_mistake(mistake_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    mistake = db.query(Mistake).join(StudyPlan).filter(
        Mistake.id == mistake_id,
        StudyPlan.user_id == user_id
    ).first()
    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")
    return MistakeResponse.model_validate(mistake)


@router.put("/{mistake_id}", response_model=MistakeResponse)
def update_mistake(mistake_id: UUID, data: MistakeUpdate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    mistake = db.query(Mistake).join(StudyPlan).filter(
        Mistake.id == mistake_id,
        StudyPlan.user_id == user_id
    ).first()
    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(mistake, key, value)

    db.commit()
    db.refresh(mistake)
    return MistakeResponse.model_validate(mistake)


@router.delete("/{mistake_id}", status_code=204)
def delete_mistake(mistake_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    mistake = db.query(Mistake).join(StudyPlan).filter(
        Mistake.id == mistake_id,
        StudyPlan.user_id == user_id
    ).first()
    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")
    db.delete(mistake)
    db.commit()


@router.post("/{mistake_id}/review", response_model=MistakeResponse)
def review_mistake(mistake_id: UUID, correct: bool = Query(...), user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    """复习错题：做对+1分，连续做对3次标记已掌握；做错清零。按艾宾浩斯曲线推算下次复习日期。"""
    mistake = db.query(Mistake).join(StudyPlan).filter(
        Mistake.id == mistake_id,
        StudyPlan.user_id == user_id
    ).first()
    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")

    today = date.today()

    if correct:
        mistake.correct_count += 1
        intervals = [1, 3, 7, 14, 30]
        idx = min(mistake.correct_count - 1, len(intervals) - 1)
        next_date = today + timedelta(days=intervals[idx])
        created = mistake.created_at.date() if mistake.created_at else today
        if next_date < created:
            next_date = created + timedelta(days=1)
        mistake.next_review_date = next_date

        # Auto mastered after 3 consecutive correct answers, fix at 30-day review
        if mistake.correct_count >= 3:
            mistake.mastered = "1"
            mistake.next_review_date = today + timedelta(days=30)
    else:
        mistake.correct_count = 0
        mistake.error_count += 1
        mistake.mastered = "0"
        # Review again tomorrow, but never before creation date
        next_date = today + timedelta(days=1)
        created = mistake.created_at.date() if mistake.created_at else today
        if next_date < created:
            next_date = created + timedelta(days=1)
        mistake.next_review_date = next_date

    db.commit()
    db.refresh(mistake)
    return MistakeResponse.model_validate(mistake)


@router.post("/{mistake_id}/master", response_model=MistakeResponse)
def mark_mastered(mistake_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    """手动标记错题已掌握 — 同步 correct_count=3 + next_review=30天后。"""
    mistake = db.query(Mistake).join(StudyPlan).filter(
        Mistake.id == mistake_id,
        StudyPlan.user_id == user_id
    ).first()
    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")

    today = date.today()
    mistake.mastered = "1"
    mistake.next_review_date = today + timedelta(days=30)
    db.commit()
    db.refresh(mistake)
    return MistakeResponse.model_validate(mistake)


@router.post("/{mistake_id}/retry", response_model=MistakeResponse)
def retry_mistake(mistake_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    """记录一次重新做错。"""
    mistake = db.query(Mistake).join(StudyPlan).filter(
        Mistake.id == mistake_id,
        StudyPlan.user_id == user_id
    ).first()
    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")

    mistake.error_count += 1
    mistake.correct_count = 0
    mistake.mastered = "0"
    mistake.next_review_date = date.today() + timedelta(days=1)
    db.commit()
    db.refresh(mistake)
    return MistakeResponse.model_validate(mistake)