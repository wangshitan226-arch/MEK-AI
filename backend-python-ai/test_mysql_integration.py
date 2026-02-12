"""
MySQL数据库集成测试
测试所有数据库模型和Repository的功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 导入数据库组件
from app.db.database import Base, check_db_connection
from app.db.models import (
    User, Organization, Employee,
    KnowledgeBase, KnowledgeItem, UserKnowledgeBase,
    Conversation, Message,
    HireRecord, TrialRecord
)
from app.db.repositories import (
    employee_repository,
    knowledge_repository,
    conversation_repository
)

# 使用SQLite内存数据库进行测试
TEST_DATABASE_URL = "sqlite:///:memory:"


class TestDatabaseIntegration(unittest.TestCase):
    """数据库集成测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 创建测试数据库引擎
        cls.engine = create_engine(TEST_DATABASE_URL, echo=False)
        
        # 创建所有表
        Base.metadata.create_all(bind=cls.engine)
        
        # 创建会话工厂
        cls.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=cls.engine
        )
        
        print("✅ 测试数据库初始化完成")
    
    def setUp(self):
        """每个测试用例前执行"""
        self.db = self.SessionLocal()
    
    def tearDown(self):
        """每个测试用例后执行"""
        self.db.rollback()
        self.db.close()
    
    # ========== 用户和组织测试 ==========
    
    def test_create_organization(self):
        """测试创建组织"""
        org = Organization(
            id="org_001",
            name="测试组织",
            description="这是一个测试组织"
        )
        self.db.add(org)
        self.db.commit()
        
        # 验证
        result = self.db.query(Organization).filter_by(id="org_001").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "测试组织")
        print("✅ 组织创建测试通过")
    
    def test_create_user(self):
        """测试创建用户"""
        # 先创建组织
        org = Organization(id="org_002", name="用户测试组织")
        self.db.add(org)
        self.db.commit()
        
        # 创建用户
        user = User(
            id="user_001",
            username="testuser",
            email="test@example.com",
            organization_id="org_002"
        )
        self.db.add(user)
        self.db.commit()
        
        # 验证
        result = self.db.query(User).filter_by(id="user_001").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.username, "testuser")
        self.assertEqual(result.organization_id, "org_002")
        print("✅ 用户创建测试通过")
    
    # ========== 员工测试 ==========
    
    def test_create_employee(self):
        """测试创建员工"""
        employee_data = {
            "id": "emp_test_001",
            "name": "AI测试助手",
            "description": "用于测试的员工",
            "price": "99",
            "status": "published",
            "category": ["test", "ai"],
            "skills": ["测试", "编程"],
            "created_by": "user_001"
        }
        
        employee = employee_repository.create(self.db, obj_in=employee_data)
        
        # 验证
        self.assertIsNotNone(employee)
        self.assertEqual(employee.name, "AI测试助手")
        self.assertEqual(employee.price, "99")
        print("✅ 员工创建测试通过")
    
    def test_get_employee(self):
        """测试获取员工"""
        # 先创建
        employee_data = {
            "id": "emp_test_002",
            "name": "获取测试员工",
            "status": "draft"
        }
        employee_repository.create(self.db, obj_in=employee_data)
        
        # 再获取
        result = employee_repository.get(self.db, "emp_test_002")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "获取测试员工")
        print("✅ 员工获取测试通过")
    
    def test_update_employee(self):
        """测试更新员工"""
        # 创建
        employee_data = {
            "id": "emp_test_003",
            "name": "更新前名称",
            "status": "draft"
        }
        employee = employee_repository.create(self.db, obj_in=employee_data)
        
        # 更新
        updated = employee_repository.update(
            self.db,
            db_obj=employee,
            obj_in={"name": "更新后名称", "status": "published"}
        )
        
        self.assertEqual(updated.name, "更新后名称")
        self.assertEqual(updated.status, "published")
        print("✅ 员工更新测试通过")
    
    def test_delete_employee(self):
        """测试删除员工"""
        # 创建
        employee_data = {
            "id": "emp_test_004",
            "name": "待删除员工"
        }
        employee_repository.create(self.db, obj_in=employee_data)
        
        # 删除
        deleted = employee_repository.delete(self.db, id="emp_test_004")
        
        # 验证
        result = employee_repository.get(self.db, "emp_test_004")
        self.assertIsNone(result)
        print("✅ 员工删除测试通过")
    
    def test_list_employees_with_filter(self):
        """测试员工列表过滤"""
        # 创建多个员工
        for i in range(5):
            employee_repository.create(self.db, obj_in={
                "id": f"emp_list_{i}",
                "name": f"员工{i}",
                "status": "published" if i % 2 == 0 else "draft",
                "category": ["test"] if i < 3 else ["other"]
            })
        
        # 测试状态过滤
        published = employee_repository.get_by_status(
            self.db, status="published"
        )
        # 0, 2, 4 是 published，再加上之前测试创建的员工
        self.assertGreaterEqual(len(published), 3)
        
        print("✅ 员工列表过滤测试通过")
    
    # ========== 知识库测试 ==========
    
    def test_create_knowledge_base(self):
        """测试创建知识库"""
        kb_data = {
            "id": "kb_test_001",
            "name": "测试知识库",
            "description": "用于测试",
            "created_by": "user_001",
            "is_public": True
        }
        
        kb = knowledge_repository.create_kb(self.db, obj_in=kb_data)
        
        self.assertIsNotNone(kb)
        self.assertEqual(kb.name, "测试知识库")
        print("✅ 知识库创建测试通过")
    
    def test_knowledge_items(self):
        """测试知识点操作"""
        # 先创建知识库
        kb_data = {
            "id": "kb_test_002",
            "name": "知识点测试库",
            "created_by": "user_001"
        }
        knowledge_repository.create_kb(self.db, obj_in=kb_data)
        
        # 添加知识点
        items = [
            {"content": "知识点1", "serial_no": 1},
            {"content": "知识点2", "serial_no": 2},
            {"content": "知识点3", "serial_no": 3}
        ]
        
        created_items = knowledge_repository.create_items(
            self.db, kb_id="kb_test_002", items=items
        )
        
        self.assertEqual(len(created_items), 3)
        
        # 验证知识点
        kb_items = knowledge_repository.get_items_by_kb(
            self.db, kb_id="kb_test_002"
        )
        self.assertEqual(len(kb_items), 3)
        
        # 验证文档计数
        kb = knowledge_repository.get_kb(self.db, "kb_test_002")
        self.assertEqual(kb.doc_count, 3)
        
        print("✅ 知识点操作测试通过")
    
    def test_knowledge_permission(self):
        """测试知识库权限"""
        # 创建用户和知识库
        user = User(id="user_perm", username="permuser")
        self.db.add(user)
        
        kb_data = {
            "id": "kb_perm_001",
            "name": "权限测试库",
            "created_by": "user_perm",
            "is_public": False
        }
        knowledge_repository.create_kb(self.db, obj_in=kb_data)
        
        # 测试创建者权限
        has_perm = knowledge_repository.check_permission(
            self.db, kb_id="kb_perm_001", user_id="user_perm"
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
        
        print("✅ 知识库权限测试通过")
    
    # ========== 对话测试 ==========
    
    def test_create_conversation(self):
        """测试创建对话"""
        conv_data = {
            "id": "conv_test_001",
            "employee_id": "emp_test_001",
            "user_id": "user_001",
            "title": "测试对话"
        }
        
        conv = conversation_repository.create_conversation(
            self.db, obj_in=conv_data
        )
        
        self.assertIsNotNone(conv)
        self.assertEqual(conv.title, "测试对话")
        print("✅ 对话创建测试通过")
    
    def test_conversation_messages(self):
        """测试对话消息"""
        # 创建对话
        conv_data = {
            "id": "conv_test_002",
            "employee_id": "emp_test_001",
            "user_id": "user_001"
        }
        conversation_repository.create_conversation(self.db, obj_in=conv_data)
        
        # 添加消息
        messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么可以帮助你的？"},
            {"role": "user", "content": "介绍一下自己"}
        ]
        
        created = conversation_repository.create_messages(
            self.db, conversation_id="conv_test_002", messages=messages
        )
        
        self.assertEqual(len(created), 3)
        
        # 验证消息计数
        conv = conversation_repository.get_conversation(
            self.db, conversation_id="conv_test_002"
        )
        self.assertEqual(conv.message_count, 3)
        
        # 获取消息列表
        msg_list = conversation_repository.get_messages(
            self.db, conversation_id="conv_test_002"
        )
        self.assertEqual(len(msg_list), 3)
        
        print("✅ 对话消息测试通过")
    
    def test_get_user_conversations(self):
        """测试获取用户对话列表"""
        # 创建多个对话
        for i in range(3):
            conversation_repository.create_conversation(self.db, obj_in={
                "id": f"conv_user_{i}",
                "employee_id": f"emp_{i}",
                "user_id": "user_conv_test"
            })
        
        # 获取用户对话
        conversations = conversation_repository.get_conversations_by_user(
            self.db, user_id="user_conv_test"
        )
        
        self.assertEqual(len(conversations), 3)
        print("✅ 用户对话列表测试通过")
    
    # ========== 雇佣记录测试 ==========
    
    def test_hire_record(self):
        """测试雇佣记录"""
        # 创建员工
        employee_repository.create(self.db, obj_in={
            "id": "emp_hire_test",
            "name": "雇佣测试员工"
        })
        
        # 创建雇佣记录
        hire_record = HireRecord(
            id="hire_001",
            employee_id="emp_hire_test",
            user_id="user_001",
            organization_id="org_001",
            status="active"
        )
        self.db.add(hire_record)
        self.db.commit()
        
        # 验证
        result = self.db.query(HireRecord).filter_by(id="hire_001").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.status, "active")
        print("✅ 雇佣记录测试通过")
    
    def test_trial_record(self):
        """测试试用记录"""
        trial_record = TrialRecord(
            id="trial_001",
            employee_id="emp_hire_test",
            user_id="user_001",
            rating=5,
            feedback="非常好用！"
        )
        self.db.add(trial_record)
        self.db.commit()
        
        # 验证
        result = self.db.query(TrialRecord).filter_by(id="trial_001").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.rating, 5)
        print("✅ 试用记录测试通过")
    



class TestDatabaseSchema(unittest.TestCase):
    """数据库Schema测试"""
    
    def test_all_tables_created(self):
        """测试所有表都已创建"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        
        # 获取所有表名
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            "organizations",
            "users",
            "employees",
            "knowledge_bases",
            "knowledge_items",
            "user_knowledge_bases",
            "vector_metadata",
            "documents",
            "conversations",
            "messages",
            "hire_records",
            "trial_records"
        ]
        
        for table in expected_tables:
            self.assertIn(table, tables, f"表 {table} 未创建")
        
        print(f"✅ 所有 {len(expected_tables)} 张表创建成功")


def run_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 MEK-AI MySQL数据库集成测试")
    print("="*60 + "\n")
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseSchema))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
    else:
        print(f"❌ 测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
    print("="*60 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
