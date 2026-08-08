from app.database.models.service import Service
from app.repositories.service_repository import ServiceRepository


class ServiceService:

    def __init__(
            self,
            repository: ServiceRepository
    ):
        self.repository = repository

    async def get_by_id(
            self,
            service_id: int
    ) -> Service | None:
        return await self.repository.get_by_id(
            service_id
        )

    async def get_active_services(
            self
    ) -> list[Service]:
        return await self.repository.get_all_active()

    async def get_by_specialist(
            self,
            specialist_id: int
    ) -> list[Service]:
        return await self.repository.get_by_specialist(
            specialist_id
        )