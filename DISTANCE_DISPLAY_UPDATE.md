# 参与者距离显示功能

## 📅 更新日期: 2024-11-29

---

## 🎯 功能概述

在推荐地点卡片中新增**各参与者距离信息**展示，让用户可以清晰看到每个参与者到候选地点的具体距离和通勤时间。

---

## ✨ 功能特性

### 1. 距离信息展示
- ✅ 显示每个参与者到地点的距离（公里）
- ✅ 显示每个参与者的通勤时间（分钟）
- ✅ 横向滚动查看，支持多人场景
- ✅ 独立的视觉设计，与推荐卡片协调

### 2. 信息呈现
- ✅ 参与者头像 + 昵称 + 距离/时间
- ✅ 蓝色系配色，区分于其他模块
- ✅ 卡片式设计，信息层次清晰
- ✅ 支持长昵称自动省略

---

## 🎨 界面设计

### 推荐地点卡片（新增距离信息）

```
┌─────────────────────────────────────┐
│ [1] 星巴克咖啡               [✕]   │
│     北京市朝阳区建国门外大街1号     │
│                                     │
│ ┌───────────────────────────────┐  │
│ │ 平均通勤  │  评分  │  匹配度  │  │
│ │ 15分钟    │ 4.5分  │  95%    │  │
│ └───────────────────────────────┘  │
│                                     │
│ ╔═══════════════════════════════╗  │
│ ║ 各参与者距离                   ║  │
│ ║ ← 滑动查看更多 →               ║  │
│ ║ ┌────┬────┬────┬────┐        ║  │
│ ║ │[头]│[头]│[头]│[头]│        ║  │
│ ║ │张三│李四│王五│赵六│        ║  │
│ ║ │2.1 │3.5 │1.8 │4.2 │        ║  │
│ ║ │km· │km· │km· │km· │        ║  │
│ ║ │10分│15分│8分 │18分│        ║  │
│ ║ └────┴────┴────┴────┘        ║  │
│ ╚═══════════════════════════════╝  │
│                                     │
│                        [导航 →]    │
└─────────────────────────────────────┘
```

### 视觉设计

**距离信息区域：**
- 背景：浅蓝色渐变 (`#F0F9FF` → `#E0F2FE`)
- 边框：蓝色边框 (`#BAE6FD`)
- 标题：深蓝色文字 (`#0369A1`)

**距离卡片：**
- 背景：白色卡片
- 头像：蓝色渐变 (`#0EA5E9` → `#0284C7`)
- 阴影：淡蓝色阴影
- 圆角：30rpx（胶囊形）

---

## 💻 技术实现

### WXML 结构

```xml
<!-- 各参与者距离信息 -->
<view class="participant-distances"
      wx:if="{{item.participant_distances && item.participant_distances.length > 0}}">
  <view class="distances-title">各参与者距离</view>

  <scroll-view
    class="distances-scroll"
    scroll-x
    show-scrollbar="{{false}}"
    enable-flex
    scroll-with-animation>
    <view class="distances-list">
      <view class="distance-item"
            wx:for="{{item.participant_distances}}"
            wx:key="temp_id"
            wx:for-item="dist">
        <!-- 头像 -->
        <view class="distance-avatar">{{dist.nickname[0] || '匿'}}</view>

        <!-- 信息 -->
        <view class="distance-info">
          <text class="distance-name">{{dist.nickname}}</text>
          <text class="distance-value">{{dist.distance}}km · {{dist.travel_time}}分钟</text>
        </view>
      </view>
    </view>
  </scroll-view>
</view>
```

### CSS 样式

