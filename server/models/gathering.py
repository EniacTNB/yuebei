"""
聚会数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class GatheringType(str, Enum):
    """聚会类型"""
    MEAL = "meal"  # 吃饭
    COFFEE = "coffee"  # 咖啡
    MOVIE = "movie"  # 电影
    KTV = "ktv"  # K歌
    OTHER = "other"  # 其他

class Location(BaseModel):
    """位置信息"""
    address: str  # 地址描述
    lng: float  # 经度
    lat: float  # 纬度
    name: Optional[str] = None  # 地点名称

class Participant(BaseModel):
    """参与者信息"""
    temp_id: str  # 临时用户ID
    nickname: Optional[str] = "匿名用户"
    location: Optional[Location] = None
    transport: Optional[str] = "driving"  # 交通方式: driving/transit/walking
    joined_at: datetime = Field(default_factory=datetime.now)

class CreateGatheringRequest(BaseModel):
    """创建聚会请求"""
    type: GatheringType = GatheringType.MEAL
    creator_location: Optional[Location] = None
    preferences: Optional[Dict] = None  # 偏好设置
    
class JoinGatheringRequest(BaseModel):
    """加入聚会请求"""
    code: str
    participant: Participant

class Gathering(BaseModel):
    """聚会信息"""
    id: str
    code: str  # 6位邀请码
    type: GatheringType
    creator_id: str
    participants: List[Participant] = []
    preferences: Dict = {}
    recommendations: List[Dict] = []  # 推荐结果
    created_at: datetime
    expires_at: datetime
    status: str = "active"  # active/expired/cancelled
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class GatheringResponse(BaseModel):
    """聚会响应"""
    success: bool
    data: Optional[Gathering] = None
    message: str = ""
    
class ParticipantDistance(BaseModel):
    """参与者距离信息"""
    temp_id: str  # 参与者临时ID
    nickname: str  # 参与者昵称
    distance: float  # 距离（公里），保留1位小数
    travel_time: float  # 通勤时间（分钟），保留1位小数
    transport_mode: str  # 交通方式

class RecommendationItem(BaseModel):
    """推荐地点"""
    id: str
    name: str
    address: str
    location: Location
    type: str  # 地点类型
    rating: Optional[float] = None
    price_level: Optional[int] = None
    avg_travel_time: float  # 平均通勤时间（分钟）
    travel_times: Dict[str, float]  # 每个人的通勤时间
    score: float  # 综合评分
    distance_from_center: float  # 距离中心点距离（米）
    participant_distances: Optional[List[ParticipantDistance]] = []  # 各参与者距离信息
