"""
智能体模块
包含所有LangChain智能体定义
"""

from app.agents.base_agent import BaseAgent
from app.agents.digital_employee_agent import DigitalEmployeeAgent

__all__ = [
    "BaseAgent",
    "DigitalEmployeeAgent"
]