from datetime import datetime, timezone, time, date

from app.database.models.appointment import Appointment
from app.repositories.appointment_repository import AppointmentRepository
from datetime import datetime, timedelta

from app.enums.appointment_status import AppointmentStatus
from app.database.models.appointment import Appointment
from app.database.models.user import User
from app.database.models.specialist import Specialist
from app.database.models.service import Service
from app.database.models.working_schedule import WorkingSchedule

from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.user_repository import UserRepository
from app.repositories.specialist_repository import SpecialistRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.working_schedule_repository import WorkingScheduleRepository

from app.exceptions.appointment import (
    UserNotFoundError,
    SpecialistNotFoundError,
    SpecialistInactiveError,
    ServiceNotFoundError,
    ServiceInactiveError,
    ServiceNotAvailableError,
    AppointmentOutsideWorkingHoursError,
    AppointmentAlreadyOccupiedError,
    AppointmentNotFoundError,
    AppointmentCannotBeCancelledError,
    AppointmentCannotBeCompletedError,
    AppointmentCannotBeConfirmedError
)


class AppointmentService:

    def __init__(
            self,
            appointment_repository: AppointmentRepository,
            user_repository: UserRepository,
            specialist_repository: SpecialistRepository,
            service_repository: ServiceRepository,
            working_schedule_repository: WorkingScheduleRepository
    ):
        self.appointment_repository = appointment_repository
        self.user_repository = user_repository
        self.specialist_repository = specialist_repository
        self.service_repository = service_repository
        self.working_schedule_repository = working_schedule_repository

    async def get_by_id(
            self,
            appointment_id: int
    ) -> Appointment:
        appointment = await self.appointment_repository.get_by_id(
            appointment_id
        )

        if appointment is None:
            raise AppointmentNotFoundError()

        return appointment

    async def get_by_user(
        self,
        user_id: int
    ) -> list[Appointment]:
        return await self.appointment_repository.get_by_user(
            user_id
        )

    async def get_by_specialist(
        self,
        specialist_id: int
    ) -> list[Appointment]:
        return await self.appointment_repository.get_by_specialist(
            specialist_id
        )

    async def get_overlapping(
        self,
        specialist_id: int,
        start_datetime: datetime,
        end_datetime: datetime
    ) -> list[Appointment]:
        return await self.appointment_repository.get_overlapping(
            specialist_id,
            start_datetime,
            end_datetime
        )

    async def create(
            self,
            user_id: int,
            specialist_id: int,
            service_id: int,
            start_datetime: datetime,
            contact_type: str | None = None,
            contact_value: str | None = None,
            problem_description: str | None = None
    ) -> Appointment:
        user = await self.user_repository.get_by_id(
            user_id
        )

        if user is None:
            raise UserNotFoundError()
        specialist = await self.specialist_repository.get_by_id(
            specialist_id
        )
        if specialist is None:
            raise SpecialistNotFoundError()
        if not specialist.is_active:
            raise SpecialistInactiveError()

        service = await self.service_repository.get_for_specialist(
            service_id,
            specialist_id
        )
        if service is None:
            raise ServiceNotAvailableError()
        if not service.is_active:
            raise ServiceInactiveError()

        schedules = await self.working_schedule_repository.get_by_specialist_and_weekday(
            specialist_id,
            start_datetime.weekday()
        )

        end_datetime = start_datetime + timedelta(
            minutes=service.duration_minutes
        )

        if start_datetime.date() != end_datetime.date():
            raise ValueError("Appointment cannot cross midnight")

        fits_schedule = any(
            schedule.start_time <= start_datetime.time()
            and end_datetime.time() <= schedule.end_time
            for schedule in schedules
        )
        if not fits_schedule:
            raise AppointmentOutsideWorkingHoursError()

        overlapping = await self.appointment_repository.get_overlapping(
            specialist_id,
            start_datetime,
            end_datetime
        )
        if overlapping:
            raise AppointmentAlreadyOccupiedError()

        appointment = Appointment(
            user_id=user_id,
            specialist_id=specialist_id,
            service_id=service_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            status=AppointmentStatus.PENDING,
            contact_type=contact_type,
            contact_value=contact_value,
            problem_description=problem_description
        )

        return await self.appointment_repository.create(
            appointment
        )

    async def get_upcoming_by_user(
            self,
            user_id: int
    ) -> list[Appointment]:
        return await self.appointment_repository.get_upcoming_by_user(
            user_id
        )

    async def get_upcoming_by_specialist(
            self,
            specialist_id: int
    ) -> list[Appointment]:
        return await self.appointment_repository.get_upcoming_by_specialist(
            specialist_id
        )

    async def cancel(
            self,
            appointment_id: int
    ) -> Appointment:
        appointment = await self.appointment_repository.get_by_id(
            appointment_id
        )

        if appointment is None:
            raise AppointmentNotFoundError()

        if appointment.status not in (
                AppointmentStatus.PENDING,
                AppointmentStatus.CONFIRMED
        ):
            raise AppointmentCannotBeCancelledError()

        if appointment.end_datetime <= datetime.now(timezone.utc):
            raise AppointmentCannotBeCancelledError()

        appointment.status = AppointmentStatus.CANCELLED

        return await self.appointment_repository.update(
            appointment
        )

    async def confirm(
            self,
            appointment_id: int
    ) -> Appointment:
        appointment = await self.appointment_repository.get_by_id(
            appointment_id
        )

        if appointment is None:
            raise AppointmentNotFoundError()

        if appointment.status not in (
                AppointmentStatus.PENDING
        ):
            raise AppointmentCannotBeConfirmedError()

        if appointment.end_datetime <= datetime.now(timezone.utc):
            raise AppointmentCannotBeConfirmedError()

        appointment.status = AppointmentStatus.CONFIRMED

        return await self.appointment_repository.update(
            appointment
        )

    async def complete(
            self,
            appointment_id: int
    ) -> Appointment:
        appointment = await self.appointment_repository.get_by_id(
            appointment_id
        )

        if appointment is None:
            raise AppointmentNotFoundError()

        if appointment.status not in (
                AppointmentStatus.CONFIRMED
        ):
            raise AppointmentCannotBeCompletedError()

        if appointment.end_datetime <= datetime.now(timezone.utc):
            raise AppointmentCannotBeCancelledError()

        appointment.status = AppointmentStatus.COMPLETED

        return await self.appointment_repository.update(
            appointment
        )

    async def get_available_slots(
            self,
            specialist_id: int,
            service_id: int,
            target_date: date
    ) -> list[tuple[datetime, datetime]]:

        specialist = await self.specialist_repository.get_by_id(
            specialist_id
        )

        if specialist is None:
            raise SpecialistNotFoundError()

        if not specialist.is_active:
            raise SpecialistInactiveError()

        service = await self.service_repository.get_for_specialist(
            service_id,
            specialist_id
        )

        if service is None:
            raise ServiceNotAvailableError()

        if not service.is_active:
            raise ServiceInactiveError()

        schedules = (
            await self.working_schedule_repository
            .get_by_specialist_and_weekday(
                specialist_id,
                target_date.weekday()
            )
        )

        if not schedules:
            return []

        day_start = datetime.combine(
            target_date,
            time.min,
            tzinfo=timezone.utc
        )

        day_end = datetime.combine(
            target_date,
            time.max,
            tzinfo=timezone.utc
        )

        appointments = await self.appointment_repository.get_overlapping(
            specialist_id,
            day_start,
            day_end
        )

        duration = timedelta(
            minutes=service.duration_minutes
        )

        slots = []

        for schedule in schedules:
            current = datetime.combine(
                target_date,
                schedule.start_time,
                tzinfo=timezone.utc
            )

            schedule_end = datetime.combine(
                target_date,
                schedule.end_time,
                tzinfo=timezone.utc
            )

            while current + duration <= schedule_end:
                slot_end = current + duration

                occupied = any(
                    appointment.start_datetime.replace(tzinfo=timezone.utc) < slot_end
                    and appointment.end_datetime.replace(tzinfo=timezone.utc) > current
                    for appointment in appointments
                )

                if not occupied:
                    slots.append(
                        (current, slot_end)
                    )

                current += timedelta(hours=1)

        return slots
