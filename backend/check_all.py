"""
一键完整诊断脚本
整合所有检查项，提供完整的系统健康报告
用法: python check_all.py
"""
import sys
import subprocess
import time
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}  {text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")

def run_check(script_name, description):
    """运行子诊断脚本并返回结果"""
    print(f"\n[*] {description}...")
    print("-" * 40)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 输出子脚本的输出
        if result.stdout:
            for line in result.stdout.split('\n'):
                if '[OK]' in line or 'PASS' in line:
                    print(f"  {Colors.GREEN}{line}{Colors.RESET}")
                elif '[FAIL]' in line or '[WARN]' in line or 'ERROR' in line:
                    print(f"  {Colors.RED if '[FAIL]' in line or 'ERROR' in line else Colors.YELLOW}{line}{Colors.RESET}")
                else:
                    print(f"  {line}")
        
        if result.stderr:
            print(f"\n  {Colors.RED}[ERROR] 输出:{Colors.RESET}")
            for line in result.stderr.split('\n'):
                if line.strip():
                    print(f"  {Colors.RED}{line}{Colors.RESET}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"  {Colors.RED}[FAIL] 脚本执行超时（30秒）{Colors.RESET}")
        return False
    except Exception as e:
        print(f"  {Colors.RED}[FAIL] 执行失败: {e}{Colors.RESET}")
        return False


def check_dependencies():
    """检查 Python 依赖是否安装"""
    print("[*] 检查 Python 依赖...")
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("aiomysql", "aiomysql"),
        ("pymilvus", "PyMilvus"),
        ("redis", "Redis"),
        ("pyjwt", "PyJWT"),
        ("openai", "OpenAI"),
        ("dotenv", "python-dotenv"),
        ("dashscope", "DashScope"),
        ("oss2", "OSS2"),
    ]
    
    installed = []
    missing = []
    
    for module, name in required_packages:
        try:
            __import__(module)
            installed.append(name)
            print(f"  {Colors.GREEN}[OK]{Colors.RESET} {name}")
        except ImportError:
            missing.append(name)
            print(f"  {Colors.RED}[FAIL]{Colors.RESET} {name} (未安装)")
    
    return len(missing) == 0, missing


def check_python_version():
    """检查 Python 版本"""
    import platform
    version = platform.python_version()
    major, minor = map(int, version.split('.')[:2])
    
    print("[*] Python 版本检查...")
    print(f"  当前版本: {version}")
    
    if major == 3 and minor >= 10:
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} 版本符合要求（>= 3.10）")
        return True
    else:
        print(f"  {Colors.RED}[FAIL]{Colors.RESET} 版本过低，需要 Python >= 3.10")
        return False


def main():
    start_time = time.time()
    
    print(f"\n{Colors.BLUE}")
    print("=" * 60)
    print("   AI识图比价系统 - 完整健康诊断工具")
    print("=" * 60)
    print(f"{Colors.RESET}")
    
    results = {
        "Python版本": False,
        "依赖包": False,
        "环境变量": False,
        "数据库连接": False,
        "API连通性": False,
    }
    
    # 1. Python 版本检查
    print_header("Step 1/4: 基础环境检查")
    results["Python版本"] = check_python_version()
    deps_ok, missing = check_dependencies()
    results["依赖包"] = deps_ok
    
    if missing:
        print(f"\n  {Colors.YELLOW}[TIP] 缺失的依赖包安装命令:{Colors.RESET}")
        print(f"  pip install {' '.join([m.lower() for m in missing])}")
    
    # 2. 环境变量检查
    print_header("Step 2/4: 环境变量配置检查")
    results["环境变量"] = run_check("check_env.py", "验证 .env 配置文件")
    
    # 3. 数据库连接测试
    print_header("Step 3/4: 数据库服务连接测试")
    results["数据库连接"] = run_check("check_database.py", "测试 MySQL/Redis/Milvus 连接")
    
    # 4. API 连通性测试
    print_header("Step 4/4: 外部 API 连通性测试")
    results["API连通性"] = run_check("check_api.py", "测试 DashScope/DeepSeek/OSS API")
    
    # 生成最终报告
    elapsed = time.time() - start_time
    
    print(f"\n\n{Colors.BLUE}")
    print("=" * 60)
    print("   最终诊断报告")
    print("=" * 60)
    print(f"{Colors.RESET}\n")
    
    all_passed = True
    for name, passed in results.items():
        status = f"{Colors.GREEN}[OK]{Colors.RESET}" if passed else f"{Colors.RED}[FAIL]{Colors.RESET}"
        print(f"  {name:<15}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\n  [TIME] 总耗时: {elapsed:.1f}s")
    
    print(f"\n{'=' * 60}")
    if all_passed:
        print(f"  {Colors.GREEN}[SUCCESS] 所有检查通过！系统可以正常启动{Colors.RESET}")
        print(f"\n  启动命令:")
        print(f"  {Colors.BLUE}python -m uvicorn app.main:app --reload --port 8000{Colors.RESET}")
        print(f"\n  或使用开发模式:")
        print(f"  {Colors.BLUE}python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000{Colors.RESET}")
    else:
        failed_items = [k for k, v in results.items() if not v]
        print(f"  {Colors.RED}[WARNING] 有 {len(failed_items)} 项检查未通过{Colors.RESET}")
        
        print(f"\n  {Colors.YELLOW}故障排除建议:{Colors.RESET}")
        if not results["Python版本"]:
            print("  - 升级 Python 到 3.10+ 版本")
        if not results["依赖包"]:
            print("  - 运行: pip install -r requirements.txt")
        if not results["环境变量"]:
            print("  - 复制 .env.example 为 .env 并填写配置")
            print("  - 运行: python check_env.py 查看详情")
        if not results["数据库连接"]:
            print("  - 确保 MySQL/Redis/Milvus 服务已启动")
            print("  - 运行: python check_database.py 查看详情")
        if not results["API连通性"]:
            print("  - 检查 API Key 是否正确配置")
            print("  - 运行: python check_api.py 查看详情")
        
        print(f"\n  {Colors.YELLOW}建议按顺序执行以下命令排查问题:{Colors.RESET}")
        print(f"  {Colors.BLUE}1. python check_env.py      # 检查环境变量{Colors.RESET}")
        print(f"  {Colors.BLUE}2. python check_database.py  # 检查数据库连接{Colors.RESET}")
        print(f"  {Colors.BLUE}3. python check_api.py       # 检查 API 连通性{Colors.RESET}")
    
    print(f"\n{'=' * 60}\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
