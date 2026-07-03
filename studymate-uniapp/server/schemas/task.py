"""Pydantic schemas for DailyTask."""

from datetime import date, datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class TaskCreate(BaseModel):
    plan_id: UUID
    date: date
    type: str  # new_study / review / mistake
    subject: str
    content: str
    chapter: str = ""
    duration: int = 25
    actual_duration: int = 0
    status: str = "pending"


class TaskUpdate(BaseModel):
    type: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    chapter: Optional[str] = None
    duration: Optional[int] = None
    actual_duration: Optional[int] = None
    status: Optional[str] = None
    completed_at: Optional[datetime] = None
    proof_image_url: Optional[str] = None


class TaskResponse(BaseModel):
    id: UUID
    plan_id: UUID
    date: date
    type: str
    subject: str
    content: str
    chapter: str
    duration: int
    actual_duration: int
    status: str
    completed_at: Optional[datetime]
    proof_image_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AITaskGenerateRequest(BaseModel):
    exam_name: str
    date: date
    subjects: list[str] = []
    days_remaining: int = 0
    available_time: int = 480