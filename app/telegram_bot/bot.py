import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from app.telegram_bot.handlers.start import router as start_router
from app.telegram_bot.handlers.appointment import router as appointments_router

load_dotenv()


async def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    bot = Bot(token=token)

    dp = Dispatcher(
        storage=MemoryStorage()
    )

    dp.include_router(start_router)
    dp.include_router(appointments_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())