"""
MEK-AI Python AI服务 - 修复版本
"""

import logging
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.utils.logger import setup_logging

# 配置日志
setup_logging()
logger = logging.getLogger(__name__)

# 创建应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="MEK-AI Python AI服务 - 企业级AI数字员工平台后端",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=True
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根路由
@app.get("/")
async def root():
    """根端点"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# 直接在这里注册路由，避免导入问题
from fastapi import APIRouter

# 创建健康检查路由器
health_router = APIRouter(prefix="/health", tags=["health"])

@health_router.get("/")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": settings.APP_NAME}

@health_router.get("/detailed")
async def detailed_health():
    """详细健康检查"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": "2024-01-01T00:00:00Z"
    }

# 创建市场路由器
marketplace_router = APIRouter(prefix="/marketplace", tags=["marketplace"])

@marketplace_router.get("/employees")
async def get_employees():
    """获取员工列表"""
    return {
        "items": [
            {
                "id": "emp-created-1",
                "name": "CEO决策大脑",
                "description": "为企业高层提供战略决策支持的AI助手"
            },
            {
                "id": "emp-created-2", 
                "name": "私域运营专家",
                "description": "专门负责私域流量运营的AI数字员工"
            }
        ],
        "total": 2,
        "page": 1,
        "page_size": 20
    }

@marketplace_router.get("/employees/{employee_id}")
async def get_employee(employee_id: str):
    """获取单个员工"""
    return {
        "id": employee_id,
        "name": f"员工{employee_id}",
        "description": "这是一个数字员工"
    }

# 创建API v1路由器
api_v1_router = APIRouter(prefix="/v1", tags=["v1"])
api_v1_router.include_router(health_router)
api_v1_router.include_router(marketplace_router)

# 注册主API路由
app.include_router(api_v1_router, prefix="/api")

# 路由调试端点
@app.get("/routes")
async def list_routes():
    """列出所有路由"""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
    return {"routes": routes}

# 启动日志
@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📊 环境: {settings.APP_ENVIRONMENT}")
    logger.info(f"🎯 主机: {settings.APP_HOST}:{settings.APP_PORT}")
    logger.info("✅ 应用启动完成")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_fixed:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
        log_level="info"
    )