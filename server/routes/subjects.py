"""User-defined subjects routes."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from jose import jwt
import json

from database import get_db, UserSubject
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


def _get_user_id(authorization: str = Header(None)) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
        return UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期")


@router.get("")
def get_subjects(user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    rows = db.query(UserSubject).filter(UserSubject.user_id == user_id).order_by(UserSubject.name).all()
    return {"subjects": [r.name for r in rows]}


@router.post("", status_code=201)
def add_subject(data: dict, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="科目名不能为空")
    existing = db.query(UserSubject).filter(UserSubject.user_id == user_id, UserSubject.name == name).first()
    if existing:
        return {"subject": name, "message": "already exists"}
    subj = UserSubject(user_id=user_id, name=name)
    db.add(subj)
    db.commit()
    return {"subject": name, "message": "created"}


@router.delete("/{name}")
def remove_subject(name: str, user_id: UUID = Depends(_get_user_id), db: Session = Depends(get_db)):
    name = name.strip()
    if name:
        db.query(UserSubject).filter(UserSubject.user_id == user_id, UserSubject.name == name).delete()
        db.commit()
    return {"message": "deleted"}
