"""Pydantic schemas for Mistake."""

from datetime import date, datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class MistakeCreate(BaseModel):
    plan_id: UUID
    question: str
    answer: str
    subject: str
    analysis: str = ""
    difficulty: str = "medium"
    image_urls: list[str] = []
    tags: list[str] = []
    next_review_date: date = None


class MistakeUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    subject: Optional[str] = None
    analysis: Optional[str] = None
    difficulty: Optional[str] = None
    image_urls: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    error_count: Optional[int] = None
    correct_count: Optional[int] = None
    mastered: Optional[str] = None
    next_review_date: Optional[date] = None


class MistakeResponse(BaseModel):
    id: UUID
    plan_id: UUID
    question: str
    answer: str
    analysis: str
    subject: str
    difficulty: str
    image_urls: list[str] = []
    tags: list[str] = []
    error_count: int
    correct_count: int
    mastered: str
    next_review_date: date
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MistakeListResponse(BaseModel):
    mistakes: list[MistakeResponse]
    total: int