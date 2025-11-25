"""
核心推荐算法
"""
import numpy as np
from typing import List, Dict, Tuple
from geopy.distance import geodesic
from models.gathering import Location, Participant, RecommendationItem
import logging

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """推荐引擎"""
    
    @staticmethod
    def calculate_center_point(participants: List[Participant]) -> Tuple[float, float]:
        """
        计算所有参与者的几何中心点
        
        Args:
            participants: 参与者列表
            
        Returns:
            (纬度, 经度)
        """
        valid_participants = [p for p in participants if p.location]
        if not valid_participants:
            return None
            
        lats = [p.location.lat for p in valid_participants]
        lngs = [p.location.lng for p in valid_participants]
        
        # 计算平均值作为中心点
        center_lat = np.mean(lats)
        center_lng = np.mean(lngs)
        
        return (center_lat, center_lng)
    
    @staticmethod
    def calculate_weighted_center(participants: List[Participant], weights: Dict[str, float] = None) -> Tuple[float, float]:
        """
        计算加权中心点（可以根据不同因素给参与者设置权重）
        
        Args:
            participants: 参与者列表
            weights: 权重字典 {participant_id: weight}
            
        Returns:
            (纬度, 经度)
        """
        valid_participants = [p for p in participants if p.location]
        if not valid_participants:
            return None
            
        if not weights:
            # 默认所有人权重相同
            weights = {p.temp_id: 1.0 for p in valid_participants}
            
        total_weight = sum(weights.values())
        weighted_lat = sum(p.location.lat * weights.get(p.temp_id, 1.0) for p in valid_participants)
        weighted_lng = sum(p.location.lng * weights.get(p.temp_id, 1.0) for p in valid_participants)
        
        center_lat = weighted_lat / total_weight
        center_lng = weighted_lng / total_weight
        
        return (center_lat, center_lng)
    
    @staticmethod
    def calculate_travel_time(from_location: Location, to_location: Location, transport: str = "driving") -> float:
        """
        估算通勤时间（简化版本，实际应调用地图API）
        
        Args:
            from_location: 起点
            to_location: 终点
            transport: 交通方式
            
        Returns:
            预估时间（分钟）
        """
        # 计算直线距离
        distance_km = geodesic(
            (from_location.lat, from_location.lng),
            (to_location.lat, to_location.lng)
        ).kilometers
        
        # 根据交通方式估算速度（km/h）
        speed_map = {
            "driving": 30,  # 城市驾车平均速度
            "transit": 25,  # 公共交通平均速度
            "walking": 5,   # 步行速度
            "cycling": 15   # 骑行速度
        }
        
        speed = speed_map.get(transport, 25)
        
        # 添加一些随机因素模拟实际路况（实际应该调用地图API）
        time_minutes = (distance_km / speed) * 60 * 1.3  # 1.3是经验系数
        
        return round(time_minutes, 1)
    
    @staticmethod
    def calculate_fairness_score(travel_times: List[float]) -> float:
        """
        计算公平性得分（标准差越小越公平）
        
        Args:
            travel_times: 所有人的通勤时间列表
            
        Returns:
            公平性得分（0-100）
        """
        if not travel_times:
            return 0
            
        std_dev = np.std(travel_times)
        mean_time = np.mean(travel_times)
        
        # 变异系数（标准差/平均值）
        if mean_time > 0:
            cv = std_dev / mean_time
            # 将变异系数转换为0-100的得分
            fairness_score = max(0, 100 * (1 - cv))
        else:
            fairness_score = 100
            
        return round(fairness_score, 2)
    
    @staticmethod
    def score_location(
        location: Location,
        participants: List[Participant],
        rating: float = None,
        price_level: int = None
    ) -> Dict:
        """
        为单个地点打分
        
        Args:
            location: 地点位置
            participants: 参与者列表
            rating: 地点评分（可选）
            price_level: 价格水平（可选）
            
        Returns:
            评分结果字典
        """
        # 计算每个人到该地点的通勤时间
        travel_times = {}
        travel_time_list = []
        
        for p in participants:
            if p.location:
                time = RecommendationEngine.calculate_travel_time(
                    p.location, 
                    location, 
                    p.transport or "driving"
                )
                travel_times[p.temp_id] = time
                travel_time_list.append(time)
        
        # 计算平均通勤时间
        avg_travel_time = np.mean(travel_time_list) if travel_time_list else 0
        
        # 计算公平性得分
        fairness_score = RecommendationEngine.calculate_fairness_score(travel_time_list)
        
        # 计算综合得分
        score_components = {
            "fairness": fairness_score * 0.4,  # 公平性权重40%
            "time": max(0, 100 - avg_travel_time) * 0.3,  # 时间权重30%
        }
        
        # 如果有评分，加入评分因素
        if rating:
            score_components["rating"] = (rating / 5) * 100 * 0.2  # 评分权重20%
        
        # 如果有价格，加入价格因素（价格越低得分越高）
        if price_level:
            score_components["price"] = max(0, 100 - price_level * 20) * 0.1  # 价格权重10%
        
        total_score = sum(score_components.values())
        
        # 计算到中心点的距离
        center_point = RecommendationEngine.calculate_center_point(participants)
        if center_point:
            distance_from_center = geodesic(
                center_point,
                (location.lat, location.lng)
            ).meters
        else:
            distance_from_center = 0
        
        return {
            "location": location,
            "travel_times": travel_times,
            "avg_travel_time": round(avg_travel_time, 1),
            "fairness_score": fairness_score,
            "total_score": round(total_score, 2),
            "distance_from_center": round(distance_from_center, 1),
            "score_components": score_components
        }
    
    @staticmethod
    def recommend_locations(
        participants: List[Participant],
        candidate_locations: List[Dict],
        max_results: int = 5
    ) -> List[RecommendationItem]:
        """
        推荐最佳聚会地点
        
        Args:
            participants: 参与者列表
            candidate_locations: 候选地点列表
            max_results: 最多返回结果数
            
        Returns:
            推荐地点列表
        """
        if not participants or not candidate_locations:
            return []
        
        # 为每个候选地点打分
        scored_locations = []
        for candidate in candidate_locations:
            location = Location(
                address=candidate.get("address", ""),
                lng=candidate["lng"],
                lat=candidate["lat"],
                name=candidate.get("name", "")
            )
            
            score_result = RecommendationEngine.score_location(
                location=location,
                participants=participants,
                rating=candidate.get("rating"),
                price_level=candidate.get("price_level")
            )
            
            # 创建推荐项
            recommendation = RecommendationItem(
                id=candidate.get("id", ""),
                name=candidate.get("name", "未知地点"),
                address=candidate.get("address", ""),
                location=location,
                type=candidate.get("type", "restaurant"),
                rating=candidate.get("rating"),
                price_level=candidate.get("price_level"),
                avg_travel_time=score_result["avg_travel_time"],
                travel_times=score_result["travel_times"],
                score=score_result["total_score"],
                distance_from_center=score_result["distance_from_center"]
            )
            
            scored_locations.append(recommendation)
        
        # 按得分排序
        scored_locations.sort(key=lambda x: x.score, reverse=True)
        
        # 返回前N个结果
        return scored_locations[:max_results]
    
    @staticmethod
    def filter_by_preferences(
        recommendations: List[RecommendationItem],
        preferences: Dict
    ) -> List[RecommendationItem]:
        """
        根据偏好过滤推荐结果
        
        Args:
            recommendations: 推荐列表
            preferences: 偏好设置
            
        Returns:
            过滤后的推荐列表
        """
        filtered = recommendations
        
        # 按价格范围过滤
        if "max_price" in preferences:
            max_price = preferences["max_price"]
            filtered = [r for r in filtered if not r.price_level or int(r.price_level) <= max_price]
        
        # 按评分过滤
        if "min_rating" in preferences:
            min_rating = preferences["min_rating"]
            filtered = [r for r in filtered if not r.rating or r.rating >= min_rating]
        
        # 按最大通勤时间过滤
        if "max_travel_time" in preferences:
            max_time = preferences["max_travel_time"]
            filtered = [r for r in filtered if r.avg_travel_time <= max_time]
        
        return filtered