"""
推荐相关API
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.gathering import Participant, Location, RecommendationItem, ParticipantDistance
from core.algorithm import RecommendationEngine
from services.map_service import get_map_service
from app.database import get_mongodb
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/calculate")
async def calculate_recommendations(
    gathering_code: str,
    preferences: Optional[dict] = None
):
    """
    计算推荐地点
    """
    #  print("This is Calculating")
    print("========>Gathering Code  "+gathering_code);
    print("========>preferences: ")
    print(preferences)
    try:
        # 获取聚会信息
        db = get_mongodb()
        gathering = await db.gatherings.find_one({"code": gathering_code.upper()})
        
        if not gathering:
            raise HTTPException(status_code=404, detail="聚会不存在")
        
        # 转换参与者数据
        participants = [Participant(**p) for p in gathering["participants"]]
        
        # 过滤出有位置信息的参与者
        valid_participants = [p for p in participants if p.location]
        
        if len(valid_participants) < 2:
            return {
                "success": False,
                "message": "需要至少2个人的位置信息才能推荐",
                "data": []
            }
        
        # 计算中心点
        center_point = RecommendationEngine.calculate_center_point(valid_participants)
        
        # 获取地图服务
        map_service = get_map_service()
        
        # 搜索附近的候选地点
        keyword_map = {
            "meal": "餐厅",
            "coffee": "咖啡厅",
            "movie": "电影院",
            "ktv": "KTV",
            "other": "商场"
        }
        keyword = keyword_map.get(gathering["type"], "餐厅")
        
        candidate_places = await map_service.search_nearby(
            center=center_point,
            keyword=keyword,
            radius=3000
        )
        print("=================>candidate_places:")
        print(candidate_places)
        
        # 使用推荐引擎计算
        recommendations = RecommendationEngine.recommend_locations(
            participants=valid_participants,
            candidate_locations=candidate_places,
            max_results=5
        )
        
        # 根据偏好过滤
        if preferences:
            recommendations = RecommendationEngine.filter_by_preferences(
                recommendations=recommendations,
                preferences=preferences
            )
        
        # 更新数据库中的推荐结果
        recommendation_dicts = [r.dict() for r in recommendations]
        await db.gatherings.update_one(
            {"code": gathering_code.upper()},
            {"$set": {"recommendations": recommendation_dicts}}
        )
        
        return {
            "success": True,
            "data": recommendations,
            "center_point": {
                "lat": center_point[0],
                "lng": center_point[1]
            },
            "participant_count": len(valid_participants)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate recommendations: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mock/{gathering_code}")
async def get_mock_recommendations(gathering_code: str):
    """
    获取模拟推荐结果（用于测试）
    """
    try:
        mock_recommendations = [
            RecommendationItem(
                id="rec_1",
                name="海底捞火锅(国贸店)",
                address="北京市朝阳区建国门外大街1号",
                location=Location(
                    address="北京市朝阳区建国门外大街1号",
                    lat=39.908,
                    lng=116.459
                ),
                type="火锅",
                rating=4.8,
                price_level="3",
                avg_travel_time=25.5,
                travel_times={
                    "user_1": 20.0,
                    "user_2": 30.0,
                    "user_3": 26.5
                },
                score=85.5,
                distance_from_center=1200.0,
                participant_distances=[
                    ParticipantDistance(
                        temp_id="user_1",
                        nickname="张三",
                        distance=2.5,
                        travel_time=20.0,
                        transport_mode="driving"
                    ),
                    ParticipantDistance(
                        temp_id="user_2",
                        nickname="李四",
                        distance=4.2,
                        travel_time=30.0,
                        transport_mode="driving"
                    ),
                    ParticipantDistance(
                        temp_id="user_3",
                        nickname="王五",
                        distance=3.1,
                        travel_time=26.5,
                        transport_mode="transit"
                    )
                ]
            ),
            RecommendationItem(
                id="rec_2",
                name="西贝莜面村(三里屯店)",
                address="北京市朝阳区三里屯路19号",
                location=Location(
                    address="北京市朝阳区三里屯路19号",
                    lat=39.934,
                    lng=116.454
                ),
                type="中餐",
                rating=4.6,
                price_level="2",
                avg_travel_time=22.0,
                travel_times={
                    "user_1": 18.0,
                    "user_2": 25.0,
                    "user_3": 23.0
                },
                score=83.2,
                distance_from_center=800.0,
                participant_distances=[
                    ParticipantDistance(
                        temp_id="user_1",
                        nickname="张三",
                        distance=2.1,
                        travel_time=18.0,
                        transport_mode="driving"
                    ),
                    ParticipantDistance(
                        temp_id="user_2",
                        nickname="李四",
                        distance=3.5,
                        travel_time=25.0,
                        transport_mode="driving"
                    ),
                    ParticipantDistance(
                        temp_id="user_3",
                        nickname="王五",
                        distance=2.8,
                        travel_time=23.0,
                        transport_mode="transit"
                    )
                ]
            ),
            RecommendationItem(
                id="rec_3",
                name="绿茶餐厅(朝阳大悦城)",
                address="北京市朝阳区朝阳北路101号",
                location=Location(
                    address="北京市朝阳区朝阳北路101号",
                    lat=39.923,
                    lng=116.436
                ),
                type="中餐",
                rating=4.5,
                price_level="2",
                avg_travel_time=28.0,
                travel_times={
                    "user_1": 25.0,
                    "user_2": 32.0,
                    "user_3": 27.0
                },
                score=78.8,
                distance_from_center=1500.0,
                participant_distances=[
                    ParticipantDistance(
                        temp_id="user_1",
                        nickname="张三",
                        distance=3.2,
                        travel_time=25.0,
                        transport_mode="driving"
                    ),
                    ParticipantDistance(
                        temp_id="user_2",
                        nickname="李四",
                        distance=4.8,
                        travel_time=32.0,
                        transport_mode="driving"
                    ),
                    ParticipantDistance(
                        temp_id="user_3",
                        nickname="王五",
                        distance=3.6,
                        travel_time=27.0,
                        transport_mode="transit"
                    )
                ]
            )
        ]

        return {
            "success": True,
            "data": mock_recommendations,
            "message": "这是模拟数据"
        }

    except Exception as e:
        logger.error(f"Failed to get mock recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh/{gathering_code}")
async def refresh_recommendations(gathering_code: str):
    """
    刷新推荐结果
    """
    try:
        # 重新计算推荐
        result = await calculate_recommendations(gathering_code)
        
        return {
            "success": True,
            "message": "推荐结果已更新",
            "data": result["data"]
        }
        
    except Exception as e:
        logger.error(f"Failed to refresh recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
