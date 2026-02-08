"""
API路由聚合
将所有API路由集中注册到FastAPI应用
"""

from fastapi import APIRouter

# 导入所有端点路由
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.chat import router as chat_router

# 尝试导入新路由
try:
    from app.api.v1.endpoints.employees import router as employees_router
    from app.api.v1.endpoints.marketplace import router as marketplace_router
    from app.api.v1.endpoints.knowledge import router as knowledge_router
except ImportError as e:
    print(f"警告: 无法导入新路由模块 - {e}")
    # 创建空的路由器作为占位符
    employees_router = APIRouter()
    marketplace_router = APIRouter()
    knowledge_router = APIRouter()

# 创建API v1路由器
api_v1_router = APIRouter(prefix="/api/v1")

# 注册健康检查路由
api_v1_router.include_router(health_router, prefix="/health", tags=["health"])

# 注册聊天路由
api_v1_router.include_router(chat_router, prefix="/chat", tags=["chat"])

# 注册员工管理路由
api_v1_router.include_router(employees_router, tags=["employees"])

# 注册市场广场路由
api_v1_router.include_router(marketplace_router, tags=["marketplace"])

# 注册知识库路由
api_v1_router.include_router(knowledge_router, tags=["knowledge-bases"])

# 创建主路由器
router = APIRouter()

# 包含API v1路由器
router.include_router(api_v1_router)

# 导出路由器
__all__ = ["router"]