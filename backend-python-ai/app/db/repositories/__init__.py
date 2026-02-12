"""
数据访问层（Repository模式）
封装数据库操作，提供CRUD接口
"""

from app.db.repositories.employee_repo import EmployeeRepository, employee_repository
from app.db.repositories.knowledge_repo import KnowledgeRepository, knowledge_repository
from app.db.repositories.conversation_repo import ConversationRepository, conversation_repository

__all__ = [
    "EmployeeRepository",
    "employee_repository",
    "KnowledgeRepository",
    "knowledge_repository",
    "ConversationRepository",
    "conversation_repository",
]
