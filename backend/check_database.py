"""
数据库连接测试脚本
检查 MySQL、Redis、Milvus 是否能正常连接
"""
import sys
import asyncio
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings


async def test_mysql():
    """测试 MySQL 连接"""
    print("\n[*] 测试 MySQL 数据库连接...")
    try:
        from sqlalchemy import text
        from app.database import engine
        
        start = time.time()
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
            elapsed = time.time() - start
        
        print(f"[OK] MySQL 连接成功")
        print(f"   地址: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}")
        print(f"   数据库: {settings.MYSQL_DATABASE}")
        print(f"   响应时间: {elapsed:.2f}s")
        
        # 检查表是否存在
        async with engine.connect() as conn:
            result = await conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = %s"
            ), (settings.MYSQL_DATABASE,))
            table_count = result.scalar()
            print(f"   表数量: {table_count}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] MySQL 连接失败")
        print(f"   错误: {e}")
        return False


async def test_redis():
    """测试 Redis 连接"""
    print("\n[*] 测试 Redis 缓存连接...")
    try:
        import redis.asyncio as aioredis
        
        start = time.time()
        redis_url = (
            f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            if settings.REDIS_PASSWORD
            else f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        )
        client = aioredis.from_url(redis_url)
        
        # 测试连接和基本操作
        await client.ping()
        test_key = "__health_check__"
        await client.set(test_key, "ok", ex=10)
        value = await client.get(test_key)
        await client.delete(test_key)
        
        elapsed = time.time() - start
        await client.close()
        
        if value and value.decode() == "ok":
            print(f"[OK] Redis 连接成功")
            print(f"   地址: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            print(f"   数据库: {settings.REDIS_DB}")
            print(f"   响应时间: {elapsed:.2f}s")
            
            # 获取 Redis 信息
            client2 = aioredis.from_url(redis_url)
            info = await client2.info()
            await client2.close()
            version = info.get("redis_version", "unknown")
            used_memory = info.get("used_memory_human", "unknown")
            print(f"   版本: {version}")
            print(f"   内存使用: {used_memory}")
            
            return True
        else:
            print("[FAIL] Redis 读写测试失败")
            return False
            
    except Exception as e:
        print(f"[FAIL] Redis 连接失败")
        print(f"   错误: {e}")
        return False


async def test_milvus():
    """测试 Milvus 连接"""
    print("\n[*] 测试 Milvus 向量库连接...")
    try:
        from pymilvus import connections, utility
        
        start = time.time()
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
        )
        
        # 检查服务状态
        list_collections = utility.list_collections()
        elapsed = time.time() - start
        
        print(f"[OK] Milvus 连接成功")
        print(f"   地址: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
        print(f"   响应时间: {elapsed:.2f}s")
        print(f"   现有集合: {len(list_collections)} 个")
        
        # 检查目标集合是否存在
        if settings.MILVUS_COLLECTION in list_collections:
            collection_info = utility.describe_collection(settings.MILVUS_COLLECTION)
            entity_count = utility.get_collection_stats(settings.MILVUS_COLLECTION).get("row_count", 0)
            print(f"   目标集合 '{settings.MILVUS_COLLECTION}': 已存在")
            print(f"   向量数量: {entity_count}")
        else:
            print(f"   目标集合 '{settings.MILVUS_COLLECTION}': 不存在（首次启动会自动创建）")
        
        connections.disconnect("default")
        return True
        
    except Exception as e:
        print(f"[FAIL] Milvus 连接失败")
        print(f"   错误: {e}")
        print(f"\n[TIP] 提示：请确保 Milvus 服务已启动")
        print(f"   Docker 启动命令示例:")
        print(f"   docker run -d --name milvus -p 19530:19530 milvusdb/milvus:v2.3.0")
        return False


async def main():
    print("=" * 60)
    print("  AI识图比价系统 - 数据库连接诊断工具")
    print("=" * 60)
    
    results = {}
    
    # 测试 MySQL
    results["MySQL"] = await test_mysql()
    
    # 测试 Redis
    results["Redis"] = await test_redis()
    
    # 测试 Milvus
    results["Milvus"] = await test_milvus()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("  [SUMMARY] 诊断汇总")
    print("=" * 60)
    
    for name, ok in results.items():
        status = "[OK] 正常" if ok else "[FAIL] 异常"
        print(f"{name}: {status}")
    
    all_ok = all(results.values())
    failed = [k for k, v in results.items() if not v]
    
    if all_ok:
        print("\n[SUCCESS] 所有数据库服务连接正常！")
    else:
        print(f"\n[WARNING] 以下服务连接失败：{', '.join(failed)}")
        print("\n请检查：")
        if not results["MySQL"]:
            print("  1. MySQL 服务是否启动")
            print("  2. .env 中 MYSQL_HOST/PORT/USER/PASSWORD 配置是否正确")
            print("  3. 数据库 ai_shopping 是否已创建")
        if not results["Redis"]:
            print("  1. Redis 服务是否启动")
            print("  2. .env 中 REDIS_HOST/PORT 配置是否正确")
        if not results["Milvus"]:
            print("  1. Milvus 服务是否启动")
            print("  2. .env 中 MILVUS_HOST/PORT 配置是否正确")
    
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
