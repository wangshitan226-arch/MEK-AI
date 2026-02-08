"""
修复的测试脚本
使用正确的请求格式
"""

import requests
import json
import os
import sys
import tempfile
import subprocess

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """测试健康检查"""
    print("=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.status_code == 200

def test_chat_with_correct_format():
    """使用正确格式测试聊天"""
    print("\n=== 测试聊天（正确格式）===")
    
    headers = {
        "X-Employee-ID": "test_emp",
        "X-User-ID": "test_user"
    }
    
    # 正确的请求格式：嵌套在 chat_request 中
    data = {
        "chat_request": {
            "message": "你好，请介绍一下你自己",
            "employee_id": "mock_emp_001",
            "conversation_id": None
        }
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=data, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"成功: {result.get('success')}")
        print(f"消息: {result.get('message')}")
        print(f"回复: {result.get('data', {}).get('response', '')[:100]}...")
        return result.get('data', {}).get('conversation_id')
    else:
        print(f"响应: {response.text}")
        return None

def test_list_endpoints():
    """列出所有可用的端点"""
    print("\n=== 列出所有端点 ===")
    
    # 检查路由文件是否正确加载
    endpoints_to_test = [
        ("/health", "GET", "健康检查"),
        ("/chat", "POST", "聊天"),
        ("/chat/conversations", "GET", "对话列表"),
        ("/employees", "GET", "员工列表"),
        ("/employees/emp_001", "GET", "员工详情"),
        ("/marketplace/employees", "GET", "市场员工"),
        ("/marketplace/categories", "GET", "分类"),
        ("/marketplace/industries", "GET", "行业")
    ]
    
    headers = {
        "X-Employee-ID": "test_emp",
        "X-User-ID": "test_user"
    }
    
    for endpoint, method, description in endpoints_to_test:
        print(f"\n{description} ({method} {endpoint}):")
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers)
            
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 404:
                print("  ❌ 路由未找到（可能未正确注册）")
            elif response.status_code == 400:
                print("  ⚠️ 请求参数错误")
            elif response.status_code == 200:
                print("  ✅ 成功")
                result = response.json()
                if result.get('success'):
                    print(f"  数据: {len(result.get('data', {}))} 个字段")
                else:
                    print(f"  错误: {result.get('message')}")
        except Exception as e:
            print(f"  ❌ 请求失败: {e}")

def test_router_registration():
    """检查路由注册情况"""
    print("\n=== 检查路由注册 ===")
    
    # 直接检查openapi.json
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        if response.status_code == 200:
            openapi_data = response.json()
            paths = list(openapi_data.get("paths", {}).keys())
            
            print("已注册的路由:")
            for path in sorted(paths):
                if path.startswith("/api/v1"):
                    print(f"  {path}")
                    
            # 检查特定路由是否存在
            required_paths = [
                "/api/v1/employees",
                "/api/v1/marketplace/employees",
                "/api/v1/marketplace/categories"
            ]
            
            print("\n缺失的路由:")
            missing_count = 0
            for path in required_paths:
                if path not in paths:
                    print(f"  ❌ {path}")
                    missing_count += 1
            
            if missing_count == 0:
                print("  ✅ 所有路由都已注册")
            else:
                print(f"\n共缺失 {missing_count} 个路由")
        else:
            print(f"无法获取openapi.json: {response.status_code}")
    except Exception as e:
        print(f"获取openapi.json失败: {e}")

