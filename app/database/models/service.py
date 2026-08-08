from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.associations import specialist_services
from app.database.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.database.models.specialist import Specialist
    from app.database.models.appointment import Appointment
class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    price: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    currency: Mapped[str | None] = mapped_column(
        String(3),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    specialists: Mapped[list["Specialist"]] = relationship(
        secondary=specialist_services,
        back_populates="services"
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="service"
    )