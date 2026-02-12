"""
用户和组织ORM模型
对应SQL: users, organizations
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.models.base import TimestampMixin


class Organization(Base, TimestampMixin):
    """组织表"""
    
    __tablename__ = "organizations"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    logo = Column(Text)
    status = Column(String(20), default="active")
    settings = Column(JSON, default=dict)
    
    # 关联关系
    users = relationship("User", back_populates="organization")
    employees = relationship("Employee", back_populates="organization")
    knowledge_bases = relationship("KnowledgeBase", back_populates="organization")


class User(Base, TimestampMixin):
    """用户表"""
    
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), unique=True)
    phone = Column(String(20), unique=True)
    password_hash = Column(String(255))
    organization_id = Column(String(50), ForeignKey("organizations.id"))
    role = Column(String(20), default="user")
    avatar = Column(Text)
    status = Column(String(20), default="active")
    last_login_at = Column(DateTime)
    settings = Column(JSON, default=dict)
    
    # 关联关系
    organization = relationship("Organization", back_populates="users")
    created_employees = relationship("Employee", foreign_keys="Employee.created_by", back_populates="creator")
    created_knowledge_bases = relationship("KnowledgeBase", foreign_keys="KnowledgeBase.created_by", back_populates="creator")
    conversations = relationship("Conversation", back_populates="user")
    hire_records = relationship("HireRecord", back_populates="user")
    trial_records = relationship("TrialRecord", back_populates="user")
    knowledge_base_permissions = relationship("UserKnowledgeBase", back_populates="user")
