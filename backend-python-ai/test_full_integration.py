"""
MEK-AI 完整集成测试
测试 API -> Service -> Repository -> Database 完整调用链
"""

import sys
import os
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置测试环境变量
os.environ["ENV"] = "test"

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 导入数据库组件
from app.db.database import Base
from app.db.models import (
    User, Organization, Employee,
    KnowledgeBase, KnowledgeItem,
    Conversation, Message
)
from app.db.repositories import (
    employee_repository,
    knowledge_repository,
    conversation_repository
)

# 导入服务层
from app.services.knowledge.knowledge_service import KnowledgeService, knowledge_service
from app.services.ai.chat_service import ChatService, chat_service
from app.services.memory.conversation_memory import ConversationMemoryManager, conversation_memory_manager
from app.services.knowledge.rag_service import RAGService

# 导入模型
from app.models.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeItemCreate
)

# 使用SQLite内存数据库进行测试
TEST_DATABASE_URL = "sqlite:///:memory:"


class TestDatabaseLayer(unittest.TestCase):
    """测试数据库层 (Repository)"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.engine = create_engine(TEST_DATABASE_URL, echo=False)
        Base.metadata.create_all(bind=cls.engine)
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        print("✅ 数据库层测试初始化完成")
    
    def setUp(self):
        """每个测试用例前执行"""
        self.db = self.SessionLocal()
    
    def tearDown(self):
        """每个测试用例后执行"""
        self.db.rollback()
        self.db.close()
    
    def test_01_create_organization(self):
        """测试创建组织"""
        org = Organization(
            id="org_test_001",
            name="测试组织",
            description="这是一个测试组织"
        )
        self.db.add(org)
        self.db.commit()
        
        result = self.db.query(Organization).filter_by(id="org_test_001").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "测试组织")
        print("✅ 测试通过: 创建组织")
    
    def test_02_create_user(self):
        """测试创建用户"""
        org = Organization(id="org_test_002", name="用户测试组织")
        self.db.add(org)
        self.db.commit()
        
        user = User(
            id="user_test_001",
            username="testuser",
            email="test@example.com",
            organization_id="org_test_002"
        )
        self.db.add(user)
        self.db.commit()
        
        result = self.db.query(User).filter_by(id="user_test_001").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.username, "testuser")
        print("✅ 测试通过: 创建用户")
    
    def test_03_create_employee(self):
        """测试创建员工"""
        employee_data = {
            "id": "emp_test_001",
            "name": "AI测试助手",
            "description": "用于测试的员工",
            "price": "99",
            "status": "published",
            "category": ["test", "ai"],
            "skills": ["测试", "编程"],
            "created_by": "user_test_001"
        }
        
        employee = employee_repository.create(self.db, obj_in=employee_data)
        
        self.assertIsNotNone(employee)
        self.assertEqual(employee.name, "AI测试助手")
        print("✅ 测试通过: 创建员工")
    
    def test_04_create_knowledge_base(self):
        """测试创建知识库"""
        kb_data = {
            "id": "kb_test_001",
            "name": "测试知识库",
            "description": "用于测试",
            "created_by": "user_test_001",
            "is_public": True
        }
        
        kb = knowledge_repository.create_kb(self.db, obj_in=kb_data)
        
        self.assertIsNotNone(kb)
        self.assertEqual(kb.name, "测试知识库")
        print("✅ 测试通过: 创建知识库")
    
    def test_05_create_knowledge_items(self):
        """测试创建知识点"""
        items = [
            {"content": "知识点1", "serial_no": 1},
            {"content": "知识点2", "serial_no": 2},
            {"content": "知识点3", "serial_no": 3}
        ]
        
        created_items = knowledge_repository.create_items(
            self.db, kb_id="kb_test_001", items=items
        )
        
        self.assertEqual(len(created_items), 3)
        
        # 验证文档计数
        kb = knowledge_repository.get_kb(self.db, "kb_test_001")
        self.assertEqual(kb.doc_count, 3)
        print("✅ 测试通过: 创建知识点")
    
    def test_06_knowledge_permission(self):
        """测试知识库权限"""
        kb_data = {
            "id": "kb_perm_001",
            "name": "权限测试库",
            "created_by": "user_test_001",
            "is_public": False
        }
        knowledge_repository.create_kb(self.db, obj_in=kb_data)
        
        # 测试创建者权限
        has_perm = knowledge_repository.check_permission(
            self.db, kb_id="kb_perm_001", user_id="user_test_001"
        )
        self.assertTrue(has_perm)
        
        # 测试其他用户权限（非公开库）
        other_user = User(id="user_other", username="otheruser")
        self.db.add(other_user)
        self.db.commit()
        
        has_perm_other = knowledge_repository.check_permission(
            self.db, kb_id="kb_perm_001", user_id="user_other"
        )
        self.assertFalse(has_perm_other)
        print("✅ 测试通过: 知识库权限")


class TestServiceLayer(unittest.TestCase):
    """测试服务层 (Service)"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.engine = create_engine(TEST_DATABASE_URL, echo=False)
        Base.metadata.create_all(bind=cls.engine)
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        
        # 初始化服务
        cls.knowledge_service = KnowledgeService()
        cls.chat_service = ChatService()
        cls.memory_manager = ConversationMemoryManager()
        
        print("✅ 服务层测试初始化完成")
    
    def setUp(self):
        """每个测试用例前执行"""
        self.db = self.SessionLocal()
        
        # 创建测试数据
        self._create_test_data()
    
    def tearDown(self):
        """每个测试用例后执行"""
        self.db.rollback()
        self.db.close()
    
    def _create_test_data(self):
        """创建测试数据"""
        # 创建用户
        user = User(id="user_svc_001", username="svcuser", email="svc@test.com")
        self.db.add(user)
        self.db.commit()
    
    def test_01_knowledge_service_list(self):
        """测试知识库服务 - 列表查询"""
        # 先创建一些知识库
        for i in range(3):
            kb_data = KnowledgeBaseCreate(
                name=f"测试知识库{i}",
                description=f"描述{i}",
                is_public=True
            )
            asyncio.run(self.knowledge_service.create_knowledge_base(
                db=self.db,
                kb_data=kb_data,
                user_id="user_svc_001"
            ))
        
        # 测试列表查询
        result = asyncio.run(self.knowledge_service.list_knowledge_bases(
            db=self.db,
            user_id="user_svc_001"
        ))
        
        self.assertGreaterEqual(len(result), 3)
        print(f"✅ 测试通过: 知识库列表查询 (返回 {len(result)} 个)")
    
    def test_02_knowledge_service_create(self):
        """测试知识库服务 - 创建"""
        kb_data = KnowledgeBaseCreate(
            name="服务测试知识库",
            description="用于服务层测试",
            is_public=False
        )
        
        result = asyncio.run(self.knowledge_service.create_knowledge_base(
            db=self.db,
            kb_data=kb_data,
            user_id="user_svc_001"
        ))
        
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "服务测试知识库")
        print("✅ 测试通过: 知识库创建")
    
    def test_03_knowledge_service_get(self):
        """测试知识库服务 - 获取详情"""
        # 先创建
        kb_data = KnowledgeBaseCreate(name="获取测试", description="测试获取")
        created = asyncio.run(self.knowledge_service.create_knowledge_base(
            db=self.db,
            kb_data=kb_data,
            user_id="user_svc_001"
        ))
        
        # 再获取
        result = asyncio.run(self.knowledge_service.get_knowledge_base(
            db=self.db,
            kb_id=created.id,
            user_id="user_svc_001"
        ))
        
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "获取测试")
        print("✅ 测试通过: 知识库获取详情")
    
    def test_04_knowledge_service_update(self):
        """测试知识库服务 - 更新"""
        # 先创建
        kb_data = KnowledgeBaseCreate(name="更新前", description="更新前描述")
        created = asyncio.run(self.knowledge_service.create_knowledge_base(
            db=self.db,
            kb_data=kb_data,
            user_id="user_svc_001"
        ))
        
        # 更新
        update_data = KnowledgeBaseUpdate(
            name="更新后",
            description="更新后描述"
        )
        
        result = asyncio.run(self.knowledge_service.update_knowledge_base(
            db=self.db,
            kb_id=created.id,
            update_data=update_data,
            user_id="user_svc_001"
        ))
        
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "更新后")
        print("✅ 测试通过: 知识库更新")
    
    def test_05_knowledge_service_delete(self):
        """测试知识库服务 - 删除"""
        # 先创建
        kb_data = KnowledgeBaseCreate(name="待删除", description="将被删除")
        created = asyncio.run(self.knowledge_service.create_knowledge_base(
            db=self.db,
            kb_data=kb_data,
            user_id="user_svc_001"
        ))
        
        # 删除
        success = asyncio.run(self.knowledge_service.delete_knowledge_base(
            db=self.db,
            kb_id=created.id,
            user_id="user_svc_001"
        ))
        
        self.assertTrue(success)
        
        # 验证已删除
        result = asyncio.run(self.knowledge_service.get_knowledge_base(
            db=self.db,
            kb_id=created.id,
            user_id="user_svc_001"
        ))
        self.assertIsNone(result)
        print("✅ 测试通过: 知识库删除")
    
    def test_06_knowledge_service_items(self):
        """测试知识库服务 - 知识点操作"""
        # 先创建知识库
        kb_data = KnowledgeBaseCreate(name="知识点测试", description="测试知识点")
        created = asyncio.run(self.knowledge_service.create_knowledge_base(
            db=self.db,
            kb_data=kb_data,
            user_id="user_svc_001"
        ))
        
        # 添加知识点
        items = [
            {"content": "知识点A", "serial_no": 1},
            {"content": "知识点B", "serial_no": 2},
        ]
        
        success = asyncio.run(self.knowledge_service.add_knowledge_items(
            db=self.db,
            kb_id=created.id,
            items=items,
            user_id="user_svc_001"
        ))
        
        self.assertTrue(success)
        
        # 获取知识点
        result = asyncio.run(self.knowledge_service.get_knowledge_items(
            db=self.db,
            kb_id=created.id,
            user_id="user_svc_001"
        ))
        
        self.assertEqual(len(result), 2)
        print("✅ 测试通过: 知识点操作")
    
    def test_07_memory_manager_create_conversation(self):
        """测试对话记忆管理器 - 创建对话"""
        conversation_id = self.memory_manager.create_conversation(
            db=self.db,
            employee_id="emp_test_001",
            user_id="user_svc_001"
        )
        
        self.assertIsNotNone(conversation_id)
        self.assertIsInstance(conversation_id, str)
        print("✅ 测试通过: 创建对话")
    
    def test_08_memory_manager_get_conversation(self):
        """测试对话记忆管理器 - 获取对话"""
        # 先创建
        conversation_id = self.memory_manager.create_conversation(
            db=self.db,
            employee_id="emp_test_001",
            user_id="user_svc_001"
        )
        
        # 获取
        state = self.memory_manager.get_conversation_state(
            db=self.db,
            conversation_id=conversation_id
        )
        
        self.assertIsNotNone(state)
        self.assertEqual(state.employee_id, "emp_test_001")
        print("✅ 测试通过: 获取对话")
    
    def test_09_memory_manager_list_conversations(self):
        """测试对话记忆管理器 - 列出的对话"""
        # 创建多个对话
        for i in range(3):
            self.memory_manager.create_conversation(
                db=self.db,
                employee_id=f"emp_{i}",
                user_id="user_svc_001"
            )
        
        # 列出
        conversations = self.memory_manager.list_conversations(
            db=self.db,
            user_id="user_svc_001"
        )
        
        self.assertGreaterEqual(len(conversations), 3)
        print(f"✅ 测试通过: 列出对话 (返回 {len(conversations)} 个)")
    
    def test_10_memory_manager_delete_conversation(self):
        """测试对话记忆管理器 - 删除对话"""
        # 先创建
        conversation_id = self.memory_manager.create_conversation(
            db=self.db,
            employee_id="emp_test_001",
            user_id="user_svc_001"
        )
        
        # 删除
        success = self.memory_manager.delete_conversation(
            db=self.db,
            conversation_id=conversation_id
        )
        
        self.assertTrue(success)
        
        # 验证已删除
        state = self.memory_manager.get_conversation_state(
            db=self.db,
            conversation_id=conversation_id
        )
        self.assertIsNone(state)
        print("✅ 测试通过: 删除对话")


