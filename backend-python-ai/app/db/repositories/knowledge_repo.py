"""
知识库数据访问层
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, and_

from app.db.repositories.base import BaseRepository
from app.db.models.knowledge import (
    KnowledgeBase,
    KnowledgeItem,
    UserKnowledgeBase,
    Document,
)


class KnowledgeRepository:
    """知识库仓库（包含多个模型操作）"""
    
    def __init__(self):
        self.kb_repo = BaseRepository(KnowledgeBase)
        self.item_repo = BaseRepository(KnowledgeItem)
        self.doc_repo = BaseRepository(Document)
    
    # ========== 知识库操作 ==========
    
    def get_kb(self, db: Session, kb_id: str) -> Optional[KnowledgeBase]:
        """获取知识库"""
        return self.kb_repo.get(db, kb_id)
    
    def get_kb_by_user(
        self,
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[KnowledgeBase]:
        """获取用户创建的知识库"""
        return (
            db.query(KnowledgeBase)
            .filter(KnowledgeBase.created_by == user_id)
            .order_by(desc(KnowledgeBase.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_public_kbs(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[KnowledgeBase]:
        """获取公开知识库"""
        return (
            db.query(KnowledgeBase)
            .filter(KnowledgeBase.is_public == True)
            .order_by(desc(KnowledgeBase.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_kb(
        self,
        db: Session,
        obj_in: Dict[str, Any]
    ) -> KnowledgeBase:
        """创建知识库"""
        return self.kb_repo.create(db, obj_in=obj_in)
    
    def update_kb(
        self,
        db: Session,
        kb_id: str,
        obj_in: Dict[str, Any]
    ) -> Optional[KnowledgeBase]:
        """更新知识库"""
        kb = self.get_kb(db, kb_id)
        if kb:
            return self.kb_repo.update(db, db_obj=kb, obj_in=obj_in)
        return None
    
    def delete_kb(self, db: Session, kb_id: str) -> bool:
        """删除知识库"""
        kb = self.kb_repo.delete(db, id=kb_id)
        return kb is not None
    
    # ========== 知识点操作 ==========
    
    def get_items_by_kb(
        self,
        db: Session,
        kb_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[KnowledgeItem]:
        """获取知识库的知识点"""
        return (
            db.query(KnowledgeItem)
            .filter(KnowledgeItem.knowledge_base_id == kb_id)
            .order_by(KnowledgeItem.serial_no)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_items(
        self,
        db: Session,
        kb_id: str,
        items: List[Dict[str, Any]]
    ) -> List[KnowledgeItem]:
        """批量创建知识点"""
        created_items = []
        for i, item_data in enumerate(items, start=1):
            item_data["knowledge_base_id"] = kb_id
            if "serial_no" not in item_data:
                item_data["serial_no"] = i
            item = self.item_repo.create(db, obj_in=item_data)
            created_items.append(item)
        
        # 更新知识库文档计数
        kb = self.get_kb(db, kb_id)
        if kb:
            count = db.query(KnowledgeItem).filter(
                KnowledgeItem.knowledge_base_id == kb_id
            ).count()
            kb.doc_count = count
            db.commit()
        
        return created_items
    
    def delete_item(
        self,
        db: Session,
        kb_id: str,
        item_id: str
    ) -> bool:
        """删除知识点"""
        item = self.item_repo.delete(db, id=item_id)
        if item:
            # 更新计数
            kb = self.get_kb(db, kb_id)
            if kb:
                kb.doc_count = max(0, kb.doc_count - 1)
                db.commit()
            return True
        return False
    
    def clear_items(self, db: Session, kb_id: str) -> bool:
        """清空知识库所有知识点"""
        result = db.query(KnowledgeItem).filter(
            KnowledgeItem.knowledge_base_id == kb_id
        ).delete()
        
        # 更新计数
        kb = self.get_kb(db, kb_id)
        if kb:
            kb.doc_count = 0
            db.commit()
        
        return result > 0
    
    # ========== 权限操作 ==========
    
    def check_permission(
        self,
        db: Session,
        kb_id: str,
        user_id: str,
        permission: str = "read"
    ) -> bool:
        """检查用户权限"""
        kb = self.get_kb(db, kb_id)
        if not kb:
            return False
        
        # 公开知识库允许读取
        if permission == "read" and kb.is_public:
            return True
        
        # 创建者有所有权限
        if kb.created_by == user_id:
            return True
        
        # 检查权限表
        user_kb = (
            db.query(UserKnowledgeBase)
            .filter(
                UserKnowledgeBase.knowledge_base_id == kb_id,
                UserKnowledgeBase.user_id == user_id
            )
            .first()
        )
        
        if user_kb:
            if permission == "read":
                return True
            if permission == "write" and user_kb.permission in ["write", "admin"]:
                return True
            if permission == "admin" and user_kb.permission == "admin":
                return True
        
        return False
    
    def grant_permission(
        self,
        db: Session,
        kb_id: str,
        user_id: str,
        permission: str,
        granted_by: str
    ) -> UserKnowledgeBase:
        """授予权限"""
        # 检查是否已存在
        existing = (
            db.query(UserKnowledgeBase)
            .filter(
                UserKnowledgeBase.knowledge_base_id == kb_id,
                UserKnowledgeBase.user_id == user_id
            )
            .first()
        )
        
        if existing:
            existing.permission = permission
            db.commit()
            db.refresh(existing)
            return existing
        
        # 创建新权限记录
        user_kb = UserKnowledgeBase(
            knowledge_base_id=kb_id,
            user_id=user_id,
            permission=permission,
            granted_by=granted_by
        )
        db.add(user_kb)
        db.commit()
        db.refresh(user_kb)
        return user_kb
    
    # ========== 文档操作 ==========
    
    def get_documents_by_kb(
        self,
        db: Session,
        kb_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """获取知识库的文档"""
        return (
            db.query(Document)
            .filter(Document.knowledge_base_id == kb_id)
            .order_by(desc(Document.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_document(
        self,
        db: Session,
        obj_in: Dict[str, Any]
    ) -> Document:
        """创建文档记录"""
        return self.doc_repo.create(db, obj_in=obj_in)
    
    def update_document_status(
        self,
        db: Session,
        doc_id: str,
        status: str,
        parse_result: Optional[Dict] = None,
        error_message: Optional[str] = None
    ) -> Optional[Document]:
        """更新文档状态"""
        doc = self.doc_repo.get(db, doc_id)
        if doc:
            doc.status = status
            if parse_result:
                doc.parse_result = parse_result
            if error_message:
                doc.error_message = error_message
            from datetime import datetime
            doc.parsed_at = datetime.utcnow()
            db.commit()
            db.refresh(doc)
        return doc


# 创建全局实例
knowledge_repository = KnowledgeRepository()
