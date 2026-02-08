"""
智能体基类
定义所有智能体的共同接口和行为
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.tools import BaseTool
from langchain_core.language_models.chat_models import BaseChatModel

from app.utils.logger import LoggerMixin

@dataclass
class AgentConfig:
    """智能体配置数据类"""
    
    name: str
    description: str
    system_prompt: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    tools: List[BaseTool] = None
    max_iterations: int = 5

class BaseAgent(ABC, LoggerMixin):
    """
    智能体基类
    所有智能体都应该继承此类
    """
    
    def __init__(
        self,
        config: AgentConfig,
        llm: BaseChatModel,
        memory_key: str = "chat_history"
    ):
        """
        初始化智能体
        
        Args:
            config: 智能体配置
            llm: 语言模型实例
            memory_key: 记忆键名
        """
        super().__init__()
        
        self.config = config
        self.llm = llm
        self.memory_key = memory_key
        
        # 智能体执行器（子类实现）
        self.agent_executor: Optional[AgentExecutor] = None
        
        # 初始化工具
        self.tools = config.tools or []
        
        self.log_info(f"初始化智能体: {config.name}")
    
    def initialize(self):
        """初始化智能体执行器 - 直接构建ReAct代理，避免兼容性问题"""
        try:
            from langchain.agents import XMLAgent
            from langchain_core.prompts import PromptTemplate
            
            # 1. 使用更兼容的XMLAgent（它实际上是ReAct的一种变体）
            # 首先定义工具描述
            tools_description = "\n".join([
                f"{tool.name}: {tool.description}"
                for tool in self.tools
            ]) if self.tools else "没有可用的工具"
            
            tool_names = ", ".join([tool.name for tool in self.tools]) if self.tools else "无"
            
            # 2. 构建系统提示（包含工具信息）
            system_prompt_with_tools = f"""{self.config.system_prompt}

你可以使用的工具：
{tools_description}

工具名称列表: {tool_names}

当你需要执行操作时，请按照以下格式思考：
Thought: 我需要做什么
Action: 工具名称
Action Input: 工具的输入参数
Observation: 工具返回的结果
...（这个循环可以重复多次）
Thought: 我现在知道了最终答案
Final Answer: 最终答案

注意：如果用户的问题不需要使用工具，请直接回答。"""
            
            # 3. 创建提示模板（简化版，避免复杂的变量传递问题）
            prompt = PromptTemplate.from_template(
                """{system_prompt}

历史对话：
{chat_history}

当前输入：{input}

请根据以上信息进行回应："""
            )
            
            # 4. 由于当前工具列表为空，我们使用最简单的代理
            # 对于无工具的情况，实际上不需要完整的ReAct代理
            # 我们创建一个简单的链来处理
            from langchain.chains import LLMChain
            from langchain.agents import Tool, AgentExecutor, ZeroShotAgent
            
            # 如果确实没有工具，创建简单的对话链
            if not self.tools:
                self.log_info("无工具模式：创建简单对话链")
                from langchain.chains import LLMChain
                from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
                from langchain.memory import ConversationBufferMemory
                
                # 创建包含系统提示的聊天提示模板
                prompt = ChatPromptTemplate.from_messages([
                    SystemMessagePromptTemplate.from_template(self.config.system_prompt),
                    MessagesPlaceholder(variable_name="history"),
                    HumanMessagePromptTemplate.from_template("{input}")
                ])
                
                memory = ConversationBufferMemory(
                    memory_key="history",
                    return_messages=True
                )
                
                # 创建LLM链（使用正确的prompt和memory）
                self.agent_executor = LLMChain(
                    llm=self.llm,
                    prompt=prompt,
                    memory=memory,
                    verbose=True
                )
            else:
                # 有工具时创建ReAct代理
                self.log_info(f"创建ReAct代理，工具数: {len(self.tools)}")
                
                # 使用ZeroShotAgent（ReAct代理的实现）
                agent = ZeroShotAgent(
                    llm_chain=LLMChain(llm=self.llm, prompt=prompt),
                    tools=self.tools,
                    verbose=True
                )
                
                self.agent_executor = AgentExecutor.from_agent_and_tools(
                    agent=agent,
                    tools=self.tools,
                    verbose=True,
                    max_iterations=self.config.max_iterations,
                    handle_parsing_errors=True
                )
            
            self.log_info(f"智能体执行器初始化完成: {self.config.name}")
            
        except Exception as e:
            self.log_error(f"初始化智能体执行器失败: {str(e)}", error=e)
            # 设置一个最小化的回退执行器
            self.agent_executor = None
    
    @abstractmethod
    async def process_message(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理消息的抽象方法
        
        Args:
            message: 用户消息
            context: 上下文信息（包含用户、员工等信息）
            
        Returns:
            Dict: 处理结果
        """
        pass
    
    def get_tools(self) -> List[BaseTool]:
        """
        获取智能体工具列表
        
        Returns:
            List[BaseTool]: 工具列表
        """
        return self.tools
    
    def add_tool(self, tool: BaseTool):
        """
        添加工具到智能体
        
        Args:
            tool: 要添加的工具
        """
        
        self.tools.append(tool)
        
        # 重新初始化智能体以包含新工具
        if self.agent_executor:
            self.initialize()
        
        self.log_info(f"添加工具到智能体 {self.config.name}: {tool.name}")
    
    def remove_tool(self, tool_name: str) -> bool:
        """
        从智能体移除工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: 是否成功移除
        """
        
        # 查找要移除的工具
        tool_to_remove = None
        for tool in self.tools:
            if tool.name == tool_name:
                tool_to_remove = tool
                break
        
        if not tool_to_remove:
            self.log_warning(f"工具不存在: {tool_name}")
            return False
        
        # 移除工具
        self.tools.remove(tool_to_remove)
        
        # 重新初始化智能体
        if self.agent_executor:
            self.initialize()
        
        self.log_info(f"从智能体 {self.config.name} 移除工具: {tool_name}")
        
        return True
    
    def get_config_dict(self) -> Dict[str, Any]:
        """
        获取智能体配置字典
        
        Returns:
            Dict: 配置字典
        """
        
        config_dict = asdict(self.config)
        
        # 处理工具列表，只保留基本信息
        config_dict["tools"] = [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in self.config.tools
        ] if self.config.tools else []
        
        return config_dict
    
    def validate(self) -> bool:
        """
        验证智能体配置是否有效
        
        Returns:
            bool: 配置是否有效
        """
        
        if not self.config.name:
            self.log_error("智能体名称不能为空")
            return False
        
        if not self.config.system_prompt:
            self.log_error("系统提示不能为空")
            return False
        
        if not self.llm:
            self.log_error("语言模型未配置")
            return False
        
        return True