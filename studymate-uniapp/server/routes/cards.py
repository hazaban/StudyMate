"""Flash card routes."""

from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from jose import jwt

from database import get_db, FlashCard, StudyPlan
from config import SECRET_KEY, ALGORITHM
from schemas.card import CardCreate, CardUpdate, CardResponse, AICardGenerateRequest, CardListResponse
from services.ai_service import generate_flash_cards
from services.memory import calculate_next_review_date, update_mastery_level

router = APIRouter(prefix="/api/cards", tags=["cards"])


def _get_user_id(authorization: str = Header(None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期")


@router.post("", response_model=CardResponse, status_code=201)
def create_card(data: CardCreate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plan = db.query(StudyPlan).filter(StudyPlan.id == data.plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    card = FlashCard(**data.model_dump())
    db.add(card)
    db.commit()
    db.refresh(card)
    return CardResponse.model_validate(card)


@router.get("", response_model=CardListResponse)
def list_cards(
    plan_id: UUID = Query(...),
    subject: str = Query(None),
    tag: str = Query(None),
    pending: str = Query(None),  # "1" = only show due today
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    query = db.query(FlashCard).filter(FlashCard.plan_id == plan_id)
    if subject:
        query = query.filter(FlashCard.subject == subject)
    if pending == "1":
        today = date.today()
        query = query.filter(FlashCard.next_review_date <= today)

    cards = query.order_by(FlashCard.next_review_date.asc()).all()

    # Filter by tag on the Python side (JSON array matching)
    if tag:
        cards = [c for c in cards if c.tags and tag in (c.tags or [])]

    return CardListResponse(
        cards=[CardResponse.model_validate(c) for c in cards],
        total=len(cards)
    )


@router.get("/pending", response_model=CardListResponse)
def list_pending_cards(
    plan_id: UUID = Query(...),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    today = date.today()
    cards = db.query(FlashCard).filter(
        FlashCard.plan_id == plan_id,
        FlashCard.next_review_date <= today
    ).order_by(FlashCard.next_review_date.asc()).all()

    return CardListResponse(
        cards=[CardResponse.model_validate(c) for c in cards],
        total=len(cards)
    )


@router.get("/subjects")
def get_card_subjects(
    plan_id: UUID = Query(...),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    """Get distinct subjects for cards under a plan."""
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    subjects = db.query(FlashCard.subject).filter(FlashCard.plan_id == plan_id).distinct().all()
    return {"subjects": [s[0] for s in subjects]}


@router.get("/tags/by-subject")
def get_card_tags_by_subject(
    plan_id: UUID = Query(...),
    subject: str = Query(None),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    """Get tags for cards, optionally filtered by subject."""
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    query = db.query(FlashCard.tags).filter(FlashCard.plan_id == plan_id)
    if subject:
        query = query.filter(FlashCard.subject == subject)
    rows = query.all()
    tag_set = set()
    for r in rows:
        if r[0]:
            for t in r[0]:
                tag_set.add(t)
    return {"tags": sorted(tag_set)}


@router.get("/export")
def export_cards(
    plan_id: UUID = Query(...),
    subject: str = Query(None),
    tag: str = Query(None),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    """Export cards data (returns full list for client-side export)."""
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    query = db.query(FlashCard).filter(FlashCard.plan_id == plan_id)
    if subject:
        query = query.filter(FlashCard.subject == subject)
    if tag:
        cards = query.order_by(FlashCard.created_at.desc()).all()
        cards = [c for c in cards if c.tags and tag in (c.tags or [])]
    else:
        cards = query.order_by(FlashCard.created_at.desc()).all()
    return {
        "cards": [CardResponse.model_validate(c).model_dump(mode='json') for c in cards],
        "total": len(cards)
    }


@router.get("/{card_id}", response_model=CardResponse)
def get_card(card_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    card = db.query(FlashCard).join(StudyPlan).filter(
        FlashCard.id == card_id,
        StudyPlan.user_id == user_id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    return CardResponse.model_validate(card)


@router.put("/{card_id}", response_model=CardResponse)
def update_card(card_id: UUID, data: CardUpdate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    card = db.query(FlashCard).join(StudyPlan).filter(
        FlashCard.id == card_id,
        StudyPlan.user_id == user_id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(card, key, value)

    db.commit()
    db.refresh(card)
    return CardResponse.model_validate(card)


@router.delete("/{card_id}", status_code=204)
def delete_card(card_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    card = db.query(FlashCard).join(StudyPlan).filter(
        FlashCard.id == card_id,
        StudyPlan.user_id == user_id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    db.delete(card)
    db.commit()


@router.post("/{card_id}/review", response_model=CardResponse)
def review_card(card_id: UUID, mastery_level: str = Query(...), user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    """Mark a card's mastery level and update the next review date."""
    card = db.query(FlashCard).join(StudyPlan).filter(
        FlashCard.id == card_id,
        StudyPlan.user_id == user_id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")

    card.mastery_level = mastery_level
    card.review_count += 1
    card.next_review_date = calculate_next_review_date(
        card.next_review_date, mastery_level, card.review_count,
        created_at=card.created_at.date()
    )

    db.commit()
    db.refresh(card)
    return CardResponse.model_validate(card)


@router.post("/ai/generate")
async def ai_generate_cards(data: AICardGenerateRequest, user_id: UUID = Depends(_get_user_id)):
    result = await generate_flash_cards(data.content, data.subject)
    return result