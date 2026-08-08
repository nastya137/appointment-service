from app.database.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:

    def __init__(
            self,
            repository: UserRepository
    ):
        self.repository = repository


    async def get_or_create_user(
            self,
            telegram_id: int,
            username: str | None,
            first_name: str | None,
            last_name: str | None
    ) -> User:

        user = await self.repository.get_by_telegram_id(
            telegram_id
        )

        if user:
            return user


        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )

        return await self.repository.create(user)