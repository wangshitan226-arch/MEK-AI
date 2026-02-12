"""
雇佣和试用记录ORM模型
对应SQL: hire_records, trial_records
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.models.base import TimestampMixin


class HireRecord(Base, TimestampMixin):
    """雇佣记录表"""
    
    __tablename__ = "hire_records"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(50), ForeignKey("employees.id"), nullable=False)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    organization_id = Column(String(50), ForeignKey("organizations.id"))
    hired_at = Column(DateTime, default=datetime.utcnow)
    expired_at = Column(DateTime)
    status = Column(String(20), default="active")
    settings = Column(JSON, default=dict)
    
    # 关联关系
    employee = relationship("Employee", back_populates="hire_records")
    user = relationship("User", back_populates="hire_records")


class TrialRecord(Base, TimestampMixin):
    """试用记录表"""
    
    __tablename__ = "trial_records"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(50), ForeignKey("employees.id"), nullable=False)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    organization_id = Column(String(50), ForeignKey("organizations.id"))
    trialed_at = Column(DateTime, default=datetime.utcnow)
    feedback = Column(Text)
    rating = Column(Integer)
    
    # 关联关系
    employee = relationship("Employee", back_populates="trial_records")
    user = relationship("User", back_populates="trial_records")
