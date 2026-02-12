"""
员工数据访问层
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.db.repositories.base import BaseRepository
from app.db.models.employee import Employee


class EmployeeRepository(BaseRepository[Employee]):
    """员工仓库"""
    
    def __init__(self):
        super().__init__(Employee)
    
    def get_by_status(
        self,
        db: Session,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """根据状态获取员工"""
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .order_by(desc(self.model.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_creator(
        self,
        db: Session,
        created_by: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """根据创建者获取员工"""
        return (
            db.query(self.model)
            .filter(self.model.created_by == created_by)
            .order_by(desc(self.model.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_marketplace_employees(
        self,
        db: Session,
        *,
        category: Optional[str] = None,
        industry: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """
        获取市场广场员工列表
        只返回已发布且创建者为system的员工
        """
        query = db.query(self.model).filter(
            self.model.status == "published",
            self.model.created_by == "system"
        )
        
        # 分类过滤
        if category:
            query = query.filter(
                self.model.category.contains(f'"{category}"')
            )
        
        # 行业过滤
        if industry:
            query = query.filter(self.model.industry == industry)
        
        # 价格过滤
        if min_price is not None:
            query = query.filter(
                or_(
                    self.model.price >= str(min_price),
                    self.model.price == "free"
                )
            )
        if max_price is not None:
            query = query.filter(self.model.price <= str(max_price))
        
        # 搜索过滤
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    self.model.name.ilike(search_pattern),
                    self.model.description.ilike(search_pattern),
                    self.model.skills.contains(f'"{search}"')
                )
            )
        
        # 排序：热门优先，然后按雇佣次数
        return (
            query.order_by(
                desc(self.model.is_hot),
                desc(self.model.hire_count),
                desc(self.model.trial_count)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update_hire_status(
        self,
        db: Session,
        employee_id: str,
        is_hired: bool = True
    ) -> Optional[Employee]:
        """更新雇佣状态（不提交事务，由调用者控制）"""
        employee = self.get(db, employee_id)
        if employee:
            employee.is_hired = is_hired
            employee.is_recruited = True
            employee.hire_count += 1
            # 不在这里提交，由调用者统一控制事务
            db.flush()
            db.refresh(employee)
        return employee
    
    def update_trial_count(
        self,
        db: Session,
        employee_id: str
    ) -> Optional[Employee]:
        """增加试用次数"""
        employee = self.get(db, employee_id)
        if employee:
            employee.trial_count += 1
            db.commit()
            db.refresh(employee)
        return employee
    
    def search_by_name(
        self,
        db: Session,
        name: str,
        limit: int = 20
    ) -> List[Employee]:
        """根据名称搜索员工"""
        return (
            db.query(self.model)
            .filter(self.model.name.ilike(f"%{name}%"))
            .limit(limit)
            .all()
        )
    
    def get_by_type(
        self,
        db: Session,
        employee_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """根据员工类型获取员工"""
        return (
            db.query(self.model)
            .filter(self.model.employee_type == employee_type)
            .order_by(desc(self.model.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_system_employees(
        self,
        db: Session,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """
        获取系统级员工列表
        
        Args:
            db: 数据库会话
            status: 状态过滤（可选）
            skip: 跳过数量
            limit: 限制数量
        """
        query = db.query(self.model).filter(self.model.employee_type == "system")
        
        if status:
            query = query.filter(self.model.status == status)
        
        return (
            query.order_by(desc(self.model.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_marketplace_employees_v2(
        self,
        db: Session,
        *,
        category: Optional[str] = None,
        industry: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """
        获取市场广场员工列表（V2版本）
        只返回系统级且已发布的员工
        """
        query = db.query(self.model).filter(
            self.model.employee_type == "system",
            self.model.status == "published"
        )
        
        # 分类过滤
        if category:
            query = query.filter(
                self.model.category.contains(f'"{category}"')
            )
        
        # 行业过滤
        if industry:
            query = query.filter(self.model.industry == industry)
        
        # 价格过滤
        if min_price is not None:
            query = query.filter(
                or_(
                    self.model.price >= str(min_price),
                    self.model.price == "free"
                )
            )
        if max_price is not None:
            query = query.filter(self.model.price <= str(max_price))
        
        # 搜索过滤
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    self.model.name.ilike(search_pattern),
                    self.model.description.ilike(search_pattern),
                    self.model.skills.contains(f'"{search}"')
                )
            )
        
        # 排序：热门优先，然后按雇佣次数
        return (
            query.order_by(
                desc(self.model.is_hot),
                desc(self.model.hire_count),
                desc(self.model.trial_count)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )


# 创建全局实例
employee_repository = EmployeeRepository()
