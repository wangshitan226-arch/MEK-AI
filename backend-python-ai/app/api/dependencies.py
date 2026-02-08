"""
API依赖项管理
包括权限验证、数据库连接等
"""

import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import Header, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 创建HTTP Bearer认证方案
security = HTTPBearer()

class UserContext:
    """
    用户上下文类
    存储当前请求的用户信息和权限
    """
    
    def __init__(
        self,
        user_id: str,
        organization_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        is_authenticated: bool = True,
        is_mock: bool = False,
        permissions: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.user_id = user_id
        self.organization_id = organization_id
        self.employee_id = employee_id
        self.is_authenticated = is_authenticated
        self.is_mock = is_mock
        self.permissions = permissions or ["chat", "read"]
        self.metadata = metadata or {}
        self.request_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "employee_id": self.employee_id,
            "is_authenticated": self.is_authenticated,
            "is_mock": self.is_mock,
            "permissions": self.permissions,
            "metadata": self.metadata,
            "request_time": self.request_time.isoformat()
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        mock_flag = "[MOCK]" if self.is_mock else ""
        return f"UserContext(user_id={self.user_id}, employee_id={self.employee_id}){mock_flag}"

async def get_current_user(
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-ID"),
    x_employee_id: Optional[str] = Header(None, alias="X-Employee-ID"),
    authorization: Optional[HTTPAuthorizationCredentials] = None
) -> UserContext:
    """
    获取当前用户上下文
    
    当前为模拟验证阶段，后期会对接Java Ruoyi进行真实验证
    
    Args:
        request: FastAPI请求对象
        x_user_id: 用户ID头
        x_organization_id: 组织ID头
        x_employee_id: 员工ID头（业务必需）
        authorization: Bearer Token
        
    Returns:
        UserContext: 用户上下文对象
        
    Raises:
        HTTPException: 当必需的头缺失或验证失败时
    """
    
    # 记录请求信息用于调试
    request_id = request.state.request_id if hasattr(request.state, 'request_id') else str(uuid.uuid4())
    logger.debug(f"[{request_id}] 开始用户验证 - "
                 f"user_id: {x_user_id}, "
                 f"employee_id: {x_employee_id}")
    
    # 检查必需的头
    if not x_employee_id:
        logger.warning(f"[{request_id}] 缺少必需的X-Employee-ID头")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Employee-ID头是必需的"
        )
    
    # 当前开发阶段：模拟验证逻辑
    if not x_user_id:
        # 如果未提供用户ID，使用模拟用户
        logger.info(f"[{request_id}] 使用模拟用户 - employee_id: {x_employee_id}")
        return UserContext(
            user_id=settings.MOCK_USER_ID,
            organization_id=settings.MOCK_ORGANIZATION_ID,
            employee_id=x_employee_id,
            is_authenticated=True,
            is_mock=True,
            permissions=["chat", "read", "upload"],
            metadata={
                "mock_reason": "开发环境模拟用户",
                "request_id": request_id,
                "client_ip": request.client.host if request.client else "unknown"
            }
        )
    
    # 如果有用户ID但没有Token，视为模拟验证
    if not authorization:
        logger.info(f"[{request_id}] 使用提供的用户ID进行模拟验证 - user_id: {x_user_id}")
        return UserContext(
            user_id=x_user_id,
            organization_id=x_organization_id,
            employee_id=x_employee_id,
            is_authenticated=True,
            is_mock=True,
            permissions=["chat", "read", "upload"],
            metadata={
                "mock_reason": "开发环境Token验证未实现",
                "request_id": request_id,
                "client_ip": request.client.host if request.client else "unknown"
            }
        )
    
    # 未来：这里会调用Java Ruoyi验证Token
    # token = authorization.credentials
    # user_info = await verify_with_ruoyi(token)
    
    # 当前：假设Token验证通过
    logger.info(f"[{request_id}] Token验证通过 - user_id: {x_user_id}")
    return UserContext(
        user_id=x_user_id,
        organization_id=x_organization_id,
        employee_id=x_employee_id,
        is_authenticated=True,
        is_mock=False,
        permissions=["chat", "read", "upload", "delete"],
        metadata={
            "auth_method": "bearer_token",
            "request_id": request_id,
            "client_ip": request.client.host if request.client else "unknown"
        }
    )

async def get_optional_user(
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_employee_id: Optional[str] = Header(None, alias="X-Employee-ID")
) -> Optional[UserContext]:
    """
    获取可选的用户上下文
    
    对于某些公开API，用户可能未认证
    
    Args:
        request: FastAPI请求对象
        x_user_id: 用户ID头
        x_employee_id: 员工ID头
        
    Returns:
        Optional[UserContext]: 用户上下文对象，如果未认证则为None
    """
    
    # 如果没有提供必需的头，返回None
    if not x_employee_id:
        return None
    
    # 如果没有用户ID，返回模拟用户
    if not x_user_id:
        return UserContext(
            user_id=settings.MOCK_USER_ID,
            organization_id=settings.MOCK_ORGANIZATION_ID,
            employee_id=x_employee_id,
            is_authenticated=True,
            is_mock=True
        )
    
    # 返回用户上下文（当前为模拟）
    return UserContext(
        user_id=x_user_id,
        employee_id=x_employee_id,
        is_authenticated=True,
        is_mock=True
    )

# 导出依赖项
__all__ = [
    "UserContext",
    "get_current_user",
    "get_optional_user",
    "security"
]