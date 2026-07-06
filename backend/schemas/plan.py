"""Pydantic schemas for StudyPlan."""

from datetime import date, datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class PlanCreate(BaseModel):
    exam_name: str
    exam_date: date
    target_scores: dict = {}
    daily_study_time: int = 480
    weak_points: list[str] = []
    notes: str = ""
    ai_plan: Optional[dict] = None
    subjects: list = []


class PlanUpdate(BaseModel):
    exam_name: Optional[str] = None
    exam_date: Optional[date] = None
    target_scores: Optional[dict] = None
    daily_study_time: Optional[int] = None
    weak_points: Optional[list[str]] = None
    notes: Optional[str] = None
    ai_plan: Optional[dict] = None
    subjects: Optional[list] = None


class PlanResponse(BaseModel):
    id: UUID
    user_id: UUID
    exam_name: str
    exam_date: date
    target_scores: dict
    daily_study_time: int
    weak_points: list[str]
    notes: str
    ai_plan: Optional[dict]
    subjects: list = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIPlanGenerateRequest(BaseModel):
    exam_name: str
    exam_date: date
    target_scores: dict = {}
    daily_study_time: int = 480
    weak_points: list[str] = []
    subjects: list = []
