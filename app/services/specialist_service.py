from app.database.models.specialist import Specialist
from app.repositories.specialist_repository import SpecialistRepository


class SpecialistService:

    def __init__(
            self,
            repository: SpecialistRepository
    ):
        self.repository = repository

    async def get_by_id(
            self,
            specialist_id: int
    ) -> Specialist | None:
        return await self.repository.get_by_id(
            specialist_id
        )

    async def get_by_telegram_id(
            self,
            telegram_id: int
    ) -> Specialist | None:
        return await self.repository.get_by_telegram_id(
            telegram_id
        )

    async def get_active_specialists(
            self
    ) -> list[Specialist]:
        return await self.repository.get_all_active()

    async def create(
            self,
            telegram_id: int,
            username: str | None,
            first_name: str | None,
            last_name: str | None,
            display_name: str,
            description: str | None = None
    ) -> Specialist:
        specialist = Specialist(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
            description=description
        )

        return await self.repository.create(specialist)