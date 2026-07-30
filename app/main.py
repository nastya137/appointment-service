import asyncio

from app.database.session import create_database

async def main():
    await create_database()

asyncio.run(main())