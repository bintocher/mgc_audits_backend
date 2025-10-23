import asyncio
from sqlalchemy import text
from app.core.database import engine


async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
    print("База данных инициализирована")


if __name__ == "__main__":
    asyncio.run(init_db())

