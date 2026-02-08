"""
自定义中间件
包括请求ID、日志、异常处理等
"""

import uuid
import time
from typing import Callable, Dict, Any
from datetime import datetime

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.utils.logger import get_logger
from app.config.constants import ErrorCode

logger = get_logger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    请求ID中间件
    
    为每个请求生成唯一的请求ID，便于追踪
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 将请求ID存储到请求状态中
        request.state.request_id = request_id
        
        # 调用下一个中间件或路由处理函数
        response = await call_next(request)
        
        # 在响应头中添加请求ID
        response.headers["X-Request-ID"] = request_id
        
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    日志中间件
    
    记录每个请求的详细信息
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求ID
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        
        # 记录请求信息
        logger.info(
            f"[{request_id}] 收到请求 - "
            f"method: {request.method}, "
            f"path: {request.url.path}, "
            f"client: {request.client.host if request.client else 'unknown'}"
        )
        
        # 记录请求头（敏感信息已过滤）
        if settings.is_development:
            filtered_headers = {
                k: v for k, v in request.headers.items()
                if k.lower() not in ['authorization', 'cookie', 'x-api-key']
            }
            logger.debug(f"[{request_id}] 请求头: {filtered_headers}")
        
        try:
            # 调用下一个中间件或路由处理函数
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(
                f"[{request_id}] 请求完成 - "
                f"status: {response.status_code}, "
                f"duration: {process_time:.3f}s"
            )
            
            # 添加处理时间到响应头
            response.headers["X-Response-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            # 计算错误处理时间
            process_time = time.time() - start_time
            
            # 记录错误信息
            logger.error(
                f"[{request_id}] 请求处理出错 - "
                f"error: {str(e)}, "
                f"duration: {process_time:.3f}s",
                exc_info=True
            )
            
            # 重新抛出异常，让异常处理中间件处理
            raise

class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """
    异常处理中间件
    
    统一处理应用中的异常，返回标准格式的错误响应
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
            
        except HTTPException as http_exc:
            # 处理HTTP异常（如401, 403, 404等）
            request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
            
            logger.warning(
                f"[{request_id}] HTTP异常 - "
                f"status: {http_exc.status_code}, "
                f"detail: {http_exc.detail}"
            )
            
            return JSONResponse(
                status_code=http_exc.status_code,
                content={
                    "success": False,
                    "error_code": self._get_error_code(http_exc.status_code),
                    "error_message": http_exc.detail,
                    "request_id": request_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as exc:
            # 处理未捕获的异常
            request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
            
            logger.error(
                f"[{request_id}] 未捕获的异常 - "
                f"type: {type(exc).__name__}, "
                f"message: {str(exc)}",
                exc_info=True
            )
            
            # 在生产环境中隐藏详细错误信息
            if settings.is_production:
                error_message = "服务器内部错误，请联系管理员"
            else:
                error_message = f"{type(exc).__name__}: {str(exc)}"
            
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error_code": ErrorCode.UNKNOWN_ERROR,
                    "error_message": error_message,
                    "request_id": request_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _get_error_code(self, status_code: int) -> int:
        """
        根据HTTP状态码获取对应的错误码
        
        Args:
            status_code: HTTP状态码
            
        Returns:
            int: 对应的错误码
        """
        error_mapping = {
            400: ErrorCode.VALIDATION_ERROR,
            401: ErrorCode.AUTHENTICATION_ERROR,
            403: ErrorCode.AUTHORIZATION_ERROR,
            404: ErrorCode.RESOURCE_NOT_FOUND,
            429: ErrorCode.MODEL_RATE_LIMIT,
            500: ErrorCode.UNKNOWN_ERROR,
            502: ErrorCode.MODEL_API_ERROR,
            503: ErrorCode.VECTOR_DB_ERROR,
            504: ErrorCode.MODEL_TIMEOUT,
        }
        
        return error_mapping.get(status_code, ErrorCode.UNKNOWN_ERROR)

# 创建CORS中间件工厂函数
def create_cors_middleware():
    """创建CORS中间件"""
    return CORSMiddleware(
        app=None,  # 将在应用中添加
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        expose_headers=["X-Request-ID", "X-Response-Time"]
    )

# 导出中间件
__all__ = [
    "RequestIDMiddleware",
    "LoggingMiddleware",
    "ExceptionHandlingMiddleware",
    "create_cors_middleware"
]