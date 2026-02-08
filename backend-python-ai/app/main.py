"""
MEK-AI Python AI服务主应用入口
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.utils.logger import setup_logging
from app.api.router import router
from app.api.middleware import (
    LoggingMiddleware,
    RequestIDMiddleware,
    ExceptionHandlingMiddleware
)

# 配置日志
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    Args:
        app: FastAPI应用实例
    """
    # 启动时执行
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"环境: {settings.APP_ENVIRONMENT}")
    logger.info(f"主机: {settings.APP_HOST}:{settings.APP_PORT}")
    
    # 在这里初始化数据库连接、缓存等
    try:
        # 初始化向量数据库连接（后续实现）
        logger.info("初始化向量数据库连接...")
        
        # 初始化AI模型管理器（确保已导入）
        from app.services.ai.model_manager import model_manager
        logger.info("AI模型管理器初始化状态: 已完成")
        
        # 初始化聊天服务
        from app.services.ai.chat_service import chat_service
        logger.info("聊天服务初始化状态: 已完成")
        
        # 初始化对话记忆管理器
        from app.services.memory.conversation_memory import conversation_memory_manager
        logger.info("对话记忆管理器初始化状态: 已完成")
        
        # 检查API密钥配置
        if settings.OPENAI_API_KEY:
            logger.info("OpenAI API密钥: 已配置")
        else:
            logger.warning("OpenAI API密钥: 未配置，部分功能可能受限")
        
        logger.info("应用启动完成")
    except Exception as e:
        logger.error(f"应用启动失败: {e}", exc_info=True)
        raise
    
    yield  # 应用运行中
    
    # 关闭时执行
    logger.info("正在关闭应用...")
    
    try:
        # 清理资源
        logger.info("清理聊天服务...")
        from app.services.ai.chat_service import chat_service
        chat_service.clear_employee_agents()
        
        logger.info("清理对话记忆...")
        from app.services.memory.conversation_memory import conversation_memory_manager
        conversation_memory_manager.clear_all_conversations()
        
        logger.info("应用已安全关闭")
    except Exception as e:
        logger.error(f"应用关闭时出错: {e}", exc_info=True)

def create_application() -> FastAPI:
    """
    创建FastAPI应用实例
    
    Returns:
        FastAPI: 配置完成的FastAPI应用实例
    """
    # 创建应用实例
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="MEK-AI Python AI服务 - 企业级AI数字员工平台后端",
        docs_url="/docs" if settings.APP_ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.APP_ENVIRONMENT != "production" else None,
        openapi_url="/openapi.json" if settings.APP_ENVIRONMENT != "production" else None,
        lifespan=lifespan,
        debug=settings.APP_DEBUG
    )
    
    # 添加CORS中间件 - 必须最先添加以确保正确处理预检请求
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time", "X-User-ID", "X-Employee-ID"],
        max_age=600  # 预检请求缓存10分钟
    )
    
    # 添加自定义中间件
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(ExceptionHandlingMiddleware)
    
    # 注册API路由
    app.include_router(router)
    
    # 添加根路由
    @app.get("/")
    async def root() -> Dict[str, Any]:
        """
        根端点 - 服务状态
        
        Returns:
            Dict: 服务基本信息
        """
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "environment": settings.APP_ENVIRONMENT,
            "docs": "/docs" if settings.APP_ENVIRONMENT != "production" else None,
            "health": "/api/v1/health"
        }
    @app.get("/routes")
    async def list_routes():
        """列出所有已注册的路由"""
        routes = []
        for route in app.routes:
            if hasattr(route, "methods"):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": route.name
                })
        return {"routes": routes}
    return app

# 创建应用实例
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_RELOAD,
        log_level=settings.APP_LOG_LEVEL.lower()
    )