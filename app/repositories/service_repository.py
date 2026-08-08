from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.associations import specialist_services
from app.database.models import Specialist
from app.database.models.service import Service


class ServiceRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        service_id: int
    ) -> Service | None:
        result = await self.session.execute(
            select(Service)
            .where(Service.id == service_id)
        )
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[Service]:
        result = await self.session.execute(
            select(Service)
            .where(Service.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def get_by_specialist(
            self,
            specialist_id: int
    ) -> list[Service]:
        result = await self.session.execute(
            select(Service)
            .join(
                specialist_services,
                Service.id == specialist_services.c.service_id
            )
            .where(
                specialist_services.c.specialist_id == specialist_id,
                Service.is_active.is_(True)
            )
        )

        return list(result.scalars().all())

    async def create(
        self,
        service: Service
    ) -> Service:
        self.session.add(service)

        await self.session.commit()
        await self.session.refresh(service)

        return service

    async def get_for_specialist(
            self,
            service_id: int,
            specialist_id: int
    ) -> Service | None:
        result = await self.session.execute(
            select(Service)
            .where(
            Service.id == service_id,
                Service.specialists.any(
                    Specialist.id == specialist_id
                )
            )
        )
        return result.scalar_one_or_none()
