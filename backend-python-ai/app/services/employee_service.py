"""
员工管理服务
处理数字员工的业务逻辑 - MySQL版本
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.utils.logger import LoggerMixin
from app.models.schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.db.repositories import employee_repository
from app.db.models import Employee


class EmployeeService(LoggerMixin):
    """
    员工管理服务
    处理员工的创建、读取、更新、删除等业务逻辑
    """
    
    def __init__(self):
        """初始化员工服务"""
        super().__init__()
        self.log_info("员工服务初始化完成 (MySQL模式)")
    
    def _employee_to_response(self, employee: Employee) -> EmployeeResponse:
        """将ORM模型转换为响应模型"""
        return EmployeeResponse(
            id=employee.id,
            name=employee.name,
            description=employee.description or "",
            avatar=employee.avatar,
            category=employee.category or [],
            tags=employee.tags or [],
            price=employee.price,
            original_price=employee.original_price,
            trial_count=employee.trial_count,
            hire_count=employee.hire_count,
            is_hired=employee.is_hired,
            is_recruited=employee.is_recruited,
            status=employee.status,
            skills=employee.skills or [],
            knowledge_base_ids=employee.knowledge_base_ids or [],
            industry=employee.industry,
            role=employee.role,
            prompt=employee.prompt,
            model=employee.model,
            is_hot=employee.is_hot,
            created_by=employee.created_by,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
        )
    
    def create_employee(
        self,
        db: Session,
        employee_data: EmployeeCreate,
        created_by: str
    ) -> EmployeeResponse:
        """
        创建新员工
        
        Args:
            db: 数据库会话
            employee_data: 员工数据
            created_by: 创建者ID
            
        Returns:
            EmployeeResponse: 创建的员工响应
        """
        try:
            # 生成员工ID
            employee_id = f"emp_{str(uuid.uuid4())[:8]}"
            
            now = datetime.utcnow()
            
            # 创建员工记录
            employee_record = {
                "id": employee_id,
                "name": employee_data.name,
                "description": employee_data.description,
                "avatar": employee_data.avatar,
                "category": employee_data.category or [],
                "tags": employee_data.tags or [],
                "price": str(employee_data.price) if employee_data.price else "0",
                "skills": employee_data.skills or [],
                "industry": employee_data.industry,
                "role": employee_data.role,
                "prompt": employee_data.prompt,
                "model": employee_data.model or "deepseek-chat",
                "knowledge_base_ids": employee_data.knowledge_base_ids or [],
                "trial_count": 0,
                "hire_count": 0,
                "is_hired": False,
                "is_recruited": False,
                "status": "draft",
                "created_by": created_by,
                "created_at": now,
                "updated_at": now,
                "is_hot": False,
            }
            
            # 保存到数据库
            employee = employee_repository.create(db, obj_in=employee_record)
            
            self.log_info(f"创建员工成功: {employee_id}, 名称: {employee_data.name}")
            
            return self._employee_to_response(employee)
            
        except Exception as e:
            self.log_error(f"创建员工失败: {str(e)}", error=e)
            raise
    
    def get_employee(
        self,
        db: Session,
        employee_id: str
    ) -> Optional[EmployeeResponse]:
        """
        获取员工详情
        
        Args:
            db: 数据库会话
            employee_id: 员工ID
            
        Returns:
            Optional[EmployeeResponse]: 员工信息，如果不存在则返回None
        """
        employee = employee_repository.get(db, employee_id)
        if not employee:
            self.log_warning(f"员工不存在: {employee_id}")
            return None
        
        return self._employee_to_response(employee)
    
    def update_employee(
        self,
        db: Session,
        employee_id: str,
        update_data: EmployeeUpdate
    ) -> Optional[EmployeeResponse]:
        """
        更新员工信息
        
        Args:
            db: 数据库会话
            employee_id: 员工ID
            update_data: 更新数据
            
        Returns:
            Optional[EmployeeResponse]: 更新后的员工信息，如果不存在则返回None
        """
        employee = employee_repository.get(db, employee_id)
        if not employee:
            self.log_warning(f"员工不存在，无法更新: {employee_id}")
            return None
        
        try:
            # 应用更新（只更新提供的字段）
            update_dict = update_data.dict(exclude_unset=True)
            
            # 处理price字段，确保转为字符串
            if "price" in update_dict and update_dict["price"] is not None:
                update_dict["price"] = str(update_dict["price"])
            
            update_dict["updated_at"] = datetime.utcnow()
            
            employee = employee_repository.update(
                db, db_obj=employee, obj_in=update_dict
            )
            
            self.log_info(f"更新员工成功: {employee_id}")
            
            return self._employee_to_response(employee)
            
        except Exception as e:
            self.log_error(f"更新员工失败: {employee_id}, 错误: {str(e)}", error=e)
            return None
    
    def delete_employee(self, db: Session, employee_id: str) -> bool:
        """
        删除员工
        
        Args:
            db: 数据库会话
            employee_id: 员工ID
            
        Returns:
            bool: 是否成功删除
        """
        employee = employee_repository.get(db, employee_id)
        if not employee:
            self.log_warning(f"员工不存在，无法删除: {employee_id}")
            return False
        
        try:
            # 检查状态，已发布的员工改为归档
            if employee.status == "published":
                employee_repository.update(
                    db,
                    db_obj=employee,
                    obj_in={"status": "archived", "updated_at": datetime.utcnow()}
                )
                self.log_info(f"员工已发布，改为归档状态: {employee_id}")
                return True
            else:
                # 直接删除
                employee_repository.delete(db, id=employee_id)
                self.log_info(f"删除员工成功: {employee_id}")
                return True
                
        except Exception as e:
            self.log_error(f"删除员工失败: {employee_id}, 错误: {str(e)}", error=e)
            return False
    
    def list_employees(
        self,
        db: Session,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[EmployeeResponse]:
        """
        列出员工

        Args:
            db: 数据库会话
            user_id: 用户ID过滤（创建者）
            status: 状态过滤
            category: 分类过滤
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[EmployeeResponse]: 员工列表
        """
        try:
            self.log_info(
                f"list_employees - user_id: {user_id}, status: {status}, "
                f"category: {category}"
            )
            
            # 构建查询
            query = db.query(Employee)
            
            # 应用过滤条件
            if user_id:
                query = query.filter(Employee.created_by == user_id)
            
            if status:
                query = query.filter(Employee.status == status)
            
            if category:
                query = query.filter(
                    Employee.category.contains(f'"{category}"')
                )
            
            # 按更新时间倒序排序
            query = query.order_by(desc(Employee.updated_at))
            
            # 应用分页
            employees = query.offset(offset).limit(limit).all()
            
            self.log_debug(f"列出员工 - 返回数量: {len(employees)}")
            
            return [self._employee_to_response(emp) for emp in employees]
            
        except Exception as e:
            self.log_error(f"列出员工失败: {str(e)}", error=e)
            return []
    
    def publish_employee(
        self,
        db: Session,
        employee_id: str
    ) -> Optional[EmployeeResponse]:
        """
        发布员工
        
        Args:
            db: 数据库会话
            employee_id: 员工ID
            
        Returns:
            Optional[EmployeeResponse]: 发布后的员工信息
        """
        employee = employee_repository.get(db, employee_id)
        if not employee:
            self.log_warning(f"员工不存在，无法发布: {employee_id}")
            return None
        
        try:
            employee = employee_repository.update(
                db,
                db_obj=employee,
                obj_in={
                    "status": "published",
                    "updated_at": datetime.utcnow()
                }
            )
            
            self.log_info(f"发布员工成功: {employee_id}")
            
            return self._employee_to_response(employee)
            
        except Exception as e:
            self.log_error(f"发布员工失败: {employee_id}, 错误: {str(e)}", error=e)
            return None
    
    def get_marketplace_employees(
        self,
        db: Session,
        user_id: Optional[str] = None,
        category: Optional[str] = None,
        industry: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[EmployeeResponse]:
        """
        获取市场广场员工列表（只包含已发布的员工）
        
        Args:
            db: 数据库会话
            user_id: 当前用户ID，用于判断雇佣状态
            category: 分类过滤
            industry: 行业过滤
            min_price: 最低价格
            max_price: 最高价格
            tags: 标签过滤
            search: 搜索关键词
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[EmployeeResponse]: 市场员工列表
        """
        try:
            employees = employee_repository.get_marketplace_employees(
                db,
                category=category,
                industry=industry,
                min_price=min_price,
                max_price=max_price,
                search=search,
                skip=offset,
                limit=limit
            )
            
            # 标签过滤（在内存中处理）
            if tags:
                filtered = []
                for emp in employees:
                    emp_tags = emp.tags or []
                    if any(tag in emp_tags for tag in tags):
                        filtered.append(emp)
                employees = filtered
            
            # 获取当前用户已雇佣的员工ID列表
            user_hired_employee_ids = set()
            self.log_info(f"[DEBUG] 准备查询雇佣记录，user_id={user_id}, user_id类型={type(user_id)}, bool={bool(user_id)}")
            if user_id:
                from app.db.models import HireRecord
                self.log_info(f"[DEBUG] 正在查询 HireRecord，user_id={user_id}")
                hire_records = db.query(HireRecord).filter(
                    HireRecord.user_id == user_id,
                    HireRecord.status == "active"
                ).all()
                user_hired_employee_ids = {record.employee_id for record in hire_records}
                self.log_info(f"[DEBUG] 用户 {user_id} 已雇佣员工: {user_hired_employee_ids}, 记录数: {len(hire_records)}")
            else:
                self.log_info(f"[DEBUG] user_id 为 falsy，跳过查询")
            
            # 构建响应，根据当前用户的雇佣状态设置 is_hired
            responses = []
            for emp in employees:
                # 根据当前用户的雇佣记录判断是否已雇佣
                is_hired = emp.id in user_hired_employee_ids if user_id else False
                
                # 创建响应对象，直接传入正确的 is_hired
                response = EmployeeResponse(
                    id=emp.id,
                    name=emp.name,
                    description=emp.description or "",
                    avatar=emp.avatar,
                    category=emp.category or [],
                    tags=emp.tags or [],
                    price=emp.price,
                    original_price=emp.original_price,
                    trial_count=emp.trial_count,
                    hire_count=emp.hire_count,
                    is_hired=is_hired,
                    is_recruited=is_hired,
                    status=emp.status,
                    skills=emp.skills or [],
                    knowledge_base_ids=emp.knowledge_base_ids or [],
                    industry=emp.industry,
                    role=emp.role,
                    prompt=emp.prompt,
                    model=emp.model,
                    is_hot=emp.is_hot,
                    created_by=emp.created_by,
                    created_at=emp.created_at,
                    updated_at=emp.updated_at,
                )
                responses.append(response)
                
            self.log_info(f"[DEBUG] 返回响应: {[(r.id, r.is_hired) for r in responses]}")
            
            self.log_debug(f"获取市场员工 - 返回数量: {len(responses)}, 用户: {user_id}")
            
            return responses
            
        except Exception as e:
            self.log_error(f"获取市场员工失败: {str(e)}", error=e)
            return []
    
    def hire_employee(
        self,
        db: Session,
        employee_id: str,
        user_id: str,
        organization_id: Optional[str] = None
    ) -> Optional[EmployeeResponse]:
        """
        雇佣员工
        
        Args:
            db: 数据库会话
            employee_id: 员工ID
            user_id: 用户ID
            organization_id: 组织ID
            
        Returns:
            Optional[EmployeeResponse]: 雇佣后的员工信息
        """
        try:
            employee = employee_repository.update_hire_status(
                db, employee_id, is_hired=True
            )
            
            if not employee:
                self.log_warning(f"员工不存在，无法雇佣: {employee_id}")
                return None
            
            # 创建雇佣记录
            from app.db.models import HireRecord
            hire_record = HireRecord(
                employee_id=employee_id,
                user_id=user_id,
                organization_id=organization_id,
                status="active"
            )
            db.add(hire_record)
            db.commit()
            
            self.log_info(f"雇佣员工成功: {employee_id}, 组织: {organization_id}")
            
            return self._employee_to_response(employee)
            
        except Exception as e:
            self.log_error(f"雇佣员工失败: {employee_id}, 错误: {str(e)}", error=e)
            return None
    
    def trial_employee(
        self,
        db: Session,
        employee_id: str,
        user_id: str,
        organization_id: Optional[str] = None
    ) -> Optional[EmployeeResponse]:
        """
        试用员工
        
        Args:
            db: 数据库会话
            employee_id: 员工ID
            user_id: 用户ID
            organization_id: 组织ID
            
        Returns:
            Optional[EmployeeResponse]: 试用后的员工信息
        """
        try:
            employee = employee_repository.update_trial_count(db, employee_id)
            
            if not employee:
                self.log_warning(f"员工不存在，无法试用: {employee_id}")
                return None
            
            # 创建试用记录
            from app.db.models import TrialRecord
            trial_record = TrialRecord(
                employee_id=employee_id,
                user_id=user_id,
                organization_id=organization_id
            )
            db.add(trial_record)
            db.commit()
            
            self.log_info(f"试用员工成功: {employee_id}, 组织: {organization_id}")
            
            return self._employee_to_response(employee)
            
        except Exception as e:
            self.log_error(f"试用员工失败: {employee_id}, 错误: {str(e)}", error=e)
            return None


# 创建全局员工服务实例
employee_service = EmployeeService()
