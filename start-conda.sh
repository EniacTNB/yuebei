#!/bin/bash

# 约呗(YueBei) Conda 版本启动脚本
# =================================

echo "🚀 约呗(YueBei) Conda 环境快速启动脚本"
echo "=============================="

# 检查conda环境是否可用
if ! command -v conda &> /dev/null; then
    echo "❌ conda 命令未找到，请确保已安装 Anaconda 或 Miniconda"
    echo "   安装完成后请重新打开终端并运行此脚本"
    exit 1
fi

# 检查conda环境是否激活
if [[ -z "$CONDA_DEFAULT_ENV" ]]; then
    echo "🔧 检测到conda未激活，正在激活base环境..."
    source $(conda info --base)/etc/profile.d/conda.sh
fi

# 检查yuebei环境是否存在
echo "🔍 检查 yuebei conda 环境..."
if ! conda env list | grep -q "^yuebei "; then
    echo "📦 创建 yuebei conda 环境..."
    conda env create -f environment.yml
    echo "✅ yuebei 环境创建完成"
else
    echo "✅ yuebei 环境已存在"
fi

# 激活yuebei环境
echo "🎯 激活 yuebei conda 环境..."
conda activate yuebei

# 检查环境激活状态
if [[ "$CONDA_DEFAULT_ENV" != "yuebei" ]]; then
    echo "❌ 环境激活失败，请手动运行: conda activate yuebei"
    exit 1
fi

echo "✅ Conda 环境已激活: $CONDA_DEFAULT_ENV"

# 检查Python版本
python_version=$(python --version 2>&1)
echo "✅ Python版本: $python_version"

# 检查依赖是否完整
echo "🔍 检查后端依赖..."
cd server

# 检查关键包是否存在
packages=("fastapi" "motor" "redis" "pymongo" "pydantic" "uvicorn")
missing_packages=()

for pkg in "${packages[@]}"; do
    if ! python -c "import $pkg" 2>/dev/null; then
        missing_packages+=("$pkg")
    fi
done

if [ ${#missing_packages[@]} -eq 0 ]; then
    echo "✅ 所有依赖均已安装"
else
    echo "📦 正在安装缺失的依赖包: ${missing_packages[*]}"
    pip install -r requirements.txt
fi

# 复制环境变量文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
    echo "⚠️  请编辑 server/.env 文件，添加您的地图API密钥"
fi

# 返回项目根目录
cd ..

# 检查MongoDB连接
echo "🗄️  正在检查MongoDB连接..."
mongo_status=$(python3 -c "
import sys
import pymongo
from server.app.config import settings
try:
    client = pymongo.MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
    client.server_info()
    print('✅ MongoDB连接成功')
    sys.exit(0)
except Exception as e:
    print(f'❌ MongoDB连接失败: {e}')
    sys.exit(1)
" 2>&1)

if [[ $? -eq 0 ]]; then
    echo "$mongo_status"
else
    echo "$mongo_status"
    echo ""
    echo "💡 MongoDB 连接失败，处理方案："
    echo "   方案1: 使用Docker启动（推荐）"
    echo "   - 运行: docker run -d --name yuebei-mongo -p 27017:27017 mongo:6.0"
    echo ""
    echo "   方案2: 使用本地安装"
    echo "   - macOS: brew install mongodb-community"
    echo "   - Ubuntu: sudo apt install mongodb"
    echo "   - CentOS: sudo yum install mongodb"
    echo ""
    echo "   方案3: 使用MongoDB Atlas（云端）"
    echo "   - 官网: https://www.mongodb.com/cloud/atlas"
    echo ""
fi

# 启动后端服务
echo "🎯 启动后端服务..."
cd server

# 检查端口是否被占用
if lsof -i :8000 >/dev/null 2>&1; then
    echo "⚠️  端口8000已被占用，正在结束占用进程..."
    pkill -f uvicorn
fi

echo "🚀 正在启动 FastAPI 服务..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
backend_pid=$!

# 等待服务启动
sleep 2

# 检查服务是否启动成功
if curl -s http://localhost:8000/api/health >/dev/null; then
    echo ""
    echo "✨ 约呗后端服务已成功启动!"
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
    echo "提示：使用 conda deactivate 可退出 conda 环境"
    echo "═══════ 服务运行中 ═══════"
    echo "按 Ctrl+C 停止服务"

    # 等待进程
    wait $backend_pid
else
    echo "❌ 后端服务启动失败，请检查配置和日志"
    pkill -f uvicorn  # 清理进程
    exit 1
fi