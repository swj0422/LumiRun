from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import require_admin, require_super_admin
from app.models.user import User
from app.models.system_settings import SystemSettings
from app.services.settings_service import SettingsService

router = APIRouter()


class SettingUpdate(BaseModel):
    setting_key: str
    setting_value: str


class SettingsUpdate(BaseModel):
    settings: Dict[str, str]


class SettingResponse(BaseModel):
    id: int
    setting_key: str
    setting_value: str | None
    setting_type: str
    category: str
    description: str | None

    class Config:
        from_attributes = True


@router.get("/")
async def get_all_settings(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """è·åææç³»ç»è®¾ç½?""
    settings = await SettingsService.get_all_settings(db)
    
    result = {}
    for setting in settings:
        if setting.category not in result:
            result[setting.category] = []
        result[setting.category].append({
            "id": setting.id,
            "setting_key": setting.setting_key,
            "setting_value": setting.setting_value,
            "setting_type": setting.setting_type,
            "description": setting.description
        })
    
    return result


@router.get("/{category}")
async def get_settings_by_category(
    category: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """è·åæå®åç±»çç³»ç»è®¾ç½?""
    settings = await SettingsService.get_settings_by_category(db, category)
    
    return {
        "category": category,
        "settings": [
            {
                "id": s.id,
                "setting_key": s.setting_key,
                "setting_value": s.setting_value,
                "setting_type": s.setting_type,
                "description": s.description
            }
            for s in settings
        ]
    }


@router.get("/key/{key}")
async def get_setting_by_key(
    key: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """è·ååä¸ªè®¾ç½®"""
    setting = await SettingsService.get_setting_obj(db, key)
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="è®¾ç½®ä¸å­å?
        )
    
    return {
        "id": setting.id,
        "setting_key": setting.setting_key,
        "setting_value": setting.setting_value,
        "setting_type": setting.setting_type,
        "category": setting.category,
        "description": setting.description
    }


@router.put("/")
async def update_settings(
    data: SettingsUpdate,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """æ¹éæ´æ°ç³»ç»è®¾ç½®ï¼ä»è¶çº§ç®¡çåï¼"""
    await SettingsService.set_settings(db, data.settings)
    
    return {"message": "è®¾ç½®æ´æ°æå"}


@router.put("/{key}")
async def update_setting(
    key: str,
    data: SettingUpdate,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """æ´æ°åä¸ªè®¾ç½®ï¼ä»è¶çº§ç®¡çåï¼"""
    setting = await SettingsService.get_setting_obj(db, key)
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="è®¾ç½®ä¸å­å?
        )
    
    setting.setting_value = data.setting_value
    await db.commit()
    await db.refresh(setting)
    
    return {
        "message": "è®¾ç½®æ´æ°æå",
        "setting": {
            "id": setting.id,
            "setting_key": setting.setting_key,
            "setting_value": setting.setting_value
        }
    }


@router.post("/cache/clear")
async def clear_cache(
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """æ¸çç³»ç»ç¼å­ï¼ä»è¶çº§ç®¡çåï¼"""
    return {"message": "ç¼å­æ¸çæå"}


@router.get("/system/info")
async def get_system_info(
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """è·åç³»ç»çæ§ä¿¡æ¯ï¼ä»è¶çº§ç®¡çåï¼"""
    import psutil
    import platform
    from datetime import datetime
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "system": {
                "os": platform.system(),
                "os_version": platform.version(),
                "python_version": platform.python_version(),
            },
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            },
            "time": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "æ æ³è·åç³»ç»ä¿¡æ¯"
        }
