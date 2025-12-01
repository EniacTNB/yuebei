# 约呗 - 快速开始指南

## 🚀 5分钟快速启动

### 方式一：一键启动（最简单）

```bash
# 1. 进入项目目录
cd yuebei

# 2. 安装 MongoDB（首次运行）
./setup-mongodb.sh
# 选择安装方式：[1] Homebrew / [2] Docker / [3] MongoDB Atlas

# 3. 启动服务（自动检测 Conda 或 venv）
./start.sh

# 4. 访问 API 文档
# http://localhost:8000/docs
```

### 方式二：使用 Conda（推荐开发环境）

```bash
# 1. 创建并激活 Conda 环境
conda env create -f environment.yml
conda activate yuebei

# 2. 安装 MongoDB
./setup-mongodb.sh

# 3. 测试数据库连接
python server/test_db_connection.py

# 4. 启动后端服务
./start-conda.sh
```

### 方式三：手动启动（完全控制）

#### 步骤 1: 准备虚拟环境

**选择 Conda:**
```bash
conda create -n yuebei python=3.11 pip -y
conda activate yuebei
cd server
pip install -r requirements.txt
```

**或选择 venv:**
```bash
python3 -m venv venv
source venv/bin/activate
cd server
pip install -r requirements.txt
```

#### 步骤 2: 启动数据库

**方式 A - 使用 Docker（推荐）:**
```bash
docker run -d \
  --name yuebei-mongo \
  -p 27017:27017 \
  -e MONGO_INITDB_DATABASE=yuebei \
  mongo:6.0
```

**方式 B - 使用 Homebrew:**
```bash
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
```

**方式 C - 使用 MongoDB Atlas:**
1. 访问 https://www.mongodb.com/cloud/atlas
2. 创建免费集群
3. 获取连接字符串
4. 配置到 `server/.env` 的 `MONGODB_URL`

#### 步骤 3: 配置环境变量

```bash
cd server
cp .env.example .env
# 编辑 .env 文件，至少配置 MONGODB_URL
```

#### 步骤 4: 测试连接

```bash
python test_db_connection.py
```

#### 步骤 5: 启动后端服务

```bash
# 确保在 server 目录
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📝 环境变量配置

编辑 `server/.env` 文件：

```env
# =================================
# 服务配置
# =================================
DEBUG=True
PORT=8000
SECRET_KEY=development-secret-key-yuebei

# =================================
# MongoDB 配置（必须）
# =================================
# 本地安装
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=yuebei

# 或使用 MongoDB Atlas（云端）
# MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/yuebei?retryWrites=true&w=majority

# =================================
# Redis 配置（可选）
# =================================
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# =================================
# 地图 API 配置（可选，不填使用模拟数据）
# =================================
# 腾讯地图
TENCENT_MAP_KEY=

# 高德地图
AMAP_KEY=

# =================================
# 业务配置
# =================================
GATHERING_EXPIRE_HOURS=24    # 聚会信息过期时间
MAX_PARTICIPANTS=20          # 最大参与人数
SEARCH_RADIUS=5000          # 搜索半径（米）
MAX_RECOMMENDATIONS=10       # 最多推荐数量
```

---

## 📱 配置小程序

### 步骤 1: 打开微信开发者工具

1. 启动微信开发者工具
2. 选择"导入项目"
3. 项目目录选择：`miniprogram`
4. AppID: 使用测试号或留空

### 步骤 2: 配置后端地址

编辑 `miniprogram/app.js`：

```javascript
App({
  globalData: {
    // 开发环境：本地后端
    baseUrl: 'http://localhost:8000/api'

    // 真机调试：使用电脑局域网IP
    // baseUrl: 'http://192.168.1.100:8000/api'

    // 生产环境：部署后的后端地址
    // baseUrl: 'https://api.yourdomain.com/api'
  }
})
```

### 步骤 3: 设置开发选项

在微信开发者工具中：
1. 详情 → 本地设置
2. 勾选"不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"

### 步骤 4: 编译运行

点击工具栏的"编译"按钮，小程序即可运行。

---

## 🧪 测试 API

### 方式 1: 使用 Swagger UI（推荐）

访问 http://localhost:8000/docs

在交互式文档中测试所有 API 接口。

### 方式 2: 使用 curl

#### 1. 健康检查

```bash
curl http://localhost:8000/api/health
```

预期返回:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### 2. 创建聚会

```bash
curl -X POST http://localhost:8000/api/gathering/create \
  -H "Content-Type: application/json" \
  -d '{
    "type": "meal",
    "creator": {
      "temp_id": "user_creator",
      "nickname": "发起人",
      "location": {
        "address": "北京市朝阳区",
        "lat": 39.908,
        "lng": 116.397
      },
      "transport_mode": "driving"
    }
  }'
```

返回示例：
```json
{
  "success": true,
  "data": {
    "code": "ABC123",
    "type": "meal",
    "status": "active",
    "participants": [...],
    "created_at": "2024-01-01T00:00:00",
    "expires_at": "2024-01-02T00:00:00"
  }
}
```

#### 3. 加入聚会

```bash
curl -X POST http://localhost:8000/api/gathering/join \
  -H "Content-Type: application/json" \
  -d '{
    "code": "ABC123",
    "participant": {
      "temp_id": "user_001",
      "nickname": "小王",
      "location": {
        "address": "北京市海淀区",
        "lat": 39.983,
        "lng": 116.309
      },
      "transport_mode": "transit"
    }
  }'
