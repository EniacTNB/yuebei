# 后端参与者距离功能实现

## 📅 更新日期: 2024-11-29

---

## 🎯 功能概述

后端添加了参与者距离信息计算功能，为每个推荐地点返回各参与者到该地点的详细距离和通勤时间数据。

---

## 📝 修改文件清单

| 文件 | 变更类型 | 变更内容 |
|------|----------|----------|
| `server/models/gathering.py` | 修改 | 新增 `ParticipantDistance` 模型，更新 `RecommendationItem` |
| `server/core/algorithm.py` | 修改 | 新增距离计算方法，更新评分逻辑 |
| `server/api/recommendation.py` | 修改 | 更新模拟数据，添加距离信息 |

---

## 🔧 详细修改

### 1. 数据模型 (`models/gathering.py`)

#### 新增 ParticipantDistance 模型

```python
class ParticipantDistance(BaseModel):
    """参与者距离信息"""
    temp_id: str  # 参与者临时ID
    nickname: str  # 参与者昵称
    distance: float  # 距离（公里），保留1位小数
    travel_time: float  # 通勤时间（分钟），保留1位小数
    transport_mode: str  # 交通方式
```

#### 更新 RecommendationItem 模型

```python
class RecommendationItem(BaseModel):
    """推荐地点"""
    id: str
    name: str
    address: str
    location: Location
    type: str
    rating: Optional[float] = None
    price_level: Optional[str] = None
    avg_travel_time: float
    travel_times: Dict[str, float]
    score: float
    distance_from_center: float
    participant_distances: Optional[List[ParticipantDistance]] = []  # ⭐ 新增字段
```

### 2. 核心算法 (`core/algorithm.py`)

#### 新增距离计算方法

```python
@staticmethod
def calculate_distance(from_location: Location, to_location: Location) -> float:
    """
    计算两点之间的直线距离

    Args:
        from_location: 起点
        to_location: 终点

    Returns:
        距离（公里）
    """
    distance_km = geodesic(
        (from_location.lat, from_location.lng),
        (to_location.lat, to_location.lng)
    ).kilometers

    return round(distance_km, 1)
```

#### 更新 score_location 方法

在计算每个参与者的通勤时间时，同时计算距离并构建 `ParticipantDistance` 对象：

```python
@staticmethod
def score_location(
    location: Location,
    participants: List[Participant],
    rating: float = None,
    price_level: int = None
) -> Dict:
    """为单个地点打分"""

    # 计算每个人到该地点的通勤时间和距离
    travel_times = {}
    travel_time_list = []
    participant_distances = []  # ⭐ 新增

    for p in participants:
        if p.location:
            # 计算通勤时间
            time = RecommendationEngine.calculate_travel_time(
                p.location,
                location,
                p.transport or "driving"
            )
            travel_times[p.temp_id] = time
            travel_time_list.append(time)

            # ⭐ 计算距离
            distance = RecommendationEngine.calculate_distance(
                p.location,
                location
            )

            # ⭐ 构建参与者距离信息
            participant_distances.append(
                ParticipantDistance(
                    temp_id=p.temp_id,
                    nickname=p.nickname or "匿名",
                    distance=distance,
                    travel_time=time,
                    transport_mode=p.transport or "driving"
                )
            )

    # ... 评分计算逻辑 ...

    return {
        "location": location,
        "travel_times": travel_times,
        "avg_travel_time": round(avg_travel_time, 1),
        "fairness_score": fairness_score,
        "total_score": round(total_score, 2),
        "distance_from_center": round(distance_from_center, 1),
        "score_components": score_components,
        "participant_distances": participant_distances  # ⭐ 新增
    }
```

#### 更新 recommend_locations 方法

使用返回的 `participant_distances` 数据：

```python
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
    distance_from_center=score_result["distance_from_center"],
    participant_distances=score_result["participant_distances"]  # ⭐ 新增
)
```

### 3. API 接口 (`api/recommendation.py`)

#### 更新模拟数据

为模拟推荐数据添加 `participant_distances` 字段：

```python
@router.get("/mock/{gathering_code}")
async def get_mock_recommendations(gathering_code: str):
    """获取模拟推荐结果"""
    mock_recommendations = [
        RecommendationItem(
            id="rec_1",
            name="海底捞火锅(国贸店)",
            # ... 其他字段 ...
            participant_distances=[  # ⭐ 新增
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
        # ... 其他推荐地点 ...
    ]

    return {
        "success": True,
        "data": mock_recommendations
    }
```

---

## 📊 数据流程

