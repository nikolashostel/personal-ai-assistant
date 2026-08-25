from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RunningWorkoutLapData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lap_number: int = Field(ge=1)
    lap_type: str | None = None

    distance_km: Decimal | None = Field(default=None, ge=0)
    duration_sec: int | None = Field(default=None, ge=0)
    pace_sec_km: int | None = Field(default=None, ge=0)

    avg_heart_rate: int | None = Field(default=None, ge=0)
    max_heart_rate: int | None = Field(default=None, ge=0)
    cadence: int | None = Field(default=None, ge=0)
    elevation_gain_m: int | None = Field(default=None, ge=0)


class RunningWorkoutData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    started_at: datetime | None = None

    distance_km: Decimal | None = Field(default=None, ge=0)
    duration_sec: int | None = Field(default=None, ge=0)

    # Stored for convenient querying; distance + duration are the source values.
    avg_pace_sec_km: int | None = Field(default=None, ge=0)
    avg_heart_rate: int | None = Field(default=None, ge=0)
    max_heart_rate: int | None = Field(default=None, ge=0)
    avg_cadence: int | None = Field(default=None, ge=0)
    elevation_gain_m: int | None = Field(default=None, ge=0)

    training_type: Literal["regular", "interval"]

    rpe: int | None = Field(default=None, ge=1, le=10)
    notes: str | None = None

    source: str = "telegram"
    source_image: str | None = None

    laps: list[RunningWorkoutLapData] = Field(default_factory=list)
