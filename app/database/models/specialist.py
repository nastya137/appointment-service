from datetime import datetime, timezone
from sqlalchemy import BigInteger, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from sqlalchemy import Text
from typing import TYPE_CHECKING
from app.database.associations import specialist_services

if TYPE_CHECKING:
    from app.database.models.service import Service
    from app.database.models.appointment import Appointment
    from app.database.models.working_schedule import WorkingSchedule
class Specialist(Base):
    __tablename__ = "specialists"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False
    )

    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    first_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    last_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    services: Mapped[list["Service"]] = relationship(
        secondary=specialist_services,
        back_populates="specialists"
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="specialist"
    )

    working_schedules: Mapped[list["WorkingSchedule"]] = relationship(
        back_populates="specialist"
    )