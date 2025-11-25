"""
配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """应用配置"""
    # 基础配置
    DEBUG: bool = True
    PORT: int = 8000
    SECRET_KEY: str = "development-secret-key"
    
    # MongoDB配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "yuebei"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # 地图API配置
    TENCENT_MAP_KEY: Optional[str] = None
    AMAP_KEY: Optional[str] = None
    
    # 业务配置
    GATHERING_EXPIRE_HOURS: int = 24
    MAX_PARTICIPANTS: int = 20
    SEARCH_RADIUS: int = 5000  # 米
    MAX_RECOMMENDATIONS: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建配置实例
settings = Settings()