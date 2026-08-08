from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.appointment import Appointment
from app.enums.appointment_status import AppointmentStatus


class AppointmentRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        appointment_id: int
    ) -> Appointment | None:
        result = await self.session.execute(
            select(Appointment)
            .where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: int
    ) -> list[Appointment]:
        result = await self.session.execute(
            select(Appointment)
            .where(Appointment.user_id == user_id)
            .order_by(Appointment.start_datetime)
        )
        return list(result.scalars().all())

    async def get_by_specialist(
        self,
        specialist_id: int
    ) -> list[Appointment]:
        result = await self.session.execute(
            select(Appointment)
            .where(Appointment.specialist_id == specialist_id)
            .order_by(Appointment.start_datetime)
        )
        return list(result.scalars().all())

    async def get_overlapping(
        self,
        specialist_id: int,
        start_datetime: datetime,
        end_datetime: datetime
    ) -> list[Appointment]:
        result = await self.session.execute(
            select(Appointment)
            .where(
                Appointment.specialist_id == specialist_id,
                Appointment.start_datetime < end_datetime,
                Appointment.end_datetime > start_datetime,
                Appointment.status != AppointmentStatus.CANCELLED
            )
        )
        return list(result.scalars().all())

    async def create(
        self,
        appointment: Appointment
    ) -> Appointment:
        self.session.add(appointment)

        await self.session.commit()
        await self.session.refresh(appointment)

        return appointment

    async def get_upcoming_by_user(
            self,
            user_id: int
    ) -> list[Appointment]:
        result = await self.session.execute(
            select(Appointment)
            .where(
                Appointment.user_id == user_id,
                Appointment.start_datetime >= datetime.now(timezone.utc)
            )
            .order_by(Appointment.start_datetime)
        )

        return list(result.scalars().all())

    async def get_upcoming_by_specialist(
            self,
            specialist_id: int
    ) -> list[Appointment]:
        result = await self.session.execute(
            select(Appointment)
            .where(
                Appointment.specialist_id == specialist_id,
                Appointment.start_datetime >= datetime.now(timezone.utc),
                Appointment.status != AppointmentStatus.CANCELLED
            )
            .order_by(Appointment.start_datetime)
        )

        return list(result.scalars().all())

    async def update(
            self,
            appointment: Appointment
    ) -> Appointment:
        await self.session.commit()
        await self.session.refresh(appointment)

        return appointment