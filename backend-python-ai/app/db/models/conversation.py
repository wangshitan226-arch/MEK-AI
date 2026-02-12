"""
对话ORM模型
对应SQL: conversations, messages
"""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.models.base import TimestampMixin


class Conversation(Base, TimestampMixin):
    """对话表"""
    
    __tablename__ = "conversations"
    
    id = Column(String(50), primary_key=True)
    employee_id = Column(String(50), ForeignKey("employees.id"), nullable=False)
    user_id = Column(String(50), ForeignKey("users.id"))
    organization_id = Column(String(50), ForeignKey("organizations.id"))
    title = Column(String(200))
    message_count = Column(Integer, default=0)
    status = Column(String(20), default="active")
    meta_data = Column("metadata", JSON, default=dict)
    
    # 关联关系
    employee = relationship("Employee", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base, TimestampMixin):
    """消息表"""
    
    __tablename__ = "messages"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(50), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer)
    model = Column(String(50))
    meta_data = Column("metadata", JSON, default=dict)
    
    # 关联关系
    conversation = relationship("Conversation", back_populates="messages")
