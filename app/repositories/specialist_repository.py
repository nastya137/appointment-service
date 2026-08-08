from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.specialist import Specialist


class SpecialistRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        specialist_id: int
    ) -> Specialist | None:
        result = await self.session.execute(
            select(Specialist)
            .where(Specialist.id == specialist_id)
        )
        return result.scalar_one_or_none()

    async def get_by_telegram_id(
        self,
        telegram_id: int
    ) -> Specialist | None:
        result = await self.session.execute(
            select(Specialist)
            .where(Specialist.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[Specialist]:
        result = await self.session.execute(
            select(Specialist)
            .where(Specialist.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def create(
        self,
        specialist: Specialist
    ) -> Specialist:
        self.session.add(specialist)

        await self.session.commit()
        await self.session.refresh(specialist)

        return specialist