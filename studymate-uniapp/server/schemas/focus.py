"""Schemas for focus records."""
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class FocusRecordCreate(BaseModel):
    plan_id: UUID
    date: date
    type: str = "focus"
    subject: str = ""
    task_id: Optional[UUID] = None
    task_name: str = ""
    duration: int = 25
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    note: str = ""


class FocusRecordUpdate(BaseModel):
    type: Optional[str] = None
    subject: Optional[str] = None
    task_id: Optional[UUID] = None
    task_name: Optional[str] = None
    duration: Optional[int] = None
    note: Optional[str] = None


class FocusRecordResponse(BaseModel):
    id: UUID
    plan_id: UUID
    user_id: UUID
    date: date
    type: str
    subject: str
    task_id: Optional[UUID] = None
    task_name: str
    duration: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    note: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FocusStatsResponse(BaseModel):
    total_minutes: int
    total_sessions: int
    avg_minutes: float
