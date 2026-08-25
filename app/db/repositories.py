from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    Conversation,
    Message,
    RunningWorkout,
    RunningWorkoutLap,
    User,
)
from app.running.schemas import RunningWorkoutData


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(self, external_id: str) -> User:
        user = self.db.scalar(
            select(User).where(User.external_id == external_id)
        )
        if user:
            return user

        user = User(external_id=external_id)
        self.db.add(user)
        self.db.flush()
        return user

    def get_or_create_conversation(
        self,
        user: User,
        external_id: str,
    ) -> Conversation:
        conversation = self.db.scalar(
            select(Conversation).where(
                Conversation.user_id == user.id,
                Conversation.external_id == external_id,
            )
        )
        if conversation:
            return conversation

        conversation = Conversation(
            user_id=user.id,
            external_id=external_id,
        )
        self.db.add(conversation)
        self.db.flush()
        return conversation

    def get_recent_messages(
        self,
        conversation: Conversation,
        limit: int = 10,
    ) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(limit)
        )
        return list(reversed(self.db.scalars(statement).all()))

    def add_message(
        self,
        conversation: Conversation,
        role: str,
        content: str,
    ) -> Message:
        message = Message(
            conversation_id=conversation.id,
            role=role,
            content=content,
        )
        self.db.add(message)
        return message


class RunningWorkoutRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_workout(
        self,
        user: User,
        workout_data: RunningWorkoutData,
    ) -> RunningWorkout:
        workout = RunningWorkout(
            user_id=user.id,
            started_at=workout_data.started_at,
            distance_km=workout_data.distance_km,
            duration_sec=workout_data.duration_sec,
            avg_pace_sec_km=workout_data.avg_pace_sec_km,
            avg_heart_rate=workout_data.avg_heart_rate,
            avg_cadence=workout_data.avg_cadence,
            training_type=workout_data.training_type,
            source=workout_data.source,
        )

        self.db.add(workout)
        self.db.flush()

        for lap_data in workout_data.laps:
            lap = RunningWorkoutLap(
                workout_id=workout.id,
                lap_number=lap_data.lap_number,
                lap_type=lap_data.lap_type,
                distance_km=lap_data.distance_km,
                duration_sec=lap_data.duration_sec,
                pace_sec_km=lap_data.pace_sec_km,
                avg_heart_rate=lap_data.avg_heart_rate,
                max_heart_rate=lap_data.max_heart_rate,
                cadence=lap_data.cadence,
                elevation_gain_m=lap_data.elevation_gain_m,
            )
            self.db.add(lap)

        self.db.flush()
        return workout
