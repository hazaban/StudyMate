"""Mistake book routes."""

from uuid import UUID

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

    mistake = Mistake(**data.model_dump())
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

    mistakes = query.order_by(Mistake.created_at.desc()).all()
    return MistakeListResponse(
        mistakes=[MistakeResponse.model_validate(m) for m in mistakes],
        total=len(mistakes)
    )


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


@router.post("/{mistake_id}/master", response_model=MistakeResponse)
def mark_mastered(mistake_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    """标记错题已掌握。"""
    mistake = db.query(Mistake).join(StudyPlan).filter(
        Mistake.id == mistake_id,
        StudyPlan.user_id == user_id
    ).first()
    if not mistake:
        raise HTTPException(status_code=404, detail="错题不存在")

    mistake.mastered = "1"
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
    db.commit()
    db.refresh(mistake)
    return MistakeResponse.model_validate(mistake)