### 推荐计算流程

```
1. 接收推荐请求
   ↓
2. 获取聚会信息和参与者列表
   ↓
3. 搜索候选地点
   ↓
4. 为每个候选地点评分
   ├─ 计算每个参与者到地点的通勤时间
   ├─ ⭐ 计算每个参与者到地点的距离
   ├─ ⭐ 构建 ParticipantDistance 对象列表
   └─ 计算综合评分
   ↓
5. 创建 RecommendationItem 对象
   └─ ⭐ 包含 participant_distances 字段
   ↓
6. 按评分排序并返回
```

---

## 🌐 API 响应示例

### POST /recommend/calculate

**请求：**
```json
{
  "gathering_code": "ABC123",
  "preferences": {}
}
```

**响应：**
```json
{
  "success": true,
  "data": [
    {
      "id": "place_123",
      "name": "星巴克咖啡",
      "address": "北京市朝阳区建国门外大街1号",
      "location": {
        "lat": 39.9042,
        "lng": 116.4074,
        "address": "北京市朝阳区建国门外大街1号"
      },
      "type": "咖啡厅",
      "rating": 4.5,
      "price_level": "2",
      "avg_travel_time": 15.0,
      "travel_times": {
        "user_1": 10.0,
        "user_2": 15.0,
        "user_3": 20.0
      },
      "score": 92.5,
      "distance_from_center": 500.0,
      "participant_distances": [
        {
          "temp_id": "user_1",
          "nickname": "张三",
          "distance": 2.1,
          "travel_time": 10.0,
          "transport_mode": "driving"
        },
        {
          "temp_id": "user_2",
          "nickname": "李四",
          "distance": 3.5,
          "travel_time": 15.0,
          "transport_mode": "transit"
        },
        {
          "temp_id": "user_3",
          "nickname": "王五",
          "distance": 4.8,
          "travel_time": 20.0,
          "transport_mode": "driving"
        }
      ]
    }
  ],
  "center_point": {
    "lat": 39.9042,
    "lng": 116.4074
  },
  "participant_count": 3
}
```

---

## 🔍 计算逻辑说明

### 距离计算

使用 `geopy.distance.geodesic` 计算两点之间的大地测量距离（考虑地球曲率）：

```python
distance_km = geodesic(
    (from_location.lat, from_location.lng),
    (to_location.lat, to_location.lng)
).kilometers

return round(distance_km, 1)  # 保留1位小数
```

### 通勤时间计算

基于距离和交通方式估算：

```python
# 交通方式对应的平均速度（km/h）
speed_map = {
    "driving": 30,   # 城市驾车
    "transit": 25,   # 公共交通
    "walking": 5,    # 步行
    "cycling": 15    # 骑行
}

speed = speed_map.get(transport, 25)
time_minutes = (distance_km / speed) * 60 * 1.3  # 1.3是路况系数
```

**注意：** 这是简化计算，生产环境应调用地图 API 获取实际路线信息。

---

## ✨ 功能特性

### 1. 自动计算
- ✅ 在评分阶段自动计算距离
- ✅ 无需额外 API 调用
- ✅ 与现有逻辑完美集成

### 2. 完整信息
- ✅ 包含每个参与者的昵称
- ✅ 距离精确到 0.1 公里
- ✅ 通勤时间精确到 0.1 分钟
- ✅ 交通方式明确标注

### 3. 性能优化
- ✅ 单次遍历计算距离和时间
- ✅ 数据结构优化，减少冗余
- ✅ 保留原有 `travel_times` 字典供兼容

---

## 🧪 测试验证

### 单元测试

```python
def test_calculate_distance():
    """测试距离计算"""
    from_loc = Location(lat=39.9042, lng=116.4074, address="位置A")
    to_loc = Location(lat=39.9142, lng=116.4174, address="位置B")

    distance = RecommendationEngine.calculate_distance(from_loc, to_loc)

    assert isinstance(distance, float)
    assert distance > 0
    assert distance == round(distance, 1)  # 验证保留1位小数

def test_participant_distances():
    """测试参与者距离信息"""
    participants = [
        Participant(
            temp_id="user_1",
            nickname="张三",
            location=Location(lat=39.9042, lng=116.4074, address="位置1"),
            transport="driving"
        ),
        Participant(
            temp_id="user_2",
            nickname="李四",
            location=Location(lat=39.9142, lng=116.4174, address="位置2"),
            transport="transit"
        )
    ]

    location = Location(lat=39.9092, lng=116.4124, address="目标地点")

    result = RecommendationEngine.score_location(
        location=location,
        participants=participants
    )

    assert "participant_distances" in result
    assert len(result["participant_distances"]) == 2

    for pd in result["participant_distances"]:
        assert pd.temp_id in ["user_1", "user_2"]
        assert pd.nickname in ["张三", "李四"]
        assert pd.distance > 0
        assert pd.travel_time > 0
        assert pd.transport_mode in ["driving", "transit"]
```

