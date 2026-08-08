import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class ApiClient:

    def __init__(self):
        self.base_url = os.getenv(
            "API_BASE_URL",
            "http://127.0.0.1:8000",
        ).rstrip("/")

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/users/telegram",
                json={
                    "telegram_id": telegram_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )

            response.raise_for_status()
            return response.json()

    async def get_services(self) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/services"
            )

            response.raise_for_status()
            return response.json()

    async def get_available_slots(
        self,
        specialist_id: int,
        service_id: int,
        target_date: str,
    ) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/appointments/available-slots",
                params={
                    "specialist_id": specialist_id,
                    "service_id": service_id,
                    "target_date": target_date,
                },
            )

            response.raise_for_status()
            return response.json()

    async def create_appointment(
        self,
        user_id: int,
        specialist_id: int,
        service_id: int,
        start_datetime: str,
        contact_type: str | None = None,
        contact_value: str | None = None,
        problem_description: str | None = None,
    ) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/appointments",
                json={
                    "user_id": user_id,
                    "specialist_id": specialist_id,
                    "service_id": service_id,
                    "start_datetime": start_datetime,
                    "contact_type": contact_type,
                    "contact_value": contact_value,
                    "problem_description": problem_description,
                },
            )

            response.raise_for_status()
            return response.json()