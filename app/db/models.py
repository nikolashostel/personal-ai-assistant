from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    relationship: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(128), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"), index=True
    )
    role: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class RunningWorkout(Base):
    __tablename__ = "running_workouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    distance_km: Mapped[float | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    duration_sec: Mapped[int | None] = mapped_column(nullable=True)

    # Stored for convenient querying; distance_km + duration_sec remain the source data.
    avg_pace_sec_km: Mapped[int | None] = mapped_column(nullable=True)
    avg_heart_rate: Mapped[int | None] = mapped_column(nullable=True)
    max_heart_rate: Mapped[int | None] = mapped_column(nullable=True)
    avg_cadence: Mapped[int | None] = mapped_column(nullable=True)
    elevation_gain_m: Mapped[int | None] = mapped_column(nullable=True)

    training_type: Mapped[str | None] = mapped_column(String(32), nullable=True)

    rpe: Mapped[int | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    source: Mapped[str] = mapped_column(String(32), default="telegram")
    source_image: Mapped[str | None] = mapped_column(
        String(512), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RunningWorkoutLap(Base):
    __tablename__ = "running_workout_laps"

    id: Mapped[int] = mapped_column(primary_key=True)
    workout_id: Mapped[int] = mapped_column(
        ForeignKey("running_workouts.id", ondelete="CASCADE"),
        index=True,
    )

    lap_number: Mapped[int] = mapped_column()
    lap_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    distance_km: Mapped[float | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    duration_sec: Mapped[int | None] = mapped_column(nullable=True)
    pace_sec_km: Mapped[int | None] = mapped_column(nullable=True)
    avg_heart_rate: Mapped[int | None] = mapped_column(nullable=True)
    max_heart_rate: Mapped[int | None] = mapped_column(nullable=True)
    cadence: Mapped[int | None] = mapped_column(nullable=True)
    elevation_gain_m: Mapped[int | None] = mapped_column(nullable=True)
