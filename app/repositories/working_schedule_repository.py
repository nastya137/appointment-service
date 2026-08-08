from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.working_schedule import WorkingSchedule


class WorkingScheduleRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        schedule_id: int
    ) -> WorkingSchedule | None:
        result = await self.session.execute(
            select(WorkingSchedule)
            .where(WorkingSchedule.id == schedule_id)
        )
        return result.scalar_one_or_none()

    async def get_by_specialist(
        self,
        specialist_id: int
    ) -> list[WorkingSchedule]:
        result = await self.session.execute(
            select(WorkingSchedule)
            .where(
                WorkingSchedule.specialist_id == specialist_id
            )
            .order_by(
                WorkingSchedule.weekday,
                WorkingSchedule.start_time
            )
        )
        return list(result.scalars().all())

    async def get_by_specialist_and_weekday(
        self,
        specialist_id: int,
        weekday: int
    ) -> list[WorkingSchedule]:
        result = await self.session.execute(
            select(WorkingSchedule)
            .where(
                WorkingSchedule.specialist_id == specialist_id,
                WorkingSchedule.weekday == weekday
            )
            .order_by(WorkingSchedule.start_time)
        )
        return list(result.scalars().all())

    async def create(
        self,
        schedule: WorkingSchedule
    ) -> WorkingSchedule:
        self.session.add(schedule)

        await self.session.commit()
        await self.session.refresh(schedule)

        return schedule