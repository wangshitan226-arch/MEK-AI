"""
数字员工智能体
为MEK-AI数字员工定制的智能体实现
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from langchain.agents import AgentExecutor
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# 导入 conversation_memory_manager 以使用新的方法
from app.services.memory.conversation_memory import conversation_memory_manager
from app.agents.base_agent import BaseAgent, AgentConfig
from app.config.settings import settings
from app.utils.logger import LoggerMixin

class DigitalEmployeeAgent(BaseAgent):
    """
    数字员工智能体
    扩展基类，添加数字员工特定功能
    """
    
    def __init__(
        self,
        employee_id: str,
        employee_config: Dict[str, Any],
        llm: BaseChatModel,
        tools: Optional[list] = None
    ):
        """
        初始化数字员工智能体
        
        Args:
            employee_id: 员工ID
            employee_config: 员工配置（人设、技能等）
            llm: 语言模型实例
            tools: 工具列表
        """
        
        # 从员工配置创建智能体配置
        config = self._create_agent_config(employee_id, employee_config, tools or [])
        
        # 调用父类初始化
        super().__init__(config, llm)
        
        # 数字员工特定属性
        self.employee_id = employee_id
        self.employee_config = employee_config
        
        # 初始化智能体
        try:
            self.initialize()
            self.log_info(f"数字员工智能体初始化完成: {employee_id}")
        except Exception as e:
            self.log_error(f"数字员工智能体初始化失败: {employee_id}, 错误: {str(e)}", error=e)
            # 即使初始化失败，我们仍然创建智能体，但使用简化模式
            self.agent_executor = None
    
    def _create_agent_config(
        self,
        employee_id: str,
        employee_config: Dict[str, Any],
        tools: list
    ) -> AgentConfig:
        """
        从员工配置创建智能体配置
        
        Args:
            employee_id: 员工ID
            employee_config: 员工配置
            tools: 工具列表
            
        Returns:
            AgentConfig: 智能体配置
        """
        
        # 获取员工基本信息
        name = employee_config.get("name", f"员工{employee_id}")
        persona = employee_config.get("persona", "")
        skills = employee_config.get("skills", [])
        
        # 构建系统提示
        system_prompt = self._build_system_prompt(name, persona, skills)
        
        # 创建配置
        config = AgentConfig(
            name=f"digital_employee_{employee_id}",
            description=f"数字员工: {name}",
            system_prompt=system_prompt,
            temperature=employee_config.get("temperature", settings.MODEL_TEMPERATURE),
            max_tokens=employee_config.get("max_tokens", settings.MODEL_MAX_TOKENS),
            tools=tools,
            max_iterations=employee_config.get("max_iterations", 5)
        )
        
        return config
    
    def _build_system_prompt(self, name: str, persona: str, skills: list) -> str:
        """
        构建系统提示
        
        Args:
            name: 员工姓名
            persona: 人设描述
            skills: 技能列表
            
        Returns:
            str: 系统提示
        """
        
        # 基础提示
        prompt_parts = [
            f"你是一个专业的数字员工，名为 {name}。",
            "你的职责是为用户提供专业的帮助和服务。"
        ]
        
        # 添加人设描述
        if persona:
            prompt_parts.append(f"你的个人风格和特点：{persona}")
        
        # 添加技能描述
        if skills:
            skills_text = "、".join(skills)
            prompt_parts.append(f"你擅长：{skills_text}。")
        
        # 添加通用指令
        prompt_parts.extend([
            "请以友好、专业、有帮助的态度回答用户的问题。",
            "如果用户的问题超出你的能力范围，请诚实地告知用户。",
            "尽量提供详细、准确的回答。",
            "使用中文进行交流，除非用户明确要求使用其他语言。"
        ])
        
        return "\n".join(prompt_parts)
    
    async def process_message(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        start_time = datetime.now()
        
        try:
            if not self.agent_executor:
                return await self._fallback_to_direct_llm(message, context, start_time)
            
            # 获取对话历史 - 从 context 中获取（chat_service 已经查询并放入）
            # 或者自己查询，使用 get_conversation_history 返回字典格式
            conversation_id = context.get("conversation_id")
            chat_history = context.get("chat_history", [])
            
            # 如果 context 中没有，自己查询
            if not chat_history and conversation_id:
                chat_history = conversation_memory_manager.get_conversation_history(
                    conversation_id, 
                    limit=10
                )
            
            # 根据是否有工具，使用不同的输入格式
            if self.tools:
                # 有工具时使用 ReAct Agent，需要提供 chat_history 和 input
                # system_prompt 已经在 prompt 模板中通过 prefix 设置
                # 注意：chat_history 是字典列表，使用 .get() 方法访问
                formatted_history = []
                for msg in chat_history:
                    # 字典格式：{"role": "user"/"assistant", "content": "..."}
                    role = "User" if msg.get('role') == 'user' else "AI"
                    formatted_history.append(f"{role}: {msg.get('content', '')}")

                inputs = {
                    "input": message,
                    "chat_history": "\n".join(formatted_history) if formatted_history else "No previous conversation."
                }
            else:
                # 无工具时使用 LLMChain，只需要 input
                # 历史和系统提示已经通过 memory 和 prompt 模板处理
                inputs = {
                    "input": message
                }
            
            # 执行
            result = await self.agent_executor.ainvoke(inputs)
            
            # 处理结果
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 【关键修复】处理 LLMChain 返回的结果格式
            # LLMChain 返回的是字典，包含 "text" 键
            if isinstance(result, dict):
                response_text = result.get("text", result.get("output", result.get("response", str(result))))
            elif hasattr(result, 'content'):
                response_text = result.content
            else:
                response_text = str(result)
            
            # 构建成功响应
            response = self._create_success_response(
                message=message,
                response=response_text,
                context=context,
                processing_time=processing_time,
                intermediate_steps=[]
            )
            
            return response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.log_error(f"处理消息时出错: {str(e)}", error=e)
            return self._create_error_response(str(e), processing_time)
    
    async def _fallback_to_direct_llm(
        self,
        message: str,
        context: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        当智能体执行器不可用时，直接使用LLM处理消息
        
        Args:
            message: 用户消息
            context: 上下文信息
            start_time: 开始时间
            
        Returns:
            Dict: 处理结果
        """
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            # 构建消息列表
            messages = [
                SystemMessage(content=self.config.system_prompt),
                HumanMessage(content=message)
            ]
            
            # 直接调用LLM
            response = await self.llm.ainvoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.log_info(f"使用直接LLM回退处理消息成功，耗时: {processing_time:.3f}s")
            
            return self._create_success_response(
                message=message,
                response=response_text,
                context=context,
                processing_time=processing_time,
                intermediate_steps=[]
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.log_error(f"直接LLM回退处理失败: {str(e)}", error=e)
            return self._create_error_response(str(e), processing_time)
    
    def _prepare_agent_inputs(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备智能体输入参数
        
        Args:
            message: 用户消息
            context: 上下文信息
            
        Returns:
            Dict: 智能体输入参数字典
        """
        
        conversation_id = context.get("conversation_id")
        
        # 获取LangChain格式的对话历史
        chat_history: List[BaseMessage] = []
        if conversation_id:
            chat_history = conversation_memory_manager.get_conversation_messages(
                conversation_id, 
                limit=10
            )
        
        # 【关键修复】确保 agent_scratchpad 是 BaseMessage 列表
        # 即使为空，也必须是 BaseMessage 类型的空列表
        # 但根据 ReAct 代理模式，我们不应该手动提供它，而是让executor处理
        
        # 因此，最简单的修复：完全移除 agent_scratchpad 键
        # 让 LangChain 内部机制处理它
        inputs = {
            "input": message,
            "chat_history": chat_history,
            # 注意：不包含 agent_scratchpad 键
        }
        
        self.log_debug(f"准备智能体输入: input={message[:50]}..., history_len={len(chat_history)}")
        
        return inputs
    
    def _create_success_response(
        self,
        message: str,
        response: str,
        context: Dict[str, Any],
        processing_time: float,
        intermediate_steps: list
    ) -> Dict[str, Any]:
        """
        创建成功响应
        
        Args:
            message: 原始消息
            response: AI回复
            context: 上下文
            processing_time: 处理时间
            intermediate_steps: 中间步骤
            
        Returns:
            Dict: 响应数据
        """
        
        # 生成消息ID
        message_id = str(uuid.uuid4())
        
        return {
            "success": True,
            "message_id": message_id,
            "conversation_id": context.get("conversation_id"),
            "employee_id": self.employee_id,
            "user_id": context.get("user_id"),
            "original_message": message,
            "response": response,
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat(),
            "model_info": {
                "provider": self.config.name.split("_")[-1] if "_" in self.config.name else "unknown",
                "model": getattr(self.llm, "model_name", "unknown"),
                "temperature": self.config.temperature
            },
            "metadata": {
                "intermediate_steps_count": len(intermediate_steps),
                "agent_name": self.config.name
            }
        }
    
    def _create_error_response(
        self,
        error_message: str,
        processing_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        创建错误响应
        
        Args:
            error_message: 错误消息
            processing_time: 处理时间
            
        Returns:
            Dict: 错误响应数据
        """
        
        return {
            "success": False,
            "error": {
                "code": "AGENT_ERROR",
                "message": error_message,
                "details": f"数字员工智能体处理失败: {self.employee_id}"
            },
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat()
        }
    
    def update_employee_config(self, new_config: Dict[str, Any]):
        """
        更新员工配置
        
        Args:
            new_config: 新配置
        """
        
        # 合并配置
        self.employee_config.update(new_config)
        
        # 重新创建智能体配置
        config = self._create_agent_config(
            self.employee_id,
            self.employee_config,
            self.tools
        )
        
        # 更新配置
        self.config = config
        
        # 重新初始化智能体
        self.initialize()
        
        self.log_info(f"更新员工配置: {self.employee_id}")
    
    def get_employee_info(self) -> Dict[str, Any]:
        """
        获取员工信息
        
        Returns:
            Dict: 员工信息
        """
        
        return {
            "employee_id": self.employee_id,
            "name": self.employee_config.get("name", ""),
            "persona": self.employee_config.get("persona", ""),
            "skills": self.employee_config.get("skills", []),
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "tools_count": len(self.tools),
            "agent_name": self.config.name,
            "agent_initialized": self.agent_executor is not None
        }