### 集成测试

```bash
# 启动后端服务
cd server
python main.py

# 测试推荐接口
curl -X POST http://localhost:8000/api/recommend/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "gathering_code": "ABC123",
    "preferences": {}
  }'

# 验证响应中包含 participant_distances 字段
```

---

## 📈 性能影响

### 计算复杂度

- **原有逻辑**: O(n * m) - n个参与者 × m个候选地点
- **新增逻辑**: O(n * m) - 复杂度不变，只是每次循环多一次距离计算

### 响应大小

每个推荐地点增加的数据：

```
participant_distances: [
  {
    temp_id: ~15 字节
    nickname: ~20 字节
    distance: ~5 字节
    travel_time: ~5 字节
    transport_mode: ~10 字节
  }
] × 参与者数量
```

假设 5 个参与者，每个推荐地点增加约 **275 字节**，5 个推荐地点总计约 **1.4 KB**，影响微乎其微。

---

## 🔄 向后兼容性

### 保留的字段

- ✅ `travel_times` 字典依然保留（供其他功能使用）
- ✅ `avg_travel_time` 依然计算（统计信息）
- ✅ 所有原有字段不变

### 新增字段

- ✅ `participant_distances` 是可选字段（`Optional[List]`）
- ✅ 默认值为空列表 `[]`
- ✅ 前端使用 `wx:if` 判断，不存在时不显示

### 兼容性保证

```python
# 旧版前端：忽略 participant_distances 字段
# 新版前端：显示详细距离信息
# 无需版本迁移
```

---

## 🚀 部署说明

### 1. 数据库迁移

无需数据库迁移，新字段会自动添加到新创建的推荐记录中。

### 2. 依赖检查

确保已安装 `geopy` 库（用于距离计算）：

```bash
pip install geopy
# 或
conda install -c conda-forge geopy
```

### 3. 服务重启

```bash
# 停止服务
pkill -f uvicorn

# 重启服务
cd server
python main.py
# 或
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 验证

访问 API 文档检查模型定义：
```
http://localhost:8000/docs
```

查看 `RecommendationItem` 模型，应包含 `participant_distances` 字段。

---

## 🔮 后续优化建议

### 1. 真实路线计算

替换简化计算，调用地图 API：

```python
async def calculate_real_distance_and_time(
    from_location: Location,
    to_location: Location,
    transport: str
) -> Tuple[float, float]:
    """调用高德/腾讯地图API获取真实路线"""
    # 实现真实 API 调用
    pass
```

### 2. 缓存优化

缓存参与者之间的距离计算结果：

```python
distance_cache = {}  # {(lat1,lng1,lat2,lng2): distance}
```

### 3. 异步计算

使用异步并发计算多个地点：

```python
async def score_locations_async(locations, participants):
    """并发计算多个地点的评分"""
    tasks = [score_location_async(loc, participants) for loc in locations]
    return await asyncio.gather(*tasks)
```

### 4. 距离排序

添加按距离排序的选项：

```python
# 按某个参与者的距离排序
recommendations.sort(key=lambda x: x.participant_distances[0].distance)
```

---

## 📞 技术支持

### 相关文档
- [前端距离显示文档](DISTANCE_DISPLAY_UPDATE.md)
- [推荐算法说明](server/core/algorithm.py)
- [数据模型定义](server/models/gathering.py)

### 常见问题

**Q1: 距离计算准确吗？**
A: 当前使用大地测量距离（geodesic），考虑地球曲率，直线距离较准确。实际路线距离需要调用地图 API。

**Q2: 通勤时间如何计算？**
A: 基于距离和交通方式估算，使用经验速度值和路况系数。生产环境建议调用地图 API。

**Q3: 为什么保留 travel_times 字典？**
A: 为了向后兼容，某些功能可能直接使用这个字典。participant_distances 提供更丰富的信息。

**Q4: 性能影响大吗？**
A: 几乎无影响。距离计算使用 geopy 库，非常高效。响应数据增加约 1-2 KB。

---

**后端更新完成！现在推荐结果包含完整的参与者距离信息！** 🎉
