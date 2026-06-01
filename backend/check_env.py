"""
环境变量配置验证脚本
检查 .env 文件是否正确加载，所有必需的环境变量是否存在
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from app.config import Settings


def check_env_file():
    """检查 .env 文件是否存在"""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("[FAIL] .env 文件不存在")
        print("   请复制 .env.example 为 .env 并填写配置")
        return False
    
    print("[OK] .env 文件存在")
    
    # 尝试加载环境变量
    result = load_dotenv(env_path)
    if result:
        print("[OK] 环境变量加载成功")
    else:
        print("[WARN] .env 文件为空或加载失败")
    
    return True


def check_settings():
    """验证所有配置项"""
    try:
        settings = Settings()
        print("\n[CONFIG] 配置项检查结果：\n")
        
        results = []
        
        # MySQL 配置
        mysql_ok = all([
            settings.MYSQL_HOST,
            settings.MYSQL_PORT,
            settings.MYSQL_USER,
            settings.MYSQL_DATABASE is not None,
        ])
        results.append(("MySQL 数据库", mysql_ok, {
            "主机": f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}",
            "用户": settings.MYSQL_USER,
            "数据库": settings.MYSQL_DATABASE,
            "密码": "***" if settings.MYSQL_PASSWORD else "(未设置)",
        }))
        
        # Milvus 配置
        milvus_ok = bool(settings.MILVUS_HOST and settings.MILVUS_PORT)
        results.append(("Milvus 向量库", milvus_ok, {
            "地址": f"{settings.MILVUS_HOST}:{settings.MILVUS_PORT}",
            "集合": settings.MILVUS_COLLECTION,
        }))
        
        # Redis 配置
        redis_ok = bool(settings.REDIS_HOST and settings.REDIS_PORT)
        results.append(("Redis 缓存", redis_ok, {
            "地址": f"{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            "密码": "***" if settings.REDIS_PASSWORD else "(无密码)",
            "数据库": str(settings.REDIS_DB),
        }))
        
        # JWT 配置
        jwt_ok = bool(settings.JWT_SECRET and len(settings.JWT_SECRET) >= 16)
        results.append(("JWT 认证", jwt_ok, {
            "密钥长度": f"{len(settings.JWT_SECRET)} 字符",
            "算法": settings.JWT_ALGORITHM,
            "过期时间": f"{settings.JWT_EXPIRE_HOURS} 小时",
        }))
        
        # DashScope API
        dashscope_ok = bool(settings.DASHSCOPE_API_KEY)
        results.append(("阿里云通义千问 API", dashscope_ok, {
            "API Key": f"{settings.DASHSCOPE_API_KEY[:10]}..." if settings.DASHSCOPE_API_KEY else "(未设置)",
            "嵌入模型": settings.EMBEDDING_MODEL,
            "视觉模型": settings.VISION_EMBEDDING_MODEL,
            "重排序模型": settings.RERANK_MODEL,
        }))
        
        # DeepSeek API
        deepseek_ok = bool(settings.DEEPSEEK_API_KEY)
        results.append(("DeepSeek 多模态 API", deepseek_ok, {
            "API Key": f"{settings.DEEPSEEK_API_KEY[:10]}..." if settings.DEEPSEEK_API_KEY else "(未设置)",
            "Base URL": settings.DEEPSEEK_BASE_URL,
            "模型": settings.DEEPSEEK_MODEL,
        }))
        
        # OSS 配置
        oss_ok = all([settings.OSS_ACCESS_KEY, settings.OSS_SECRET_KEY, 
                      settings.OSS_ENDPOINT, settings.OSS_BUCKET])
        results.append(("阿里云 OSS 存储", oss_ok, {
            "Access Key": f"{settings.OSS_ACCESS_KEY[:8]}..." if settings.OSS_ACCESS_KEY else "(未设置)",
            "Endpoint": settings.OSS_ENDPOINT if settings.OSS_ENDPOINT else "(未设置)",
            "Bucket": settings.OSS_BUCKET if settings.OSS_BUCKET else "(未设置)",
        }))
        
        # 打印结果
        for name, ok, details in results:
            status = "[OK]" if ok else "[FAIL]"
            print(f"{status} {name}")
            for key, value in details.items():
                print(f"   {key}: {value}")
            print()
        
        # 汇总
        all_ok = all(r[1] for r in results)
        failed_count = sum(1 for r in results if not r[1])
        
        print("=" * 50)
        if all_ok:
            print("[SUCCESS] 所有配置项验证通过！")
        else:
            print(f"[WARNING] 有 {failed_count} 项配置需要完善")
            print("\n提示：")
            if not dashscope_ok:
                print("  - 通义千问 API Key 是核心功能必需的")
            if not deepseek_ok:
                print("  - DeepSeek API Key 用于图像识别功能")
            if not oss_ok:
                print("  - OSS 配置用于图片上传存储功能")
        
        return all_ok
        
    except Exception as e:
        print(f"[FAIL] 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("  AI识图比价系统 - 环境变量诊断工具")
    print("=" * 60)
    print()
    
    # 检查 .env 文件
    if not check_env_file():
        sys.exit(1)
    
    # 验证配置
    if not check_settings():
        sys.exit(1)
    
    print("\n[TIP] 提示：配置正确后，可以运行以下命令启动服务：")
    print("   python -m uvicorn app.main:app --reload --port 8000")


if __name__ == "__main__":
    main()
