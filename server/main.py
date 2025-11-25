"""
约呗后端服务主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from app.config import settings
from app.database import init_db, close_db
from api import gathering, location, recommendation
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting Yuebei Server...")
    await init_db()
    yield
    # 关闭时
    logger.info("Shutting down Yuebei Server...")
    await close_db()

# 创建FastAPI应用
app = FastAPI(
    title="约呗 API",
    description="智能聚会地点推荐服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(gathering.router, prefix="/api/gathering", tags=["聚会"])
app.include_router(location.router, prefix="/api/location", tags=["位置"])
app.include_router(recommendation.router, prefix="/api/recommend", tags=["推荐"])

@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "service": "Yuebei API", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    """API健康检查"""
    return {
        "status": "healthy",
        "database": "connected",
        "cache": "connected"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )