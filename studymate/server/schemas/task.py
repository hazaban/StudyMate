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
    duration: int = 25
    status: str = "pending"
    repeat_type: str = "none"  # none / daily / weekday / holiday
    actual_duration: int = 0
    chapter: str = ""
    importance: str = ""  # important_urgent / important_not_urgent / urgent_not_important / not_important_not_urgent


class TaskUpdate(BaseModel):
    type: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    duration: Optional[int] = None
    status: Optional[str] = None
    completed_at: Optional[datetime] = None
    proof_image_url: Optional[str] = None
    repeat_type: Optional[str] = None
    actual_duration: Optional[int] = None
    chapter: Optional[str] = None
    importance: Optional[str] = None


class TaskResponse(BaseModel):
    id: UUID
    plan_id: UUID
    date: date
    type: str
    subject: str
    content: str
    duration: int
    status: str
    completed_at: Optional[datetime]
    proof_image_url: str
    repeat_type: str = "none"
    completed_dates: list[str] = []
    actual_duration: int = 0
    chapter: str = ""
    importance: str = ""
    created_at: datetime

    model_config = {"from_attributes": True}


class AITaskGenerateRequest(BaseModel):
    exam_name: str
    date: date
    subjects: list[str] = []
    days_remaining: int = 0
    available_time: int = 480
