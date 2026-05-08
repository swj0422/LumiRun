from app.api.v1.websocket import manager
from typing import Dict


async def send_order_notification(user_id: int, class_id: int, message_data: Dict):
    """
    发送订单相关的实时通知
    
    Args:
        user_id: 接收消息的用户ID
        class_id: 班级ID
        message_data: 消息数据，包含type和content字段
    """
    try:
        await manager.send_personal_message(
            {
                "type": "order_notification",
                "data": message_data
            },
            user_id,
            class_id
        )
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"WebSocket推送消息失? user_id={user_id}, class_id={class_id}, error={str(e)}")
        return False