```

#### 4. 获取聚会详情

```bash
curl http://localhost:8000/api/gathering/ABC123
```

#### 5. 计算推荐地点

```bash
curl -X POST http://localhost:8000/api/recommend/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "gathering_code": "ABC123"
  }'
```

返回推荐地点列表，按综合评分排序。

---

## 🔧 开发工具与调试

### API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/api/health

### 数据库管理

**MongoDB:**
```bash
# 连接数据库
mongosh

# 查看所有数据库
show dbs

# 使用 yuebei 数据库
use yuebei

# 查看集合
show collections

# 查询聚会数据
db.gatherings.find().pretty()
```

**Redis (可选):**
```bash
# 连接 Redis
redis-cli

# 查看所有键
KEYS *

# 获取值
GET gathering:ABC123
```

### 查看日志

后端服务会在控制台输出日志，包括：
- HTTP 请求
- 数据库操作
- 错误信息

---

## 📱 小程序真机调试

### 步骤 1: 获取电脑局域网 IP

**macOS:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Windows:**
```bash
ipconfig
```

假设 IP 为 `192.168.1.100`

### 步骤 2: 修改小程序配置

编辑 `miniprogram/app.js`:
```javascript
baseUrl: 'http://192.168.1.100:8000/api'
```

### 步骤 3: 启动后端服务

确保后端监听所有网络接口：
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤 4: 真机预览

1. 在微信开发者工具中点击"预览"
2. 扫描二维码
3. 在手机微信中打开小程序

---

## 🐛 常见问题排查

### Q1: MongoDB 连接失败

**症状:**
```
pymongo.errors.ServerSelectionTimeoutError: localhost:27017
```

**解决方案:**
```bash
# 1. 检查 MongoDB 是否运行
lsof -i :27017
ps aux | grep mongod

# 2. 启动 MongoDB
# Docker:
docker start yuebei-mongo

# Homebrew:
brew services start mongodb-community@7.0

# 3. 测试连接
python server/test_db_connection.py
```

### Q2: Conda 环境激活失败

**症状:**
```
conda activate yuebei
# 无响应或找不到环境
```

**解决方案:**
```bash
# 1. 初始化 conda
conda init zsh  # 或 bash

# 2. 重新打开终端

# 3. 检查环境
conda env list

# 4. 如果环境不存在，重新创建
conda env create -f environment.yml
```

### Q3: 端口 8000 被占用

**症状:**
```
Error: Address already in use
```

**解决方案:**
```bash
# 查找占用进程
lsof -i :8000

# 结束进程
kill -9 <PID>

# 或使用其他端口
uvicorn main:app --port 8001
```

### Q4: 小程序无法连接后端

**检查清单:**
- [ ] 后端服务是否运行（访问 http://localhost:8000/docs）
- [ ] `baseUrl` 配置是否正确
- [ ] 是否勾选"不校验合法域名"
- [ ] 防火墙是否允许 8000 端口
- [ ] 真机调试时，手机和电脑是否在同一网络

### Q5: 地图服务不工作

**解决方案:**
- 未配置 API Key 时，系统会自动使用模拟数据
- 模拟数据足够进行开发和测试
- 如需真实数据，申请腾讯地图或高德地图 API Key

### Q6: pip 安装依赖失败

**解决方案:**
```bash
# 1. 升级 pip
pip install --upgrade pip

# 2. 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 单独安装失败的包
pip install <package-name> --no-cache-dir
```

---

## 📊 验证安装

运行以下命令验证环境是否正确配置：

```bash
# 1. 检查 Python 版本
python --version
# 预期: Python 3.11.x

# 2. 检查关键包
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import motor; print('Motor:', motor.version)"
python -c "import pymongo; print('PyMongo:', pymongo.__version__)"

# 3. 测试数据库连接
python server/test_db_connection.py

# 4. 测试后端服务
curl http://localhost:8000/api/health

# 5. 检查 MongoDB
mongosh --eval "db.version()"

# 6. 检查 Conda 环境（如果使用）
conda env list | grep yuebei
```

全部通过后，环境配置完成！

---

## 🎯 下一步

环境配置完成后，你可以：

1. ✅ **阅读代码**: 从 `server/main.py` 开始了解后端架构
2. ✅ **查看算法**: `server/core/algorithm.py` 包含推荐算法核心逻辑
3. ✅ **测试 API**: 使用 http://localhost:8000/docs 测试所有接口
4. ✅ **开发小程序**: 在 `miniprogram/pages` 下修改页面
5. ✅ **阅读文档**:
   - [README.md](README.md) - 项目总览
   - [SETUP_CONDA.md](SETUP_CONDA.md) - Conda 详细配置
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考

---

## 📞 需要帮助？

- 📖 **完整文档**: [README.md](README.md)
- 🔧 **Conda 配置**: [SETUP_CONDA.md](SETUP_CONDA.md)
- 📝 **快速参考**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- 🌐 **API 文档**: http://localhost:8000/docs
- 💬 **提交 Issue**: [GitHub Issues](https://github.com/your-repo/issues)

---

🎉 **恭喜！您已成功启动约呗服务，开始享受智能聚会推荐吧！**
