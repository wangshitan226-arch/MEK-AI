"""
ORM模型模块
"""

from app.db.models.base import BaseModel, TimestampMixin
from app.db.models.user import User, Organization
from app.db.models.employee import Employee
from app.db.models.knowledge import KnowledgeBase, KnowledgeItem, UserKnowledgeBase, VectorMetadata, Document
from app.db.models.conversation import Conversation, Message
from app.db.models.record import HireRecord, TrialRecord

__all__ = [
    # 基础
    "BaseModel",
    "TimestampMixin",
    # 用户/组织
    "User",
    "Organization",
    # 员工
    "Employee",
    # 知识库
    "KnowledgeBase",
    "KnowledgeItem",
    "UserKnowledgeBase",
    "VectorMetadata",
    "Document",
    # 对话
    "Conversation",
    "Message",
    # 记录
    "HireRecord",
    "TrialRecord",
]
