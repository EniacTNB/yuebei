# 约呗 - 快速开始指南

## 🚀 5分钟快速启动

### 方式一：使用启动脚本（推荐）

```bash
# 1. 进入项目目录
cd yuebei

# 2. 运行启动脚本
./start.sh

# 3. 访问 http://localhost:8000/docs 查看API文档
```

### 方式二：手动启动

#### 1. 启动后端服务

```bash
# 安装依赖
cd server
pip install -r requirements.txt

# 复制环境配置
cp .env.example .env

# 启动服务（开发模式）
uvicorn main:app --reload --port 8000
```

#### 2. 启动数据库（可选）

```bash
# 使用Docker Compose
docker-compose up -d mongodb redis

# 或手动启动
mongod --dbpath ./data/db
redis-server
```

#### 3. 配置小程序

1. 打开微信开发者工具
2. 导入项目，选择 `miniprogram` 目录
3. 修改 `miniprogram/app.js` 中的 `baseUrl` 为您的后端地址
4. 点击编译预览

## 📝 环境变量配置

编辑 `server/.env` 文件：

```env
# 必须配置
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379

# 可选配置（地图服务）
TENCENT_MAP_KEY=您的腾讯地图密钥
# 或
AMAP_KEY=您的高德地图密钥
```

## 🧪 测试API

### 1. 创建聚会

```bash
curl -X POST http://localhost:8000/api/gathering/create \
  -H "Content-Type: application/json" \
  -d '{
    "type": "meal",
    "preferences": {}
  }'
```

返回示例：
```json
{
  "success": true,
  "data": {
    "code": "ABC123",
    "type": "meal",
    ...
  }
}
```

### 2. 加入聚会

```bash
curl -X POST http://localhost:8000/api/gathering/join \
  -H "Content-Type: application/json" \
  -d '{
    "code": "ABC123",
    "participant": {
      "temp_id": "user_001",
      "nickname": "小王",
      "location": {
        "address": "北京市朝阳区",
        "lat": 39.908,
        "lng": 116.397
      }
    }
  }'
```

### 3. 获取推荐

```bash
curl http://localhost:8000/api/recommend/calculate?gathering_code=ABC123
```

## 🛠 开发工具

### API文档

访问 http://localhost:8000/docs 查看交互式API文档（Swagger UI）

### 健康检查

```bash
curl http://localhost:8000/api/health
```

## 📱 小程序调试

1. **真机调试**：
   - 确保手机和电脑在同一网络
   - 将 `baseUrl` 改为电脑的局域网IP
   - 例如：`http://192.168.1.100:8000/api`

2. **位置权限**：
   - 在微信开发者工具中勾选"不校验合法域名"
   - 真机调试时需要用户授权位置信息

## 🐛 常见问题

### Q: MongoDB连接失败
A: 确保MongoDB服务已启动，默认端口27017未被占用

### Q: 地图服务不工作
A: 检查是否配置了地图API密钥，未配置时将使用模拟数据

### Q: 小程序无法连接后端
A: 检查：
1. 后端服务是否正常运行
2. `baseUrl` 配置是否正确
3. 防火墙是否允许8000端口

## 📞 需要帮助？

- 查看完整文档：[README.md](README.md)
- API文档：http://localhost:8000/docs
- 提交Issue：[GitHub Issues](https://github.com/your-repo/issues)

---

🎉 恭喜！您已成功启动约呗服务，开始享受智能聚会推荐吧！