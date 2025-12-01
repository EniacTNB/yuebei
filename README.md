# 约呗 (YueBei) - 智能聚会地点推荐小程序

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![WeChat MiniProgram](https://img.shields.io/badge/微信小程序-原生-brightgreen.svg)](https://developers.weixin.qq.com/miniprogram/dev/framework/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0-success.svg)](https://www.mongodb.com/)

## 📱 项目简介

约呗是一款帮助朋友快速找到最方便聚会地点的微信小程序，通过智能算法计算多人位置的最优聚会点。

### 核心价值
- 🚫 **无需注册** - 使用临时ID快速发起聚会
- 🎯 **智能推荐** - 综合考虑通勤时间、公平性、地点评分
- 🔗 **简单分享** - 6位邀请码轻松邀请好友
- ⏰ **自动过期** - 聚会数据24小时后自动清理

---

## 🛠️ 技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| **前端** | 微信小程序原生框架 | WXML + WXSS + JavaScript |
| **后端** | Python 3.11 + FastAPI | 现代化异步Web框架 |
| **数据库** | MongoDB 6.0 | 文档型数据库 |
| **缓存** | Redis 7 (可选) | 实时更新支持 |
| **地图服务** | 腾讯地图API / 高德地图API | 位置服务与POI搜索 |
| **虚拟环境** | Conda / venv | 依赖管理 |

---

## 📂 项目结构

```
yuebei/
├── miniprogram/              # 微信小程序前端
│   ├── pages/               # 页面目录
│   │   ├── index/          # 首页
│   │   ├── create/         # 创建聚会
│   │   ├── join/           # 加入聚会
│   │   └── result/         # 推荐结果
│   ├── app.js              # 小程序入口
│   └── project.config.json # 小程序配置
│
├── server/                  # Python 后端服务
│   ├── api/                # API 路由
│   ├── core/               # 核心算法
│   ├── models/             # 数据模型
│   ├── services/           # 外部服务
│   ├── app/                # 应用配置
│   ├── main.py             # FastAPI 入口
│   └── requirements.txt    # Python 依赖
│
├── start.sh                # 启动脚本 (支持 Conda & venv)
├── start-conda.sh          # Conda 专用启动脚本
├── setup-mongodb.sh        # MongoDB 安装向导
├── environment.yml         # Conda 环境配置
├── docker-compose.yml      # Docker 编排配置
└── README.md              # 项目说明
```

---

## 🚀 快速开始

### 方式一：一键启动（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd yuebei

# 2. 安装 MongoDB（首次运行）
./setup-mongodb.sh
# 选择安装方式：[1] Homebrew / [2] Docker / [3] MongoDB Atlas

# 3. 启动服务（自动检测 Conda 或 venv）
./start.sh
```

### 方式二：使用 Conda（推荐）

```bash
# 1. 创建 Conda 环境
conda env create -f environment.yml
conda activate yuebei

# 2. 安装 MongoDB
./setup-mongodb.sh

# 3. 测试数据库连接
python server/test_db_connection.py

# 4. 启动后端服务
./start-conda.sh
```

### 方式三：使用 venv

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r server/requirements.txt

# 3. 安装 MongoDB
./setup-mongodb.sh

# 4. 启动服务
./start.sh
```

---

## 📝 配置说明

### 1. 环境变量配置

复制 `server/.env.example` 到 `server/.env` 并编辑：

```bash
# 服务配置
DEBUG=True
PORT=8000

# MongoDB 配置
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=yuebei

# 地图 API（可选，不填使用模拟数据）
TENCENT_MAP_KEY=your_key_here
AMAP_KEY=your_key_here

# 业务配置
GATHERING_EXPIRE_HOURS=24
MAX_PARTICIPANTS=20
```

### 2. 小程序配置

编辑 `miniprogram/app.js`：

```javascript
globalData: {
  baseUrl: 'http://localhost:8000/api'  // 后端API地址
}
```

---

## 🧪 测试与验证

### 测试数据库连接

```bash
conda activate yuebei  # 或 source venv/bin/activate
python server/test_db_connection.py
```

### 访问 API 文档

启动服务后访问：
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health

### 测试小程序

1. 使用微信开发者工具打开 `miniprogram` 目录
2. 配置 AppID（可选，使用测试号）
3. 点击编译预览

---

## ✨ 核心功能

- ✅ **快速发起聚会** - 无需注册，一键创建
- ✅ **实时位置收集** - 支持多种定位方式
- ✅ **智能地点推荐** - 多维度评分算法
  - 公平性评估（40%）
  - 平均通勤时间（30%）
  - 地点评分（20%）
  - 价格水平（10%）
- ✅ **微信分享邀请** - 6位邀请码快速分享
- ✅ **聚会历史** - 本地缓存最近聚会
- ✅ **自动过期** - 24小时后自动清理数据

---

## 📱 小程序页面

| 页面 | 路径 | 功能 |
|------|------|------|
| 首页 | `/pages/index/index` | 输入邀请码 / 发起聚会 |
| 创建聚会 | `/pages/create/create` | 选择类型、位置、发起聚会 |
| 加入聚会 | `/pages/join/join` | 输入昵称、位置、交通方式 |
| 推荐结果 | `/pages/result/result` | 查看推荐地点列表 |

---

## 🗂️ API 接口

### 聚会管理

```
POST   /api/gathering/create          # 创建聚会
POST   /api/gathering/join            # 加入聚会
GET    /api/gathering/{code}          # 获取聚会详情
DELETE /api/gathering/{code}          # 取消聚会
GET    /api/gathering/list/recent     # 最近聚会列表
```

### 推荐算法

```
POST   /api/recommend/calculate       # 计算推荐地点
POST   /api/recommend/refresh/{code}  # 刷新推荐
GET    /api/recommend/mock/{code}     # 获取模拟数据
```

### 位置服务

```
POST   /api/location/geocode          # 地址转坐标
POST   /api/location/reverse-geocode  # 坐标转地址
POST   /api/location/validate         # 验证位置
GET    /api/location/search           # 搜索地点
```

---

## 🔧 开发工具

### 常用命令

```bash
# Conda 环境
conda env list                        # 查看所有环境
conda activate yuebei                 # 激活环境
conda deactivate                      # 退出环境

# MongoDB (Homebrew)
brew services start mongodb-community@7.0   # 启动
brew services stop mongodb-community@7.0    # 停止

# MongoDB (Docker)
docker start yuebei-mongo             # 启动
docker stop yuebei-mongo              # 停止
docker logs yuebei-mongo              # 查看日志

# 后端服务
uvicorn main:app --reload            # 启动开发服务器
python test_db_connection.py        # 测试数据库连接
```

### 调试工具

- **API 文档**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **小程序调试**: 微信开发者工具

---

## 📚 文档

- [快速开始指南](QUICKSTART.md)
- [Conda 环境配置](SETUP_CONDA.md)
- [快速参考手册](QUICK_REFERENCE.md)
- [项目上下文](CLAUDE_CONTEXT.md)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 🔗 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [微信小程序开发文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [MongoDB 文档](https://www.mongodb.com/docs/)
- [腾讯地图 API](https://lbs.qq.com/miniProgram/jsSdk/jsSdkGuide/jsSdkOverview)
