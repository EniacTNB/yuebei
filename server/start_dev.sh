#!/bin/bash

echo "🚀 启动约呗后端开发服务器"
echo "========================="

# 检查MongoDB是否运行
if ! pgrep -x "mongod" > /dev/null
then
    echo "⚠️  MongoDB未运行，尝试启动..."
    # macOS使用brew启动
    if command -v brew &> /dev/null; then
        brew services start mongodb-community
    else
        # 尝试直接启动mongod
        mongod --dbpath /usr/local/var/mongodb --fork --logpath /usr/local/var/log/mongodb/mongo.log 2>/dev/null || true
    fi
    sleep 2
fi

# 检查Redis是否运行（可选）
if ! pgrep -x "redis-server" > /dev/null
then
    echo "ℹ️  Redis未运行（可选服务）"
fi

# 创建.env文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "📝 创建.env文件..."
    cat > .env << 'EOF'
# 服务配置
DEBUG=True
PORT=8000
SECRET_KEY=development-secret-key

# MongoDB配置（本地开发无需认证）
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=yuebei

# Redis配置（可选）
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# 地图服务（可选）
TENCENT_MAP_KEY=
AMAP_KEY=

# 业务配置
GATHERING_EXPIRE_HOURS=24
MAX_PARTICIPANTS=20
SEARCH_RADIUS=5000
MAX_RECOMMENDATIONS=10
EOF
    echo "✅ .env文件已创建"
fi

# 安装依赖（如果需要）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查是否需要安装依赖
if ! pip show fastapi &> /dev/null; then
    echo "📦 安装依赖..."
    pip install -r requirements.txt
fi

# 启动服务
echo ""
echo "🎯 启动FastAPI服务..."
echo "========================="
echo "📍 API地址: http://localhost:8000"
echo "📚 文档地址: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000