from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import Optional, List, Union, Dict, Any
from app.core.database import get_db
from app.core.security import get_current_user, require_manager
from app.models.gift import Gift
from app.models.gift_stock import GiftStock
from app.models.gift_class_relation import GiftClassRelation as GiftClass
from app.models.class_info import ClassInfo
from app.models.user import User
from pydantic import BaseModel, Field
from app.core.logger import logger
import shutil
import os
import json
import time
from app.core.config import get_settings

settings = get_settings()

router = APIRouter()


class GiftCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: int = Field(..., ge=0)
    stock: int = Field(..., ge=0)


class GiftUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    status: Optional[int] = None


@router.post("/")
async def create_gift(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: str = Form(...),
    stock: str = Form(...),
    status: str = Form("1"),
    images: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """创建礼品"""
    # 检查请求类型
    content_type = request.headers.get("Content-Type", "")
    
    # 处理 JSON 请求
    if "application/json" in content_type:
        json_data = await request.json()
        name = json_data.get("name")
        description = json_data.get("description")
        price = json_data.get("price")
        stock = json_data.get("stock")
        status = json_data.get("status", 1)
        image_urls = []
    # 处理 FormData 请求
    else:
        # 处理文件上传
        image_urls = []
        if images:
            # 确保上传目录存在
            upload_dir = os.path.join(settings.UPLOAD_DIR, "gifts")
            os.makedirs(upload_dir, exist_ok=True)
            
            for image in images:
                # 生成唯一文件名
                filename = f"{current_user.id}_{int(time.time())}_{image.filename}"
                file_path = os.path.join(upload_dir, filename)
                
                # 保存文件
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                # 构建文件 URL
                image_url = f"/uploads/gifts/{filename}"
                image_urls.append(image_url)
    
    # 确保 price 和 stock 是整数
    try:
        price = int(price) if price else 0
        stock = int(stock) if stock else 0
        # 确保 status 是布尔值
        if isinstance(status, str):
            status = status.lower() == '1' or status.lower() == 'true'
        elif isinstance(status, int):
            status = status == 1
        else:
            status = True
    except:
        price = 0
        stock = 0
        status = True
    
    # 创建礼品
    gift = Gift(
        name=name,
        description=description,
        price=price,
        status=status,
        teacher_id=current_user.id,
        image_url=image_urls[0] if image_urls else None
    )
    db.add(gift)
    await db.flush()
    
    # 创建库存记录
    gift_stock = GiftStock(
        gift_id=gift.id,
        current_stock=stock,
        total_in_stock=stock,
        total_out_stock=0
    )
    db.add(gift_stock)
    await db.commit()
    await db.refresh(gift)
    
    logger.info(f"创建礼品: {gift.name}")
    
    return {
        "id": gift.id,
        "name": gift.name,
        "description": gift.description,
        "price": gift.price,
        "stock": stock,
        "status": gift.status,
        "image_path": gift.image_url,
        "images": image_urls,
        "created_at": gift.created_at
    }


@router.get("/")
async def get_gifts(
    gift_status: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """获取礼品列表"""
    try:
        logger.info(f"[DEBUG] get_gifts called with status: {gift_status}, skip: {skip}, limit: {limit}, user_id: {current_user.id}")
        
        query = select(Gift).where(Gift.teacher_id == current_user.id)
        logger.info(f"[DEBUG] Query: {query}")
        
        if gift_status is not None:
            query = query.where(Gift.status == gift_status)
            logger.info(f"[DEBUG] Query with status: {query}")
        
        count_query = select(func.count()).select_from(query.subquery())
        logger.info(f"[DEBUG] Count query: {count_query}")
        total = (await db.execute(count_query)).scalar()
        logger.info(f"[DEBUG] Total: {total}")
        
        query = query.order_by(Gift.created_at.desc()).offset(skip).limit(limit)
        logger.info(f"[DEBUG] Final query: {query}")
        result = await db.execute(query)
        gifts = result.scalars().all()
        logger.info(f"[DEBUG] Gifts found: {len(gifts)}")
        
        gift_list = []
        for gift in gifts:
            logger.info(f"[DEBUG] Processing gift: {gift.id}, {gift.name}")
            stock_result = await db.execute(
                select(GiftStock).where(GiftStock.gift_id == gift.id)
            )
            gift_stock = stock_result.scalar_one_or_none()
            logger.info(f"[DEBUG] Gift stock: {gift_stock}")
            
            gift_list.append({
                "id": gift.id,
                "name": gift.name,
                "description": gift.description,
                "price": gift.price,
                "stock": gift_stock.current_stock if gift_stock else 0,
                "status": gift.status,
                "image_path": gift.image_url,
                "created_at": gift.created_at
            })
        
        logger.info(f"[DEBUG] Gift list: {gift_list}")
        return {
            "items": gift_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"[DEBUG] get_gifts error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取礼品列表失败: {str(e)}"
        )


@router.get("/{gift_id}")
async def get_gift(
    gift_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """获取礼品详情"""
    result = await db.execute(
        select(Gift).where(Gift.id == gift_id, Gift.teacher_id == current_user.id)
    )
    gift = result.scalar_one_or_none()
    
    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="礼品不存在"
        )
    
    stock_result = await db.execute(
        select(GiftStock).where(GiftStock.gift_id == gift.id)
    )
    gift_stock = stock_result.scalar_one_or_none()
    
    return {
        "id": gift.id,
        "name": gift.name,
        "description": gift.description,
        "price": gift.price,
        "stock": gift_stock.current_stock if gift_stock else 0,
        "status": gift.status,
        "image_path": gift.image_url,
        "created_at": gift.created_at,
        "updated_at": gift.updated_at
    }


@router.put("/{gift_id}/")
async def update_gift(
    request: Request,
    gift_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """更新礼品"""
    logger.info(f"[DEBUG] 开始更新礼品，gift_id: {gift_id}, user_id: {current_user.id}")
    
    result = await db.execute(
        select(Gift).where(Gift.id == gift_id, Gift.teacher_id == current_user.id)
    )
    gift = result.scalar_one_or_none()
    
    if not gift:
        logger.error(f"[DEBUG] 礼品不存在，gift_id: {gift_id}")
        raise HTTPException(
            status_code=404,
            detail="礼品不存在"
        )
    
    logger.info(f"[DEBUG] 找到礼品: {gift.name}")
    
    # 获取 Content-Type
    content_type = request.headers.get("Content-Type", "")
    logger.info(f"[DEBUG] Content-Type: {content_type}")
    
    # 初始化变量
    name = None
    description = None
    price = None
    stock = None
    gift_status = None
    images = []
    image_urls = []
    
    # 处理请求数据
    if "multipart/form-data" in content_type:
        # 处理 FormData 格式请求
        logger.info(f"[DEBUG] 检测到 FormData 请求")
        try:
            form_data = await request.form()
            logger.info(f"[DEBUG] FormData: {form_data}")
            
            # 获取表单字段
            if "name" in form_data:
                name = form_data["name"]
                logger.info(f"[DEBUG] name: {name}")
            if "description" in form_data:
                description = form_data["description"]
                logger.info(f"[DEBUG] description: {description}")
            if "price" in form_data:
                try:
                    price = int(form_data["price"])
                    logger.info(f"[DEBUG] price: {price}")
                except:
                    price = None
            if "stock" in form_data:
                try:
                    stock = int(form_data["stock"])
                    logger.info(f"[DEBUG] stock: {stock}")
                except:
                    stock = None
            if "status" in form_data:
                try:
                    gift_status = form_data["status"]
                    # 确保 status 是布尔值
                    if isinstance(gift_status, str):
                        gift_status = gift_status.lower() == '1' or gift_status.lower() == 'true'
                    elif isinstance(gift_status, int):
                        gift_status = gift_status == 1
                    else:
                        gift_status = True
                    logger.info(f"[DEBUG] status: {gift_status}")
                except:
                    gift_status = None
            
            # 处理文件上传
            if "images" in form_data:
                uploaded_files = form_data.getlist("images")
                logger.info(f"[DEBUG] Uploaded files count: {len(uploaded_files)}")
                
                # 确保上传目录存在
                upload_dir = os.path.join(settings.UPLOAD_DIR, "gifts")
                os.makedirs(upload_dir, exist_ok=True)
                logger.info(f"[DEBUG] Upload directory: {upload_dir}")
                
                for image in uploaded_files:
                    logger.info(f"[DEBUG] Processing image: {image}")
                    if hasattr(image, "file"):
                        # 生成唯一文件名
                        import time
                        filename = f"{current_user.id}_{int(time.time())}_{image.filename}"
                        file_path = os.path.join(upload_dir, filename)
                        logger.info(f"[DEBUG] Saving file to: {file_path}")
                        
                        # 保存文件
                        with open(file_path, "wb") as buffer:
                            shutil.copyfileobj(image.file, buffer)
                        
                        logger.info(f"[DEBUG] File saved successfully")
                        
                        # 构建文件 URL
                        image_url = f"/uploads/gifts/{filename}"
                        image_urls.append(image_url)
                        logger.info(f"[DEBUG] Image URL: {image_url}")
                
                # 更新礼品图片
                if image_urls:
                    gift.image_url = image_urls[0]
                    logger.info(f"[DEBUG] Updated gift image_url: {gift.image_url}")
            else:
                logger.info(f"[DEBUG] No images in form_data")
        except Exception as e:
            logger.error(f"[DEBUG] 处理 FormData 时出错: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"处理请求失败: {str(e)}"
            )
    elif "application/json" in content_type:
        # 处理 JSON 格式请求
        json_data = await request.json()
        logger.info(f"[DEBUG] JSON data: {json_data}")
        
        if "name" in json_data:
            name = json_data["name"]
        if "description" in json_data:
            description = json_data["description"]
        if "price" in json_data:
            price = int(json_data["price"])
        if "stock" in json_data:
            stock = int(json_data["stock"])
        if "status" in json_data:
            gift_status = int(json_data["status"])
    else:
        # 不支持的请求格式
        raise HTTPException(
            status_code=400,
            detail="不支持的请求格式"
        )
    
    # 更新礼品信息
    if name is not None:
        gift.name = name
    if description is not None:
        gift.description = description
    if price is not None:
        gift.price = price
    if gift_status is not None:
        gift.status = gift_status
    
    # 更新库存
    stock_result = await db.execute(
        select(GiftStock).where(GiftStock.gift_id == gift.id)
    )
    gift_stock = stock_result.scalar_one_or_none()
    
    if stock is not None:
        if gift_stock:
            # 更新现有库存记录
            old_stock = gift_stock.current_stock
            gift_stock.current_stock = stock
            if stock > old_stock:
                gift_stock.total_in_stock += (stock - old_stock)
            logger.info(f"[DEBUG] Updated stock: {old_stock} -> {stock}")
        else:
            # 创建新的库存记录
            gift_stock = GiftStock(
                gift_id=gift.id,
                current_stock=stock,
                total_in_stock=stock,
                total_out_stock=0
            )
            db.add(gift_stock)
            logger.info(f"[DEBUG] Created new stock record: {stock}")
    elif gift_stock:
        logger.info(f"[DEBUG] Stock not provided, keeping existing stock: {gift_stock.current_stock}")
    else:
        logger.info(f"[DEBUG] No stock record exists and no stock provided")
    
    await db.commit()
    await db.refresh(gift)
    
    logger.info(f"更新礼品: {gift.name}")
    
    return {
        "id": gift.id,
        "name": gift.name,
        "description": gift.description,
        "price": gift.price,
        "stock": gift_stock.current_stock if gift_stock else 0,
        "status": gift.status,
        "image_path": gift.image_url,
        "images": image_urls if image_urls else [],
        "created_at": gift.created_at
    }


@router.delete("/{gift_id}")
async def delete_gift(
    gift_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """删除礼品"""
    result = await db.execute(
        select(Gift).where(Gift.id == gift_id, Gift.teacher_id == current_user.id)
    )
    gift = result.scalar_one_or_none()
    
    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="礼品不存在"
        )
    
    await db.execute(
        GiftClass.__table__.delete().where(GiftClass.gift_id == gift_id)
    )
    
    await db.execute(
        GiftStock.__table__.delete().where(GiftStock.gift_id == gift_id)
    )
    
    await db.delete(gift)
    await db.commit()
    
    logger.info(f"删除礼品: {gift.name}")
    
    return {"message": "删除成功"}


class GiftClassCreate(BaseModel):
    gift_id: int
    class_id: int


@router.post("/class")
async def add_gift_class(
    gift_class_data: GiftClassCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """添加礼品开放班级"""
    # 检查礼品是否存在且属于当前导师
    gift_result = await db.execute(
        select(Gift).where(Gift.id == gift_class_data.gift_id, Gift.teacher_id == current_user.id)
    )
    gift = gift_result.scalar_one_or_none()
    
    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="礼品不存在"
        )
    
    # 检查班级是否存在且属于当前导师
    class_result = await db.execute(
        select(ClassInfo).where(ClassInfo.id == gift_class_data.class_id, ClassInfo.teacher_id == current_user.id)
    )
    class_info = class_result.scalar_one_or_none()
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    # 检查是否已存在关联
    existing = await db.execute(
        select(GiftClass).where(
            GiftClass.gift_id == gift_class_data.gift_id,
            GiftClass.class_id == gift_class_data.class_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="礼品已开放给该班级"
        )
    
    gift_class = GiftClass(
        gift_id=gift_class_data.gift_id,
        class_id=gift_class_data.class_id
    )
    
    db.add(gift_class)
    await db.commit()
    await db.refresh(gift_class)
    
    logger.info(f"礼品 {gift.name} 开放给班级 {class_info.class_name}")
    
    return {
        "id": gift_class.id,
        "gift_id": gift_class.gift_id,
        "class_id": gift_class.class_id,
        "class_name": class_info.class_name,
        "school_name": class_info.school_name
    }


@router.delete("/class/{gift_id}/{class_id}")
async def remove_gift_class(
    gift_id: int,
    class_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """移除礼品开放班级"""
    # 检查礼品是否存在且属于当前导师
    gift_result = await db.execute(
        select(Gift).where(Gift.id == gift_id, Gift.teacher_id == current_user.id)
    )
    gift = gift_result.scalar_one_or_none()
    
    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="礼品不存在"
        )
    
    # 检查班级是否存在且属于当前导师
    class_result = await db.execute(
        select(ClassInfo).where(ClassInfo.id == class_id, ClassInfo.teacher_id == current_user.id)
    )
    class_info = class_result.scalar_one_or_none()
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    # 删除关联
    result = await db.execute(
        GiftClass.__table__.delete().where(
            GiftClass.gift_id == gift_id,
            GiftClass.class_id == class_id
        )
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联不存在"
        )
    
    await db.commit()
    
    logger.info(f"移除礼品 {gift.name} 对班级 {class_info.class_name} 的开放")
    
    return {"message": "移除成功"}


@router.get("/{gift_id}/classes")
async def get_gift_classes(
    gift_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """获取礼品开放的班级"""
    # 检查礼品是否存在且属于当前导师
    gift_result = await db.execute(
        select(Gift).where(Gift.id == gift_id, Gift.teacher_id == current_user.id)
    )
    gift = gift_result.scalar_one_or_none()
    
    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="礼品不存在"
        )
    
    # 获取礼品开放的班级
    result = await db.execute(
        select(
            GiftClass.class_id,
            ClassInfo.class_name,
            ClassInfo.school_name
        ).join(
            ClassInfo, ClassInfo.id == GiftClass.class_id
        ).where(
            GiftClass.gift_id == gift_id
        )
    )
    
    classes = []
    for row in result.all():
        classes.append({
            "class_id": row[0],
            "class_name": row[1],
            "school_name": row[2]
        })
    
    return {
        "gift_id": gift_id,
        "gift_name": gift.name,
        "classes": classes
    }


@router.get("/class/{class_id}")
async def get_gifts_by_class(
    class_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """获取班级可用的礼品列表"""
    # 检查班级是否存在且属于当前导师
    class_result = await db.execute(
        select(ClassInfo).where(ClassInfo.id == class_id, ClassInfo.teacher_id == current_user.id)
    )
    class_info = class_result.scalar_one_or_none()
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    # 打印调试信息
    logger.info(f"[DEBUG] get_gifts_by_class called for class_id: {class_id}, user_id: {current_user.id}")
    
    # 查询与该班级关联的礼品
    result = await db.execute(
        select(Gift).join(
            GiftClass, GiftClass.gift_id == Gift.id
        ).where(
            GiftClass.class_id == class_id,
            Gift.status == 1,  # 只显示启用的礼品
            Gift.teacher_id == current_user.id  # 只显示当前用户的礼品
        )
    )
    
    gifts = result.scalars().all()
    logger.info(f"[DEBUG] Found {len(gifts)} gifts for class_id: {class_id}")
    
    gift_list = []
    
    for gift in gifts:
        # 检查礼品库存
        stock_result = await db.execute(
            select(GiftStock).where(GiftStock.gift_id == gift.id)
        )
        gift_stock = stock_result.scalar_one_or_none()
        
        logger.info(f"[DEBUG] Gift {gift.id} ({gift.name}): stock={gift_stock.current_stock if gift_stock else 0}")
        
        if gift_stock and gift_stock.current_stock > 0:
            gift_list.append({
                "id": gift.id,
                "name": gift.name,
                "description": gift.description,
                "price": gift.price,
                "stock": gift_stock.current_stock,
                "status": gift.status,
                "image_path": gift.image_url
            })
        else:
            logger.info(f"[DEBUG] Gift {gift.id} ({gift.name}) skipped: no stock or stock <= 0")
    
    logger.info(f"[DEBUG] Returning {len(gift_list)} available gifts")
    
    return {
        "items": gift_list
    }


@router.get("/inventory/warnings")
async def get_stock_warnings(
    threshold: Optional[int] = Query(None, description="库存预警阈值"),
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """获取库存预警信息"""
    from app.services.inventory_service import InventoryService
    
    # 检查库存预警
    warnings = await InventoryService.check_stock_warnings(db)
    
    # 如果指定了阈值，获取低于该阈值的礼品
    if threshold is not None:
        low_stock_gifts = await InventoryService.get_low_stock_gifts(db, threshold)
        return {
            "warnings": low_stock_gifts,
            "threshold": threshold
        }
    
    return {
        "warnings": warnings,
        "threshold": InventoryService.STOCK_WARNING_THRESHOLD
    }


@router.post("/inventory/check")
async def check_inventory(
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """检查库存预警"""
    from app.services.inventory_service import InventoryService
    
    # 检查库存预警
    warnings = await InventoryService.check_stock_warnings(db)
    
    # 记录系统日志
    from app.models.system_log import SystemLog, LogType, LogLevel
    system_log = SystemLog(
        user_id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        log_type=LogType.OTHER,
        log_level=LogLevel.INFO,
        module="库存管理",
        action="检查库存预警",
        request_params=f"{{\"warning_count\": {len(warnings)}}}"
    )
    db.add(system_log)
    await db.commit()
    
    return {
        "message": f"库存检查完成，发现 {len(warnings)} 个礼品库存不足",
        "warnings": warnings
    }


@router.get("/student/available")
async def get_student_available_gifts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取学员当前班级可兑换的礼品列表"""
    from app.models.student_profile import StudentProfile
    from app.models.class_student import ClassStudent, BindStatus
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    # 查找用户的学员档案
    student_profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    student_profile = student_profile_result.scalar_one_or_none()

    if not student_profile:
        return {"items": []}

    # 查找该学员档案的已绑定班级
    bindings_result = await db.execute(
        select(ClassStudent).options(
            selectinload(ClassStudent.class_info)
        ).where(
            ClassStudent.student_profile_id == student_profile.id,
            ClassStudent.bind_status == BindStatus.APPROVED
        )
    )
    bindings = bindings_result.scalars().all()

    if not bindings:
        return {"items": []}

    # 获取所有已绑定班级的ID
    class_ids = [b.class_id for b in bindings]

    # 查询与这些班级关联的礼品（状态为启用且有库存的）
    result = await db.execute(
        select(Gift).join(
            GiftClass, GiftClass.gift_id == Gift.id
        ).where(
            GiftClass.class_id.in_(class_ids),
            Gift.status == 1  # 只显示启用的礼品
        ).distinct()
    )

    gifts = result.scalars().all()

    gift_list = []
    for gift in gifts:
        # 检查礼品库存
        stock_result = await db.execute(
            select(GiftStock).where(GiftStock.gift_id == gift.id)
        )
        gift_stock = stock_result.scalar_one_or_none()

        # 获取礼品适用的班级列表
        class_result = await db.execute(
            select(ClassInfo.class_name).join(
                GiftClass, GiftClass.class_id == ClassInfo.id
            ).where(
                GiftClass.gift_id == gift.id
            )
        )
        class_names = [r[0] for r in class_result.all()]

        gift_list.append({
            "id": gift.id,
            "name": gift.name,
            "description": gift.description,
            "price": gift.price,
            "stock": gift_stock.current_stock if gift_stock and gift_stock.current_stock > 0 else 0,
            "status": gift.status,
            "image_path": gift.image_url,
            "applicable_classes": class_names  # 添加适用班级信息
        })

    return {
        "items": gift_list
    }
