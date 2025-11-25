"""
位置相关API
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.gathering import Location
from services.map_service import get_map_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/geocode")
async def geocode_address(address: str):
    """
    地址转坐标（地理编码）
    """
    try:
        map_service = get_map_service()
        # 这里简化处理，实际应调用地图API
        # 返回模拟数据
        return {
            "success": True,
            "data": {
                "address": address,
                "location": {
                    "lat": 39.908 + (hash(address) % 100) / 10000,
                    "lng": 116.397 + (hash(address) % 100) / 10000
                }
            }
        }
    except Exception as e:
        logger.error(f"Geocoding failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reverse-geocode")
async def reverse_geocode(lat: float, lng: float):
    """
    坐标转地址（逆地理编码）
    """
    try:
        # 这里简化处理，实际应调用地图API
        return {
            "success": True,
            "data": {
                "location": {"lat": lat, "lng": lng},
                "address": f"北京市朝阳区（{lat:.3f}, {lng:.3f}）附近",
                "formatted_address": f"北京市朝阳区建国路{abs(hash(f'{lat}{lng}')) % 100}号"
            }
        }
    except Exception as e:
        logger.error(f"Reverse geocoding failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_location(location: Location):
    """
    验证位置有效性
    """
    try:
        # 检查经纬度范围
        if not (-90 <= location.lat <= 90):
            return {"success": False, "message": "纬度无效"}
        if not (-180 <= location.lng <= 180):
            return {"success": False, "message": "经度无效"}
        
        # 检查是否在中国境内（简化判断）
        if not (3.86 <= location.lat <= 53.55 and 73.66 <= location.lng <= 135.05):
            return {"success": False, "message": "位置不在服务范围内"}
        
        return {
            "success": True,
            "message": "位置有效",
            "data": location
        }
    except Exception as e:
        logger.error(f"Location validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_location(keyword: str, city: str = "北京"):
    """
    搜索地点
    """
    try:
        # 模拟搜索结果
        mock_results = [
            {
                "id": "1",
                "name": f"{keyword}(朝阳店)",
                "address": f"{city}市朝阳区",
                "location": {"lat": 39.908, "lng": 116.397}
            },
            {
                "id": "2",
                "name": f"{keyword}(海淀店)",
                "address": f"{city}市海淀区",
                "location": {"lat": 39.989, "lng": 116.313}
            }
        ]
        
        return {
            "success": True,
            "data": mock_results,
            "count": len(mock_results)
        }
    except Exception as e:
        logger.error(f"Location search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))