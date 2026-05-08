from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, Dict, Any, List
from app.models.system_settings import SystemSettings


class SettingsService:
    @staticmethod
    async def get_setting(db: AsyncSession, key: str) -> Optional[str]:
        result = await db.execute(
            select(SystemSettings).where(SystemSettings.setting_key == key)
        )
        setting = result.scalar_one_or_none()
        return setting.setting_value if setting else None

    @staticmethod
    async def get_setting_obj(db: AsyncSession, key: str) -> Optional[SystemSettings]:
        result = await db.execute(
            select(SystemSettings).where(SystemSettings.setting_key == key)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_settings_by_category(db: AsyncSession, category: str) -> List[SystemSettings]:
        result = await db.execute(
            select(SystemSettings).where(SystemSettings.category == category)
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_settings(db: AsyncSession) -> List[SystemSettings]:
        result = await db.execute(select(SystemSettings).order_by(SystemSettings.category, SystemSettings.id))
        return result.scalars().all()

    @staticmethod
    async def get_settings_dict(db: AsyncSession) -> Dict[str, str]:
        settings = await SettingsService.get_all_settings(db)
        return {s.setting_key: s.setting_value for s in settings}

    @staticmethod
    async def set_setting(db: AsyncSession, key: str, value: str) -> SystemSettings:
        setting = await SettingsService.get_setting_obj(db, key)
        if setting:
            setting.setting_value = value
            await db.commit()
            await db.refresh(setting)
            return setting
        else:
            new_setting = SystemSettings(setting_key=key, setting_value=value)
            db.add(new_setting)
            await db.commit()
            await db.refresh(new_setting)
            return new_setting

    @staticmethod
    async def set_settings(db: AsyncSession, settings: Dict[str, str]) -> None:
        for key, value in settings.items():
            await SettingsService.set_setting(db, key, value)

    @staticmethod
    async def get_bool_setting(db: AsyncSession, key: str, default: bool = False) -> bool:
        value = await SettingsService.get_setting(db, key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes')

    @staticmethod
    async def get_int_setting(db: AsyncSession, key: str, default: int = 0) -> int:
        value = await SettingsService.get_setting(db, key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    @staticmethod
    async def get_json_setting(db: AsyncSession, key: str, default: Any = None) -> Any:
        import json
        value = await SettingsService.get_setting(db, key)
        if value is None:
            return default
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default
