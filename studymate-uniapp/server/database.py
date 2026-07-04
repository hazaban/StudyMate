"""Database connection and table definitions."""

import uuid
from datetime import datetime, date, timezone

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Date, DateTime,
    ForeignKey, Text, JSON, Enum as SAEnum, func
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "connect_timeout": 10,
        "sslmode": "prefer"
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency: get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def utcnow():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nickname = Column(String(100), default="")
    avatar_url = Column(Text, default="")
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    plans = relationship("StudyPlan", back_populates="user", cascade="all, delete-orphan")


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_name = Column(String(200), nullable=False)
    exam_date = Column(Date, nullable=False)
    target_scores = Column(JSON, default=dict)
    daily_study_time = Column(Integer, default=480)
    weak_points = Column(ARRAY(String), default=list)
    study_phase = Column(String(50), default="基础阶段")
    notes = Column(Text, default="")
    ai_plan = Column(JSON, default=None)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="plans")
    tasks = relationship("DailyTask", back_populates="plan", cascade="all, delete-orphan")
    cards = relationship("FlashCard", back_populates="plan", cascade="all, delete-orphan")
    mistakes = relationship("Mistake", back_populates="plan", cascade="all, delete-orphan")
    plants = relationship("Plant", back_populates="plan", cascade="all, delete-orphan")


class DailyTask(Base):
    __tablename__ = "daily_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    type = Column(String(20), nullable=False)       # new_study / review / mistake
    subject = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    duration = Column(Integer, default=25)           # minutes
    status = Column(String(20), default="pending")   # pending / doing / completed
    completed_at = Column(DateTime(timezone=True), default=None)
    proof_image_url = Column(Text, default="")
    actual_duration = Column(Integer, default=0)        # actual minutes tracked by pomodoro
    chapter = Column(String(100), default="")
    created_at = Column(DateTime(timezone=True), default=utcnow)

    plan = relationship("StudyPlan", back_populates="tasks")


class FlashCard(Base):
    __tablename__ = "flash_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    subject = Column(String(100), nullable=False)
    mastery_level = Column(String(20), default="unmastered")  # unmastered / familiar / mastered
    next_review_date = Column(Date, nullable=False, index=True)
    review_count = Column(Integer, default=0)
    image_urls = Column(JSON, default=list)  # list of image URLs (deprecated, kept for migration)
    question_images = Column(JSON, default=list)  # images for question
    answer_images = Column(JSON, default=list)    # images for answer
    tags = Column(JSON, default=list)        # custom tags
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    plan = relationship("StudyPlan", back_populates="cards")


class Mistake(Base):
    __tablename__ = "mistakes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    analysis = Column(Text, default="")
    subject = Column(String(100), nullable=False)
    difficulty = Column(String(20), default="medium")          # easy / medium / hard
    image_urls = Column(JSON, default=list)                    # list of image URLs (deprecated, kept for migration)
    question_images = Column(JSON, default=list)                # images for question
    answer_images = Column(JSON, default=list)                  # images for answer
    error_count = Column(Integer, default=1)                   # how many times got wrong
    correct_count = Column(Integer, default=0)                 # consecutive correct answers
    mastered = Column(String(1), default="0")                  # '0' or '1'
    next_review_date = Column(Date, nullable=False, index=True)  # next review date (Ebbinghaus)
    tags = Column(JSON, default=list)                            # custom tags
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    plan = relationship("StudyPlan", back_populates="mistakes")


class Plant(Base):
    __tablename__ = "plants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(20), default="seed")        # seed / sprout / growing / mature / harvested
    subject = Column(String(100), nullable=False)
    progress = Column(Integer, default=0)             # 0-100
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    plan = relationship("StudyPlan", back_populates="plants")


class FarmState(Base):
    __tablename__ = "farm_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    coins = Column(Integer, default=0)
    experience = Column(Integer, default=0)
    level = Column(Integer, default=1)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class FocusRecord(Base):
    __tablename__ = "focus_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    type = Column(String(20), default="focus")        # focus / manual / break
    subject = Column(String(100), default="")
    task_id = Column(UUID(as_uuid=True), ForeignKey("daily_tasks.id", ondelete="SET NULL"), nullable=True)
    task_name = Column(String(255), default="")
    duration = Column(Integer, default=25)              # minutes
    start_time = Column(DateTime(timezone=True), default=None)
    end_time = Column(DateTime(timezone=True), default=None)
    note = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    plan = relationship("StudyPlan")
    task = relationship("DailyTask")


class UserSubject(Base):
    """Per-user custom subjects. Each user has their own subject list stored server-side."""
    __tablename__ = "user_subjects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)


# ---------------------------------------------------------------------------
# Create tables
# ---------------------------------------------------------------------------
def init_db():
    Base.metadata.create_all(bind=engine)