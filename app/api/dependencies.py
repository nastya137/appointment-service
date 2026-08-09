from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.specialist_repository import SpecialistRepository
from app.repositories.user_repository import UserRepository
from app.repositories.working_schedule_repository import (
    WorkingScheduleRepository,
)
from app.services.appointment_service import AppointmentService
from app.services.service_service import ServiceService
from app.services.specialist_service import SpecialistService
from app.services.user_service import UserService


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


def get_appointment_service(
    session: AsyncSession = Depends(get_session),
) -> AppointmentService:
    return AppointmentService(
        appointment_repository=AppointmentRepository(session),
        user_repository=UserRepository(session),
        specialist_repository=SpecialistRepository(session),
        service_repository=ServiceRepository(session),
        working_schedule_repository=WorkingScheduleRepository(session),
    )


def get_service_service(
    session: AsyncSession = Depends(get_session),
) -> ServiceService:
    return ServiceService(
        repository=ServiceRepository(session)
    )


def get_user_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(
        repository=UserRepository(session)
    )


def get_specialist_service(
    session: AsyncSession = Depends(get_session),
) -> SpecialistService:
    return SpecialistService(
        repository=SpecialistRepository(session)
    )