class TestAPICompatibility(unittest.TestCase):
    """测试API层兼容性 - 验证方法签名"""
    
    def test_01_knowledge_service_signatures(self):
        """测试知识库服务方法签名"""
        import inspect
        
        # 检查关键方法是否接受 db 参数
        methods_to_check = [
            'list_knowledge_bases',
            'get_knowledge_base',
            'create_knowledge_base',
            'update_knowledge_base',
            'delete_knowledge_base',
            'get_knowledge_items',
            'add_knowledge_items',
            'delete_knowledge_item',
            'clear_knowledge_items',
            'update_vectorized_status',
        ]
        
        for method_name in methods_to_check:
            method = getattr(knowledge_service, method_name)
            sig = inspect.signature(method)
            params = list(sig.parameters.keys())
            
            self.assertIn('db', params, f"方法 {method_name} 缺少 db 参数")
        
        print(f"✅ 测试通过: 知识库服务方法签名检查 ({len(methods_to_check)} 个方法)")
    
    def test_02_chat_service_signatures(self):
        """测试聊天服务方法签名"""
        import inspect
        
        # 检查关键方法是否接受 db 参数
        sig = inspect.signature(chat_service.process_chat_message)
        params = list(sig.parameters.keys())
        
        self.assertIn('db', params, "process_chat_message 方法缺少 db 参数")
        
        print("✅ 测试通过: 聊天服务方法签名检查")
    
    def test_03_memory_manager_signatures(self):
        """测试对话记忆管理器方法签名"""
        import inspect
        
        # 检查关键方法是否接受 db 参数
        methods_to_check = [
            'create_conversation',
            'get_conversation_state',
            'get_conversation_history',
            'get_conversation_summary',
            'delete_conversation',
            'list_conversations',
        ]
        
        for method_name in methods_to_check:
            method = getattr(conversation_memory_manager, method_name)
            sig = inspect.signature(method)
            params = list(sig.parameters.keys())
            
            self.assertIn('db', params, f"方法 {method_name} 缺少 db 参数")
        
        print(f"✅ 测试通过: 对话记忆管理器方法签名检查 ({len(methods_to_check)} 个方法)")


