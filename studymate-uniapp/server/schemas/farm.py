"""Pydantic schemas for Farm."""

from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, field_validator


class PlantCreate(BaseModel):
    plan_id: UUID
    subject: str
    type: str = "seed"
    progress: int = 0
    water_count: int = 0
    fertilize_count: int = 0


class PlantUpdate(BaseModel):
    type: Optional[str] = None
    progress: Optional[int] = None
    water_count: Optional[int] = None
    fertilize_count: Optional[int] = None


class PlantResponse(BaseModel):
    id: UUID
    plan_id: UUID
    type: str
    subject: str
    progress: int
    water_count: int
    fertilize_count: int
    created_at: datetime
    updated_at: datetime

    @field_validator("water_count", "fertilize_count", mode="before")
    @classmethod
    def null_to_zero(cls, v: int | None) -> int:
        """Fix old DB rows where migration left these columns NULL."""
        return v if v is not None else 0

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
