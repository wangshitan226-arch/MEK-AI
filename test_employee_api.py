"""
员工API自测文件
用于验证员工创建和列表获取功能
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

# 测试用户ID
TEST_USER_ID = "test_user_123"

# 存储创建的员工ID
created_employee_ids = []


def test_create_employee():
    """测试创建员工"""
    print("\n" + "="*60)
    print("测试1: 创建员工")
    print("="*60)
    
    url = f"{BASE_URL}/employees/"
    
    employee_data = {
        "employee_data": {
            "name": "测试员工",
            "description": "这是一个测试员工",
            "prompt": "你是测试员工，请友好地回答用户问题",
            "skills": ["测试", "对话"],
            "tags": ["test"],
            "category": ["测试分类"],
            "status": "draft"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": TEST_USER_ID
    }
    
    try:
        response = requests.post(url, json=employee_data, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get("success"):
                employee_id = data.get("data", {}).get("id")
                created_employee_ids.append(employee_id)
                print(f"✅ 创建员工成功: {employee_id}")
                
                # 检查是否有 created 标签
                tags = data.get("data", {}).get("tags", [])
                if "created" in tags:
                    print(f"✅ 员工有 'created' 标签")
                else:
                    print(f"❌ 员工缺少 'created' 标签，当前标签: {tags}")
                
                return True
            else:
                print(f"❌ 创建员工失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def test_list_employees():
    """测试获取员工列表"""
    print("\n" + "="*60)
    print("测试2: 获取员工列表")
    print("="*60)
    
    url = f"{BASE_URL}/employees/"
    
    headers = {
        "X-User-ID": TEST_USER_ID
    }
    
    params = {
        "created_by": TEST_USER_ID
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据结构: {list(data.keys())}")
            
            if data.get("success"):
                response_data = data.get("data", {})
                
                # 检查数据结构
                if isinstance(response_data, list):
                    print(f"⚠️  data 是数组，期望是对象")
                    items = response_data
                else:
                    items = response_data.get("items", [])
                    total = response_data.get("total", 0)
                    print(f"总数: {total}")
                
                print(f"员工数量: {len(items)}")
                
                if len(items) > 0:
                    print(f"✅ 获取到 {len(items)} 个员工")
                    for emp in items:
                        print(f"  - {emp.get('name')} (ID: {emp.get('id')}, tags: {emp.get('tags')})")
                    return True
                else:
                    print(f"❌ 员工列表为空")
                    return False
            else:
                print(f"❌ 获取列表失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def test_list_all_employees():
    """测试获取所有员工（不过滤创建者）"""
    print("\n" + "="*60)
    print("测试3: 获取所有员工（不过滤创建者）")
    print("="*60)
    
    url = f"{BASE_URL}/employees/"
    
    headers = {
        "X-User-ID": TEST_USER_ID
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                response_data = data.get("data", {})
                items = response_data.get("items", []) if isinstance(response_data, dict) else response_data
                
                print(f"所有员工数量: {len(items)}")
                
                # 统计 created_by 为 TEST_USER_ID 的员工
                user_employees = [emp for emp in items if emp.get("created_by") == TEST_USER_ID]
                print(f"当前用户创建的员工: {len(user_employees)}")
                
                for emp in items[:5]:  # 只显示前5个
                    print(f"  - {emp.get('name')} (created_by: {emp.get('created_by')}, tags: {emp.get('tags')})")
                
                return True
            else:
                print(f"❌ 获取列表失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def cleanup():
    """清理测试数据"""
    print("\n" + "="*60)
    print("清理: 删除测试员工")
    print("="*60)
    
    for employee_id in created_employee_ids:
        url = f"{BASE_URL}/employees/{employee_id}"
        headers = {"X-User-ID": TEST_USER_ID}
        
        try:
            response = requests.delete(url, headers=headers)
            if response.status_code == 200:
                print(f"✅ 删除员工 {employee_id}")
            else:
                print(f"⚠️  删除员工 {employee_id} 失败: {response.status_code}")
        except Exception as e:
            print(f"⚠️  删除员工 {employee_id} 异常: {str(e)}")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("员工API自测")
    print("="*60)
    
    results = []
    
    # 测试创建员工
    results.append(("创建员工", test_create_employee()))
    
    # 测试获取员工列表
    results.append(("获取员工列表", test_list_employees()))
    
    # 测试获取所有员工
    results.append(("获取所有员工", test_list_all_employees()))
    
    # 清理
    cleanup()
    
    # 打印总结
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n✅ 所有测试通过！")
        return 0
    else:
        print("\n❌ 部分测试失败！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
