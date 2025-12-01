#!/usr/bin/env python3
"""
MongoDB 和 Redis 连接测试脚本
用于验证数据库配置是否正确
"""
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_mongodb():
    """测试MongoDB连接"""
    print("=" * 60)
    print("🗄️  测试 MongoDB 连接")
    print("=" * 60)

    try:
        from app.config import settings
        import pymongo

        print(f"📍 MongoDB URL: {settings.MONGODB_URL}")
        print(f"📦 数据库名称: {settings.MONGODB_DB}")

        # 创建客户端，设置2秒超时
        client = pymongo.MongoClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=2000
        )

        # 测试连接
        print("🔍 正在连接到 MongoDB...")
        server_info = client.server_info()

        print("✅ MongoDB 连接成功!")
        print(f"   - 版本: {server_info.get('version', 'unknown')}")

        # 测试数据库访问
        db = client[settings.MONGODB_DB]
        collections = db.list_collection_names()
        print(f"   - 当前数据库集合: {collections if collections else '[]'}")

        # 测试写入权限
        test_collection = db.test_collection
        test_doc = {"test": "connection", "timestamp": "now"}
        result = test_collection.insert_one(test_doc)
        print(f"   - 写入权限: ✅ (测试文档ID: {result.inserted_id})")

        # 删除测试文档
        test_collection.delete_one({"_id": result.inserted_id})

        # 关闭连接
        client.close()
        return True

    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("❌ MongoDB 连接超时")
        print(f"   错误: {e}")
        print("\n💡 解决方案:")
        print("   1. 检查 MongoDB 是否已启动")
        print("      - macOS/Linux: sudo systemctl status mongod")
        print("      - 或者查找进程: ps aux | grep mongod")
        print("   2. 检查连接地址是否正确 (当前: {})".format(settings.MONGODB_URL))
        print("   3. 如果使用 Docker:")
        print("      docker run -d --name yuebei-mongo -p 27017:27017 mongo:6.0")
        return False

    except pymongo.errors.ConfigurationError as e:
        print("❌ MongoDB 配置错误")
        print(f"   错误: {e}")
        print("\n💡 请检查 server/.env 文件中的 MONGODB_URL 配置")
        return False

    except Exception as e:
        print(f"❌ MongoDB 连接失败: {type(e).__name__}")
        print(f"   详细错误: {e}")
        return False


def test_redis():
    """测试Redis连接"""
    print("\n" + "=" * 60)
    print("💾 测试 Redis 连接")
    print("=" * 60)

    try:
        from app.config import settings
        import redis

        print(f"📍 Redis URL: {settings.REDIS_URL}")

        # 创建客户端，设置2秒超时
        client = redis.from_url(
            settings.REDIS_URL,
            socket_timeout=2,
            socket_connect_timeout=2,
            decode_responses=True
        )

        print("🔍 正在连接到 Redis...")

        # 测试连接
        pong = client.ping()
        if pong:
            print("✅ Redis 连接成功!")

            # 获取Redis信息
            info = client.info()
            print(f"   - 版本: {info.get('redis_version', 'unknown')}")
            print(f"   - 内存使用: {info.get('used_memory_human', 'unknown')}")

            # 测试读写
            client.set("test_key", "test_value")
            value = client.get("test_key")
            print(f"   - 读写权限: ✅ (测试值: {value})")
            client.delete("test_key")

            client.close()
            return True

    except redis.exceptions.ConnectionError as e:
        print("❌ Redis 连接失败")
        print(f"   错误: {e}")
        print("\n💡 解决方案 (Redis为可选服务):")
        print("   1. 启动 Redis 服务:")
        print("      - macOS: brew services start redis")
        print("      - Ubuntu: sudo systemctl start redis")
        print("      - Docker: docker run -d --name yuebei-redis -p 6379:6379 redis:7-alpine")
        print("   2. 或者不使用 Redis，系统会自动降级到仅使用 MongoDB")
        return False

    except Exception as e:
        print(f"❌ Redis 连接失败: {type(e).__name__}")
        print(f"   详细错误: {e}")
        print("   (Redis 为可选服务，不影响核心功能)")
        return False


