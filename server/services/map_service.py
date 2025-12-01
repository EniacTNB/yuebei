"""
地图服务集成（腾讯地图/高德地图）
"""
import httpx
from typing import List, Dict, Optional, Tuple
from app.config import settings
import logging
import json
import hashlib
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class MapService:
    """地图服务基类"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def search_nearby(self, center: Tuple[float, float], keyword: str, radius: int) -> List[Dict]:
        """搜索附近的地点"""
        raise NotImplementedError
    
    async def calculate_route(self, from_point: Tuple[float, float], to_point: Tuple[float, float], mode: str) -> Dict:
        """计算路线"""
        raise NotImplementedError

class TencentMapService(MapService):
    """腾讯地图服务"""

    def __init__(self):
        super().__init__()
        self.key = settings.TENCENT_MAP_KEY
        self.sk = settings.TENCENT_MAP_SK
        self.base_url = "https://apis.map.qq.com"

    def _generate_signature(self, path: str, params: Dict) -> str:
        """
        生成腾讯地图API的SK签名

        签名算法:
        1. 对参数按key进行字典升序排序
        2. 拼接请求路径和参数: /path?key1=value1&key2=value2&key=KEY
        3. 在末尾加上SK: /path?key1=value1&key2=value2&key=KEYSK值（注意：SK直接拼接，不加&）
        4. 计算MD5值作为签名

        Args:
            path: API路径,如 /ws/place/v1/search
            params: 请求参数字典

        Returns:
            签名字符串
        """
        if not self.sk:
            return None

        # 1. 对参数按key排序
        sorted_params = sorted(params.items(), key=lambda x: x[0])

        # 2. 手动拼接参数字符串（不进行urlencode，使用原始值）
        param_pairs = []
        for key, value in sorted_params:
            param_pairs.append(f"{key}={value}")
        param_str = "&".join(param_pairs)
        
        print(f"参数字符串: {param_str}")

        # 3. 拼接完整字符串: path?params+SK（SK直接拼接，不加&符号）
        sign_str = f"{path}?{param_str}{self.sk}"
        print(f"签名字符串: {sign_str}")

        # 4. 计算MD5（小写）
        signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        print(f"计算得到签名: {signature}")

        logger.debug(f"Sign string: {sign_str}")
        logger.debug(f"Signature: {signature}")

        return signature
    
    async def search_nearby(self, center: Tuple[float, float], keyword: str = "餐厅", radius: int = 3000) -> List[Dict]:
        """
        搜索附近的餐厅/咖啡厅等

        Args:
            center: (纬度, 经度)
            keyword: 搜索关键词
            radius: 搜索半径（米）

        Returns:
            地点列表
        """
        if not self.key:
            logger.warning("Tencent Map API key not configured, using mock data")
            return self._get_mock_places(center)

        path = "/ws/place/v1/search"
        url = f"{self.base_url}{path}"
        params = {
            "key": self.key,
            "keyword": keyword,
            "boundary": f"nearby({center[0]},{center[1]},{radius})",
            "orderby": "_distance",
            "page_size": 20
        }

        # 如果配置了SK,生成签名
        if self.sk:
            signature = self._generate_signature(path, params)
            params["sig"] = signature

        try:
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                print(data)
                if data.get("status") == 0:
                    places = []
                    for item in data.get("data", []):
                        places.append({
                            "id": item.get("id"),
                            "name": item.get("title"),
                            "address": item.get("address"),
                            "lat": item["location"]["lat"],
                            "lng": item["location"]["lng"],
                            "type": item.get("category", "餐厅"),
                            "rating": item.get("_distance", {}).get("rating"),
                            "price_level": self._parse_price_level(item.get("price")),
                            "tel": item.get("tel")
                        })
                    return places
                else:
                    logger.error(f"Tencent Map API error: status={data.get('status')}, message={data.get('message')}")
            else:
                logger.error(f"Tencent Map API HTTP error: {response.status_code}, {response.text}")
        except Exception as e:
            logger.error(f"Failed to search nearby places: {e}")

        return self._get_mock_places(center)
    
    async def calculate_route(self, from_point: Tuple[float, float], to_point: Tuple[float, float], mode: str = "driving") -> Dict:
        """
        计算路线和通勤时间

        Args:
            from_point: 起点 (纬度, 经度)
            to_point: 终点 (纬度, 经度)
            mode: 出行方式 driving/transit/walking/bicycling

        Returns:
            路线信息
        """
        if not self.key:
            # 返回估算值
            return {
                "distance": 5000,
                "duration": 20,
                "mode": mode
            }

        # 腾讯地图出行方式映射
        path_map = {
            "driving": "/ws/direction/v1/driving",
            "transit": "/ws/direction/v1/transit",
            "walking": "/ws/direction/v1/walking",
            "bicycling": "/ws/direction/v1/bicycling"
        }

        path = path_map.get(mode, path_map["driving"])
        url = f"{self.base_url}{path}"
        params = {
            "key": self.key,
            "from": f"{from_point[0]},{from_point[1]}",
            "to": f"{to_point[0]},{to_point[1]}"
        }

        # 如果配置了SK,生成签名
        if self.sk:
            signature = self._generate_signature(path, params)
            params["sig"] = signature

        try:
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 0 and data.get("result"):
                    routes = data["result"]["routes"]
                    if routes:
                        route = routes[0]
                        return {
                            "distance": route.get("distance", 0),
                            "duration": route.get("duration", 0) / 60,  # 转换为分钟
                            "mode": mode
                        }
                else:
                    logger.error(f"Tencent Map route API error: status={data.get('status')}, message={data.get('message')}")
            else:
                logger.error(f"Tencent Map route API HTTP error: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to calculate route: {e}")

        # 返回估算值
        return {
            "distance": 5000,
            "duration": 20,
            "mode": mode
        }
    
    def _parse_price_level(self, price_str: str) -> Optional[int]:
        """解析价格等级"""
        if not price_str:
            return None
        # 根据价格字符串返回1-5的等级
        if "0-50" in price_str:
            return 1
        elif "50-100" in price_str:
            return 2
        elif "100-200" in price_str:
            return 3
        elif "200-500" in price_str:
            return 4
        else:
            return 5
    
    def _get_mock_places(self, center: Tuple[float, float]) -> List[Dict]:
        """获取模拟数据（开发测试用）"""
        mock_places = [
            {
                "id": "mock_1",
                "name": "海底捞火锅(国贸店)",
                "address": "北京市朝阳区建国门外大街1号国贸商城",
                "lat": center[0] + 0.01,
                "lng": center[1] + 0.01,
                "type": "火锅",
                "rating": 4.8,
                "price_level": 3,
                "tel": "010-12345678"
            },
            {
                "id": "mock_2",
                "name": "西贝莜面村(三里屯店)",
                "address": "北京市朝阳区三里屯路19号",
                "lat": center[0] - 0.008,
                "lng": center[1] + 0.012,
                "type": "中餐",
                "rating": 4.6,
                "price_level": 2,
                "tel": "010-87654321"
            },
            {
                "id": "mock_3",
                "name": "星巴克(CBD店)",
                "address": "北京市朝阳区CBD核心区",
                "lat": center[0] + 0.005,
                "lng": center[1] - 0.008,
                "type": "咖啡厅",
                "rating": 4.5,
                "price_level": 2,
                "tel": "010-11111111"
            },
            {
                "id": "mock_4",
                "name": "绿茶餐厅(朝阳大悦城店)",
                "address": "北京市朝阳区朝阳北路101号",
                "lat": center[0] - 0.012,
                "lng": center[1] - 0.005,
                "type": "中餐",
                "rating": 4.7,
                "price_level": 2,
                "tel": "010-22222222"
            },
            {
                "id": "mock_5",
                "name": "必胜客(望京店)",
                "address": "北京市朝阳区望京街",
                "lat": center[0] + 0.015,
                "lng": center[1] - 0.01,
                "type": "西餐",
                "rating": 4.3,
                "price_level": 2,
                "tel": "010-33333333"
            }
        ]
        return mock_places

class AMapService(MapService):
    """高德地图服务（备用）"""
    
    def __init__(self):
        super().__init__()
        self.key = settings.AMAP_KEY
        self.base_url = "https://restapi.amap.com"
    
    async def search_nearby(self, center: Tuple[float, float], keyword: str = "餐厅", radius: int = 3000) -> List[Dict]:
        """搜索附近的地点（高德地图实现）"""
        if not self.key:
            return []
        
        url = f"{self.base_url}/v3/place/around"
        params = {
            "key": self.key,
            "location": f"{center[1]},{center[0]}",  # 高德使用经度,纬度
            "keywords": keyword,
            "radius": radius,
            "offset": 20,
            "extensions": "all"
        }
        
        try:
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    places = []
                    for item in data.get("pois", []):
                        location = item.get("location", "").split(",")
                        if len(location) == 2:
                            places.append({
                                "id": item.get("id"),
                                "name": item.get("name"),
                                "address": item.get("address"),
                                "lng": float(location[0]),
                                "lat": float(location[1]),
                                "type": item.get("type", "").split(";")[0],
                                "rating": float(item.get("rating", 0)),
                                "tel": item.get("tel")
                            })
                    return places
        except Exception as e:
            logger.error(f"Failed to search with AMap: {e}")
        
        return []

# 工厂函数
def get_map_service() -> MapService:
    """获取地图服务实例"""
    if settings.TENCENT_MAP_KEY:
        return TencentMapService()
    elif settings.AMAP_KEY:
        return AMapService()
    else:
        # 默认使用腾讯地图（会返回模拟数据）
        return TencentMapService()
