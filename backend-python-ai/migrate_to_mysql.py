"""
数据迁移脚本：从内存存储迁移到MySQL

使用方法:
1. 确保MySQL已启动并创建了数据库
2. 运行: python migrate_to_mysql.py

注意: 此脚本应在应用启动前运行一次
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from sqlalchemy.orm import Session

from app.db import SessionLocal, init_db
from app.db.repositories import (
    employee_repository,
    knowledge_repository,
    conversation_repository
)
from app.db.models import (
    User, Organization, Employee,
    KnowledgeBase, KnowledgeItem,
    Conversation, Message,
    HireRecord, TrialRecord
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DataMigrator:
    """数据迁移器"""
    
    def __init__(self):
        self.db: Session = SessionLocal()
        self.stats = {
            "organizations": 0,
            "users": 0,
            "employees": 0,
            "knowledge_bases": 0,
            "knowledge_items": 0,
            "conversations": 0,
            "messages": 0,
            "hire_records": 0,
            "trial_records": 0,
        }
    
    def migrate_all(self):
        """执行所有迁移"""
        logger.info("🚀 开始数据迁移...")
        
        try:
            # 初始化数据库表
            logger.info("📦 初始化数据库表...")
            init_db()
            
            # 迁移组织
            self.migrate_organizations()
            
            # 迁移用户
            self.migrate_users()
            
            # 迁移员工
            self.migrate_employees()
            
            # 迁移知识库
            self.migrate_knowledge_bases()
            
            # 迁移对话
            self.migrate_conversations()
            
            # 提交所有更改
            self.db.commit()
            
            # 输出统计
            self.print_stats()
            
            logger.info("✅ 数据迁移完成！")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ 数据迁移失败: {str(e)}", exc_info=True)
            raise
        finally:
            self.db.close()
    
    def migrate_organizations(self):
        """迁移组织数据"""
        logger.info("🏢 迁移组织数据...")
        
        # 创建默认组织
        default_org = Organization(
            id="org_default",
            name="默认组织",
            description="系统默认组织",
            status="active"
        )
        self.db.add(default_org)
        self.stats["organizations"] = 1
        
        logger.info("✅ 组织数据迁移完成")
    
    def migrate_users(self):
        """迁移用户数据"""
        logger.info("👤 迁移用户数据...")
        
        # 创建系统用户
        system_user = User(
            id="system",
            username="system",
            email="system@mekai.ai",
            organization_id="org_default",
            role="admin",
            status="active"
        )
        self.db.add(system_user)
        
        # 创建匿名用户
        anonymous_user = User(
            id="anonymous",
            username="anonymous",
            organization_id="org_default",
            role="guest",
            status="active"
        )
        self.db.add(anonymous_user)
        
        self.stats["users"] = 2
        logger.info("✅ 用户数据迁移完成")
    
    def migrate_employees(self):
        """迁移员工数据"""
        logger.info("🤖 迁移员工数据...")
        
        # 从旧服务导入数据
        try:
            from app.services.employee_service import employee_service
            
            # 获取内存中的员工数据
            old_employees = getattr(employee_service, '_employees', {})
            
            for emp_id, emp_data in old_employees.items():
                employee_record = {
                    "id": emp_data.get("id", emp_id),
                    "name": emp_data.get("name", "未命名员工"),
                    "description": emp_data.get("description", ""),
                    "avatar": emp_data.get("avatar"),
                    "category": emp_data.get("category", []),
                    "tags": emp_data.get("tags", []),
                    "price": str(emp_data.get("price", "0")),
                    "original_price": emp_data.get("original_price"),
                    "trial_count": emp_data.get("trial_count", 0),
                    "hire_count": emp_data.get("hire_count", 0),
                    "is_hired": emp_data.get("is_hired", False),
                    "is_recruited": emp_data.get("is_recruited", False),
                    "status": emp_data.get("status", "draft"),
                    "skills": emp_data.get("skills", []),
                    "knowledge_base_ids": emp_data.get("knowledge_base_ids", []),
                    "industry": emp_data.get("industry"),
                    "role": emp_data.get("role"),
                    "prompt": emp_data.get("prompt"),
                    "model": emp_data.get("model", "deepseek-chat"),
                    "is_hot": emp_data.get("is_hot", False),
                    "personality": emp_data.get("personality"),
                    "welcome_message": emp_data.get("welcome_message"),
                    "created_by": emp_data.get("created_by", "system"),
                    "organization_id": emp_data.get("organization_id", "org_default"),
                    "created_at": emp_data.get("created_at", datetime.utcnow()),
                    "updated_at": emp_data.get("updated_at", datetime.utcnow()),
                }
                
                employee_repository.create(self.db, obj_in=employee_record)
                self.stats["employees"] += 1
            
            logger.info(f"✅ 员工数据迁移完成，共 {self.stats['employees']} 条")
            
        except Exception as e:
            logger.warning(f"⚠️ 员工数据迁移跳过: {str(e)}")
    
    def migrate_knowledge_bases(self):
        """迁移知识库数据"""
        logger.info("📚 迁移知识库数据...")
        
        try:
            from app.services.knowledge.knowledge_service import knowledge_service
            
            # 迁移知识库
            old_kbs = getattr(knowledge_service, '_knowledge_bases', {})
            
            for kb_id, kb_data in old_kbs.items():
                kb_record = {
                    "id": kb_data.get("id", kb_id),
                    "name": kb_data.get("name", "未命名知识库"),
                    "description": kb_data.get("description", ""),
                    "category": kb_data.get("category"),
                    "doc_count": kb_data.get("doc_count", 0),
                    "created_by": kb_data.get("created_by", "system"),
                    "organization_id": kb_data.get("organization_id", "org_default"),
                    "status": kb_data.get("status", "active"),
                    "tags": kb_data.get("tags", []),
                    "is_public": kb_data.get("is_public", True),
                    "vectorized": kb_data.get("vectorized", False),
                    "embedding_model": kb_data.get("embedding_model", "text-embedding-3-small"),
                    "vector_store_path": kb_data.get("vector_store_path"),
                    "settings": kb_data.get("settings", {}),
                    "created_at": kb_data.get("created_at", datetime.utcnow()),
                    "updated_at": kb_data.get("updated_at", datetime.utcnow()),
                }
                
                knowledge_repository.create_kb(self.db, obj_in=kb_record)
                self.stats["knowledge_bases"] += 1
                
                # 迁移知识点
                old_items = getattr(knowledge_service, '_knowledge_items', {}).get(kb_id, [])
                for i, item_data in enumerate(old_items, start=1):
                    item_record = {
                        "id": item_data.get("id", f"{kb_id}_item_{i}"),
                        "knowledge_base_id": kb_id,
                        "serial_no": item_data.get("serial_no", i),
                        "content": item_data.get("content", ""),
                        "word_count": item_data.get("word_count", 0),
                        "source_file": item_data.get("source_file"),
                        "metadata": item_data.get("metadata", {}),
                    }
                    
                    self.db.add(KnowledgeItem(**item_record))
                    self.stats["knowledge_items"] += 1
            
            logger.info(f"✅ 知识库数据迁移完成，共 {self.stats['knowledge_bases']} 个知识库，{self.stats['knowledge_items']} 个知识点")
            
        except Exception as e:
            logger.warning(f"⚠️ 知识库数据迁移跳过: {str(e)}")
    
    def migrate_conversations(self):
        """迁移对话数据"""
        logger.info("💬 迁移对话数据...")
        
        try:
            from app.services.memory.conversation_memory import conversation_memory_manager
            
            # 迁移对话
            old_convs = getattr(conversation_memory_manager, '_conversations', {})
            
            for conv_id, conv_data in old_convs.items():
                conv_record = {
                    "id": conv_data.get("id", conv_id),
                    "employee_id": conv_data.get("employee_id", "unknown"),
                    "user_id": conv_data.get("user_id"),
                    "organization_id": conv_data.get("organization_id", "org_default"),
                    "title": conv_data.get("title", "未命名对话"),
                    "message_count": conv_data.get("message_count", 0),
                    "status": conv_data.get("status", "active"),
                    "metadata": conv_data.get("metadata", {}),
                    "created_at": conv_data.get("created_at", datetime.utcnow()),
                    "updated_at": conv_data.get("updated_at", datetime.utcnow()),
                }
                
                conversation_repository.create_conversation(self.db, obj_in=conv_record)
                self.stats["conversations"] += 1
                
                # 迁移消息
                messages = conv_data.get("messages", [])
                for msg_data in messages:
                    msg_record = {
                        "id": msg_data.get("id", f"{conv_id}_msg_{len(messages)}"),
                        "conversation_id": conv_id,
                        "role": msg_data.get("role", "user"),
                        "content": msg_data.get("content", ""),
                        "token_count": msg_data.get("token_count"),
                        "model": msg_data.get("model"),
                        "metadata": msg_data.get("metadata", {}),
                        "created_at": msg_data.get("created_at", datetime.utcnow()),
                    }
                    
                    self.db.add(Message(**msg_record))
                    self.stats["messages"] += 1
            
            logger.info(f"✅ 对话数据迁移完成，共 {self.stats['conversations']} 个对话，{self.stats['messages']} 条消息")
            
        except Exception as e:
            logger.warning(f"⚠️ 对话数据迁移跳过: {str(e)}")
    
    def print_stats(self):
        """打印迁移统计"""
        logger.info("\n" + "="*60)
        logger.info("📊 数据迁移统计")
        logger.info("="*60)
        for key, value in self.stats.items():
            logger.info(f"  {key}: {value}")
        logger.info("="*60 + "\n")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 MEK-AI 数据迁移工具")
    print("="*60 + "\n")
    
    # 确认
    confirm = input("确认要将数据迁移到MySQL吗？这将清空现有数据 [y/N]: ")
    if confirm.lower() != 'y':
        print("❌ 操作已取消")
        return
    
    # 执行迁移
    migrator = DataMigrator()
    migrator.migrate_all()
    
    print("\n✅ 迁移完成！")


if __name__ == "__main__":
    main()
