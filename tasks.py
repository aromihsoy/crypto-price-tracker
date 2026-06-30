from celery_app import celery_app
from config import settings
from models import Alert
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from decimal import Decimal

import httpx
import asyncio




BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"

@celery_app.task(name="tasks.poll_and_evaluate")
def poll_and_evaluate():
    asyncio.run(_poll_and_evaluate())


async def _poll_and_evaluate():
    engine = create_async_engine(settings.DATABASE_URL)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        result = await session.execute(select(Alert.symbol).where(Alert.is_active == True).distinct())
        symbols = result.scalars().all()
        for symbol in symbols:
            try:
                price = await fetch_price(symbol)
                print(f"{symbol}: {price}")
            except Exception as e:
                print(f"failed to fetch {symbol}: {e}")
                continue
    await engine.dispose()



async def fetch_price(symbol):
    async with httpx.AsyncClient() as client:
        result = await client.get(BINANCE_URL, params={"symbol": symbol})
        result.raise_for_status()
        price = Decimal(result.json()["price"])
        return price