import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from jose import JWTError, jwt
from typing import Optional

from backend.app.config import settings
from backend.app.services.redis_service import RedisService

router = APIRouter(tags=["websocket"])

def verify_ws_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    await websocket.accept()
    
    if not token or not verify_ws_token(token):
        await websocket.close(code=1008)
        return
        
    redis_service = RedisService(settings.REDIS_URL)
    await redis_service.connect()
    
    try:
        # Subscribe to channels
        channels = ["detections", "alerts", "camera_status", "analytics"]
        pubsub = redis_service.redis_client.pubsub()
        await pubsub.subscribe(*channels)
        
        async def reader():
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        await websocket.send_json({
                            "channel": message["channel"],
                            "data": message["data"]
                        })
                    except Exception:
                        break
        
        task = asyncio.create_task(reader())
        
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        pass
    finally:
        if 'task' in locals():
            task.cancel()
        await pubsub.unsubscribe(*channels)
        await pubsub.aclose()
        await redis_service.disconnect()
