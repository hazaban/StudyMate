"""Pydantic schemas for TaskReflection."""

from datetime import date, datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class TaskReflectionCreate(BaseModel):
    task_id: UUID
    plan_id: UUID
    task_date: date
    actual_duration: int = 0
    completion_issues: str = ""
    incomplete_reason: str = ""


class TaskReflectionUpdate(BaseModel):
    actual_duration: Optional[int] = None
    completion_issues: Optional[str] = None
    incomplete_reason: Optional[str] = None


class TaskReflectionResponse(BaseModel):
    id: UUID
    task_id: UUID
    plan_id: UUID
    task_date: date
    actual_duration: int
    completion_issues: str
    incomplete_reason: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
