"""
员工ORM模型
对应SQL: employees
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.models.base import TimestampMixin


class Employee(Base, TimestampMixin):
    """数字员工表"""
    
    __tablename__ = "employees"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    avatar = Column(Text)
    category = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    price = Column(String(20), default="0")
    original_price = Column(Integer)
    trial_count = Column(Integer, default=0)
    hire_count = Column(Integer, default=0)
    is_hired = Column(Boolean, default=False)
    is_recruited = Column(Boolean, default=False)
    status = Column(String(20), default="draft")
    skills = Column(JSON, default=list)
    knowledge_base_ids = Column(JSON, default=list)
    industry = Column(String(50))
    role = Column(String(50))
    prompt = Column(Text)
    model = Column(String(50), default="deepseek-chat")
    model_config = Column(JSON, default=dict)
    is_hot = Column(Boolean, default=False)
    personality = Column(String(500))
    welcome_message = Column(Text)
    created_by = Column(String(50), ForeignKey("users.id"))
    organization_id = Column(String(50), ForeignKey("organizations.id"))
    
    # 员工类型：system-系统级（管理员创建），user-用户级（普通用户创建）
    employee_type = Column(String(20), default="user", index=True)
    # 是否为系统默认员工
    is_system_default = Column(Boolean, default=False, index=True)
    
    # 关联关系
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_employees")
    organization = relationship("Organization", back_populates="employees")
    conversations = relationship("Conversation", back_populates="employee")
    hire_records = relationship("HireRecord", back_populates="employee")
    trial_records = relationship("TrialRecord", back_populates="employee")
