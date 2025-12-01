#!/bin/bash

# MongoDB 安装和配置脚本 (macOS)
# ================================

echo "╔════════════════════════════════════════════════════════╗"
echo "║      约呗 (YueBei) - MongoDB 安装配置脚本              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 检测操作系统
OS="$(uname -s)"
echo "🖥️  操作系统: $OS"

if [[ "$OS" != "Darwin" ]]; then
    echo "⚠️  此脚本仅支持 macOS 系统"
    echo "   对于其他操作系统，请参考以下安装方式："
    echo ""
    echo "   Ubuntu/Debian:"
    echo "   sudo apt-get install -y mongodb-org"
    echo ""
    echo "   CentOS/RHEL:"
    echo "   sudo yum install -y mongodb-org"
    echo ""
    echo "   Docker (推荐，跨平台):"
    echo "   docker run -d --name yuebei-mongo -p 27017:27017 mongo:6.0"
    exit 1
fi

# 检查 Homebrew 是否安装
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew 未安装"
    echo ""
    echo "请先安装 Homebrew:"
    echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "✅ Homebrew 已安装"

# 询问用户选择安装方式
echo ""
echo "请选择 MongoDB 安装方式："
echo ""
echo "  [1] 通过 Homebrew 安装本地 MongoDB (推荐，永久安装)"
echo "  [2] 使用 Docker 运行 MongoDB (轻量，易管理)"
echo "  [3] 使用 MongoDB Atlas (云端免费版)"
echo "  [0] 取消安装"
echo ""
read -p "请输入选项 [1/2/3/0]: " choice

case $choice in
    1)
        echo ""
        echo "📦 正在通过 Homebrew 安装 MongoDB..."
        echo "════════════════════════════════════════"

        # 添加 MongoDB tap
        echo "1️⃣  添加 MongoDB Homebrew tap..."
        brew tap mongodb/brew

        # 安装 MongoDB
        echo "2️⃣  安装 MongoDB Community Edition..."
        brew install mongodb-community@7.0

        if [[ $? -ne 0 ]]; then
            echo "❌ MongoDB 安装失败"
            exit 1
        fi

        echo "✅ MongoDB 安装成功"

        # 启动 MongoDB
        echo ""
        echo "3️⃣  启动 MongoDB 服务..."
        brew services start mongodb-community@7.0

        # 等待服务启动
        echo "⏳ 等待 MongoDB 服务启动..."
        sleep 3

        # 检查服务状态
        if brew services list | grep mongodb-community | grep started; then
            echo "✅ MongoDB 服务已启动"

            # 显示连接信息
            echo ""
            echo "═══════════════════════════════════════════════════════"
            echo "🎉 MongoDB 安装配置完成！"
            echo "═══════════════════════════════════════════════════════"
            echo "📍 连接地址: mongodb://localhost:27017"
            echo "🗂️  数据目录: /opt/homebrew/var/mongodb"
            echo "📝 配置文件: /opt/homebrew/etc/mongod.conf"
            echo "📊 日志文件: /opt/homebrew/var/log/mongodb"
            echo ""
            echo "常用命令:"
            echo "  启动服务: brew services start mongodb-community@7.0"
            echo "  停止服务: brew services stop mongodb-community@7.0"
            echo "  重启服务: brew services restart mongodb-community@7.0"
            echo "  连接数据库: mongosh"
            echo "═══════════════════════════════════════════════════════"
        else
            echo "❌ MongoDB 服务启动失败"
            echo "   请查看日志: /opt/homebrew/var/log/mongodb/mongo.log"
            exit 1
        fi
        ;;

    2)
        echo ""
        echo "🐳 使用 Docker 运行 MongoDB..."
        echo "════════════════════════════════════════"

        # 检查 Docker 是否安装
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker 未安装"
            echo "   请先安装 Docker Desktop for Mac"
            echo "   下载地址: https://www.docker.com/products/docker-desktop"
            exit 1
        fi

        echo "✅ Docker 已安装"

        # 检查是否已有容器
        if docker ps -a | grep -q yuebei-mongo; then
            echo "⚠️  检测到已存在 yuebei-mongo 容器"
            read -p "是否删除旧容器并重新创建? [y/N]: " confirm
            if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
                docker rm -f yuebei-mongo
            else
                echo "取消操作"
                exit 0
            fi
        fi

        # 运行 MongoDB 容器
        echo "🚀 启动 MongoDB 容器..."
        docker run -d \
            --name yuebei-mongo \
            -p 27017:27017 \
            -e MONGO_INITDB_DATABASE=yuebei \
            -v yuebei-mongo-data:/data/db \
            mongo:6.0

        if [[ $? -eq 0 ]]; then
            echo ""
            echo "═══════════════════════════════════════════════════════"
            echo "🎉 MongoDB Docker 容器启动成功！"
            echo "═══════════════════════════════════════════════════════"
            echo "📍 连接地址: mongodb://localhost:27017"
            echo "🗂️  数据卷: yuebei-mongo-data"
            echo ""
            echo "常用命令:"
            echo "  查看容器: docker ps"
            echo "  停止容器: docker stop yuebei-mongo"
            echo "  启动容器: docker start yuebei-mongo"
            echo "  删除容器: docker rm -f yuebei-mongo"
            echo "  查看日志: docker logs yuebei-mongo"
            echo "  进入容器: docker exec -it yuebei-mongo mongosh"
            echo "═══════════════════════════════════════════════════════"
        else
            echo "❌ Docker 容器启动失败"
            exit 1
        fi
        ;;

    3)
        echo ""
        echo "☁️  使用 MongoDB Atlas 云端数据库"
        echo "════════════════════════════════════════"
        echo ""
        echo "1. 访问 MongoDB Atlas: https://www.mongodb.com/cloud/atlas"
        echo "2. 注册/登录账号"
        echo "3. 创建免费集群 (Free Tier)"
        echo "4. 配置网络访问 (Allow Access from Anywhere: 0.0.0.0/0)"
        echo "5. 创建数据库用户"
        echo "6. 获取连接字符串"
        echo "7. 将连接字符串配置到 server/.env 文件中的 MONGODB_URL"
        echo ""
        echo "示例连接字符串:"
        echo "MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/yuebei?retryWrites=true&w=majority"
        echo ""
        ;;

    0)
        echo "取消安装"
        exit 0
        ;;

    *)
        echo "❌ 无效的选项"
        exit 1
        ;;
esac

# 测试连接
echo ""
echo "🔍 测试 MongoDB 连接..."
sleep 2

# 简单的连接测试
if command -v mongosh &> /dev/null; then
    mongosh --eval "db.version()" --quiet 2>/dev/null
    if [[ $? -eq 0 ]]; then
        echo "✅ MongoDB 连接测试成功！"
    else
        echo "⚠️  连接测试失败，但服务可能正在启动中"
        echo "   请稍后运行: python server/test_db_connection.py"
    fi
else
    echo "💡 提示: 安装 mongosh 可以方便地管理数据库"
    echo "   brew install mongosh"
fi

echo ""
echo "下一步："
echo "  运行数据库连接测试: python server/test_db_connection.py"
echo "  或启动后端服务: ./start-conda.sh"
