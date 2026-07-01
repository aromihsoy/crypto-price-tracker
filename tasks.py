from celery_app import celery_app
from config import settings
from models import Alert
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from decimal import Decimal
from redis.asyncio import Redis
from datetime import datetime, timezone, timedelta

import httpx
import asyncio




BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"
COOLDOWN = timedelta(seconds=60)


@celery_app.task(name="tasks.poll_and_evaluate")
def poll_and_evaluate():
    asyncio.run(_poll_and_evaluate())


async def _poll_and_evaluate():
    engine = create_async_engine(settings.DATABASE_URL)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        async with session_maker() as session:
            result = await session.execute(select(Alert.symbol).where(Alert.is_active == True).distinct())
            symbols = result.scalars().all()
            for symbol in symbols:
                try:
                    price = await fetch_price(symbol)
                    await redis.set(f"price:{symbol}", str(price))
                    print(f"{symbol}: {price}")
                except Exception as e:
                    print(f"failed to fetch {symbol}: {type(e).__name__}: {e}")
                    continue
            
            active_alerts = await session.execute(select(Alert).where(Alert.is_active == True))
            active_alerts = active_alerts.scalars().all()
            now = datetime.now(timezone.utc)

            for alert in active_alerts:
                raw = await redis.get(f"price:{alert.symbol}")
                if raw is None:
                    continue
                price = Decimal(str(raw))

                triggered = (
                    (alert.condition == "gt" and price > alert.threshold) or (alert.condition == "lt" and price < alert.threshold)
                )
                if not triggered:
                    continue
                
                cooldown_passed = (
                    alert.last_triggered_at is None or now - alert.last_triggered_at >= COOLDOWN
                    )
                if cooldown_passed:
                    alert.last_triggered_at = now
                    print(f"ALERT TRIGGERED: alert={alert.id} {alert.symbol} {alert.condition} {alert.threshold} @ {price}")
            await session.commit()




    finally:
        await redis.aclose()
        await engine.dispose()



async def fetch_price(symbol):
    async with httpx.AsyncClient(timeout=5.0) as client:
        result = await client.get(BINANCE_URL, params={"symbol": symbol})
        result.raise_for_status()
        return Decimal(result.json()["price"])