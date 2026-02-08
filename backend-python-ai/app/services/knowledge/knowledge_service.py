"""
知识库管理服务 - 内存存储版本（预留用户权限字段）
处理知识库的CRUD、文档管理
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.models.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeItemResponse,
    DocumentUploadConfig,
)


class KnowledgeService(LoggerMixin):
    """
    知识库管理服务
    使用内存存储，预留用户权限字段便于后续迁移到数据库
    """
    
    def __init__(self):
        """初始化知识库服务"""
        super().__init__()
        
        # 内存存储
        self._knowledge_bases: Dict[str, Dict[str, Any]] = {}
        self._knowledge_items: Dict[str, List[Dict[str, Any]]] = {}
        
        # 用户-知识库关联表（预留，用于权限控制）
        self._user_knowledge_bases: Dict[str, List[str]] = {}
        
        # 初始化示例数据
        self._init_sample_data()
        
        self.log_info("知识库服务初始化完成")
    
    def _init_sample_data(self):
        """初始化示例数据"""
        sample_kbs = [
            {
                "id": "kb1",
                "name": "企业AI战略报告",
                "description": "包含企业AI战略规划、实施路径和案例分析",
                "doc_count": 9,
                "created_by": "admin",
                "created_at": datetime(2024, 1, 15, 10, 30, 0),
                "updated_at": datetime(2024, 2, 1, 14, 20, 0),
                "status": "active",
                "tags": ["战略", "AI", "企业规划"],
                "is_public": True,
                "vectorized": True,
                "category": "战略文档",
                # 预留权限字段
                "owner_id": "admin",
                "organization_id": None,
                "permissions": {"read": ["*"], "write": ["admin"]},
            },
            {
                "id": "kb2",
                "name": "产品需求文档",
                "description": "各版本产品需求文档和用户反馈",
                "doc_count": 4,
                "created_by": "product-manager",
                "created_at": datetime(2024, 1, 20, 9, 15, 0),
                "updated_at": datetime(2024, 1, 28, 16, 45, 0),
                "status": "active",
                "tags": ["PRD", "需求", "用户反馈"],
                "is_public": False,
                "vectorized": True,
                "category": "产品文档",
                # 预留权限字段
                "owner_id": "product-manager",
                "organization_id": None,
                "permissions": {"read": ["product-manager", "admin"], "write": ["product-manager"]},
            },
            {
                "id": "kb3",
                "name": "技术架构设计",
                "description": "系统架构、技术选型和设计文档",
                "doc_count": 7,
                "created_by": "tech-lead",
                "created_at": datetime(2024, 1, 25, 13, 0, 0),
                "updated_at": datetime(2024, 1, 31, 11, 30, 0),
                "status": "active",
                "tags": ["架构", "技术", "设计"],
                "is_public": True,
                "vectorized": False,
                "category": "技术文档",
                # 预留权限字段
                "owner_id": "tech-lead",
                "organization_id": None,
                "permissions": {"read": ["*"], "write": ["tech-lead", "admin"]},
            },
        ]
        
        for kb in sample_kbs:
            self._knowledge_bases[kb["id"]] = kb
            self._knowledge_items[kb["id"]] = []
        
        # 添加示例知识点
        sample_items = [
            {
                "id": "ki-001",
                "knowledge_base_id": "kb1",
                "serial_no": 1,
                "content": "人工智能（Artificial Intelligence，AI）是一门旨在使计算机系统能够模拟、延伸和扩展人类智能的技术科学。",
                "word_count": 128,
                "create_time": datetime(2024, 2, 1, 22, 32, 0),
                "source_file": "AI战略报告.pdf",
                "metadata": {"section": "第一章", "page": 1, "confidence": 0.95},
            },
        ]
        
        for item in sample_items:
            kb_id = item["knowledge_base_id"]
            if kb_id in self._knowledge_items:
                self._knowledge_items[kb_id].append(item)
    
    # ========== 权限检查方法（预留） ==========
    
    def _check_permission(
        self,
        kb_id: str,
        user_id: str,
        permission: str = "read"
    ) -> bool:
        """
        检查用户权限（预留方法）
        
        Args:
            kb_id: 知识库ID
            user_id: 用户ID
            permission: 权限类型（read/write/delete）
            
        Returns:
            bool: 是否有权限
        """
        kb = self._knowledge_bases.get(kb_id)
        if not kb:
            return False
        
        # 公开知识库允许读取
        if permission == "read" and kb.get("is_public", True):
            return True
        
        # 创建者有所有权限
        if kb.get("created_by") == user_id:
            return True
        
        # 检查权限配置
        permissions = kb.get("permissions", {})
        allowed_users = permissions.get(permission, [])
        
        if "*" in allowed_users:  # 通配符表示所有用户
            return True
        
        return user_id in allowed_users
    
    def _filter_by_permission(
        self,
        kbs: List[Dict[str, Any]],
        user_id: str,
        permission: str = "read"
    ) -> List[Dict[str, Any]]:
        """
        根据权限过滤知识库列表
        
        Args:
            kbs: 知识库列表
            user_id: 用户ID
            permission: 权限类型
            
        Returns:
            List[Dict]: 过滤后的列表
        """
        result = []
        for kb in kbs:
            kb_id = kb.get("id")
            if self._check_permission(kb_id, user_id, permission):
                result.append(kb)
        return result
    
    # ========== 知识库CRUD ==========
    
    async def create_knowledge_base(
        self,
        kb_data: KnowledgeBaseCreate,
        user_id: str,
        organization_id: Optional[str] = None,
    ) -> Optional[KnowledgeBaseResponse]:
        """
        创建知识库
        
        Args:
            kb_data: 知识库数据
            user_id: 创建者ID（预留权限字段）
            organization_id: 组织ID（预留权限字段）
            
        Returns:
            Optional[KnowledgeBaseResponse]: 创建的知识库
        """
        try:
            kb_id = f"kb_{uuid.uuid4().hex[:8]}"
            now = datetime.now()
            
            kb_record = {
                "id": kb_id,
                "name": kb_data.name,
                "description": kb_data.description or "",
                "doc_count": 0,
                "created_by": user_id,
                "created_at": now,
                "updated_at": now,
                "status": "active",
                "tags": kb_data.tags or [],
                "is_public": kb_data.is_public,
                "vectorized": False,
                "category": kb_data.category,
                # 预留权限字段
                "owner_id": user_id,
                "organization_id": organization_id,
                "permissions": {
                    "read": ["*"] if kb_data.is_public else [user_id],
                    "write": [user_id],
                    "delete": [user_id],
                },
            }
            
            self._knowledge_bases[kb_id] = kb_record
            self._knowledge_items[kb_id] = []
            
            # 更新用户-知识库关联
            if user_id not in self._user_knowledge_bases:
                self._user_knowledge_bases[user_id] = []
            self._user_knowledge_bases[user_id].append(kb_id)
            
            self.log_info(f"创建知识库成功: {kb_id}, 名称: {kb_data.name}")
            
            return KnowledgeBaseResponse(**kb_record)
            
        except Exception as e:
            self.log_error(f"创建知识库失败: {str(e)}", error=e)
            return None
    
    async def get_knowledge_base(
        self,
        kb_id: str,
        user_id: Optional[str] = None,
    ) -> Optional[KnowledgeBaseResponse]:
        """
        获取知识库详情
        
        Args:
            kb_id: 知识库ID
            user_id: 用户ID（用于权限检查）
            
        Returns:
            Optional[KnowledgeBaseResponse]: 知识库信息
        """
        kb = self._knowledge_bases.get(kb_id)
        if not kb:
            return None
        
        # 权限检查
        if user_id and not self._check_permission(kb_id, user_id, "read"):
            self.log_warning(f"权限拒绝: 用户 {user_id} 尝试访问知识库 {kb_id}")
            return None
        
        return KnowledgeBaseResponse(**kb)
    
    async def update_knowledge_base(
        self,
        kb_id: str,
        update_data: KnowledgeBaseUpdate,
        user_id: str,
    ) -> Optional[KnowledgeBaseResponse]:
        """
        更新知识库
        
        Args:
            kb_id: 知识库ID
            update_data: 更新数据
            user_id: 用户ID（用于权限检查）
            
        Returns:
            Optional[KnowledgeBaseResponse]: 更新后的知识库
        """
        kb = self._knowledge_bases.get(kb_id)
        if not kb:
            return None
        
        # 权限检查
        if not self._check_permission(kb_id, user_id, "write"):
            self.log_warning(f"权限拒绝: 用户 {user_id} 尝试更新知识库 {kb_id}")
            return None
        
        try:
            # 应用更新
            update_dict = update_data.dict(exclude_unset=True)
            for key, value in update_dict.items():
                if value is not None:
                    kb[key] = value
            
            kb["updated_at"] = datetime.now()
            
            self.log_info(f"更新知识库成功: {kb_id}")
            
            return KnowledgeBaseResponse(**kb)
            
        except Exception as e:
            self.log_error(f"更新知识库失败: {str(e)}", error=e)
            return None
    
    async def delete_knowledge_base(
        self,
        kb_id: str,
        user_id: str,
    ) -> bool:
        """
        删除知识库
        
        Args:
            kb_id: 知识库ID
            user_id: 用户ID（用于权限检查）
            
        Returns:
            bool: 是否成功
        """
        kb = self._knowledge_bases.get(kb_id)
        if not kb:
            return False
        
        # 权限检查
        if not self._check_permission(kb_id, user_id, "delete"):
            self.log_warning(f"权限拒绝: 用户 {user_id} 尝试删除知识库 {kb_id}")
            return False
        
        try:
            # 删除知识库
            del self._knowledge_bases[kb_id]
            if kb_id in self._knowledge_items:
                del self._knowledge_items[kb_id]
            
            # 更新用户-知识库关联
            if user_id in self._user_knowledge_bases:
                if kb_id in self._user_knowledge_bases[user_id]:
                    self._user_knowledge_bases[user_id].remove(kb_id)
            
            self.log_info(f"删除知识库成功: {kb_id}")
            return True
            
        except Exception as e:
            self.log_error(f"删除知识库失败: {str(e)}", error=e)
            return False
    
    async def list_knowledge_bases(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        is_public: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[KnowledgeBaseResponse]:
        """
        列出知识库
        
        Args:
            user_id: 用户ID（用于权限过滤）
            status: 状态过滤
            is_public: 是否公开过滤
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[KnowledgeBaseResponse]: 知识库列表
        """
        try:
            filtered_kbs = []
            
            for kb_id, kb_data in self._knowledge_bases.items():
                # 状态过滤
                if status and kb_data.get("status") != status:
                    continue
                
                # 公开状态过滤
                if is_public is not None and kb_data.get("is_public") != is_public:
                    continue
                
                filtered_kbs.append(kb_data)
            
            # 权限过滤
            if user_id:
                filtered_kbs = self._filter_by_permission(filtered_kbs, user_id, "read")
            
            # 按更新时间倒序排序
            filtered_kbs.sort(key=lambda x: x.get("updated_at", datetime.min), reverse=True)
            
            # 分页
            paginated = filtered_kbs[offset:offset + limit]
            
            return [KnowledgeBaseResponse(**kb) for kb in paginated]
            
        except Exception as e:
            self.log_error(f"列出知识库失败: {str(e)}", error=e)
            return []
    
    # ========== 知识点管理 ==========
    
    async def add_knowledge_items(
        self,
        kb_id: str,
        items: List[Dict[str, Any]],
        user_id: str,
    ) -> bool:
        """
        添加知识点
        
        Args:
            kb_id: 知识库ID
            items: 知识点列表
            user_id: 用户ID（用于权限检查）
            
        Returns:
            bool: 是否成功
        """
        if kb_id not in self._knowledge_bases:
            return False
        
        # 权限检查
        if not self._check_permission(kb_id, user_id, "write"):
            self.log_warning(f"权限拒绝: 用户 {user_id} 尝试添加知识点到 {kb_id}")
            return False
        
        try:
            kb = self._knowledge_bases[kb_id]
            
            for i, item_data in enumerate(items, start=len(self._knowledge_items.get(kb_id, [])) + 1):
                item_id = f"ki_{uuid.uuid4().hex[:8]}"
                
                item = {
                    "id": item_id,
                    "knowledge_base_id": kb_id,
                    "serial_no": item_data.get("serial_no", i),
                    "content": item_data.get("content", ""),
                    "word_count": len(item_data.get("content", "")),
                    "create_time": datetime.now(),
                    "source_file": item_data.get("source_file"),
                    "metadata": item_data.get("metadata", {}),
                }
                
                if kb_id not in self._knowledge_items:
                    self._knowledge_items[kb_id] = []
                
                self._knowledge_items[kb_id].append(item)
            
            # 更新文档计数
            kb["doc_count"] = len(self._knowledge_items[kb_id])
            kb["updated_at"] = datetime.now()
            
            self.log_info(f"添加知识点成功: 知识库={kb_id}, 数量={len(items)}")
            return True
            
        except Exception as e:
            self.log_error(f"添加知识点失败: {str(e)}", error=e)
            return False
    
    async def get_knowledge_items(
        self,
        kb_id: str,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[KnowledgeItemResponse]:
        """
        获取知识点列表
        
        Args:
            kb_id: 知识库ID
            user_id: 用户ID（用于权限检查）
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[KnowledgeItemResponse]: 知识点列表
        """
        if kb_id not in self._knowledge_bases:
            return []
        
        # 权限检查
        if user_id and not self._check_permission(kb_id, user_id, "read"):
            self.log_warning(f"权限拒绝: 用户 {user_id} 尝试获取知识点 {kb_id}")
            return []
        
        items = self._knowledge_items.get(kb_id, [])
        
        # 按序号排序
        items.sort(key=lambda x: x.get("serial_no", 0))
        
        # 分页
        paginated = items[offset:offset + limit]
        
        return [KnowledgeItemResponse(**item) for item in paginated]
    
    async def delete_knowledge_item(
        self,
        kb_id: str,
        item_id: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        删除单个知识点
        
        Args:
            kb_id: 知识库ID
            item_id: 知识点ID
            user_id: 用户ID（用于权限检查）
            
        Returns:
            bool: 是否删除成功
        """
        if kb_id not in self._knowledge_bases:
            return False
        
        # 权限检查
        if user_id and not self._check_permission(kb_id, user_id, "delete"):
            self.log_warning(f"权限拒绝: 用户 {user_id} 尝试删除知识点 {item_id}")
            return False
        
        items = self._knowledge_items.get(kb_id, [])
        original_count = len(items)
        
        # 过滤掉要删除的知识点
        self._knowledge_items[kb_id] = [
            item for item in items 
            if item.get("id") != item_id
        ]
        
        deleted = len(self._knowledge_items[kb_id]) < original_count
        
        if deleted:
            # 更新知识库文档计数
            self._knowledge_bases[kb_id]["doc_count"] = len(self._knowledge_items[kb_id])
            self._knowledge_bases[kb_id]["updated_at"] = datetime.now()
            self.log_info(f"删除知识点成功: {item_id} from {kb_id}")
        
        return deleted
    
    async def clear_knowledge_items(
        self,
        kb_id: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        清空知识库所有知识点
        
        Args:
            kb_id: 知识库ID
            user_id: 用户ID（用于权限检查）
            
        Returns:
            bool: 是否清空成功
        """
        if kb_id not in self._knowledge_bases:
            return False
        
        # 权限检查
        if user_id and not self._check_permission(kb_id, user_id, "delete"):
            self.log_warning(f"权限拒绝: 用户 {user_id} 尝试清空知识库 {kb_id}")
            return False
        
        # 清空知识点
        self._knowledge_items[kb_id] = []
        
        # 更新知识库文档计数
        self._knowledge_bases[kb_id]["doc_count"] = 0
        self._knowledge_bases[kb_id]["updated_at"] = datetime.now()
        
        self.log_info(f"清空知识库成功: {kb_id}")
        return True
    
    # ========== 配置管理 ==========
    
    async def get_document_config(self) -> DocumentUploadConfig:
        """获取默认文档处理配置"""
        return DocumentUploadConfig(
            file_type="text",
            knowledge_length=2000,
            overlap_length=30,
            line_break_segment=True,
            max_segment_length=500,
        )
    
    async def update_vectorized_status(
        self,
        kb_id: str,
        vectorized: bool,
    ) -> bool:
        """更新知识库向量化状态"""
        if kb_id not in self._knowledge_bases:
            return False
        
        self._knowledge_bases[kb_id]["vectorized"] = vectorized
        self._knowledge_bases[kb_id]["updated_at"] = datetime.now()
        
        return True


# 创建全局实例
knowledge_service = KnowledgeService()
