from datetime import datetime, time, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database.models.specialist import Specialist

class WorkingSchedule(Base):
    __tablename__ = "working_schedules"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    specialist_id: Mapped[int] = mapped_column(
        ForeignKey("specialists.id"),
        nullable=False
    )

    weekday: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    specialist: Mapped["Specialist"] = relationship(
        back_populates="working_schedules"
    )