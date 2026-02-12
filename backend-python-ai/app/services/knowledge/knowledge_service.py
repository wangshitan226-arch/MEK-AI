"""
知识库服务层
处理知识库业务逻辑，协调Repository和向量存储
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.repositories import knowledge_repository
from app.db.models import KnowledgeBase, KnowledgeItem
from app.models.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeItemResponse,
    DocumentUploadConfig,
)
from app.utils.logger import LoggerMixin


class KnowledgeService(LoggerMixin):
    """
    知识库服务
    处理知识库的CRUD操作和业务逻辑
    """
    
    def __init__(self):
        """初始化知识库服务"""
        super().__init__()
        self.repo = knowledge_repository
        self.log_info("知识库服务初始化完成")
    
    async def list_knowledge_bases(
        self,
        db: Session,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        is_public: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[KnowledgeBaseResponse]:
        """
        获取知识库列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID（用于过滤）
            status: 状态过滤
            is_public: 是否公开过滤
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            List[KnowledgeBaseResponse]: 知识库列表
        """
        try:
            # 构建查询
            query = db.query(KnowledgeBase)
            
            # 应用过滤条件
            if user_id:
                # 用户可以看到：自己创建的 + 公开的
                query = query.filter(
                    (KnowledgeBase.created_by == user_id) | 
                    (KnowledgeBase.is_public == True)
                )
            
            if is_public is not None:
                query = query.filter(KnowledgeBase.is_public == is_public)
            
            if status:
                query = query.filter(KnowledgeBase.status == status)
            
            # 排序和分页
            query = query.order_by(KnowledgeBase.updated_at.desc())
            query = query.offset(offset).limit(limit)
            
            # 执行查询
            kbs = query.all()
            
            # 转换为响应模型
            result = []
            for kb in kbs:
                result.append(self._kb_to_response(kb))
            
            self.log_info(f"获取知识库列表: {len(result)} 个")
            return result
            
        except Exception as e:
            self.log_error(f"获取知识库列表失败: {str(e)}", error=e)
            return []
    
    async def get_knowledge_base(
        self,
        db: Session,
        kb_id: str,
        user_id: Optional[str] = None,
    ) -> Optional[KnowledgeBaseResponse]:
        """
        获取知识库详情
        
        Args:
            db: 数据库会话
            kb_id: 知识库ID
            user_id: 用户ID（用于权限检查）
            
        Returns:
            Optional[KnowledgeBaseResponse]: 知识库详情
        """
        try:
            kb = self.repo.get_kb(db, kb_id)
            
            if not kb:
                return None
            
            # 权限检查：非公开且非创建者无法访问
            if not kb.is_public and kb.created_by != user_id:
                return None
            
            return self._kb_to_response(kb)
            
        except Exception as e:
            self.log_error(f"获取知识库详情失败: {str(e)}", error=e)
            return None
    
    async def create_knowledge_base(
        self,
        db: Session,
        kb_data: KnowledgeBaseCreate,
        user_id: str,
        organization_id: Optional[str] = None,
    ) -> Optional[KnowledgeBaseResponse]:
        """
        创建知识库
        
        Args:
            db: 数据库会话
            kb_data: 知识库创建数据
            user_id: 创建者ID
            organization_id: 组织ID
            
        Returns:
            Optional[KnowledgeBaseResponse]: 创建的知识库
        """
        try:
            # 生成ID
            kb_id = f"kb_{uuid.uuid4().hex[:16]}"
            
            # 构建创建数据
            create_data = {
                "id": kb_id,
                "name": kb_data.name,
                "description": kb_data.description or "",
                "created_by": user_id,
                "organization_id": organization_id,
                "is_public": kb_data.is_public if hasattr(kb_data, 'is_public') else False,
                "status": "active",
                "doc_count": 0,
                "vectorized": False,
            }
            
            # 处理标签
            if hasattr(kb_data, 'tags') and kb_data.tags:
                create_data["tags"] = kb_data.tags
            
            # 处理分类
            if hasattr(kb_data, 'category') and kb_data.category:
                create_data["category"] = kb_data.category
            
            # 创建知识库
            kb = self.repo.create_kb(db, create_data)
            
            self.log_info(f"创建知识库成功: {kb_id}, 名称: {kb_data.name}")
            
            return self._kb_to_response(kb)
            
        except Exception as e:
            self.log_error(f"创建知识库失败: {str(e)}", error=e)
            return None
    
    async def update_knowledge_base(
        self,
        db: Session,
        kb_id: str,
        update_data: KnowledgeBaseUpdate,
        user_id: str,
    ) -> Optional[KnowledgeBaseResponse]:
        """
        更新知识库
        
        Args:
            db: 数据库会话
            kb_id: 知识库ID
            update_data: 更新数据
            user_id: 用户ID（用于权限检查）
            
        Returns:
            Optional[KnowledgeBaseResponse]: 更新后的知识库
        """
        try:
            # 获取知识库
            kb = self.repo.get_kb(db, kb_id)
            
            if not kb:
                return None
            
            # 权限检查：只有创建者可以更新
            if kb.created_by != user_id:
                self.log_warning(f"用户 {user_id} 尝试更新知识库 {kb_id}，但无权限")
                return None
            
            # 构建更新数据
            update_dict = {}
            if hasattr(update_data, 'name') and update_data.name is not None:
                update_dict["name"] = update_data.name
            if hasattr(update_data, 'description') and update_data.description is not None:
                update_dict["description"] = update_data.description
            if hasattr(update_data, 'is_public') and update_data.is_public is not None:
                update_dict["is_public"] = update_data.is_public
            if hasattr(update_data, 'tags') and update_data.tags is not None:
                update_dict["tags"] = update_data.tags
            if hasattr(update_data, 'category') and update_data.category is not None:
                update_dict["category"] = update_data.category
            if hasattr(update_data, 'status') and update_data.status is not None:
                update_dict["status"] = update_data.status
            
            # 更新时间
            update_dict["updated_at"] = datetime.utcnow()
            
            # 执行更新
            updated_kb = self.repo.update_kb(db, kb_id, update_dict)
            
            if updated_kb:
                self.log_info(f"更新知识库成功: {kb_id}")
                return self._kb_to_response(updated_kb)
            
            return None
            
        except Exception as e:
            self.log_error(f"更新知识库失败: {str(e)}", error=e)
            return None
    
    async def delete_knowledge_base(
        self,
        db: Session,
        kb_id: str,
        user_id: str,
    ) -> bool:
        """
        删除知识库
        
        Args:
            db: 数据库会话
            kb_id: 知识库ID
            user_id: 用户ID（用于权限检查）
            
        Returns:
            bool: 是否成功删除
        """
        try:
            # 获取知识库
            kb = self.repo.get_kb(db, kb_id)
            
            if not kb:
                return False
            
            # 权限检查：只有创建者可以删除
            if kb.created_by != user_id:
                self.log_warning(f"用户 {user_id} 尝试删除知识库 {kb_id}，但无权限")
                return False
            
            # 删除知识库（关联的知识点会被级联删除）
            success = self.repo.delete_kb(db, kb_id)
            
            if success:
                self.log_info(f"删除知识库成功: {kb_id}")
            
            return success
            
        except Exception as e:
            self.log_error(f"删除知识库失败: {str(e)}", error=e)
            return False
    
    async def get_knowledge_items(
        self,
        db: Session,
        kb_id: str,
        user_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[KnowledgeItemResponse]:
        """
        获取知识库的知识点列表
        
        Args:
            db: 数据库会话
            kb_id: 知识库ID
            user_id: 用户ID（用于权限检查）
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            List[KnowledgeItemResponse]: 知识点列表
        """
        try:
            # 权限检查
            kb = self.repo.get_kb(db, kb_id)
            if not kb:
                return []
            
            if not kb.is_public and kb.created_by != user_id:
                return []
            
            # 获取知识点
            items = self.repo.get_items_by_kb(db, kb_id, skip=offset, limit=limit)
            
            # 转换为响应模型
            result = []
            for item in items:
                result.append(self._item_to_response(item))
            
            return result
            
        except Exception as e:
            self.log_error(f"获取知识点列表失败: {str(e)}", error=e)
            return []
    
    async def add_knowledge_items(
        self,
        db: Session,
        kb_id: str,
        items: List[Dict[str, Any]],
        user_id: str,
    ) -> bool:
        """
        添加知识点到知识库
        
        Args:
            db: 数据库会话
            kb_id: 知识库ID
            items: 知识点列表
            user_id: 用户ID（用于权限检查）
            
        Returns:
            bool: 是否成功添加
        """
        try:
            # 权限检查
            kb = self.repo.get_kb(db, kb_id)
            if not kb:
                return False
            
            if kb.created_by != user_id:
                self.log_warning(f"用户 {user_id} 尝试向知识库 {kb_id} 添加知识点，但无权限")
                return False
            
            # 添加知识点
            created_items = self.repo.create_items(db, kb_id, items)
            
            self.log_info(f"添加知识点成功: 知识库 {kb_id}, 数量 {len(created_items)}")
            
            return True
            
        except Exception as e:
            self.log_error(f"添加知识点失败: {str(e)}", error=e)
            return False
    
    async def delete_knowledge_item(
        self,
        db: Session,
        kb_id: str,
        item_id: str,
        user_id: str,
    ) -> bool:
        """
        删除知识点
        
        Args:
            db: 数据库会话
            kb_id: 知识库ID
            item_id: 知识点ID
            user_id: 用户ID（用于权限检查）
            
        Returns:
            bool: 是否成功删除
        """
        try:
            # 权限检查
            kb = self.repo.get_kb(db, kb_id)
            if not kb:
                return False
            
            if kb.created_by != user_id:
                return False
            
            # 删除知识点
            success = self.repo.delete_item(db, kb_id, item_id)
            
            return success
            
        except Exception as e:
            self.log_error(f"删除知识点失败: {str(e)}", error=e)
            return False
    
    async def clear_knowledge_items(
        self,
        db: Session,
        kb_id: str,
        user_id: str,
    ) -> bool:
        """
        清空知识库的所有知识点
        
        Args:
            db: 数据库会话
            kb_id: 知识库ID
            user_id: 用户ID（用于权限检查）
            
        Returns:
            bool: 是否成功清空
        """
        try:
            # 权限检查
            kb = self.repo.get_kb(db, kb_id)
            if not kb:
                return False
            
            if kb.created_by != user_id:
                return False
            
            # 清空知识点
            success = self.repo.clear_items(db, kb_id)
            
            return success
            
        except Exception as e:
            self.log_error(f"清空知识库失败: {str(e)}", error=e)
            return False
    
    async def update_vectorized_status(
        self,
        db: Session,
        kb_id: str,
        vectorized: bool = True,
    ) -> bool:
        """
        更新知识库的向量化状态
        
        Args:
            db: 数据库会话
            kb_id: 知识库ID
            vectorized: 向量化状态
            
        Returns:
            bool: 是否成功更新
        """
        try:
            updated = self.repo.update_kb(db, kb_id, {"vectorized": vectorized})
            return updated is not None
            
        except Exception as e:
            self.log_error(f"更新向量化状态失败: {str(e)}", error=e)
            return False
    
    async def get_document_config(self) -> DocumentUploadConfig:
        """
        获取文档处理配置
        
        Returns:
            DocumentUploadConfig: 文档处理配置
        """
        return DocumentUploadConfig(
            knowledge_length=1000,
            overlap_length=200,
            line_break_segment=True,
        )
    
    def _kb_to_response(self, kb: KnowledgeBase) -> KnowledgeBaseResponse:
        """将KnowledgeBase模型转换为响应模型"""
        return KnowledgeBaseResponse(
            id=kb.id,
            name=kb.name,
            description=kb.description or "",
            created_by=kb.created_by,
            is_public=kb.is_public,
            status=kb.status,
            doc_count=kb.doc_count,
            vectorized=kb.vectorized,
            tags=kb.tags or [],
            category=kb.category or "",
            created_at=kb.created_at,
            updated_at=kb.updated_at,
        )
    
    def _item_to_response(self, item: KnowledgeItem) -> KnowledgeItemResponse:
        """将KnowledgeItem模型转换为响应模型"""
        return KnowledgeItemResponse(
            id=item.id,
            knowledge_base_id=item.knowledge_base_id,
            serial_no=item.serial_no,
            content=item.content,
            word_count=item.word_count,
            create_time=item.created_at,
            source_file=item.source_file or "",
            embeddings=None,
            metadata=item.meta_data or {},
        )


# 创建全局实例
knowledge_service = KnowledgeService()
