"""
聚会相关API
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timedelta
import random
import string
from models.gathering import (
    CreateGatheringRequest, 
    JoinGatheringRequest, 
    Gathering, 
    GatheringResponse,
    Participant
)
from app.database import get_mongodb, get_redis
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def generate_invite_code() -> str:
    """生成6位邀请码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@router.post("/create", response_model=GatheringResponse)
async def create_gathering(request: CreateGatheringRequest):
    """
    创建新聚会
    """
    try:
        db = get_mongodb()
        
        # 生成唯一邀请码
        code = generate_invite_code()
        while await db.gatherings.find_one({"code": code}):
            code = generate_invite_code()
        
        # 创建聚会对象
        gathering = {
            "id": f"gathering_{datetime.now().timestamp()}_{code}",
            "code": code,
            "type": request.type,
            "creator_id": f"creator_{random.randint(1000, 9999)}",
            "participants": [],
            "preferences": request.preferences or {},
            "recommendations": [],
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=settings.GATHERING_EXPIRE_HOURS),
            "status": "active"
        }
        
        # 如果创建者提供了位置，添加为第一个参与者
        if request.creator_location:
            creator = Participant(
                temp_id=gathering["creator_id"],
                nickname="发起人",
                location=request.creator_location,
                transport="driving"
            )
            gathering["participants"].append(creator.dict())
        
        # 保存到数据库
        await db.gatherings.insert_one(gathering)
        
        # 缓存到Redis（用于实时更新）
        redis = get_redis()
        if redis:
            await redis.setex(
                f"gathering:{code}",
                settings.GATHERING_EXPIRE_HOURS * 3600,
                Gathering(**gathering).json()
            )
        
        logger.info(f"Created gathering with code: {code}")
        
        return GatheringResponse(
            success=True,
            data=Gathering(**gathering),
            message="聚会创建成功"
        )
        
    except Exception as e:
        logger.error(f"Failed to create gathering: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/join", response_model=GatheringResponse)
async def join_gathering(request: JoinGatheringRequest):
    """
    加入聚会
    """
    try:
        db = get_mongodb()
        
        # 查找聚会
        gathering = await db.gatherings.find_one({"code": request.code.upper()})
        if not gathering:
            return GatheringResponse(
                success=False,
                message="邀请码无效或已过期"
            )
        
        # 检查是否过期
        if gathering["expires_at"] < datetime.now():
            await db.gatherings.update_one(
                {"code": request.code},
                {"$set": {"status": "expired"}}
            )
            return GatheringResponse(
                success=False,
                message="聚会已过期"
            )
        
        # 检查人数限制
        if len(gathering["participants"]) >= settings.MAX_PARTICIPANTS:
            return GatheringResponse(
                success=False,
                message=f"聚会人数已达上限（{settings.MAX_PARTICIPANTS}人）"
            )
        
        # 检查是否已经加入
        participant_ids = [p["temp_id"] for p in gathering["participants"]]
        if request.participant.temp_id in participant_ids:
            # 更新位置信息
            for i, p in enumerate(gathering["participants"]):
                if p["temp_id"] == request.participant.temp_id:
                    gathering["participants"][i] = request.participant.dict()
                    break
        else:
            # 添加新参与者
            gathering["participants"].append(request.participant.dict())
        
        # 更新数据库
        await db.gatherings.update_one(
            {"code": request.code.upper()},
            {"$set": {"participants": gathering["participants"]}}
        )
        
        # 更新Redis缓存
        redis = get_redis()
        if redis:
            await redis.setex(
                f"gathering:{request.code}",
                settings.GATHERING_EXPIRE_HOURS * 3600,
                Gathering(**gathering).json()
            )
        
        logger.info(f"User {request.participant.temp_id} joined gathering {request.code}")
        
        return GatheringResponse(
            success=True,
            data=Gathering(**gathering),
            message="成功加入聚会"
        )
        
    except Exception as e:
        logger.error(f"Failed to join gathering: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{code}", response_model=GatheringResponse)
async def get_gathering(code: str):
    """
    获取聚会详情
    """
    try:
        # 先从Redis获取
        redis = get_redis()
        if redis:
            cached = await redis.get(f"gathering:{code.upper()}")
            if cached:
                gathering = Gathering.parse_raw(cached)
                return GatheringResponse(
                    success=True,
                    data=gathering
                )
        
        # 从MongoDB获取
        db = get_mongodb()
        gathering = await db.gatherings.find_one({"code": code.upper()})
        
        if not gathering:
            return GatheringResponse(
                success=False,
                message="聚会不存在"
            )
        
        return GatheringResponse(
            success=True,
            data=Gathering(**gathering)
        )
        
    except Exception as e:
        logger.error(f"Failed to get gathering: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{code}")
async def cancel_gathering(code: str):
    """
    取消聚会
    """
    try:
        db = get_mongodb()
        
        result = await db.gatherings.update_one(
            {"code": code.upper()},
            {"$set": {"status": "cancelled"}}
        )
        
        if result.modified_count == 0:
            return {"success": False, "message": "聚会不存在"}
        
        # 从Redis删除
        redis = get_redis()
        if redis:
            await redis.delete(f"gathering:{code.upper()}")
        
        return {"success": True, "message": "聚会已取消"}
        
    except Exception as e:
        logger.error(f"Failed to cancel gathering: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list/recent")
async def list_recent_gatherings(limit: int = 10):
    """
    获取最近的聚会列表（用于调试）
    """
    try:
        db = get_mongodb()
        
        cursor = db.gatherings.find(
            {"status": "active"}
        ).sort("created_at", -1).limit(limit)
        
        gatherings = []
        async for doc in cursor:
            gatherings.append(Gathering(**doc))
        
        return {
            "success": True,
            "data": gatherings,
            "count": len(gatherings)
        }
        
    except Exception as e:
        logger.error(f"Failed to list gatherings: {e}")
        raise HTTPException(status_code=500, detail=str(e))