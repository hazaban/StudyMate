"""Export routes for cards and mistakes (Excel/PDF)."""

from uuid import UUID
from datetime import date
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from jose import jwt

from database import get_db, FlashCard, Mistake, StudyPlan
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/api/export", tags=["export"])


def _get_user_id(authorization: str = Header(None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期")


def _escape_csv_field(val):
    """Escape a CSV field."""
    if val is None:
        return ""
    s = str(val).replace('"', '""')
    if "," in s or "\n" in s or '"' in s:
        return f'"{s}"'
    return s


def _generate_csv(headers: list, rows: list[list]) -> str:
    """Generate CSV content."""
    lines = [",".join(_escape_csv_field(h) for h in headers)]
    for row in rows:
        lines.append(",".join(_escape_csv_field(c) for c in row))
    return "\n".join(lines)


@router.get("/cards/csv")
def export_cards_csv(
    plan_id: UUID = Query(...),
    subject: str = Query(None),
    tag: str = Query(None),
    mastery_level: str = Query(None),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    query = db.query(FlashCard).filter(FlashCard.plan_id == plan_id)
    if subject:
        query = query.filter(FlashCard.subject == subject)
    if mastery_level:
        query = query.filter(FlashCard.mastery_level == mastery_level)

    cards = query.order_by(FlashCard.created_at.desc()).all()

    # Filter by tag on Python side
    if tag:
        cards = [c for c in cards if c.tags and tag in (c.tags or [])]

    headers = ["科目", "问题", "答案", "掌握程度", "复习次数", "标签", "下次复习日期", "创建日期"]
    rows = []
    for c in cards:
        rows.append([
            c.subject,
            c.question,
            c.answer,
            c.mastery_level,
            str(c.review_count),
            ", ".join(c.tags or []),
            str(c.next_review_date) if c.next_review_date else "",
            str(c.created_at.date()) if c.created_at else ""
        ])

    csv_content = _generate_csv(headers, rows)
    # Add BOM for Excel compatibility
    csv_bytes = ("\ufeff" + csv_content).encode("utf-8")

    return StreamingResponse(
        BytesIO(csv_bytes),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=knowledge_cards.csv"}
    )


@router.get("/mistakes/csv")
def export_mistakes_csv(
    plan_id: UUID = Query(...),
    subject: str = Query(None),
    tag: str = Query(None),
    difficulty: str = Query(None),
    mastered: str = Query(None),
    user_id: UUID = Depends(_get_user_id),
    db: Session = Depends(get_db)
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id, StudyPlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    query = db.query(Mistake).filter(Mistake.plan_id == plan_id)
    if subject:
        query = query.filter(Mistake.subject == subject)
    if difficulty:
        query = query.filter(Mistake.difficulty == difficulty)
    if mastered is not None:
        query = query.filter(Mistake.mastered == mastered)

    mistakes = query.order_by(Mistake.created_at.desc()).all()

    # Filter by tag
    if tag:
        mistakes = [m for m in mistakes if m.tags and tag in (m.tags or [])]

    headers = ["科目", "题目", "答案", "错误分析", "难度", "错误次数", "正确次数", "是否掌握", "标签", "下次复习日期", "创建日期"]
    rows = []
    for m in mistakes:
        rows.append([
            m.subject,
            m.question,
            m.answer,
            m.analysis or "",
            m.difficulty,
            str(m.error_count),
            str(m.correct_count),
            "已掌握" if m.mastered == "1" else "未掌握",
            ", ".join(m.tags or []),
            str(m.next_review_date) if m.next_review_date else "",
            str(m.created_at.date()) if m.created_at else ""
        ])

    csv_content = _generate_csv(headers, rows)
    csv_bytes = ("\ufeff" + csv_content).encode("utf-8")

    return StreamingResponse(
        BytesIO(csv_bytes),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=mistakes.csv"}
    )