class TestEndToEnd(unittest.TestCase):
    """端到端测试 - 模拟完整业务流程"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.engine = create_engine(TEST_DATABASE_URL, echo=False)
        Base.metadata.create_all(bind=cls.engine)
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        
        cls.knowledge_service = KnowledgeService()
        cls.memory_manager = ConversationMemoryManager()
        
        print("✅ 端到端测试初始化完成")
    
    def setUp(self):
        """每个测试用例前执行"""
        self.db = self.SessionLocal()
    
    def tearDown(self):
        """每个测试用例后执行"""
        self.db.rollback()
        self.db.close()
    
    def test_01_full_knowledge_base_workflow(self):
        """测试完整知识库工作流"""
        user_id = "user_e2e_001"
        
        # 1. 创建知识库
        kb_data = KnowledgeBaseCreate(
            name="端到端测试知识库",
            description="测试完整工作流",
            is_public=True
        )
        
        kb = asyncio.run(self.knowledge_service.create_knowledge_base(
            db=self.db,
            kb_data=kb_data,
            user_id=user_id
        ))
        
        self.assertIsNotNone(kb)
        print(f"  1. 创建知识库: {kb.id}")
        
        # 2. 添加知识点
        items = [
            {"content": "人工智能是一门研究如何让计算机模拟人类智能的学科。", "serial_no": 1},
            {"content": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习。", "serial_no": 2},
            {"content": "深度学习是机器学习的一种方法，使用多层神经网络。", "serial_no": 3},
        ]
        
        success = asyncio.run(self.knowledge_service.add_knowledge_items(
            db=self.db,
            kb_id=kb.id,
            items=items,
            user_id=user_id
        ))
        
        self.assertTrue(success)
        print(f"  2. 添加知识点: {len(items)} 个")
        
        # 3. 获取知识库详情
        kb_detail = asyncio.run(self.knowledge_service.get_knowledge_base(
            db=self.db,
            kb_id=kb.id,
            user_id=user_id
        ))
        
        self.assertIsNotNone(kb_detail)
        self.assertEqual(kb_detail.doc_count, 3)
        print(f"  3. 获取知识库详情: 文档数={kb_detail.doc_count}")
        
        # 4. 获取知识点列表
        kb_items = asyncio.run(self.knowledge_service.get_knowledge_items(
            db=self.db,
            kb_id=kb.id,
            user_id=user_id
        ))
        
        self.assertEqual(len(kb_items), 3)
        print(f"  4. 获取知识点列表: {len(kb_items)} 个")
        
        # 5. 更新知识库
        update_data = KnowledgeBaseUpdate(
            name="已更新的知识库",
            description="已更新描述"
        )
        
        updated = asyncio.run(self.knowledge_service.update_knowledge_base(
            db=self.db,
            kb_id=kb.id,
            update_data=update_data,
            user_id=user_id
        ))
        
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, "已更新的知识库")
        print(f"  5. 更新知识库: {updated.name}")
        
        # 6. 删除知识库
        success = asyncio.run(self.knowledge_service.delete_knowledge_base(
            db=self.db,
            kb_id=kb.id,
            user_id=user_id
        ))
        
        self.assertTrue(success)
        print(f"  6. 删除知识库: 成功")
        
        print("✅ 测试通过: 完整知识库工作流")
    
    def test_02_full_conversation_workflow(self):
        """测试完整对话工作流"""
        user_id = "user_e2e_002"
        employee_id = "emp_e2e_001"
        
        # 1. 创建对话
        conversation_id = self.memory_manager.create_conversation(
            db=self.db,
            employee_id=employee_id,
            user_id=user_id
        )
        
        self.assertIsNotNone(conversation_id)
        print(f"  1. 创建对话: {conversation_id}")
        
        # 2. 获取对话状态
        state = self.memory_manager.get_conversation_state(
            db=self.db,
            conversation_id=conversation_id
        )
        
        self.assertIsNotNone(state)
        self.assertEqual(state.employee_id, employee_id)
        print(f"  2. 获取对话状态: employee_id={state.employee_id}")
        
        # 3. 获取对话历史
        history = self.memory_manager.get_conversation_history(
            db=self.db,
            conversation_id=conversation_id
        )
        
        self.assertIsInstance(history, list)
        print(f"  3. 获取对话历史: {len(history)} 条消息")
        
        # 4. 获取对话摘要
        summary = self.memory_manager.get_conversation_summary(
            db=self.db,
            conversation_id=conversation_id
        )
        
        # 新对话可能没有摘要
        print(f"  4. 获取对话摘要: {summary if summary else '无'}")
        
        # 5. 列出用户对话
        conversations = self.memory_manager.list_conversations(
            db=self.db,
            user_id=user_id
        )
        
        self.assertGreaterEqual(len(conversations), 1)
        print(f"  5. 列出用户对话: {len(conversations)} 个")
        
        # 6. 删除对话
        success = self.memory_manager.delete_conversation(
            db=self.db,
            conversation_id=conversation_id
        )
        
        self.assertTrue(success)
        print(f"  6. 删除对话: 成功")
        
        print("✅ 测试通过: 完整对话工作流")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*70)
    print("  MEK-AI 完整集成测试")
    print("  测试范围: API -> Service -> Repository -> Database")
    print("="*70 + "\n")
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestServiceLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestAPICompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "="*70)
    print("  测试结果汇总")
    print("="*70)
    
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
        print(f"   运行测试: {result.testsRun}")
        print(f"   失败: 0")
        print(f"   错误: 0")
    else:
        print(f"❌ 测试失败:")
        print(f"   运行测试: {result.testsRun}")
        print(f"   失败: {len(result.failures)}")
        print(f"   错误: {len(result.errors)}")
        
        if result.failures:
            print("\n  失败的测试:")
            for test, trace in result.failures:
                print(f"   - {test}")
        
        if result.errors:
            print("\n  错误的测试:")
            for test, trace in result.errors:
                print(f"   - {test}")
    
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
