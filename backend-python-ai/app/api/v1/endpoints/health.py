"""
健康检查端点
提供应用健康状况和系统信息
"""

import platform
import sys
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import get_current_user
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 创建路由器
router = APIRouter()

@router.get("/", summary="健康检查", tags=["health"])
async def health_check() -> Dict[str, Any]:
    """
    基本健康检查端点
    
    返回：
        Dict: 包含服务状态和基本信息
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENVIRONMENT,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/detailed", summary="详细健康检查", tags=["health"])
async def detailed_health_check() -> Dict[str, Any]:
    """
    详细健康检查端点
    
    返回系统详细信息，包括：
    - 应用状态
    - 系统信息
    - Python环境
    - 配置概览
    - 关键服务状态
    
    返回：
        Dict: 包含详细系统信息的字典
    """
    
    # 收集系统信息
    system_info = {
        "platform": platform.platform(),
        "python_version": sys.version,
        "processor": platform.processor(),
        "machine": platform.machine(),
        "system": platform.system(),
        "release": platform.release()
    }
    
    # 收集应用信息
    app_info = {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENVIRONMENT,
        "debug": settings.APP_DEBUG,
        "log_level": settings.APP_LOG_LEVEL
    }
    
    # 检查关键配置
    config_checks = {
        "openai_api_key_configured": bool(settings.OPENAI_API_KEY),
        "vector_db_configured": True,  # 后续添加实际检查
        "upload_dir_exists": True,  # 后续添加实际检查
        "max_upload_size": settings.MAX_UPLOAD_SIZE,
        "allowed_extensions": settings.allowed_extensions_list
    }
    
    # 模拟服务状态检查（后续会替换为实际检查）
    service_checks = {
        "api_service": {
            "status": "healthy",
            "response_time": "0.001s",
            "details": "API服务运行正常"
        },
        "llm_service": {
            "status": "healthy" if settings.OPENAI_API_KEY else "unconfigured",
            "details": "OpenAI API已配置" if settings.OPENAI_API_KEY else "OpenAI API未配置"
        },
        "vector_db": {
            "status": "healthy",
            "details": "向量数据库连接正常"
        }
    }
    
    # 计算整体状态
    overall_status = "healthy"
    if not settings.OPENAI_API_KEY:
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "app": app_info,
        "system": system_info,
        "config": config_checks,
        "services": service_checks
    }

@router.get("/protected", summary="受保护的健康检查", tags=["health"])
async def protected_health_check(
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    受保护的健康检查端点
    
    需要用户认证，用于验证权限系统是否正常工作
    
    参数：
        current_user: 通过依赖注入获取的当前用户
        
    返回：
        Dict: 包含用户信息和健康状态的字典
    """
    
    logger.info(f"受保护的健康检查被调用 - 用户: {current_user.user_id}")
    
    return {
        "status": "healthy",
        "message": "受保护的健康检查通过",
        "timestamp": datetime.now().isoformat(),
        "user_info": {
            "user_id": current_user.user_id,
            "employee_id": current_user.employee_id,
            "organization_id": current_user.organization_id,
            "is_authenticated": current_user.is_authenticated,
            "is_mock": current_user.is_mock,
            "permissions": current_user.permissions
        },
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@router.get("/metrics", summary="应用指标", tags=["health"])
async def get_metrics() -> Dict[str, Any]:
    """
    获取应用性能指标
    
    返回基本指标信息，后续可以集成Prometheus
    
    返回：
        Dict: 包含应用指标的字典
    """
    
    # 导入psutil用于系统指标（如果可用）
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_usage = psutil.disk_usage("/")
        
        system_metrics = {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory_info.total,
                "available": memory_info.available,
                "percent": memory_info.percent,
                "used": memory_info.used
            },
            "disk": {
                "total": disk_usage.total,
                "used": disk_usage.used,
                "free": disk_usage.free,
                "percent": disk_usage.percent
            }
        }
    except ImportError:
        system_metrics = {
            "cpu_percent": None,
            "memory": {"error": "psutil未安装"},
            "disk": {"error": "psutil未安装"}
        }
    
    # 应用指标（后续会添加更多）
    app_metrics = {
        "uptime": "0:00:00",  # 后续添加实际计算
        "requests_served": 0,  # 后续添加计数器
        "active_connections": 0,
        "llm_calls": 0
    }
    
    return {
        "timestamp": datetime.now().isoformat(),
        "system": system_metrics,
        "application": app_metrics,
        "settings": {
            "environment": settings.APP_ENVIRONMENT,
            "debug": settings.APP_DEBUG,
            "log_level": settings.APP_LOG_LEVEL
        }
    }

@router.get("/version", summary="版本信息", tags=["health"])
async def get_version() -> Dict[str, Any]:
    """
    获取应用版本信息
    
    返回：
        Dict: 包含版本信息的字典
    """
    
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "build": "development",  # 后续从环境变量获取
        "commit": "unknown",  # 后续从环境变量获取
        "build_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "python_version": sys.version,
        "fastapi_version": "0.104.1",  # 后续从导入获取
        "langchain_version": "0.0.340"  # 后续从导入获取
    }

@router.get("/config", summary="配置信息", tags=["health"])
async def get_config_summary() -> Dict[str, Any]:
    """
    获取配置信息摘要
    
    注意：不返回敏感信息如API密钥
    
    返回：
        Dict: 包含配置摘要的字典
    """
    
    # 过滤敏感配置
    safe_config = {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "app_environment": settings.APP_ENVIRONMENT,
        "app_debug": settings.APP_DEBUG,
        "app_host": settings.APP_HOST,
        "app_port": settings.APP_PORT,
        "app_log_level": settings.APP_LOG_LEVEL,
        "cors_origins": settings.CORS_ORIGINS,
        "default_model_provider": settings.DEFAULT_MODEL_PROVIDER,
        "default_model_name": settings.DEFAULT_MODEL_NAME,
        "model_temperature": settings.MODEL_TEMPERATURE,
        "model_max_tokens": settings.MODEL_MAX_TOKENS,
        "vector_db_type": settings.VECTOR_DB_TYPE,
        "upload_dir": settings.UPLOAD_DIR,
        "max_upload_size": settings.MAX_UPLOAD_SIZE,
        "allowed_extensions": settings.allowed_extensions_list,
        "redis_host": settings.REDIS_HOST,
        "redis_port": settings.REDIS_PORT,
        "enable_metrics": settings.ENABLE_METRICS,
        "is_development": settings.is_development,
        "is_production": settings.is_production,
        "is_testing": settings.is_testing
    }
    
    # 检查敏感配置是否已设置（但不显示值）
    config_checks = {
        "openai_api_key_set": bool(settings.OPENAI_API_KEY),
        "anthropic_api_key_set": bool(settings.ANTHROPIC_API_KEY),
        "gemini_api_key_set": bool(settings.GEMINI_API_KEY),
        "redis_password_set": bool(settings.REDIS_PASSWORD),
        "secret_key_set": bool(settings.SECRET_KEY) and settings.SECRET_KEY != "your-secret-key-here-change-in-production"
    }
    
    return {
        "timestamp": datetime.now().isoformat(),
        "config": safe_config,
        "security_checks": config_checks
    }

# 导出路由器
__all__ = ["router"]