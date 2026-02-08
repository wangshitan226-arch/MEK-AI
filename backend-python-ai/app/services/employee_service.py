"""
员工管理服务
处理数字员工的业务逻辑
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.utils.logger import LoggerMixin
from app.models.schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse

class EmployeeService(LoggerMixin):
    """
    员工管理服务
    处理员工的创建、读取、更新、删除等业务逻辑
    """
    
    def __init__(self):
        """初始化员工服务"""
        super().__init__()
        
        # 内存存储（后续可替换为数据库）
        self._employees: Dict[str, Dict[str, Any]] = {}
        
        # 初始化一些示例数据
        self._init_sample_employees()
        
        self.log_info("员工服务初始化完成")
    
    def _init_sample_employees(self):
        """初始化示例员工数据"""
        
        sample_employees = [
            {
                "id": "emp_001",
                "name": "AI营销专家",
                "description": "专业的AI营销顾问，擅长市场分析和营销策略制定",
                "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=marketing",
                "category": ["marketing", "strategy"],
                "tags": ["expert", "pro"],
                "price": 299,
                "original_price": 399,
                "trial_count": 42,
                "hire_count": 28,
                "is_hired": False,
                "is_recruited": True,
                "status": "published",
                "skills": ["市场分析", "营销策略", "竞品分析", "用户调研"],
                "knowledge_base_ids": ["kb_001"],
                "industry": "互联网",
                "role": "营销顾问",
                "prompt": "你是一名专业的AI营销专家，请用专业但易懂的语言回答用户问题。",
                "model": "gpt-4",
                "created_by": "system",
                "created_at": datetime(2024, 1, 1, 10, 0, 0),
                "updated_at": datetime(2024, 1, 15, 14, 30, 0),
                "is_hot": True
            },
            {
                "id": "emp_002",
                "name": "技术支持工程师",
                "description": "专业的技术支持，擅长解决各种技术问题和故障排除",
                "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=support",
                "category": ["technical", "support"],
                "tags": ["expert", "responsive"],
                "price": 199,
                "original_price": 299,
                "trial_count": 35,
                "hire_count": 22,
                "is_hired": False,
                "is_recruited": True,
                "status": "published",
                "skills": ["故障排除", "代码调试", "系统维护", "技术咨询"],
                "knowledge_base_ids": ["kb_002"],
                "industry": "科技",
                "role": "技术支持",
                "prompt": "你是一名专业的技术支持工程师，请耐心细致地解决用户的技术问题。",
                "model": "gpt-3.5-turbo",
                "created_by": "system",
                "created_at": datetime(2024, 1, 5, 9, 0, 0),
                "updated_at": datetime(2024, 1, 20, 11, 0, 0),
                "is_hot": False
            },
            {
                "id": "emp_003",
                "name": "创意文案助手",
                "description": "专业的文案创作助手，擅长各种创意文案和内容创作",
                "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=creative",
                "category": ["creative", "writing"],
                "tags": ["creative", "writer"],
                "price": "free",
                "trial_count": 158,
                "hire_count": 0,
                "is_hired": False,
                "is_recruited": False,
                "status": "published",
                "skills": ["文案创作", "内容策划", "广告语", "社交媒体文案"],
                "knowledge_base_ids": [],
                "industry": "媒体",
                "role": "文案创作",
                "prompt": "你是一名创意文案专家，请用富有创意的语言帮助用户进行文案创作。",
                "model": "claude-3",
                "created_by": "user_001",
                "created_at": datetime(2024, 1, 10, 14, 0, 0),
                "updated_at": datetime(2024, 1, 25, 16, 0, 0),
                "is_hot": True
            }
        ]
        
        for emp in sample_employees:
            self._employees[emp["id"]] = emp
    
    def create_employee(self, employee_data: EmployeeCreate, created_by: str) -> EmployeeResponse:
        """
        创建新员工
        
        Args:
            employee_data: 员工数据
            created_by: 创建者ID
            
        Returns:
            EmployeeResponse: 创建的员工响应
        """
        
        try:
            # 生成员工ID
            employee_id = f"emp_{str(uuid.uuid4())[:8]}"
            
            now = datetime.now()
            
            # 创建员工记录
            employee_record = {
                "id": employee_id,
                **employee_data.dict(),
                "trial_count": 0,
                "hire_count": 0,
                "is_hired": False,
                "is_recruited": False,
                "status": "draft",
                "created_by": created_by,
                "created_at": now,
                "updated_at": now,
                "is_hot": False
            }
            
            # 保存到内存存储
            self._employees[employee_id] = employee_record
            
            self.log_info(f"创建员工成功: {employee_id}, 名称: {employee_data.name}")
            
            return EmployeeResponse(**employee_record)
            
        except Exception as e:
            self.log_error(f"创建员工失败: {str(e)}", error=e)
            raise
    
    def get_employee(self, employee_id: str) -> Optional[EmployeeResponse]:
        """
        获取员工详情
        
        Args:
            employee_id: 员工ID
            
        Returns:
            Optional[EmployeeResponse]: 员工信息，如果不存在则返回None
        """
        
        if employee_id not in self._employees:
            self.log_warning(f"员工不存在: {employee_id}")
            return None
        
        return EmployeeResponse(**self._employees[employee_id])
    
    def update_employee(self, employee_id: str, update_data: EmployeeUpdate) -> Optional[EmployeeResponse]:
        """
        更新员工信息
        
        Args:
            employee_id: 员工ID
            update_data: 更新数据
            
        Returns:
            Optional[EmployeeResponse]: 更新后的员工信息，如果不存在则返回None
        """
        
        if employee_id not in self._employees:
            self.log_warning(f"员工不存在，无法更新: {employee_id}")
            return None
        
        try:
            # 获取现有员工数据
            employee = self._employees[employee_id]
            
            # 应用更新（只更新提供的字段）
            update_dict = update_data.dict(exclude_unset=True)
            
            for key, value in update_dict.items():
                if value is not None:
                    employee[key] = value
            
            # 更新更新时间
            employee["updated_at"] = datetime.now()
            
            self.log_info(f"更新员工成功: {employee_id}")
            
            return EmployeeResponse(**employee)
            
        except Exception as e:
            self.log_error(f"更新员工失败: {employee_id}, 错误: {str(e)}", error=e)
            return None
    
    def delete_employee(self, employee_id: str) -> bool:
        """
        删除员工
        
        Args:
            employee_id: 员工ID
            
        Returns:
            bool: 是否成功删除
        """
        
        if employee_id not in self._employees:
            self.log_warning(f"员工不存在，无法删除: {employee_id}")
            return False
        
        try:
            # 检查状态，已发布的员工不能直接删除
            employee = self._employees[employee_id]
            if employee["status"] == "published":
                # 改为归档状态
                employee["status"] = "archived"
                employee["updated_at"] = datetime.now()
                self.log_info(f"员工已发布，改为归档状态: {employee_id}")
                return True
            else:
                # 直接删除
                del self._employees[employee_id]
                self.log_info(f"删除员工成功: {employee_id}")
                return True
                
        except Exception as e:
            self.log_error(f"删除员工失败: {employee_id}, 错误: {str(e)}", error=e)
            return False
    
    # 在 app/services/employee_service.py 中找到 list_employees 方法，修改如下：

    def list_employees(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[EmployeeResponse]:
        """
        列出员工

        Args:
            user_id: 用户ID过滤（创建者）
            status: 状态过滤
            category: 分类过滤
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[EmployeeResponse]: 员工列表
        """

        try:
            self.log_info(f"list_employees 被调用 - user_id: {user_id}, status: {status}, category: {category}")
            self.log_info(f"当前员工总数: {len(self._employees)}")

            filtered_employees = []

            for emp_id, emp_data in self._employees.items():
                self.log_debug(f"检查员工: {emp_id}, status: {emp_data.get('status')}, created_by: {emp_data.get('created_by')}")
                # 应用过滤条件
                # 修改这里：如果没有提供user_id，不过滤创建者
                if user_id and emp_data.get("created_by") != user_id:
                    continue
                
                if status and emp_data.get("status") != status:
                    continue
                
                if category and category not in emp_data.get("category", []):
                    continue
                
                filtered_employees.append(EmployeeResponse(**emp_data))
            
            # 按更新时间倒序排序
            filtered_employees.sort(key=lambda x: x.updated_at, reverse=True)
            
            # 应用分页
            start_idx = offset
            end_idx = offset + limit
            paginated_employees = filtered_employees[start_idx:end_idx]
            
            self.log_debug(f"列出员工 - 过滤后数量: {len(filtered_employees)}, 分页后: {len(paginated_employees)}")
            
            return paginated_employees
            
        except Exception as e:
            self.log_error(f"列出员工失败: {str(e)}", error=e)
            return []
    
    def publish_employee(self, employee_id: str) -> Optional[EmployeeResponse]:
        """
        发布员工
        
        Args:
            employee_id: 员工ID
            
        Returns:
            Optional[EmployeeResponse]: 发布后的员工信息
        """
        
        if employee_id not in self._employees:
            self.log_warning(f"员工不存在，无法发布: {employee_id}")
            return None
        
        try:
            employee = self._employees[employee_id]
            
            # 更新状态为已发布
            employee["status"] = "published"
            employee["updated_at"] = datetime.now()
            
            self.log_info(f"发布员工成功: {employee_id}")
            
            return EmployeeResponse(**employee)
            
        except Exception as e:
            self.log_error(f"发布员工失败: {employee_id}, 错误: {str(e)}", error=e)
            return None
    
    def get_marketplace_employees(
        self,
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
            marketplace_employees = []
            
            for emp_id, emp_data in self._employees.items():
                # 只包含已发布的员工
                if emp_data.get("status") != "published":
                    continue
                
                # 应用过滤条件
                if category and category not in emp_data.get("category", []):
                    continue
                
                if industry and emp_data.get("industry") != industry:
                    continue
                
                # 价格过滤
                price = emp_data.get("price", 0)
                if isinstance(price, str) and price == "free":
                    price_value = 0
                else:
                    price_value = int(price) if price else 0
                
                if min_price is not None and price_value < min_price:
                    continue
                
                if max_price is not None and price_value > max_price:
                    continue
                
                # 标签过滤
                if tags:
                    emp_tags = emp_data.get("tags", [])
                    if not any(tag in emp_tags for tag in tags):
                        continue
                
                # 搜索过滤
                if search:
                    search_lower = search.lower()
                    name_matches = search_lower in emp_data.get("name", "").lower()
                    desc_matches = search_lower in emp_data.get("description", "").lower()
                    skills_matches = any(search_lower in skill.lower() for skill in emp_data.get("skills", []))
                    
                    if not (name_matches or desc_matches or skills_matches):
                        continue
                
                marketplace_employees.append(EmployeeResponse(**emp_data))
            
            # 按热门程度和雇佣次数排序
            marketplace_employees.sort(
                key=lambda x: (
                    -x.is_hot if x.is_hot is not None else 0,
                    -x.hire_count,
                    -x.trial_count
                )
            )
            
            # 应用分页
            start_idx = offset
            end_idx = offset + limit
            paginated_employees = marketplace_employees[start_idx:end_idx]
            
            self.log_debug(f"获取市场员工 - 过滤后数量: {len(marketplace_employees)}, 分页后: {len(paginated_employees)}")
            
            return paginated_employees
            
        except Exception as e:
            self.log_error(f"获取市场员工失败: {str(e)}", error=e)
            return []
    
    def hire_employee(self, employee_id: str, organization_id: Optional[str] = None) -> Optional[EmployeeResponse]:
        """
        雇佣员工
        
        Args:
            employee_id: 员工ID
            organization_id: 组织ID
            
        Returns:
            Optional[EmployeeResponse]: 雇佣后的员工信息
        """
        
        if employee_id not in self._employees:
            self.log_warning(f"员工不存在，无法雇佣: {employee_id}")
            return None
        
        try:
            employee = self._employees[employee_id]
            
            # 更新雇佣状态和计数
            employee["is_hired"] = True
            employee["is_recruited"] = True
            employee["hire_count"] = employee.get("hire_count", 0) + 1
            employee["updated_at"] = datetime.now()
            
            self.log_info(f"雇佣员工成功: {employee_id}, 组织: {organization_id}")
            
            return EmployeeResponse(**employee)
            
        except Exception as e:
            self.log_error(f"雇佣员工失败: {employee_id}, 错误: {str(e)}", error=e)
            return None
    
    def trial_employee(self, employee_id: str, organization_id: Optional[str] = None) -> Optional[EmployeeResponse]:
        """
        试用员工
        
        Args:
            employee_id: 员工ID
            organization_id: 组织ID
            
        Returns:
            Optional[EmployeeResponse]: 试用后的员工信息
        """
        
        if employee_id not in self._employees:
            self.log_warning(f"员工不存在，无法试用: {employee_id}")
            return None
        
        try:
            employee = self._employees[employee_id]
            
            # 更新试用计数
            employee["trial_count"] = employee.get("trial_count", 0) + 1
            employee["updated_at"] = datetime.now()
            
            self.log_info(f"试用员工成功: {employee_id}, 组织: {organization_id}")
            
            return EmployeeResponse(**employee)
            
        except Exception as e:
            self.log_error(f"试用员工失败: {employee_id}, 错误: {str(e)}", error=e)
            return None

# 创建全局员工服务实例
employee_service = EmployeeService()