"""
市场广场API端点
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.dependencies import get_current_user, get_optional_user, UserContext
from app.services.employee_service import employee_service
from app.models.schemas import (
    SuccessResponse,
    MarketplaceFilter,
    HireRequest,
    TrialRequest
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/marketplace", tags=["marketplace"])

@router.get(
    "/employees",
    response_model=SuccessResponse,
    summary="获取市场员工列表",
    description="获取市场广场上的员工列表，支持过滤和搜索"
)
async def get_marketplace_employees(
    category: Optional[str] = Query(None, description="分类过滤"),
    industry: Optional[str] = Query(None, description="行业过滤"),
    min_price: Optional[int] = Query(None, ge=0, description="最低价格"),
    max_price: Optional[int] = Query(None, ge=0, description="最高价格"),
    tags: Optional[str] = Query(None, description="标签过滤（逗号分隔）"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    current_user: Optional[UserContext] = Depends(get_optional_user)
) -> SuccessResponse:
    """
    获取市场员工列表端点
    
    Args:
        category: 分类过滤
        industry: 行业过滤
        min_price: 最低价格
        max_price: 最高价格
        tags: 标签过滤
        search: 搜索关键词
        page: 页码
        page_size: 每页大小
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含市场员工列表
    """
    
    try:
        # 解析标签
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取市场员工列表
        employees = employee_service.get_marketplace_employees(
            category=category,
            industry=industry,
            min_price=min_price,
            max_price=max_price,
            tags=tag_list,
            search=search,
            limit=page_size,
            offset=offset
        )
        
        # 获取总数 - 修复这里：使用 emp_id 而不是 emp
        total_employees = len([
            emp_id for emp_id, emp_data in employee_service._employees.items()
            if emp_data.get("status") == "published"
        ])
        
        # 计算总页数
        total_pages = (total_employees + page_size - 1) // page_size
        
        user_id = current_user.user_id if current_user else "anonymous"
        logger.info(f"获取市场员工列表 - 用户: {user_id}, 页码: {page}, 数量: {len(employees)}")
        
        return SuccessResponse(
            success=True,
            message="获取市场员工列表成功",
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
        logger.error(f"获取市场员工列表异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取市场员工列表时发生错误: {str(e)}"
        )

@router.get(
    "/categories",
    response_model=SuccessResponse,
    summary="获取分类列表",
    description="获取市场广场上的员工分类列表"
)
async def get_marketplace_categories(
    current_user: Optional[UserContext] = Depends(get_optional_user)
) -> SuccessResponse:
    """
    获取分类列表端点
    
    Args:
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含分类列表
    """
    
    try:
        # 收集所有分类
        categories = set()
        
        for emp_id, emp_data in employee_service._employees.items():
            if emp_data.get("status") == "published":
                for category in emp_data.get("category", []):
                    categories.add(category)
        
        # 转换为列表
        category_list = list(categories)
        category_list.sort()
        
        logger.info(f"获取分类列表 - 数量: {len(category_list)}")
        
        return SuccessResponse(
            success=True,
            message="获取分类列表成功",
            data={
                "categories": category_list,
                "total": len(category_list)
            }
        )
        
    except Exception as e:
        logger.error(f"获取分类列表异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类列表时发生错误: {str(e)}"
        )

@router.get(
    "/industries",
    response_model=SuccessResponse,
    summary="获取行业列表",
    description="获取市场广场上的员工行业列表"
)
async def get_marketplace_industries(
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    获取行业列表端点
    
    Args:
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含行业列表
    """
    
    try:
        # 收集所有行业
        industries = set()
        
        for emp_id, emp_data in employee_service._employees.items():
            if emp_data.get("status") == "published":
                industry = emp_data.get("industry")
                if industry:
                    industries.add(industry)
        
        # 转换为列表
        industry_list = list(industries)
        industry_list.sort()
        
        logger.info(f"获取行业列表 - 数量: {len(industry_list)}")
        
        return SuccessResponse(
            success=True,
            message="获取行业列表成功",
            data={
                "industries": industry_list,
                "total": len(industry_list)
            }
        )
        
    except Exception as e:
        logger.error(f"获取行业列表异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取行业列表时发生错误: {str(e)}"
        )

@router.post(
    "/{employee_id}/hire",
    response_model=SuccessResponse,
    summary="雇佣员工",
    description="从市场广场雇佣指定的员工"
)
async def hire_employee(
    employee_id: str,
    hire_request: HireRequest,
    current_user: Optional[UserContext] = Depends(get_optional_user)
) -> SuccessResponse:
    """
    雇佣员工端点
    
    Args:
        employee_id: 员工ID
        hire_request: 雇佣请求
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含雇佣结果
    """
    
    try:
        # 检查员工是否存在且已发布
        existing_employee = employee_service.get_employee(employee_id)
        
        if not existing_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"员工不存在: {employee_id}"
            )
        
        if existing_employee.status != "published":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能雇佣已发布的员工"
            )
        
        # 检查是否已雇佣
        if existing_employee.is_hired:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该员工已被雇佣"
            )
        
        # 雇佣员工
        user_id = current_user.user_id if current_user else "anonymous"
        organization_id = hire_request.organization_id or (current_user.organization_id if current_user else None)
        hired_employee = employee_service.hire_employee(employee_id, organization_id)
        
        if not hired_employee:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="雇佣员工失败"
            )
        
        logger.info(f"雇佣员工成功 - 员工: {employee_id}, 用户: {user_id}")
        
        return SuccessResponse(
            success=True,
            message="员工雇佣成功",
            data={
                "employee": hired_employee.dict(),
                "hire_time": hired_employee.updated_at,
                "user_id": user_id,
                "organization_id": organization_id
            }
        )
        
    except HTTPException as he:
        logger.warning(f"雇佣员工业务错误 - 员工: {employee_id}, 错误: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"雇佣员工异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"雇佣员工时发生错误: {str(e)}"
        )

@router.post(
    "/{employee_id}/trial",
    response_model=SuccessResponse,
    summary="试用员工",
    description="从市场广场试用指定的员工"
)
async def trial_employee(
    employee_id: str,
    trial_request: TrialRequest,
    current_user: Optional[UserContext] = Depends(get_optional_user)
) -> SuccessResponse:
    """
    试用员工端点
    
    Args:
        employee_id: 员工ID
        trial_request: 试用请求
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含试用结果
    """
    
    try:
        # 检查员工是否存在且已发布
        existing_employee = employee_service.get_employee(employee_id)
        
        if not existing_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"员工不存在: {employee_id}"
            )
        
        if existing_employee.status != "published":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能试用已发布的员工"
            )
        
        # 试用员工
        user_id = current_user.user_id if current_user else "anonymous"
        organization_id = trial_request.organization_id or (current_user.organization_id if current_user else None)
        trial_employee_result = employee_service.trial_employee(employee_id, organization_id)
        
        if not trial_employee_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="试用员工失败"
            )
        
        logger.info(f"试用员工成功 - 员工: {employee_id}, 用户: {user_id}")
        
        return SuccessResponse(
            success=True,
            message="员工试用成功",
            data={
                "employee": trial_employee_result.dict(),
                "trial_time": trial_employee_result.updated_at,
                "user_id": user_id,
                "organization_id": organization_id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"试用员工异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"试用员工时发生错误: {str(e)}"
        )

# 导出路由器
__all__ = ["router"]