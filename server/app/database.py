"""
数据库连接管理
"""
from motor.motor_asyncio import AsyncIOMotorClient
from redis import asyncio as aioredis
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# 全局数据库连接
mongodb_client: AsyncIOMotorClient = None
mongodb = None
redis_client = None

async def init_db():
    """初始化数据库连接"""
    global mongodb_client, mongodb, redis_client
    
    try:
        # MongoDB连接
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb = mongodb_client[settings.MONGODB_DB]
        
        # 测试连接
        await mongodb_client.server_info()
        logger.info("MongoDB connection established")
        
        # 尝试创建索引（如果失败则跳过）
        try:
            await create_indexes()
            logger.info("Database indexes created")
        except Exception as idx_error:
            logger.warning(f"Could not create indexes (may already exist): {idx_error}")
        
        # Redis连接（可选）
        try:
            redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            await redis_client.ping()
            logger.info("Redis connection established")
        except Exception as redis_error:
            logger.warning(f"Redis not available, using MongoDB only: {redis_error}")
            redis_client = None
        
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        # 对于开发环境，继续运行但功能受限
        if settings.DEBUG:
            logger.warning("Running in DEBUG mode without full database connectivity")
        else:
            raise

async def close_db():
    """关闭数据库连接"""
    global mongodb_client, redis_client
    
    if mongodb_client:
        mongodb_client.close()
    if redis_client:
        await redis_client.close()
    
    logger.info("Database connections closed")

async def create_indexes():
    """创建数据库索引"""
    # 聚会集合索引
    gatherings = mongodb.gatherings
    await gatherings.create_index("code", unique=True)
    await gatherings.create_index("created_at")
    await gatherings.create_index("expires_at")
    
    # 位置集合索引（如果需要持久化）
    locations = mongodb.locations
    await locations.create_index([("location", "2dsphere")])
    
    logger.info("Database indexes created")

def get_mongodb():
    """获取MongoDB数据库实例"""
    return mongodb

def get_redis():
    """获取Redis客户端实例"""
    return redis_client