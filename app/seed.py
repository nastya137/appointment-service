#Заполняет БД для теста

import asyncio
from datetime import time

from sqlalchemy import select
from sqlalchemy import select

from app.database.associations import specialist_services
from app.database.models.service import Service
from app.database.models.specialist import Specialist
from app.database.models.user import User
from app.database.models.working_schedule import WorkingSchedule
from app.database.session import async_session, create_database


async def seed():
    await create_database()

    async with async_session() as session:
        # User
        result = await session.execute(
            select(User).where(User.telegram_id == 100001)
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                telegram_id=100001,
                username="test_user",
                first_name="Test",
                last_name="User",
            )
            session.add(user)

        # Specialist
        result = await session.execute(
            select(Specialist).where(Specialist.telegram_id == 200001)
        )
        specialist = result.scalar_one_or_none()

        if specialist is None:
            specialist = Specialist(
                telegram_id=200001,
                username="test_specialist",
                first_name="Test",
                last_name="Specialist",
                display_name="Тестовый психолог",
                description="Специалист для тестирования API",
            )
            session.add(specialist)

        # Service
        result = await session.execute(
            select(Service).where(
                Service.name == "Тестовая консультация"
            )
        )
        service = result.scalar_one_or_none()

        if service is None:
            service = Service(
                name="Тестовая консультация",
                description="Услуга для тестирования API",
                duration_minutes=60,
                price=2000,
                currency="RUB",
            )
            session.add(service)

        # Нам нужны ID перед созданием связей.
        await session.flush()

        # Specialist <-> Service
        result = await session.execute(
            select(specialist_services).where(
                specialist_services.c.specialist_id == specialist.id,
                specialist_services.c.service_id == service.id,
            )
        )

        if result.first() is None:
            await session.execute(
                specialist_services.insert().values(
                    specialist_id=specialist.id,
                    service_id=service.id,
                )
            )

        # Working schedule: Monday-Friday, 09:00-18:00
        result = await session.execute(
            select(WorkingSchedule).where(
                WorkingSchedule.specialist_id == specialist.id
            )
        )
        schedules = list(result.scalars().all())

        existing_weekdays = {
            schedule.weekday
            for schedule in schedules
        }

        for weekday in range(5):
            if weekday not in existing_weekdays:
                session.add(
                    WorkingSchedule(
                        specialist_id=specialist.id,
                        weekday=weekday,
                        start_time=time(9, 0),
                        end_time=time(18, 0),
                    )
                )

        await session.commit()

        print("Seed completed.")
        print(f"User:       id={user.id}")
        print(f"Specialist: id={specialist.id}")
        print(f"Service:    id={service.id}")


if __name__ == "__main__":
    asyncio.run(seed())