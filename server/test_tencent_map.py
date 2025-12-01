"""
测试腾讯地图API SK签名
"""
import asyncio
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from services.map_service import TencentMapService
from app.config import settings

async def test_search_nearby():
    """测试地点搜索"""
    print("=" * 60)
    print("测试腾讯地图API - 地点搜索")
    print("=" * 60)

    # 检查配置
    print(f"\n配置信息:")
    print(f"  Key: {settings.TENCENT_MAP_KEY}")
    print(f"  SK:  {settings.TENCENT_MAP_SK if settings.TENCENT_MAP_SK else '未配置'}")

    # 创建服务实例
    service = TencentMapService()

    # 测试北京国贸附近的餐厅
    center = (39.908, 116.397)  # 北京国贸
    print(f"\n搜索位置: 纬度={center[0]}, 经度={center[1]}")
    print(f"搜索关键词: 餐厅")
    print(f"搜索半径: 3000米")

    print("\n正在调用API...")
    places = await service.search_nearby(
        center=center,
        keyword="餐厅",
        radius=3000
    )

    print(f"\n找到 {len(places)} 个地点:\n")
    for i, place in enumerate(places[:5], 1):
        print(f"{i}. {place['name']}")
        print(f"   地址: {place['address']}")
        print(f"   类型: {place['type']}")
        print(f"   坐标: ({place['lat']}, {place['lng']})")
        if place.get('rating'):
            print(f"   评分: {place['rating']}")
        if place.get('tel'):
            print(f"   电话: {place['tel']}")
        print()

    return len(places) > 0

async def test_calculate_route():
    """测试路线规划"""
    print("=" * 60)
    print("测试腾讯地图API - 路线规划")
    print("=" * 60)

    service = TencentMapService()

    # 从国贸到三里屯
    from_point = (39.908, 116.397)  # 国贸
    to_point = (39.934, 116.454)     # 三里屯

    print(f"\n起点: 纬度={from_point[0]}, 经度={from_point[1]} (国贸)")
    print(f"终点: 纬度={to_point[0]}, 经度={to_point[1]} (三里屯)")

    for mode in ["driving", "transit", "walking"]:
        print(f"\n正在计算 {mode} 路线...")
        result = await service.calculate_route(
            from_point=from_point,
            to_point=to_point,
            mode=mode
        )

        print(f"  距离: {result['distance']} 米")
        print(f"  时间: {result['duration']:.1f} 分钟")

    return True

async def main():
    """主测试函数"""
    print("\n🚀 开始测试腾讯地图API SK签名集成\n")

    try:
        # 测试1: 地点搜索
        search_ok = await test_search_nearby()

        print("\n" + "=" * 60)

        # 测试2: 路线规划
        route_ok = await test_calculate_route()

        print("\n" + "=" * 60)
        print("测试结果:")
        print("=" * 60)
        print(f"✅ 地点搜索: {'通过' if search_ok else '失败'}")
        print(f"✅ 路线规划: {'通过' if route_ok else '失败'}")
        print()

        if search_ok and route_ok:
            print("🎉 所有测试通过!")
        else:
            print("⚠️  部分测试失败,请检查配置")

    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
