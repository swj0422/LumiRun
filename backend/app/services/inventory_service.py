from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.gift import Gift
from app.models.gift_stock import GiftStock
from app.core.logger import logger


class InventoryService:
    """库存管理服务"""
    
    # 库存预警阈值
    STOCK_WARNING_THRESHOLD = 10
    
    @staticmethod
    async def check_stock_warnings(db: AsyncSession) -> list:
        """检查库存预警"""
        # 查询所有礼品的库存
        query = select(Gift, GiftStock).join(
            GiftStock, Gift.id == GiftStock.gift_id
        )
        result = await db.execute(query)
        stocks = result.all()
        
        # 检查库存预警
        warnings = []
        for gift, stock in stocks:
            if stock.current_stock < InventoryService.STOCK_WARNING_THRESHOLD:
                warnings.append({
                    "gift_id": gift.id,
                    "gift_name": gift.name,
                    "current_stock": stock.current_stock,
                    "threshold": InventoryService.STOCK_WARNING_THRESHOLD,
                    "status": "warning" if stock.current_stock > 0 else "critical"
                })
        
        # 记录预警信息
        if warnings:
            logger.warning(f"库存预警: 发现 {len(warnings)} 个礼品库存不足")
            for warning in warnings:
                logger.warning(f"  - {warning['gift_name']}: 库存 {warning['current_stock']}，低于阈值 {warning['threshold']}")
        
        return warnings
    
    @staticmethod
    async def get_low_stock_gifts(db: AsyncSession, threshold: int = None) -> list:
        """获取低库存礼品"""
        if threshold is None:
            threshold = InventoryService.STOCK_WARNING_THRESHOLD
        
        query = select(Gift, GiftStock).join(
            GiftStock, Gift.id == GiftStock.gift_id
        ).where(
            GiftStock.current_stock < threshold
        )
        result = await db.execute(query)
        stocks = result.all()
        
        low_stock_gifts = []
        for gift, stock in stocks:
            low_stock_gifts.append({
                "id": gift.id,
                "name": gift.name,
                "description": gift.description,
                "price": gift.price,
                "current_stock": stock.current_stock,
                "threshold": threshold,
                "status": "warning" if stock.current_stock > 0 else "critical"
            })
        
        return low_stock_gifts
    
    @staticmethod
    async def update_stock_threshold(db: AsyncSession, gift_id: int, threshold: int) -> bool:
        """更新礼品库存预警阈值"""
        # 这里可以扩展，为每个礼品设置单独的预警阈值
        # 目前使用全局阈值，此方法预留
        return True
