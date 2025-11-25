#!/bin/bash

echo "🚀 约呗(YueBei)快速启动脚本"
echo "=============================="

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "✅ Python版本: $python_version"

# 创建Python虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装后端依赖
echo "📦 安装后端依赖..."
cd server
pip install -r requirements.txt

# 复制环境变量文件
if [ ! -f ".env" ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
    echo "⚠️  请编辑 server/.env 文件，添加您的地图API密钥"
fi

# 启动MongoDB和Redis（使用Docker）
echo "🗄️  启动数据库服务..."
cd ..
if command -v docker-compose &> /dev/null; then
    docker-compose up -d mongodb redis
    echo "✅ MongoDB和Redis已启动"
else
    echo "⚠️  请先安装Docker和Docker Compose，或手动启动MongoDB和Redis"
fi

# 启动后端服务
echo "🎯 启动后端服务..."
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
backend_pid=$!

echo ""
echo "✨ 约呗后端服务已启动!"
echo "=============================="
echo "📍 API地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo "🔑 健康检查: http://localhost:8000/api/health"
echo ""
echo "📱 小程序开发:"
echo "1. 使用微信开发者工具打开 miniprogram 目录"
echo "2. 配置AppID (如有)"
echo "3. 点击编译预览"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待进程
wait $backend_pid