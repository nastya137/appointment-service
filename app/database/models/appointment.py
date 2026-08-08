from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from app.database.base import Base
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.database.models.user import User
    from app.database.models.specialist import Specialist
    from app.database.models.service import Service

class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    specialist_id: Mapped[int] = mapped_column(
        ForeignKey("specialists.id"),
        nullable=False
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id"),
        nullable=False
    )

    start_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    end_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"
    )

    contact_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    contact_value: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    problem_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="appointments"
    )

    specialist: Mapped["Specialist"] = relationship(
        back_populates="appointments"
    )

    service: Mapped["Service"] = relationship(
        back_populates="appointments"
    )