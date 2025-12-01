#!/bin/bash

# 约呗(YueBei) 快速启动脚本
# 支持 Conda 和 venv 两种虚拟环境
# =================================

echo "🚀 约呗(YueBei) 快速启动脚本"
echo "=============================="

# 检测虚拟环境类型
USE_CONDA=false

if command -v conda &> /dev/null; then
    echo "✅ 检测到 Conda 环境"
    USE_CONDA=true
else
    echo "📦 使用 Python venv 环境"
fi

# =================================
# 环境设置
# =================================

if [ "$USE_CONDA" = true ]; then
    # Conda 环境设置
    echo "🔧 设置 Conda 环境..."

    # 初始化 conda（如果需要）
    if [[ -z "$CONDA_DEFAULT_ENV" ]]; then
        echo "   初始化 Conda..."
        if [ -f "$(conda info --base)/etc/profile.d/conda.sh" ]; then
            source "$(conda info --base)/etc/profile.d/conda.sh"
        fi
    fi

    # 检查 yuebei 环境是否存在
    if ! conda env list | grep -q "^yuebei "; then
        echo "📦 创建 yuebei conda 环境..."

        if [ -f "environment.yml" ]; then
            conda create -n yuebei python=3.11 pip --override-channels -c conda-forge -y
        else
            conda create -n yuebei python=3.11 pip --override-channels -c conda-forge -y
        fi

        if [ $? -ne 0 ]; then
            echo "❌ Conda 环境创建失败"
            exit 1
        fi
    fi

    # 激活 yuebei 环境
    echo "   激活 yuebei 环境..."
    conda activate yuebei

    if [[ "$CONDA_DEFAULT_ENV" != "yuebei" ]]; then
        echo "❌ 环境激活失败"
        echo "   请手动运行: conda activate yuebei"
        exit 1
    fi

    echo "✅ Conda 环境已激活: $CONDA_DEFAULT_ENV"

else
    # venv 环境设置
    if [ ! -d "venv" ]; then
        echo "📦 创建 Python 虚拟环境..."
        python3 -m venv venv
    fi

    echo "🔧 激活虚拟环境..."
    source venv/bin/activate
fi

# 检查Python版本
python_version=$(python --version 2>&1)
echo "✅ Python 版本: $python_version"

# =================================
# 安装后端依赖
# =================================

echo "📦 检查后端依赖..."
cd server

# 检查关键包是否已安装
if ! python -c "import fastapi" 2>/dev/null; then
    echo "   安装后端依赖..."
    pip install -r requirements.txt
else
    echo "✅ 后端依赖已安装"
fi

# =================================
# 环境变量配置
# =================================

if [ ! -f ".env" ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
    echo "⚠️  请编辑 server/.env 文件，添加您的地图API密钥"
fi

cd ..

# =================================
# 启动数据库服务
# =================================

echo "🗄️  检查数据库服务..."

# 检查 MongoDB 是否运行
if lsof -i :27017 >/dev/null 2>&1; then
    echo "✅ MongoDB 已运行 (端口 27017)"
else
    echo "⚠️  MongoDB 未运行"

    # 尝试使用 Docker 启动
    if command -v docker &> /dev/null; then
        echo "   尝试使用 Docker 启动 MongoDB..."

        # 检查容器是否存在
        if docker ps -a | grep -q yuebei-mongo; then
            docker start yuebei-mongo
        else
            docker run -d \
                --name yuebei-mongo \
                -p 27017:27017 \
                -e MONGO_INITDB_DATABASE=yuebei \
                mongo:6.0
        fi

        if [ $? -eq 0 ]; then
            echo "✅ MongoDB 容器已启动"
            sleep 2
        else
            echo "❌ Docker 启动失败"
        fi
    else
        echo ""
        echo "💡 请手动启动 MongoDB，或运行: ./setup-mongodb.sh"
        echo "   方式1: brew services start mongodb-community@7.0"
        echo "   方式2: docker run -d --name yuebei-mongo -p 27017:27017 mongo:6.0"
        echo ""
    fi
fi

# 检查 Redis（可选）
if lsof -i :6379 >/dev/null 2>&1; then
    echo "✅ Redis 已运行 (端口 6379)"
else
    echo "💡 Redis 未运行 (可选服务，不影响核心功能)"
fi

# =================================
# 启动后端服务
# =================================

echo ""
echo "🎯 启动后端服务..."
cd server

# 检查端口是否被占用
if lsof -i :8000 >/dev/null 2>&1; then
    echo "⚠️  端口 8000 已被占用，正在清理..."
    pkill -f "uvicorn main:app"
    sleep 1
fi

# 启动服务
echo "🚀 正在启动 FastAPI 服务..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
backend_pid=$!

# 等待服务启动
sleep 2

# 检查服务是否成功启动
if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo "✨ 约呗后端服务已成功启动!"
    echo "═══════════════════════════════════════════════════════"
    echo "📍 API 地址: http://localhost:8000"
    echo "📚 API 文档: http://localhost:8000/docs"
    echo "🔑 健康检查: http://localhost:8000/api/health"
    echo ""
    echo "📱 小程序开发:"
    echo "1. 使用微信开发者工具打开 miniprogram 目录"
    echo "2. 配置 AppID (如有)"
    echo "3. 点击编译预览"
    echo ""
    if [ "$USE_CONDA" = true ]; then
        echo "💡 当前使用 Conda 环境: $CONDA_DEFAULT_ENV"
        echo "   退出环境: conda deactivate"
    else
        echo "💡 当前使用 venv 环境"
        echo "   退出环境: deactivate"
    fi
    echo "═══════════════════════════════════════════════════════"
    echo "按 Ctrl+C 停止服务"
    echo ""

    # 等待进程
    wait $backend_pid
else
    echo ""
    echo "❌ 后端服务启动失败"
    echo "   请检查："
    echo "   1. MongoDB 是否运行: lsof -i :27017"
    echo "   2. 依赖是否安装: pip list | grep fastapi"
    echo "   3. 运行测试: python test_db_connection.py"
    echo ""
    pkill -f "uvicorn main:app"  # 清理进程
    exit 1
fi