"""
基础仓库类
提供通用CRUD操作
"""

from typing import TypeVar, Generic, Type, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    基础仓库类
    所有具体仓库都应继承此类
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        初始化仓库
        
        Args:
            model: SQLAlchemy模型类
        """
        self.model = model
    
    def get(self, db: Session, id: str) -> Optional[ModelType]:
        """
        根据ID获取记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            Optional[ModelType]: 记录对象或None
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        desc_order: bool = True
    ) -> List[ModelType]:
        """
        获取多条记录
        
        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 返回数量限制
            order_by: 排序字段
            desc_order: 是否降序
            
        Returns:
            List[ModelType]: 记录列表
        """
        query = db.query(self.model)
        
        if order_by:
            order_column = getattr(self.model, order_by)
            if desc_order:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: Dict[str, Any]) -> ModelType:
        """
        创建记录
        
        Args:
            db: 数据库会话
            obj_in: 创建数据
            
        Returns:
            ModelType: 创建的记录
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """
        更新记录
        
        Args:
            db: 数据库会话
            db_obj: 数据库对象
            obj_in: 更新数据
            
        Returns:
            ModelType: 更新后的记录
        """
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, id: str) -> Optional[ModelType]:
        """
        删除记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            Optional[ModelType]: 删除的记录或None
        """
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def count(self, db: Session) -> int:
        """
        获取记录总数
        
        Args:
            db: 数据库会话
            
        Returns:
            int: 记录总数
        """
        return db.query(self.model).count()
