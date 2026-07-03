"""Farm routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from jose import jwt

from database import get_db, Plant, FarmState, StudyPlan
from config import SECRET_KEY, ALGORITHM
from schemas.farm import PlantCreate, PlantUpdate, PlantResponse, FarmStateResponse, FarmResponse

router = APIRouter(prefix="/api/farm", tags=["farm"])


def _get_user_id(authorization: str = Header(None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期")


def _get_or_create_farm_state(plan_id: UUID, db: Session) -> FarmState:
    state = db.query(FarmState).filter(FarmState.plan_id == plan_id).first()
    if not state:
        state = FarmState(plan_id=plan_id, coins=0, experience=0, level=1)
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


@router.get("", response_model=FarmResponse)
def get_farm(
    plan_id: UUID = Query(...),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    plants = db.query(Plant).filter(Plant.plan_id == plan_id).all()
    farm_state = _get_or_create_farm_state(plan_id, db)

    return FarmResponse(
        plants=[PlantResponse.model_validate(p) for p in plants],
        farm_state=FarmStateResponse.model_validate(farm_state) if farm_state else None,
        coins=farm_state.coins,
        experience=farm_state.experience,
        level=farm_state.level
    )


@router.post("/plants", response_model=PlantResponse, status_code=201)
def plant_seed(data: PlantCreate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plan = db.query(StudyPlan).filter(StudyPlan.id == data.plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    # Deduct coins
    farm_state = _get_or_create_farm_state(data.plan_id, db)
    if farm_state.coins < 10:
        raise HTTPException(status_code=400, detail="金币不足")

    farm_state.coins -= 10

    plant = Plant(**data.model_dump())
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return PlantResponse.model_validate(plant)


@router.put("/plants/{plant_id}", response_model=PlantResponse)
def update_plant(plant_id: UUID, data: PlantUpdate, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plant = db.query(Plant).join(StudyPlan).filter(
        Plant.id == plant_id,
        StudyPlan.user_id == user_id
    ).first()
    if not plant:
        raise HTTPException(status_code=404, detail="植物不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(plant, key, value)

    db.commit()
    db.refresh(plant)
    return PlantResponse.model_validate(plant)


@router.post("/plants/{plant_id}/water", response_model=PlantResponse)
def water_plant(plant_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plant = db.query(Plant).join(StudyPlan).filter(
        Plant.id == plant_id,
        StudyPlan.user_id == user_id
    ).first()
    if not plant:
        raise HTTPException(status_code=404, detail="植物不存在")

    if plant.type == "harvested":
        raise HTTPException(status_code=400, detail="已收获的植物不能浇水")

    # Increase progress
    plant.progress = min(100, plant.progress + 15)

    # Update plant type based on progress
    if plant.progress >= 100:
        plant.type = "mature"
    elif plant.progress >= 70:
        plant.type = "growing"
    elif plant.progress >= 30:
        plant.type = "sprout"

    # Add experience
    farm_state = _get_or_create_farm_state(plant.plan_id, db)
    farm_state.experience += 5
    if farm_state.experience >= farm_state.level * 100:
        farm_state.level += 1

    db.commit()
    db.refresh(plant)
    return PlantResponse.model_validate(plant)


@router.post("/plants/{plant_id}/harvest", response_model=PlantResponse)
def harvest_plant(plant_id: UUID, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    plant = db.query(Plant).join(StudyPlan).filter(
        Plant.id == plant_id,
        StudyPlan.user_id == user_id
    ).first()
    if not plant:
        raise HTTPException(status_code=404, detail="植物不存在")

    if plant.type != "mature":
        raise HTTPException(status_code=400, detail="植物尚未成熟")

    plant.type = "harvested"
    plant.progress = 100

    # Reward coins
    farm_state = _get_or_create_farm_state(plant.plan_id, db)
    farm_state.coins += 50
    farm_state.experience += 20

    db.commit()
    db.refresh(plant)
    return PlantResponse.model_validate(plant)