def test_motor_async():
    """测试 Motor 异步 MongoDB 驱动"""
    print("\n" + "=" * 60)
    print("⚡ 测试 Motor 异步驱动")
    print("=" * 60)

    try:
        import asyncio
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.config import settings

        async def test():
            print("🔍 正在使用 Motor 连接 MongoDB...")
            client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=2000
            )

            # 测试连接
            await client.server_info()
            print("✅ Motor 异步驱动连接成功!")

            # 测试异步操作
            db = client[settings.MONGODB_DB]
            test_collection = db.test_async

            # 插入
            result = await test_collection.insert_one({"test": "async"})
            print(f"   - 异步写入: ✅ (ID: {result.inserted_id})")

            # 查询
            doc = await test_collection.find_one({"_id": result.inserted_id})
            print(f"   - 异步读取: ✅ (数据: {doc})")

            # 删除
            await test_collection.delete_one({"_id": result.inserted_id})

            client.close()
            return True

        result = asyncio.run(test())
        return result

    except Exception as e:
        print(f"❌ Motor 异步驱动测试失败: {type(e).__name__}")
        print(f"   详细错误: {e}")
        return False


def check_env_file():
    """检查环境变量文件"""
    print("\n" + "=" * 60)
    print("📝 检查环境变量配置")
    print("=" * 60)

    env_file = Path(__file__).parent / ".env"

    if not env_file.exists():
        print("⚠️  .env 文件不存在")
        print("   正在从 .env.example 创建...")

        example_file = Path(__file__).parent / ".env.example"
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ .env 文件已创建")
            print("   请编辑 server/.env 文件配置必要参数")
        else:
            print("❌ .env.example 文件也不存在，无法创建配置文件")
            return False
    else:
        print("✅ .env 文件存在")

    # 读取并显示关键配置
    try:
        from app.config import settings
        print("\n当前配置:")
        print(f"   - DEBUG: {settings.DEBUG}")
        print(f"   - PORT: {settings.PORT}")
        print(f"   - MONGODB_URL: {settings.MONGODB_URL}")
        print(f"   - MONGODB_DB: {settings.MONGODB_DB}")
        print(f"   - REDIS_URL: {settings.REDIS_URL}")
        print(f"   - TENCENT_MAP_KEY: {'已配置' if settings.TENCENT_MAP_KEY else '未配置 (将使用模拟数据)'}")
        print(f"   - AMAP_KEY: {'已配置' if settings.AMAP_KEY else '未配置'}")
        return True
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "约呗 (YueBei) 数据库连接测试" + " " * 17 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # 检查环境变量
    env_ok = check_env_file()
    if not env_ok:
        print("\n❌ 环境配置检查失败，请先配置 .env 文件")
        sys.exit(1)

    # 测试MongoDB
    mongo_ok = test_mongodb()

    # 测试Redis
    redis_ok = test_redis()

    # 测试Motor异步驱动
    motor_ok = test_motor_async() if mongo_ok else False

    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    print(f"MongoDB (pymongo):  {'✅ 通过' if mongo_ok else '❌ 失败'}")
    print(f"Motor (异步驱动):   {'✅ 通过' if motor_ok else '❌ 失败'}")
    print(f"Redis (可选):       {'✅ 通过' if redis_ok else '⚠️  未连接 (不影响核心功能)'}")
    print("=" * 60)

    if mongo_ok and motor_ok:
        print("\n🎉 所有必需的数据库连接测试通过！")
        print("   后端服务可以正常启动")
        sys.exit(0)
    else:
        print("\n❌ 数据库连接测试失败")
        print("   请根据上述提示修复问题后重试")
        sys.exit(1)


if __name__ == "__main__":
    main()
