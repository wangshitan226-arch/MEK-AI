"""
基础模型类
提供通用字段和方法
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declared_attr

from app.db.database import Base


class BaseModel(Base):
    """
    基础模型类
    所有ORM模型都应继承此类
    """
    
    __abstract__ = True
    
    # 主键ID
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    @declared_attr
    def __tablename__(cls):
        """自动生成表名"""
        return cls.__name__.lower()
    
    def to_dict(self) -> dict:
        """
        转换为字典
        
        Returns:
            dict: 模型数据字典
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def update(self, **kwargs):
        """
        更新字段
        
        Args:
            **kwargs: 要更新的字段
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class TimestampMixin:
    """
    时间戳混入类
    提供创建时间和更新时间字段
    """
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MetadataMixin:
    """
    元数据混入类
    提供metadata JSON字段
    """
    
    meta_data = Column("metadata", JSON, default=dict)
