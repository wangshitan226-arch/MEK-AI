"""
知识库ORM模型
对应SQL: knowledge_bases, knowledge_items, user_knowledge_bases, vector_metadata, documents
"""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.models.base import TimestampMixin


class KnowledgeBase(Base, TimestampMixin):
    """知识库表"""
    
    __tablename__ = "knowledge_bases"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    doc_count = Column(Integer, default=0)
    created_by = Column(String(50), ForeignKey("users.id"))
    organization_id = Column(String(50), ForeignKey("organizations.id"))
    status = Column(String(20), default="active")
    tags = Column(JSON, default=list)
    is_public = Column(Boolean, default=True)
    vectorized = Column(Boolean, default=False)
    embedding_model = Column(String(50), default="text-embedding-3-small")
    vector_store_path = Column(Text)
    settings = Column(JSON, default=dict)
    
    # 关联关系
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_knowledge_bases")
    organization = relationship("Organization", back_populates="knowledge_bases")
    items = relationship("KnowledgeItem", back_populates="knowledge_base", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")
    user_permissions = relationship("UserKnowledgeBase", back_populates="knowledge_base", cascade="all, delete-orphan")
    vector_metadata = relationship("VectorMetadata", back_populates="knowledge_base", cascade="all, delete-orphan")


class KnowledgeItem(Base, TimestampMixin):
    """知识点表"""
    
    __tablename__ = "knowledge_items"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    knowledge_base_id = Column(String(50), ForeignKey("knowledge_bases.id"), nullable=False)
    serial_no = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    source_file = Column(String(255))
    meta_data = Column("metadata", JSON, default=dict)
    
    # 关联关系
    knowledge_base = relationship("KnowledgeBase", back_populates="items")
    vector_metadata = relationship("VectorMetadata", back_populates="knowledge_item", cascade="all, delete-orphan")


class UserKnowledgeBase(Base, TimestampMixin):
    """用户-知识库权限关联表"""
    
    __tablename__ = "user_knowledge_bases"
    
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    knowledge_base_id = Column(String(50), ForeignKey("knowledge_bases.id"), nullable=False)
    permission = Column(String(20), default="read")
    granted_by = Column(String(50))
    
    # 关联关系
    user = relationship("User", back_populates="knowledge_base_permissions")
    knowledge_base = relationship("KnowledgeBase", back_populates="user_permissions")


class VectorMetadata(Base, TimestampMixin):
    """向量存储元数据表"""
    
    __tablename__ = "vector_metadata"
    
    id = Column(String(50), primary_key=True)
    knowledge_base_id = Column(String(50), ForeignKey("knowledge_bases.id"), nullable=False)
    item_id = Column(String(50), ForeignKey("knowledge_items.id"), nullable=False)
    embedding_model = Column(String(50))
    vector_id = Column(String(100))
    chunk_index = Column(Integer, default=0)
    chunk_text = Column(Text)
    meta_data = Column("metadata", JSON, default=dict)
    
    # 关联关系
    knowledge_base = relationship("KnowledgeBase", back_populates="vector_metadata")
    knowledge_item = relationship("KnowledgeItem", back_populates="vector_metadata")


class Document(Base, TimestampMixin):
    """文档表"""
    
    __tablename__ = "documents"
    
    id = Column(String(50), primary_key=True)
    knowledge_base_id = Column(String(50), ForeignKey("knowledge_bases.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(BigInteger)
    mime_type = Column(String(100))
    status = Column(String(20), default="pending")
    parse_result = Column(JSON, default=dict)
    error_message = Column(Text)
    parsed_at = Column(DateTime)
    created_by = Column(String(50))
    
    # 关联关系
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