def check_import_issues():
    """检查导入问题（修复跨进程变量引用 + 正确路径）"""
    print("\n=== 检查导入问题 ===")
    
    # 1. 获取当前脚本的项目根目录（关键）
    CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    print(f"📌 项目根目录（simple_test.py所在位置）: {CURRENT_SCRIPT_DIR}")
    print(f"📌 app文件夹是否存在: {os.path.exists(os.path.join(CURRENT_SCRIPT_DIR, 'app'))}")
    
    # 2. 编写独立的测试代码（完全在子进程内运行，不依赖主进程变量）
    test_code = f'''
import sys
import os

# 强制将项目根目录加入Python搜索路径
PROJECT_ROOT = r"{CURRENT_SCRIPT_DIR}"
sys.path.insert(0, PROJECT_ROOT)

# 打印路径排查
print("🔍 项目根目录（强制加入）:", PROJECT_ROOT)
print("🔍 Python搜索路径前3个:", sys.path[:3])
print("🔍 app模块路径:", os.path.join(PROJECT_ROOT, "app"))
print("🔍 app模块是否存在:", os.path.exists(os.path.join(PROJECT_ROOT, "app")))

# 测试employees_router导入
try:
    from app.api.v1.endpoints import employees_router
    print("[OK] employees_router 导入成功")
    print(f"    路由器前缀: {{{employees_router.prefix}}}")
    print(f"    路由器标签: {{{employees_router.tags}}}")
except ImportError as e:
    print(f"[ERROR] employees_router 导入失败: {{e}}")
    print(f"    错误详情: {{e}}")
except Exception as e:
    print(f"[ERROR] employees_router 导入异常: {{e}}")
    print(f"    错误类型: {{type(e).__name__}}")

# 测试marketplace_router导入
try:
    from app.api.v1.endpoints import marketplace_router
    print("[OK] marketplace_router 导入成功")
    print(f"    路由器前缀: {{{marketplace_router.prefix}}}")
    print(f"    路由器标签: {{{marketplace_router.tags}}}")
except ImportError as e:
    print(f"[ERROR] marketplace_router 导入失败: {{e}}")
    print(f"    错误详情: {{e}}")
except Exception as e:
    print(f"[ERROR] marketplace_router 导入异常: {{e}}")
    print(f"    错误类型: {{type(e).__name__}}")
'''
    
    print("\n导入测试代码:")
    print(test_code)
    
    # 3. 保存临时文件并运行（避免跨进程变量引用）
    temp_file_path = None
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(test_code)
            temp_file_path = f.name
        
        print("\n运行导入测试...")
        # 执行子进程，指定项目根目录为工作目录
        result = subprocess.run(
            [sys.executable, temp_file_path],  # 使用当前Python解释器
            cwd=CURRENT_SCRIPT_DIR,
            capture_output=True
        )
        
        # 安全解码输出（适配Windows编码）
        def safe_decode(byte_data):
            if not byte_data:
                return ""
            try:
                return byte_data.decode('gbk')  # Windows默认编码
            except UnicodeDecodeError:
                return byte_data.decode('utf-8', errors='ignore')
        
        # 打印输出结果
        stdout = safe_decode(result.stdout)
        stderr = safe_decode(result.stderr)
        
        if stdout:
            print("标准输出:")
            print(stdout)
        if stderr:
            print("错误输出:")
            print(stderr)
            
    except Exception as e:
        print(f"运行测试失败: {e}")
        print(f"错误类型: {type(e).__name__}")
    finally:
        # 清理临时文件（兼容Windows文件占用）
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except PermissionError:
                print(f"警告：临时文件 {temp_file_path} 无法立即删除，稍后会自动清理")

def main():
    """主测试函数"""
    print("开始修复测试MEK-AI后端服务...")
    print("=" * 60)
    
    # 测试健康检查
    if not test_health():
        print("✗ 健康检查失败，服务可能未启动")
        return
    
    # 测试聊天（正确格式）
    conversation_id = test_chat_with_correct_format()
    
    if conversation_id:
        print(f"✓ 聊天成功，对话ID: {conversation_id}")
    
    # 列出所有端点
    test_list_endpoints()
    
    # 检查路由注册
    test_router_registration()
    
    # 检查导入问题
    check_import_issues()
    
    print("\n" + "=" * 60)
    print("修复测试完成！")

if __name__ == "__main__":
    main()