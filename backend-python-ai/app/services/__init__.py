"""
服务层模块
"""

# 导入已有的服务
from app.services.ai.chat_service import chat_service
from app.services.memory.conversation_memory import conversation_memory_manager
from app.services.ai.model_manager import model_manager

# 新增导入
try:
    from app.services.employee_service import employee_service
except ImportError:
    # 如果模块还不存在，创建占位符
    employee_service = None

# 导出所有服务实例
__all__ = [
    "chat_service",
    "conversation_memory_manager",
    "model_manager",
    "employee_service"
]