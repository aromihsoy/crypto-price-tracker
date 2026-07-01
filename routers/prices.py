from fastapi import APIRouter, HTTPException

from redis_client import redis_client




router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/{symbol}")
async def get_prices(symbol: str):
    symbol = symbol.upper()
    result = await redis_client.get(f"price:{symbol}")
    if result is None:
        raise HTTPException(status_code=404, detail="Price not found")
    return {"symbol": symbol, "price": result}
    