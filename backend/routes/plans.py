"""Study plan routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from jose import jwt

from database import get_db, User, StudyPlan
from config import SECRET_KEY, ALGORITHM
from schemas.plan import PlanCreate, PlanUpdate, PlanResponse, AIPlanGenerateRequest
from services.ai_service import generate_study_plan

router = APIRouter(prefix="/api/plans", tags=["plans"])


def _get_user_id(authorization: str = Header(None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期")


@router.post("", response_model=PlanResponse, status_code=201)
def create_plan(data: PlanCreate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plan = StudyPlan(user_id=user_id, **data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return PlanResponse.model_validate(plan)


@router.get("", response_model=list[PlanResponse])
def list_plans(user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plans = db.query(StudyPlan).filter(StudyPlan.user_id == user_id).order_by(StudyPlan.created_at.desc()).all()
    return [PlanResponse.model_validate(p) for p in plans]


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    return PlanResponse.model_validate(plan)


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: UUID, data: PlanUpdate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, key, value)

    db.commit()
    db.refresh(plan)
    return PlanResponse.model_validate(plan)


@router.delete("/{plan_id}", status_code=204)
def delete_plan(plan_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    db.delete(plan)
    db.commit()


@router.post("/ai/generate")
async def ai_generate_plan(data: AIPlanGenerateRequest, user_id: UUID = Depends(_get_user_id)):
    result = await generate_study_plan(data.model_dump())
    return {"plan": result}


@router.post("/ai/phases")
async def ai_generate_phases(data: dict, user_id: UUID = Depends(_get_user_id)):
    """AI 为每个科目建议阶段划分（第几周到第几周做什么）"""
    from services.ai_service import generate_subject_phases
    result = await generate_subject_phases(data)
    return result