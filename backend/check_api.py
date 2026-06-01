"""
API 密钥连通性测试脚本
检查 DashScope、DeepSeek、OSS 等 API 是否能正常调用
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings


def test_dashscope_api():
    """测试阿里云通义千问 API"""
    print("\n[*] 测试阿里云通义千问 API (DashScope)...")
    
    if not settings.DASHSCOPE_API_KEY:
        print("[WARN] DASHSCOPE_API_KEY 未配置，跳过测试")
        return None
    
    try:
        import dashscope
        
        dashscope.api_key = settings.DASHSCOPE_API_KEY
        
        # 测试文本嵌入接口
        start = time.time()
        response = dashscope.TextEmbedding.call(
            model=settings.EMBEDDING_MODEL,
            input="测试文本"
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            embedding_len = len(response.output.embeddings[0].embedding)
            print(f"[OK] 通义千问 API 连接成功")
            print(f"   模型: {settings.EMBEDDING_MODEL}")
            print(f"   响应时间: {elapsed:.2f}s")
            print(f"   向量维度: {embedding_len}")
            return True
        else:
            print(f"[FAIL] API 调用失败")
            print(f"   状态码: {response.status_code}")
            print(f"   错误: {response.message}")
            return False
            
    except Exception as e:
        print(f"[FAIL] API 连接异常")
        print(f"   错误: {e}")
        return False


def test_deepseek_api():
    """测试 DeepSeek 多模态 API"""
    print("\n[*] 测试 DeepSeek 多模态 API...")
    
    if not settings.DEEPSEEK_API_KEY:
        print("[WARN] DEEPSEEK_API_KEY 未配置，跳过测试")
        return None
    
    try:
        from openai import OpenAI
        
        start = time.time()
        client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        
        # 简单的文本对话测试
        response = client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=10,
        )
        elapsed = time.time() - start
        
        content = response.choices[0].message.content
        print(f"[OK] DeepSeek API 连接成功")
        print(f"   模型: {settings.DEEPSEEK_MODEL}")
        print(f"   Base URL: {settings.DEEPSEEK_BASE_URL}")
        print(f"   响应时间: {elapsed:.2f}s")
        print(f"   测试回复: {content[:50]}...")
        return True
        
    except Exception as e:
        print(f"[FAIL] DeepSeek API 连接异常")
        print(f"   错误: {e}")
        return False


def test_oss_connection():
    """测试阿里云 OSS 连接"""
    print("\n[*] 测试阿里云 OSS 对象存储...")
    
    if not all([settings.OSS_ACCESS_KEY, settings.OSS_SECRET_KEY, 
                settings.OSS_ENDPOINT, settings.OSS_BUCKET]):
        print("[WARN] OSS 配置不完整，跳过测试")
        print("   需要配置: OSS_ACCESS_KEY, OSS_SECRET_KEY, OSS_ENDPOINT, OSS_BUCKET")
        return None
    
    try:
        import oss2
        
        start = time.time()
        auth = oss2.Auth(settings.OSS_ACCESS_KEY, settings.OSS_SECRET_KEY)
        bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET)
        
        # 尝试获取 Bucket 信息
        bucket_info = bucket.get_bucket_info()
        elapsed = time.time() - start
        
        print(f"[OK] OSS 连接成功")
        print(f"   Endpoint: {settings.OSS_ENDPOINT}")
        print(f"   Bucket: {settings.OSS_BUCKET}")
        print(f"   响应时间: {elapsed:.2f}s")
        print(f"   存储类型: {bucket_info.storage_class}")
        print(f"   所在区域: {bucket_info.location}")
        return True
        
    except ImportError:
        print("[FAIL] OSS SDK 未安装 (pip install oss2)")
        return False
    except Exception as e:
        print(f"[FAIL] OSS 连接失败")
        print(f"   错误: {e}")
        return False


def main():
    print("=" * 60)
    print("  AI识图比价系统 - API 连通性诊断工具")
    print("=" * 60)
    
    results = {}
    
    # 测试各 API
    results["通义千问 (DashScope)"] = test_dashscope_api()
    results["DeepSeek 多模态"] = test_deepseek_api()
    results["阿里云 OSS"] = test_oss_connection()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("  [SUMMARY] API 诊断汇总")
    print("=" * 60)
    
    for name, result in results.items():
        if result is None:
            status = "[SKIP] 未配置"
        elif result:
            status = "[OK] 正常"
        else:
            status = "[FAIL] 异常"
        print(f"{name}: {status}")
    
    tested = [r for r in results.values() if r is not None]
    passed = sum(1 for r in tested if r)
    
    print("\n[TIP] 提示：")
    if not any(results.values()):
        print("  - 所有 API 都未配置或连接失败")
        print("  - 核心功能需要至少配置通义千问 API")
    else:
        print(f"  - 已测试 {len(tested)} 个 API，{passed} 个正常")
        if not results.get("通义千问 (DashScope)"):
            print("  - [WARN] 通义千问是核心功能必需的 API")
    
    return all(r for r in results.values() if r is not None)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
