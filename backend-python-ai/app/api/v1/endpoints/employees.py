"""
数字员工管理API端点 - MySQL版本
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_optional_user, UserContext
from app.db import get_db
from app.services.employee_service import employee_service
from app.db.repositories import employee_repository
from app.models.schemas import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    SuccessResponse,
    PaginatedResponse,
    PaginationParams,
    HireRequest,
    TrialRequest
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/employees", tags=["employees"])


@router.get(
    "",
    response_model=SuccessResponse,
    summary="获取员工列表",
    description="获取数字员工列表，支持分页和过滤"
)
async def get_employees(
    status_filter: Optional[str] = Query(None, alias="status", description="状态过滤: draft/published/archived"),
    category: Optional[str] = Query(None, description="分类过滤"),
    created_by: Optional[str] = Query(None, description="创建者过滤: 指定用户ID获取该用户创建的员工"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    current_user: Optional[UserContext] = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """
    获取员工列表端点
    
    Args:
        status_filter: 状态过滤
        category: 分类过滤
        created_by: 创建者过滤
        page: 页码
        page_size: 每页大小
        current_user: 当前用户上下文
        db: 数据库会话
        
    Returns:
        SuccessResponse: 成功响应，包含员工列表
    """
    
    try:
        # 计算偏移量
        offset = (page - 1) * page_size

        # 获取当前用户ID（可能为None或anonymous）
        user_id = current_user.user_id if current_user else None
        # 如果是anonymous，视为未登录，不应用用户过滤
        if user_id == "anonymous":
            user_id = None
        
        # 如果指定了 created_by 参数，优先使用它进行过滤
        filter_user_id = created_by if created_by else user_id

        # 获取员工列表
        employees = employee_service.list_employees(
            db=db,
            user_id=filter_user_id,
            status=status_filter,
            category=category,
            limit=page_size,
            offset=offset
        )
        
        # 获取总数
        total_employees = employee_repository.count(db)
        
        # 计算总页数
        total_pages = (total_employees + page_size - 1) // page_size if total_employees > 0 else 1
        
        logger.info(f"获取员工列表 - 用户: {user_id}, 页码: {page}, 数量: {len(employees)}")
        
        return SuccessResponse(
            success=True,
            message="获取员工列表成功",
            data={
                "items": [emp.dict() for emp in employees],
                "total": total_employees,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        )
        
    except Exception as e:
        logger.error(f"获取员工列表异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取员工列表时发生错误: {str(e)}"
        )


@router.post(
    "",
    response_model=SuccessResponse,
    summary="创建员工",
    description="创建新的数字员工"
)
async def create_employee(
    employee_data: EmployeeCreate,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """
    创建员工端点

    Args:
        employee_data: 员工数据
        current_user: 当前用户上下文
        db: 数据库会话

    Returns:
        SuccessResponse: 成功响应，包含创建的员工信息
    """

    try:
        # 创建员工
        employee = employee_service.create_employee(
            db=db, 
            employee_data=employee_data, 
            created_by=current_user.user_id
        )
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建员工失败"
            )
        
        logger.info(f"创建员工成功 - ID: {employee.id}, 名称: {employee.name}")
        
        return SuccessResponse(
            success=True,
            message="员工创建成功",
            data=employee.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建员工异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建员工时发生错误: {str(e)}"
        )


@router.get(
    "/categories",
    response_model=SuccessResponse,
    summary="获取分类列表",
    description="获取所有员工的分类列表"
)
async def get_employee_categories(
    current_user: Optional[UserContext] = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """
    获取分类列表端点
    
    Args:
        current_user: 当前用户上下文（可选）
        db: 数据库会话
        
    Returns:
        SuccessResponse: 成功响应，包含分类列表
    """
    
    try:
        # 从数据库获取所有已发布员工的分类
        from sqlalchemy import func
        from app.db.models import Employee
        
        # 查询所有已发布员工的分类
        employees = db.query(Employee).filter(Employee.status == "published").all()
        
        # 收集所有分类
        categories = set()
        for emp in employees:
            for category in (emp.category or []):
                categories.add(category)
        
        # 转换为列表并排序
        category_list = sorted(list(categories))
        
        # 格式化分类数据
        formatted_categories = [
            {"id": cat.lower().replace(" ", "-"), "name": cat, "count": 0}
            for cat in category_list
        ]
        
        logger.info(f"获取分类列表 - 数量: {len(formatted_categories)}")
        
        return SuccessResponse(
            success=True,
            message="获取分类列表成功",
            data=formatted_categories
        )
        
    except Exception as e:
        logger.error(f"获取分类列表异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类列表时发生错误: {str(e)}"
        )


@router.get(
    "/{employee_id}",
    response_model=SuccessResponse,
    summary="获取员工详情",
    description="获取指定员工的详细信息"
)
async def get_employee(
    employee_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """
    获取员工详情端点
    
    Args:
        employee_id: 员工ID
        current_user: 当前用户上下文
        db: 数据库会话
        
    Returns:
        SuccessResponse: 成功响应，包含员工详情
    """
    
    try:
        # 获取员工详情
        employee = employee_service.get_employee(db=db, employee_id=employee_id)
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"员工不存在: {employee_id}"
            )
        
        # 检查权限（仅创建者可以查看草稿状态的员工）
        if employee.status == "draft" and employee.created_by != current_user.user_id:
            logger.warning(f"权限拒绝 - 用户: {current_user.user_id} 尝试查看草稿员工: {employee_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此员工"
            )
        
        logger.info(f"获取员工详情 - ID: {employee_id}")
        
        return SuccessResponse(
            success=True,
            message="获取员工详情成功",
            data=employee.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取员工详情异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取员工详情时发生错误: {str(e)}"
        )


@router.put(
    "/{employee_id}",
    response_model=SuccessResponse,
    summary="更新员工",
    description="更新指定员工的信息"
)
async def update_employee(
    employee_id: str,
    update_data: EmployeeUpdate,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """
    更新员工端点
    
    Args:
        employee_id: 员工ID
        update_data: 更新数据
        current_user: 当前用户上下文
        db: 数据库会话
        
    Returns:
        SuccessResponse: 成功响应，包含更新后的员工信息
    """
    
    try:
        # 检查员工是否存在
        existing_employee = employee_service.get_employee(db=db, employee_id=employee_id)
        
        if not existing_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"员工不存在: {employee_id}"
            )
        
        # 检查权限（仅创建者可以更新）
        if existing_employee.created_by != current_user.user_id:
            logger.warning(f"权限拒绝 - 用户: {current_user.user_id} 尝试更新员工: {employee_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权更新此员工"
            )
        
        # 更新员工
        updated_employee = employee_service.update_employee(
            db=db, 
            employee_id=employee_id, 
            update_data=update_data
        )
        
        if not updated_employee:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新员工失败"
            )
        
        logger.info(f"更新员工成功 - ID: {employee_id}")
        
        return SuccessResponse(
            success=True,
            message="员工更新成功",
            data=updated_employee.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新员工异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新员工时发生错误: {str(e)}"
        )


@router.delete(
    "/{employee_id}",
    response_model=SuccessResponse,
    summary="删除员工",
    description="删除指定的员工"
)
async def delete_employee(
    employee_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """
    删除员工端点
    
    Args:
        employee_id: 员工ID
        current_user: 当前用户上下文
        db: 数据库会话
        
    Returns:
        SuccessResponse: 成功响应
    """
    
    try:
        # 检查员工是否存在
        existing_employee = employee_service.get_employee(db=db, employee_id=employee_id)
        
        if not existing_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"员工不存在: {employee_id}"
            )
        
        # 检查权限（仅创建者可以删除）
        if existing_employee.created_by != current_user.user_id:
            logger.warning(f"权限拒绝 - 用户: {current_user.user_id} 尝试删除员工: {employee_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此员工"
            )
        
        # 删除员工
        success = employee_service.delete_employee(db=db, employee_id=employee_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除员工失败"
            )
        
        logger.info(f"删除员工成功 - ID: {employee_id}")
        
        return SuccessResponse(
            success=True,
            message="员工删除成功",
            data={
                "employee_id": employee_id,
                "deleted": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除员工异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除员工时发生错误: {str(e)}"
        )


@router.post(
    "/{employee_id}/publish",
    response_model=SuccessResponse,
    summary="发布员工",
    description="将员工状态改为已发布"
)
async def publish_employee(
    employee_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """
    发布员工端点
    
    Args:
        employee_id: 员工ID
        current_user: 当前用户上下文
        db: 数据库会话
        
    Returns:
        SuccessResponse: 成功响应，包含发布后的员工信息
    """
    
    try:
        # 检查员工是否存在
        existing_employee = employee_service.get_employee(db=db, employee_id=employee_id)
        
        if not existing_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"员工不存在: {employee_id}"
            )
        
        # 检查权限（仅创建者可以发布）
        if existing_employee.created_by != current_user.user_id:
            logger.warning(f"权限拒绝 - 用户: {current_user.user_id} 尝试发布员工: {employee_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权发布此员工"
            )
        
        # 发布员工
        published_employee = employee_service.publish_employee(db=db, employee_id=employee_id)
        
        if not published_employee:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="发布员工失败"
            )
        
        logger.info(f"发布员工成功 - ID: {employee_id}")
        
        return SuccessResponse(
            success=True,
            message="员工发布成功",
            data=published_employee.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发布员工异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发布员工时发生错误: {str(e)}"
        )


# 导出路由器
__all__ = ["router"]
