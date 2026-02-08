"""
API v1端点模块
"""

# 导入所有端点路由
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.employees import router as employees_router
from app.api.v1.endpoints.marketplace import router as marketplace_router

# 导出所有路由
__all__ = [
    "health_router",
    "chat_router",
    "employees_router",
    "marketplace_router"
]