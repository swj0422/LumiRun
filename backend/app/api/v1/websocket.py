from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user_from_token
from app.models.user import User
import json
from typing import Dict, Set

router = APIRouter()

# 存储WebSocket连接
# 结构: {user_id: {class_id: websocket}}
connections: Dict[int, Dict[int, WebSocket]] = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, class_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        self.active_connections[user_id][class_id] = websocket
    
    def disconnect(self, user_id: int, class_id: int):
        if user_id in self.active_connections:
            if class_id in self.active_connections[user_id]:
                del self.active_connections[user_id][class_id]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: int, class_id: int):
        if user_id in self.active_connections and class_id in self.active_connections[user_id]:
            await self.active_connections[user_id][class_id].send_json(message)
    
    async def broadcast_to_class(self, message: dict, class_id: int):
        for user_id, classes in self.active_connections.items():
            if class_id in classes:
                await classes[class_id].send_json(message)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    class_id: int
):
    """WebSocket连接端点"""
    try:
        # 验证token
        user = await get_current_user_from_token(token)
        if not user:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        # 连接WebSocket
        await manager.connect(websocket, user.id, class_id)
        
        # 发送连接成功消息
        await manager.send_personal_message(
            {
                "type": "connection_established",
                "message": "WebSocket连接成功",
                "user_id": user.id,
                "class_id": class_id
            },
            user.id,
            class_id
        )
        
        # 处理消息
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # 处理不同类型的消息
                if message.get("type") == "ping":
                    await manager.send_personal_message(
                        {"type": "pong"},
                        user.id,
                        class_id
                    )
                elif message.get("type") == "get_leaderboard":
                    # 处理获取排行榜请求
                    from app.services.growth_service import GrowthService
                    from app.core.database import async_session
                    
                    async with async_session() as db:
                        leaderboard = await GrowthService.get_leaderboard(
                            db, user.id, class_id, limit=10
                        )
                        await manager.send_personal_message(
                            {
                                "type": "leaderboard_update",
                                "data": leaderboard
                            },
                            user.id,
                            class_id
                        )
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Invalid JSON format"
                    },
                    user.id,
                    class_id
                )
    except WebSocketDisconnect:
        manager.disconnect(user.id, class_id)
    except Exception as e:
        if 'user' in locals():
            manager.disconnect(user.id, class_id)
        await websocket.close(code=1011, reason=f"Internal error: {str(e)}")
