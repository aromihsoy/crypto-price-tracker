from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from redis.asyncio import Redis

from config import settings
from security import decode_access_token




router = APIRouter(tags=["ws"])


@router.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket, token: str):
    user_id = decode_access_token(token)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await websocket.accept()

    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"alerts:{user_id}")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    await websocket.send_text(message["data"])
                except Exception:
                    break
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(f"alerts:{user_id}")
        await pubsub.aclose()
        await redis.aclose()