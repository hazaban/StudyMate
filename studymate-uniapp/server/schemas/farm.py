"""Pydantic schemas for Farm."""

from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class PlantCreate(BaseModel):
    plan_id: UUID
    subject: str
    type: str = "seed"
    progress: int = 0


class PlantUpdate(BaseModel):
    type: Optional[str] = None
    progress: Optional[int] = None


class PlantResponse(BaseModel):
    id: UUID
    plan_id: UUID
    type: str
    subject: str
    progress: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FarmStateResponse(BaseModel):
    id: UUID
    plan_id: UUID
    coins: int
    experience: int
    level: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class FarmResponse(BaseModel):
    plants: list[PlantResponse]
    farm_state: Optional[FarmStateResponse]
    coins: int
    experience: int
    level: int