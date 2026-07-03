"""Pydantic schemas for FlashCard."""

from datetime import date, datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class CardCreate(BaseModel):
    plan_id: UUID
    question: str
    answer: str
    subject: str
    mastery_level: str = "unmastered"
    next_review_date: date
    image_urls: list[str] = []


class CardUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    subject: Optional[str] = None
    mastery_level: Optional[str] = None
    next_review_date: Optional[date] = None
    review_count: Optional[int] = None
    image_urls: Optional[list[str]] = None


class CardResponse(BaseModel):
    id: UUID
    plan_id: UUID
    question: str
    answer: str
    subject: str
    mastery_level: str
    next_review_date: date
    review_count: int
    image_urls: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AICardGenerateRequest(BaseModel):
    content: str
    subject: str = "通用"


class CardListResponse(BaseModel):
    cards: list[CardResponse]
    total: int