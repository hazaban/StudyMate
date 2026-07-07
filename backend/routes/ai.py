"""AI service routes."""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from jose import jwt

from database import get_db, DailyTask, StudyPlan
from config import SECRET_KEY, ALGORITHM
from services.ai_service import (
    generate_study_plan, generate_daily_tasks,
    generate_flash_cards, generate_daily_review,
    analyze_syllabus_image,
    PlanAgent, TaskAgent, SyllabusAgent
)

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _get_user_id(authorization: str = Header(None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期")


@router.post("/plan")
async def generate_plan(data: dict, user_id: UUID = Depends(_get_user_id)):
    result = await generate_study_plan(data)
    return {"plan": result}


@router.post("/tasks")
async def generate_tasks(data: dict, user_id: UUID = Depends(_get_user_id)):
    result = await generate_daily_tasks(data)
    return result


@router.post("/cards")
async def generate_cards(data: dict, user_id: UUID = Depends(_get_user_id)):
    result = await generate_flash_cards(
        data.get("content", ""),
        data.get("subject", "通用")
    )
    return result


@router.post("/review")
async def generate_review(
    plan_id: UUID,
    task_date: str,
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    """Generate daily review summary."""
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    from datetime import date
    d = date.fromisoformat(task_date) if isinstance(task_date, str) else task_date
    tasks = db.query(DailyTask).filter(DailyTask.plan_id == plan_id, DailyTask.date == d).all()

    planned = len(tasks)
    completed = sum(1 for t in tasks if t.status == "completed")
    planned_time = sum(t.duration for t in tasks)
    actual_time = sum(t.duration for t in tasks if t.status == "completed")

    result = await generate_daily_review(
        planned_tasks=[t.content for t in tasks],
        completed_tasks=[t.content for t in tasks if t.status == "completed"],
        planned_time=planned_time,
        actual_time=actual_time
    )
    return result


@router.post("/syllabus")
async def analyze_syllabus(request: Request, user_id: UUID = Depends(_get_user_id)):
    """Analyze a syllabus image using Qwen Vision. Returns chapter-level study plan."""
    import json as _json
    body = await request.body()
    data = _json.loads(body) if body else {}
    result = await analyze_syllabus_image(
        data.get("image", ""),
        data.get("subject", ""),
        data.get("description", "")
    )
    return result


@router.post("/chat")
async def ai_chat(request: Request, user_id: UUID = Depends(_get_user_id)):
    """Unified AI chat endpoint. PlanAgent analyzes intent and coordinates TaskAgent/SyllabusAgent."""
    import json as _json
    body = await request.body()
    data = _json.loads(body) if body else {}

    text = data.get("text", "")
    image_url = data.get("image", "")
    plan_id = data.get("plan_id", None)

    if not text and not image_url:
        raise HTTPException(status_code=400, detail="请提供文本或图片输入")

    result = await PlanAgent.run(text, image_url, plan_id)
    return result


@router.post("/parse-task")
async def parse_task(request: Request, user_id: UUID = Depends(_get_user_id)):
    """直接调用 TaskAgent 解析任务，不走意图识别。用于添加任务弹窗等明确场景。"""
    import json as _json
    body = await request.body()
    data = _json.loads(body) if body else {}

    text = data.get("text", "")
    image_url = data.get("image", "")

    if not text and not image_url:
        raise HTTPException(status_code=400, detail="请提供文本或图片输入")

    result = await TaskAgent.parse(text, image_url)
    return result