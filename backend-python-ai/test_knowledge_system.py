"""
知识库系统测试脚本 - 适配实际后端API
"""

import requests
import json
import time
import tempfile
import os

BASE_URL = "http://localhost:8000/api/v1"


def test_knowledge_base_crud():
    """测试知识库CRUD操作"""
    print("\n" + "="*60)
    print("=== 测试知识库CRUD ===")
    print("="*60)
    
    headers = {
        "X-Employee-ID": "test_emp",
        "X-User-ID": "test_user"
    }
    
    kb_id = None
    
    # 1. 获取知识库列表（初始状态）
    print("\n1. 获取知识库列表（初始状态）:")
    response = requests.get(f"{BASE_URL}/knowledge-bases", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        items = result.get('data', {}).get('items', [])
        print(f"   现有知识库数量: {len(items)}")
        for item in items:
            print(f"   - {item.get('name')} (ID: {item.get('id')})")
    else:
        print(f"   错误: {response.text}")
    
    # 2. 创建知识库
    print("\n2. 创建知识库:")
    kb_data = {
        "kb_data": {
            "name": "测试知识库-API测试",
            "description": "用于API测试的知识库",
            "tags": ["测试", "API", "文档"],
            "is_public": True,
            "category": "测试分类"
        }
    }
    
    response = requests.post(f"{BASE_URL}/knowledge-bases", json=kb_data, headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        kb_info = result.get('data', {})
        kb_id = kb_info.get('id')
        print(f"   ✅ 成功创建知识库: {kb_info.get('name')} (ID: {kb_id})")
        print(f"   创建时间: {kb_info.get('created_at')}")
    else:
        print(f"   ❌ 失败: {response.text}")
        return None
    
    # 3. 获取知识库详情
    print(f"\n3. 获取知识库详情 (ID: {kb_id}):")
    response = requests.get(f"{BASE_URL}/knowledge-bases/{kb_id}", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        kb_detail = result.get('data', {})
        print(f"   知识库名称: {kb_detail.get('name')}")
        print(f"   描述: {kb_detail.get('description')}")
        print(f"   文档数量: {kb_detail.get('doc_count')}")
        print(f"   是否公开: {kb_detail.get('is_public')}")
        print(f"   是否向量化: {kb_detail.get('vectorized')}")
    else:
        print(f"   错误: {response.text}")
    
    # 4. 更新知识库
    print(f"\n4. 更新知识库 (ID: {kb_id}):")
    update_data = {
        "update_data": {
            "description": "更新后的描述-API测试",
            "tags": ["测试", "API", "文档", "已更新"]
        }
    }
    
    response = requests.put(f"{BASE_URL}/knowledge-bases/{kb_id}", json=update_data, headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        kb_updated = result.get('data', {})
        print(f"   ✅ 更新成功")
        print(f"   新描述: {kb_updated.get('description')}")
        print(f"   标签: {kb_updated.get('tags')}")
    else:
        print(f"   ❌ 失败: {response.text}")
    
    # 5. 获取文档处理配置
    print("\n5. 获取文档处理配置:")
    response = requests.get(f"{BASE_URL}/knowledge-bases/config/document-processing")
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        config = result.get('data', {})
        print(f"   ✅ 配置获取成功")
        print(f"   知识点长度: {config.get('knowledge_length')}")
        print(f"   重叠长度: {config.get('overlap_length')}")
        print(f"   自动分段: {config.get('line_break_segment')}")
    else:
        print(f"   错误: {response.text}")
    
    return kb_id


def test_document_upload_and_parse(kb_id: str):
    """测试文档上传和解析"""
    print("\n" + "="*60)
    print(f"=== 测试文档上传和解析 (知识库: {kb_id}) ===")
    print("="*60)
    
    headers = {
        "X-Employee-ID": "test_emp",
        "X-User-ID": "test_user"
    }
    
    # 创建测试文本文件
    test_content = """人工智能（Artificial Intelligence，AI）是一门旨在使计算机系统能够模拟、延伸和扩展人类智能的技术科学。

AI的发展历史可以追溯到20世纪50年代。1956年，达特茅斯会议上首次提出了"人工智能"这一术语，标志着AI作为一门独立学科的诞生。

机器学习是AI的核心技术之一。它使计算机能够从数据中学习规律，而无需进行明确的编程。深度学习作为机器学习的一个分支，通过多层神经网络实现了突破性的进展。

自然语言处理（NLP）是AI的另一个重要领域。它研究如何让计算机理解、解释和生成人类语言。近年来，大语言模型如GPT系列取得了显著成就。

计算机视觉也是AI的关键应用方向。通过深度学习技术，计算机现在可以识别图像中的物体、人脸，甚至理解场景内容。

AI技术在医疗、金融、教育、交通等各个领域都有广泛应用。未来，AI将继续深刻改变我们的生活方式和工作模式。"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        temp_file_path = f.name
    
    try:
        # 1. 上传文档
        print("\n1. 上传文档:")
        with open(temp_file_path, 'rb') as file:
            files = {'file': ('AI介绍文档.txt', file, 'text/plain')}
            data = {'chunk_size': 500, 'chunk_overlap': 100}
            
            response = requests.post(
                f"{BASE_URL}/knowledge-bases/{kb_id}/upload",
                files=files,
                data=data,
                headers=headers
            )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 上传成功")
            print(f"   消息: {result.get('message')}")
            print(f"   生成知识块数: {result.get('data', {}).get('chunks_processed')}")
            
            # 等待向量化处理
            print("   等待向量化处理完成...")
            time.sleep(3)
        else:
            print(f"   ❌ 失败: {response.text}")
            return
    
    finally:
        # 清理临时文件
        os.unlink(temp_file_path)
    
    # 2. 获取知识点列表
    print("\n2. 获取知识点列表:")
    response = requests.get(f"{BASE_URL}/knowledge-bases/{kb_id}/documents", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        items = result.get('data', {}).get('items', [])
        print(f"   ✅ 获取成功")
        print(f"   知识点数量: {len(items)}")
        
        for i, doc in enumerate(items[:3]):
            content = doc.get('content', '')
            print(f"   知识点{i+1} (序号{doc.get('serial_no')}): {content[:60]}...")
    else:
        print(f"   错误: {response.text}")
    
    # 3. 测试搜索功能
    print("\n3. 测试向量搜索:")
    search_data = {
        "query": "什么是人工智能",
        "top_k": 3,
        "score_threshold": 0.3
    }
    
    response = requests.post(f"{BASE_URL}/knowledge-bases/{kb_id}/search", json=search_data, headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        search_results = result.get('data', {}).get('results', [])
        print(f"   ✅ 搜索成功")
        print(f"   查询: {result.get('data', {}).get('query')}")
        print(f"   结果数量: {len(search_results)}")
        
        for i, result_item in enumerate(search_results):
            score = result_item.get('score', 0)
            content = result_item.get('content', '')
            print(f"   结果{i+1} (相似度: {score:.3f}): {content[:60]}...")
    else:
        print(f"   错误: {response.text}")
    
    # 4. 获取知识库统计
    print("\n4. 获取知识库统计:")
    response = requests.get(f"{BASE_URL}/knowledge-bases/{kb_id}/stats", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        stats = result.get('data', {})
        print(f"   ✅ 获取成功")
        print(f"   知识库名称: {stats.get('name')}")
        print(f"   文档数量: {stats.get('doc_count')}")
        print(f"   向量数量: {stats.get('vector_count')}")
        print(f"   是否向量化: {stats.get('vectorized')}")
    else:
        print(f"   错误: {response.text}")


def test_manual_knowledge_items(kb_id: str):
    """测试手动添加知识点"""
    print("\n" + "="*60)
    print(f"=== 测试手动添加知识点 (知识库: {kb_id}) ===")
    print("="*60)
    
    headers = {
        "X-Employee-ID": "test_emp",
        "X-User-ID": "test_user",
        "Content-Type": "application/json"
    }
    
    # 1. 手动添加知识点
    print("\n1. 手动添加知识点:")
    knowledge_items = {
        "items": [
            {
                "content": "机器学习是人工智能的一个分支，它使计算机系统能够从数据中学习并改进性能。",
                "serial_no": 1,
                "source_file": "manual_input.txt",
                "metadata": {"type": "manual", "topic": "机器学习"}
            },
            {
                "content": "深度学习是机器学习的一种方法，它使用多层神经网络来模拟人脑的工作方式。",
                "serial_no": 2,
                "source_file": "manual_input.txt",
                "metadata": {"type": "manual", "topic": "深度学习"}
            },
            {
                "content": "自然语言处理（NLP）是人工智能和语言学领域的交叉学科，研究如何让计算机理解人类语言。",
                "serial_no": 3,
                "source_file": "manual_input.txt",
                "metadata": {"type": "manual", "topic": "NLP"}
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/knowledge-bases/{kb_id}/knowledge",
        json=knowledge_items,
        headers=headers
    )
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ 添加成功")
        print(f"   消息: {result.get('message')}")
        print(f"   保存数量: {result.get('data', {}).get('saved_count')}")
    else:
        print(f"   ❌ 失败: {response.text}")
    
    # 2. 验证知识点已添加
    print("\n2. 验证知识点列表:")
    response = requests.get(f"{BASE_URL}/knowledge-bases/{kb_id}/documents", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        items = result.get('data', {}).get('items', [])
        print(f"   ✅ 获取成功")
        print(f"   总知识点数量: {len(items)}")
        
        # 显示最后添加的几个
        for i, doc in enumerate(items[-3:]):
            print(f"   知识点{len(items)-2+i}: {doc.get('content', '')[:50]}...")


def test_delete_knowledge_base(kb_id: str):
    """测试删除知识库"""
    print("\n" + "="*60)
    print(f"=== 测试删除知识库 (ID: {kb_id}) ===")
    print("="*60)
    
    headers = {
        "X-Employee-ID": "test_emp",
        "X-User-ID": "test_user"
    }
    
    print("\n1. 删除知识库:")
    response = requests.delete(f"{BASE_URL}/knowledge-bases/{kb_id}", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ 删除成功")
        print(f"   消息: {result.get('message')}")
        print(f"   删除的知识库ID: {result.get('data', {}).get('knowledge_base_id')}")
    else:
        print(f"   ❌ 失败: {response.text}")
    
    # 验证已删除
    print("\n2. 验证知识库已删除:")
    response = requests.get(f"{BASE_URL}/knowledge-bases/{kb_id}", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 404:
        print(f"   ✅ 知识库已不存在（符合预期）")
    else:
        print(f"   ⚠️ 知识库仍然存在: {response.text}")


def test_error_handling():
    """测试错误处理"""
    print("\n" + "="*60)
    print("=== 测试错误处理 ===")
    print("="*60)
    
    headers = {
        "X-Employee-ID": "test_emp",
        "X-User-ID": "test_user"
    }
    
    # 1. 访问不存在的知识库
    print("\n1. 访问不存在的知识库:")
    response = requests.get(f"{BASE_URL}/knowledge-bases/non_existent_id", headers=headers)
    print(f"   状态码: {response.status_code}")
    print(f"   预期: 404, 实际: {response.status_code}")
    if response.status_code == 404:
        print(f"   ✅ 正确处理404错误")
    
    # 2. 创建无效数据的知识库
    print("\n2. 创建无效数据的知识库:")
    invalid_data = {
        "kb_data": {
            "name": "",  # 空名称应该被拒绝
            "description": "测试"
        }
    }
    response = requests.post(f"{BASE_URL}/knowledge-bases", json=invalid_data, headers=headers)
    print(f"   状态码: {response.status_code}")
    print(f"   预期: 422, 实际: {response.status_code}")
    if response.status_code == 422:
        print(f"   ✅ 正确验证数据")


def test_system_health():
    """测试系统健康状态"""
    print("\n" + "="*60)
    print("=== 测试系统健康状态 ===")
    print("="*60)
    
    # 测试根路径
    print("\n1. 测试根路径:")
    try:
        response = requests.get("http://localhost:8000/")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 服务运行正常")
            print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
    
    # 测试API文档
    print("\n2. 测试API文档:")
    try:
        response = requests.get("http://localhost:8000/docs")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ API文档可访问")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
    
    # 测试知识库API
    print("\n3. 测试知识库API:")
    try:
        response = requests.get(f"{BASE_URL}/knowledge-bases")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 知识库API正常")
        else:
            print(f"   ⚠️ 知识库API返回: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")


def main():
    """主测试函数"""
    print("\n" + "="*70)
    print("  知识库系统API测试")
    print("  目标: http://localhost:8000")
    print("="*70)
    
    # 首先检查系统健康
    test_system_health()
    
    # 测试知识库CRUD
    kb_id = test_knowledge_base_crud()
    
    if kb_id:
        # 测试文档上传和解析
        test_document_upload_and_parse(kb_id)
        
        # 测试手动添加知识点
        test_manual_knowledge_items(kb_id)
        
        # 测试删除知识库
        test_delete_knowledge_base(kb_id)
    
    # 测试错误处理
    test_error_handling()
    
    print("\n" + "="*70)
    print("  测试完成！")
    print("="*70)


if __name__ == "__main__":
    main()