```css
/* 距离信息容器 */
.participant-distances {
  margin: 20rpx 0;
  padding: 20rpx;
  background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
  border-radius: 12rpx;
  border: 1rpx solid #BAE6FD;
}

/* 标题 */
.distances-title {
  font-size: 26rpx;
  color: #0369A1;
  font-weight: 600;
  margin-bottom: 16rpx;
}

/* 横向滚动 */
.distances-scroll {
  width: 100%;
  white-space: nowrap;
}

.distances-list {
  display: inline-flex;
  gap: 16rpx;
}

/* 距离卡片 */
.distance-item {
  display: inline-flex;
  align-items: center;
  gap: 12rpx;
  background: #fff;
  padding: 12rpx 16rpx;
  border-radius: 30rpx;
  flex-shrink: 0;
  box-shadow: 0 2rpx 4rpx rgba(3, 105, 161, 0.1);
  min-width: 180rpx;
}

/* 头像 */
.distance-avatar {
  width: 44rpx;
  height: 44rpx;
  background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: bold;
  flex-shrink: 0;
}

/* 文字信息 */
.distance-info {
  display: flex;
  flex-direction: column;
  gap: 2rpx;
  flex: 1;
  min-width: 0;
}

.distance-name {
  font-size: 26rpx;
  color: #0C4A6E;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.distance-value {
  font-size: 22rpx;
  color: #0369A1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

---

## 📊 数据格式

### 后端返回数据结构

推荐地点的数据应包含 `participant_distances` 字段：

```json
{
  "id": "place_123",
  "name": "星巴克咖啡",
  "address": "北京市朝阳区建国门外大街1号",
  "location": {
    "lat": 39.9042,
    "lng": 116.4074
  },
  "rating": 4.5,
  "avg_travel_time": 15,
  "score": 95,
  "participant_distances": [
    {
      "temp_id": "user_1701234567890",
      "nickname": "张三",
      "distance": 2.1,
      "travel_time": 10,
      "transport_mode": "driving"
    },
    {
      "temp_id": "user_1701234567891",
      "nickname": "李四",
      "distance": 3.5,
      "travel_time": 15,
      "transport_mode": "driving"
    },
    {
      "temp_id": "user_1701234567892",
      "nickname": "王五",
      "distance": 1.8,
      "travel_time": 8,
      "transport_mode": "walking"
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `temp_id` | String | 参与者临时ID |
| `nickname` | String | 参与者昵称 |
| `distance` | Number | 距离（公里），保留1位小数 |
| `travel_time` | Number | 通勤时间（分钟），整数 |
| `transport_mode` | String | 交通方式（driving/transit/walking） |

---

## 🔌 后端 API 更新

### 推荐计算接口

```
POST /recommend/calculate
```

**返回数据需要包含 `participant_distances`：**

```json
{
  "success": true,
  "data": [
    {
      "id": "place_123",
      "name": "星巴克咖啡",
      "address": "北京市朝阳区建国门外大街1号",
      "location": { "lat": 39.9042, "lng": 116.4074 },
      "rating": 4.5,
      "avg_travel_time": 15,
      "score": 95,
      "participant_distances": [
        {
          "temp_id": "user_xxx",
          "nickname": "张三",
          "distance": 2.1,
          "travel_time": 10,
          "transport_mode": "driving"
        }
      ]
    }
  ]
}
```

### 后端计算逻辑

1. **获取所有参与者位置**
2. **计算每个参与者到候选地点的距离**
   - 使用地图 API 计算实际路线距离
   - 根据交通方式计算通勤时间
3. **组装 `participant_distances` 数据**
4. **返回推荐结果**

---

## 🎯 用户体验

### 信息透明度
- ✅ 用户可以清楚看到每个人的距离
- ✅ 便于发现不公平的推荐
- ✅ 帮助做出更明智的选择

### 交互体验
- ✅ 横向滚动查看所有参与者
- ✅ 卡片式设计，信息层次清晰
- ✅ 蓝色配色区分于其他模块
- ✅ 平滑滚动动画

### 视觉层次
```
推荐地点卡片
├── 地点名称和地址（黑色）
├── 统计信息（灰色背景）
│   ├── 平均通勤
│   ├── 评分
│   └── 匹配度
├── 各参与者距离（蓝色背景）⭐ 新增
│   ├── 张三 - 2.1km · 10分钟
│   ├── 李四 - 3.5km · 15分钟
│   └── ...
└── 导航按钮（红色）
```

---

## 🧪 测试场景

### 场景 1: 正常显示
1. 多人聚会（3人及以上）
2. 查看推荐地点
3. ✅ 预期：显示"各参与者距离"区域，每个人的距离和时间正确

### 场景 2: 横向滚动
1. 参与者较多（5人以上）
2. 距离信息卡片超出屏幕宽度
3. ✅ 预期：可以左右滑动查看所有参与者

### 场景 3: 文字超长
1. 参与者昵称很长
2. ✅ 预期：昵称自动省略显示 "..."

### 场景 4: 数据缺失
1. 后端未返回 `participant_distances`
2. ✅ 预期：不显示距离信息区域（wx:if 判断）

### 场景 5: 单人模式
1. 只有一个参与者
2. ✅ 预期：显示附近地点，不显示参与者距离（因为只有一个人）

---

## 📱 响应式设计

### 距离卡片宽度
- **最小宽度**: 180rpx
- **自适应内容**: 根据昵称和距离文字长度自动扩展
- **防止挤压**: `flex-shrink: 0`

### 文字处理
- **昵称超长**: 省略号显示
- **距离格式**: `X.Xkm · XX分钟`
- **对齐方式**: 左对齐

---

## 🎨 设计亮点

### 1. 色彩系统
- 使用蓝色系区分于其他功能模块
- 渐变背景增加视觉层次
- 与主色调（紫色）形成对比

### 2. 信息层次
- 标题 → 横向滚动列表 → 个人卡片
- 三级信息层次，清晰明了

### 3. 交互细节
- 隐藏滚动条，界面更简洁
- 平滑滚动动画
- 卡片阴影增加立体感

### 4. 可扩展性
- 支持任意数量参与者
- 横向滚动自适应
- 文字超长自动省略

---

## 🔄 与现有功能的关系

### 统计信息区域
```css
background: #f8f8f8;  /* 灰色背景 */
```
- 显示：平均通勤、评分、匹配度
- 功能：整体统计数据

### 距离信息区域（新增）
```css
background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);  /* 蓝色背景 */
```
- 显示：每个参与者的详细距离
- 功能：个性化信息

### 关系
- **统计信息**：宏观数据，快速判断
- **距离信息**：微观数据，详细了解
- **互补关系**：两者结合提供完整视图

---

## 📊 数据示例

### 3人聚会推荐

```json
{
  "name": "海底捞火锅",
  "avg_travel_time": 12,
  "score": 92,
  "participant_distances": [
    {
      "nickname": "张三",
      "distance": 1.5,
      "travel_time": 8
    },
    {
      "nickname": "李四",
      "distance": 2.8,
      "travel_time": 12
    },
    {
      "nickname": "王五",
      "distance": 3.2,
      "travel_time": 15
    }
  ]
}
```

### 界面显示

```
╔═══════════════════════════════════╗
║ 各参与者距离                       ║
║ ┌────────┬────────┬────────┐    ║
║ │ [张] 张三│ [李] 李四│ [王] 王五│    ║
║ │ 1.5km ·│ 2.8km ·│ 3.2km ·│    ║
║ │ 8分钟  │ 12分钟 │ 15分钟 │    ║
║ └────────┴────────┴────────┘    ║
╚═══════════════════════════════════╝

平均通勤：12分钟
```

---

## ✅ 完成清单

功能实现检查：

- [x] WXML 结构添加距离信息区域
- [x] CSS 样式完整实现
- [x] 横向滚动支持
- [x] 头像和昵称显示
- [x] 距离和时间格式化
- [x] 文字超长省略
- [x] 响应式设计
- [x] 视觉效果优化

待后端支持：

- [ ] API 返回 `participant_distances` 字段
- [ ] 计算每个参与者到地点的距离
- [ ] 根据交通方式计算通勤时间
- [ ] 数据格式化（距离保留1位小数）

---

## 🔮 后续优化建议

### 1. 交通方式图标
显示每个参与者使用的交通方式：
```
张三 🚗 1.5km · 8分钟
李四 🚌 2.8km · 12分钟
王五 🚶 3.2km · 15分钟
```

### 2. 距离排序
按距离从近到远排序显示

### 3. 距离差异提示
如果某个参与者距离特别远，显示提示：
```
⚠️ 王五距离较远（3.2km），考虑其他地点？
```

### 4. 点击展开详情
点击距离卡片显示详细路线信息

### 5. 颜色编码
- 近距离（<2km）：绿色
- 中距离（2-5km）：蓝色
- 远距离（>5km）：橙色

---

## 📞 技术支持

### 相关文档
- [项目总览](README.md)
- [协同管理功能](COLLABORATIVE_MANAGEMENT.md)
- [前端更新日志](FRONTEND_UPDATES.md)

### API 对接
后端需要在推荐计算接口中返回 `participant_distances` 数组，包含每个参与者到地点的距离和通勤时间。

---

**功能开发完成！等待后端 API 支持！** 🎉
