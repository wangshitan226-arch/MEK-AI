"""
对话数据访问层
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.db.repositories.base import BaseRepository
from app.db.models.conversation import Conversation, Message


class ConversationRepository:
    """对话仓库"""
    
    def __init__(self):
        self.conv_repo = BaseRepository(Conversation)
        self.msg_repo = BaseRepository(Message)
    
    # ========== 对话操作 ==========
    
    def get_conversation(
        self,
        db: Session,
        conversation_id: str
    ) -> Optional[Conversation]:
        """获取对话"""
        return self.conv_repo.get(db, conversation_id)
    
    def get_conversations_by_user(
        self,
        db: Session,
        user_id: str,
        employee_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Conversation]:
        """获取用户的对话列表"""
        query = db.query(Conversation).filter(Conversation.user_id == user_id)
        
        if employee_id:
            query = query.filter(Conversation.employee_id == employee_id)
        
        return (
            query.order_by(desc(Conversation.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_conversations_by_employee(
        self,
        db: Session,
        employee_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Conversation]:
        """获取员工的对话列表"""
        return (
            db.query(Conversation)
            .filter(Conversation.employee_id == employee_id)
            .order_by(desc(Conversation.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_conversation(
        self,
        db: Session,
        obj_in: Dict[str, Any]
    ) -> Conversation:
        """创建对话"""
        return self.conv_repo.create(db, obj_in=obj_in)
    
    def update_conversation(
        self,
        db: Session,
        conversation_id: str,
        obj_in: Dict[str, Any]
    ) -> Optional[Conversation]:
        """更新对话"""
        conv = self.get_conversation(db, conversation_id)
        if conv:
            return self.conv_repo.update(db, db_obj=conv, obj_in=obj_in)
        return None
    
    def update_message_count(
        self,
        db: Session,
        conversation_id: str
    ) -> Optional[Conversation]:
        """更新消息计数"""
        conv = self.get_conversation(db, conversation_id)
        if conv:
            count = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).count()
            conv.message_count = count
            db.commit()
            db.refresh(conv)
        return conv
    
    def delete_conversation(
        self,
        db: Session,
        conversation_id: str
    ) -> bool:
        """删除对话（级联删除消息）"""
        conv = self.conv_repo.delete(db, id=conversation_id)
        return conv is not None
    
    # ========== 消息操作 ==========
    
    def get_messages(
        self,
        db: Session,
        conversation_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """获取对话的消息列表"""
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(asc(Message.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_recent_messages(
        self,
        db: Session,
        conversation_id: str,
        limit: int = 10
    ) -> List[Message]:
        """获取最近的消息"""
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .all()
        )[::-1]  # 反转回正序
    
    def create_message(
        self,
        db: Session,
        obj_in: Dict[str, Any]
    ) -> Message:
        """创建消息"""
        message = self.msg_repo.create(db, obj_in=obj_in)
        # 更新对话消息计数
        self.update_message_count(db, message.conversation_id)
        return message
    
    def create_messages(
        self,
        db: Session,
        conversation_id: str,
        messages: List[Dict[str, Any]]
    ) -> List[Message]:
        """批量创建消息"""
        created = []
        for msg_data in messages:
            msg_data["conversation_id"] = conversation_id
            msg = self.msg_repo.create(db, obj_in=msg_data)
            created.append(msg)
        
        # 更新计数
        self.update_message_count(db, conversation_id)
        return created
    
    def get_message_count(
        self,
        db: Session,
        conversation_id: str
    ) -> int:
        """获取消息数量"""
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .count()
        )
    
    def search_conversations(
        self,
        db: Session,
        user_id: str,
        keyword: str,
        limit: int = 20
    ) -> List[Conversation]:
        """
        搜索对话（通过消息内容）
        """
        # 先找到包含关键词的消息
        message_subquery = (
            db.query(Message.conversation_id)
            .filter(Message.content.ilike(f"%{keyword}%"))
            .distinct()
            .subquery()
        )
        
        # 再获取对应的对话
        return (
            db.query(Conversation)
            .filter(
                Conversation.user_id == user_id,
                Conversation.id.in_(message_subquery)
            )
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .all()
        )


# 创建全局实例
conversation_repository = ConversationRepository()
