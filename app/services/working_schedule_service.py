from app.database.models.working_schedule import WorkingSchedule
from app.repositories.working_schedule_repository import WorkingScheduleRepository

class WorkingScheduleService:
    def __init__(
            self,
            repository: WorkingScheduleRepository
    ):
        self.repository = repository

    async def get_by_id(
            self,
            schedule_id: int
    ) -> WorkingSchedule | None:
        return await self.repository.get_by_id(
            schedule_id
        )

    async def get_by_specialist(
        self,
        specialist_id: int
    ) -> list[WorkingSchedule]:
        return await self.repository.get_by_specialist(
            specialist_id
        )

    async def get_by_specialist_and_weekday(
        self,
        specialist_id: int,
        weekday: int
    ) -> list[WorkingSchedule]:
        return await self.repository.get_by_specialist_and_weekday(
            specialist_id,
            weekday
        )