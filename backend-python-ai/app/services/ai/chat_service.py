"""
聊天服务
处理聊天逻辑，协调智能体、记忆和模型
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.ai.model_manager import model_manager
from app.services.memory.conversation_memory import conversation_memory_manager
from app.services.employee_service import employee_service
from app.agents.digital_employee_agent import DigitalEmployeeAgent
from app.config.settings import settings
from app.utils.logger import LoggerMixin, log_execution_time

class ChatService(LoggerMixin):
    """
    聊天服务
    处理所有聊天相关的业务逻辑
    """
    
    def __init__(self):
        """初始化聊天服务"""
        super().__init__()
        
        # 存储员工智能体实例
        self._employee_agents: Dict[str, DigitalEmployeeAgent] = {}
        
        self.log_info("聊天服务初始化完成")
    
    @log_execution_time()
    async def process_chat_message(
        self,
        db: Session,
        message: str,
        employee_id: str,
        conversation_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
        model_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理聊天消息
        
        Args:
            db: 数据库会话
            message: 用户消息
            employee_id: 员工ID
            conversation_id: 对话ID，如果为None则创建新对话
            user_context: 用户上下文
            model_config: 模型配置覆盖
            
        Returns:
            Dict: 聊天响应
        """
        
        # 记录开始时间
        start_time = datetime.now()
        
        try:
            # 1. 验证输入
            if not message or not message.strip():
                return self._create_validation_error("消息不能为空")
            
            if not employee_id:
                return self._create_validation_error("员工ID不能为空")
            
            # 2. 获取或创建对话
            conversation_info = await self._get_or_create_conversation(
                db=db,
                conversation_id=conversation_id,
                employee_id=employee_id,
                user_context=user_context
            )
            
            # 3. 获取或创建员工智能体
            employee_agent = await self._get_or_create_employee_agent(
                db=db,
                employee_id=employee_id,
                model_config=model_config
            )
            
            if not employee_agent:
                return self._create_agent_error(f"无法创建员工智能体: {employee_id}")
            
            # 4. 准备上下文
            context = self._prepare_context(
                db=db,
                conversation_info=conversation_info,
                user_context=user_context
            )
            
            # 5. 处理消息
            result = await employee_agent.process_message(message, context)
            
            # 6. 如果处理成功，保存消息到记忆
            if result.get("success", False):
                # 保存用户消息
                conversation_memory_manager.add_message(
                    conversation_id=conversation_info["conversation_id"],
                    role="user",
                    content=message,
                    metadata={
                        "user_id": user_context.get("user_id") if user_context else None,
                        "message_id": result.get("message_id", str(uuid.uuid4()))
                    }
                )
                
                # 保存AI回复
                conversation_memory_manager.add_message(
                    conversation_id=conversation_info["conversation_id"],
                    role="assistant",
                    content=result.get("response", ""),
                    metadata={
                        "employee_id": employee_id,
                        "message_id": result.get("message_id", str(uuid.uuid4())),
                        "model_info": result.get("model_info", {})
                    }
                )
                
                # 更新响应中的对话ID
                if not result.get("conversation_id"):
                    result["conversation_id"] = conversation_info["conversation_id"]
            
            # 7. 计算总处理时间
            total_time = (datetime.now() - start_time).total_seconds()
            result["total_processing_time"] = total_time
            
            self.log_info(f"聊天处理完成 - "
                         f"员工: {employee_id}, "
                         f"对话: {conversation_info['conversation_id']}, "
                         f"耗时: {total_time:.3f}s")
            
            return result
            
        except Exception as e:
            # 记录错误
            self.log_error(f"处理聊天消息时出错: {str(e)}", error=e)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return self._create_error_response(
                error_message="处理聊天消息时发生错误",
                details=str(e),
                processing_time=processing_time
            )
    
    async def _get_or_create_conversation(
        self,
        db: Session,
        conversation_id: Optional[str],
        employee_id: str,
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        获取或创建对话
        
        Args:
            db: 数据库会话
            conversation_id: 对话ID
            employee_id: 员工ID
            user_context: 用户上下文
            
        Returns:
            Dict: 对话信息
        """
        
        # 如果有对话ID，检查对话是否存在
        if conversation_id:
            conversation_state = conversation_memory_manager.get_conversation_state(db, conversation_id)
            
            if conversation_state:
                # 验证对话属于当前员工
                if conversation_state.employee_id != employee_id:
                    self.log_warning(f"对话 {conversation_id} 不属于员工 {employee_id}")
                    # 仍然返回对话信息，但记录警告
                
                return {
                    "conversation_id": conversation_id,
                    "exists": True,
                    "employee_id": conversation_state.employee_id
                }
        
        # 创建新对话
        new_conversation_id = conversation_memory_manager.create_conversation(
            db=db,
            employee_id=employee_id,
            user_id=user_context.get("user_id") if user_context else None,
            organization_id=user_context.get("organization_id") if user_context else None,
            metadata={
                "created_by_service": "chat_service",
                "employee_id": employee_id,
                "user_context": user_context
            }
        )
        
        self.log_info(f"创建新对话: {new_conversation_id}, 员工: {employee_id}")
        
        return {
            "conversation_id": new_conversation_id,
            "exists": False,
            "employee_id": employee_id
        }
    
    async def _get_or_create_employee_agent(
        self,
        db: Session,
        employee_id: str,
        model_config: Optional[Dict[str, Any]] = None
    ) -> Optional[DigitalEmployeeAgent]:
        """
        获取或创建员工智能体
        
        Args:
            db: 数据库会话
            employee_id: 员工ID
            model_config: 模型配置覆盖
            
        Returns:
            Optional[DigitalEmployeeAgent]: 员工智能体，如果创建失败则返回None
        """
        
        # 检查是否已有智能体实例
        if employee_id in self._employee_agents:
            return self._employee_agents[employee_id]
        
        # 创建新的智能体
        try:
            # 获取模型配置
            final_model_config = model_config or {}
            
            # 创建模型配置对象
            from app.services.ai.model_manager import ModelConfig
            
            config = model_manager.create_model_config_from_request(
                provider=final_model_config.get("provider"),
                model_name=final_model_config.get("model_name"),
                temperature=final_model_config.get("temperature"),
                max_tokens=final_model_config.get("max_tokens")
            )
            
            # 验证配置
            if not model_manager.validate_model_config(config):
                self.log_error(f"模型配置无效: {config}")
                return None
            
            # 创建聊天模型
            chat_model = model_manager.create_chat_model(config)
            
            # 获取员工配置（从员工服务获取真实数据）
            employee_config = self._get_employee_config(db, employee_id)
            
            # 创建工具列表
            tools = []
            
            # 如果员工配置了知识库，添加知识库检索工具
            knowledge_base_ids = employee_config.get("knowledge_base_ids", [])
            if knowledge_base_ids:
                from app.agents.tools.knowledge_retrieval_tool import create_knowledge_retrieval_tool
                knowledge_tool = create_knowledge_retrieval_tool(knowledge_base_ids)
                tools.append(knowledge_tool)
                self.log_info(f"为员工 {employee_id} 添加知识库检索工具，知识库: {knowledge_base_ids}")
            
            # 创建智能体
            agent = DigitalEmployeeAgent(
                employee_id=employee_id,
                employee_config=employee_config,
                llm=chat_model,
                tools=tools
            )
            
            # 存储智能体实例
            self._employee_agents[employee_id] = agent
            
            self.log_info(f"创建员工智能体: {employee_id}")
            
            return agent
            
        except Exception as e:
            self.log_error(f"创建员工智能体失败: {employee_id}, 错误: {str(e)}", error=e)
            return None
    
    def _get_employee_config(self, db: Session, employee_id: str) -> Dict[str, Any]:
        """
        获取员工配置
        
        从员工服务获取真实员工数据
        
        Args:
            db: 数据库会话
            employee_id: 员工ID
            
        Returns:
            Dict: 员工配置
        """
        
        # 从员工服务获取真实员工数据
        employee = employee_service.get_employee(db, employee_id)
        
        if employee:
            # 使用真实员工数据
            return {
                "name": employee.name,
                "persona": employee.prompt or "专业的数字员工，为用户提供帮助和服务。",
                "skills": employee.skills or ["基本对话", "信息提供"],
                "temperature": settings.MODEL_TEMPERATURE,
                "max_tokens": settings.MODEL_MAX_TOKENS,
                "prompt": employee.prompt,
                "knowledge_base_ids": employee.knowledge_base_ids,
                "model": employee.model,
                "industry": employee.industry,
                "role": employee.role,
            }
        
        # 如果找不到员工，返回默认配置
        self.log_warning(f"找不到员工 {employee_id}，使用默认配置")
        return {
            "name": f"员工{employee_id}",
            "persona": "专业的数字员工，为用户提供帮助和服务。",
            "skills": ["基本对话", "信息提供"],
            "temperature": settings.MODEL_TEMPERATURE,
            "max_tokens": settings.MODEL_MAX_TOKENS
        }
    
    def _prepare_context(
        self,
        db: Session,
        conversation_info: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        准备上下文信息
        
        Args:
            db: 数据库会话
            conversation_info: 对话信息
            user_context: 用户上下文
            
        Returns:
            Dict: 上下文信息
        """
        
        context = {
            "conversation_id": conversation_info["conversation_id"],
            "employee_id": conversation_info["employee_id"]
        }
        
        # 添加用户上下文
        if user_context:
            context.update({
                "user_id": user_context.get("user_id"),
                "organization_id": user_context.get("organization_id"),
                "user_permissions": user_context.get("permissions", [])
            })
        
        # 获取对话历史
        if conversation_info["conversation_id"]:
            history = conversation_memory_manager.get_conversation_history(
                db=db,
                conversation_id=conversation_info["conversation_id"],
                limit=10  # 限制历史条数
            )
            context["chat_history"] = history
        
        return context
    
    def _create_validation_error(self, message: str) -> Dict[str, Any]:
        """创建验证错误响应"""
        
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": message
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_agent_error(self, message: str) -> Dict[str, Any]:
        """创建智能体错误响应"""
        
        return {
            "success": False,
            "error": {
                "code": "AGENT_ERROR",
                "message": message
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_error_response(
        self,
        error_message: str,
        details: Optional[str] = None,
        processing_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """创建通用错误响应"""
        
        error_response = {
            "success": False,
            "error": {
                "code": "CHAT_SERVICE_ERROR",
                "message": error_message
            },
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            error_response["error"]["details"] = details
        
        if processing_time is not None:
            error_response["processing_time"] = processing_time
        
        return error_response
    
    def get_employee_agent(self, employee_id: str) -> Optional[DigitalEmployeeAgent]:
        """
        获取员工智能体
        
        Args:
            employee_id: 员工ID
            
        Returns:
            Optional[DigitalEmployeeAgent]: 员工智能体，如果不存在则返回None
        """
        
        return self._employee_agents.get(employee_id)
    
    def list_employee_agents(self) -> Dict[str, Any]:
        """
        列出所有员工智能体
        
        Returns:
            Dict: 智能体列表信息
        """
        
        agents_info = []
        
        for emp_id, agent in self._employee_agents.items():
            agents_info.append({
                "employee_id": emp_id,
                "agent_name": agent.config.name,
                "tools_count": len(agent.tools)
            })
        
        return {
            "total": len(agents_info),
            "agents": agents_info
        }
    
    def clear_employee_agents(self):
        """清除所有员工智能体"""
        
        count = len(self._employee_agents)
        self._employee_agents.clear()
        
        self.log_info(f"清除所有员工智能体，共 {count} 个")

# 创建全局聊天服务实例
chat_service = ChatService()
