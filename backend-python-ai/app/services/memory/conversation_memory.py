"""
对话记忆管理器
基于LangChain Memory组件，管理对话历史
"""

import uuid
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from app.config.settings import settings
from app.utils.logger import LoggerMixin

@dataclass
class ConversationState:
    """对话状态数据类"""
    
    conversation_id: str
    employee_id: str
    user_id: Optional[str]
    organization_id: Optional[str]
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

class ConversationMemoryManager(LoggerMixin):
    """
    对话记忆管理器
    管理对话历史和状态
    """
    
    def __init__(self, max_history: int = 20):
        """
        初始化对话记忆管理器
        
        Args:
            max_history: 最大对话历史条数
        """
        super().__init__()
        
        # 存储对话状态的内存字典
        self._conversations: Dict[str, ConversationState] = {}
        
        # LangChain记忆实例字典
        self._memories: Dict[str, ConversationBufferMemory] = {}
        
        # 配置
        self.max_history = max_history
        
        self.log_info(f"对话记忆管理器初始化完成，最大历史: {max_history}")
    
    def create_conversation(
        self,
        employee_id: str,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        initial_system_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        创建新对话
        
        Args:
            employee_id: 员工ID
            user_id: 用户ID
            organization_id: 组织ID
            initial_system_message: 初始系统消息
            metadata: 额外元数据
            
        Returns:
            str: 对话ID
        """
        
        # 生成唯一对话ID
        conversation_id = str(uuid.uuid4())
        now = datetime.now()
        
        # 创建对话状态
        conversation_state = ConversationState(
            conversation_id=conversation_id,
            employee_id=employee_id,
            user_id=user_id,
            organization_id=organization_id,
            messages=[],
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        
        # 创建LangChain记忆实例
        memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            output_key="output",
            max_token_limit=2000  # 限制token数量
        )
        
        # 如果有初始系统消息，添加到记忆
        if initial_system_message:
            system_message = SystemMessage(content=initial_system_message)
            memory.chat_memory.add_message(system_message)
            
            # 记录到对话状态
            conversation_state.messages.append({
                "role": "system",
                "content": initial_system_message,
                "timestamp": now.isoformat()
            })
        
        # 存储对话状态和记忆
        self._conversations[conversation_id] = conversation_state
        self._memories[conversation_id] = memory
        
        self.log_info(f"创建新对话: {conversation_id}, 员工: {employee_id}, 用户: {user_id}")
        
        return conversation_id
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        添加消息到对话
        
        Args:
            conversation_id: 对话ID
            role: 消息角色 (user/assistant/system)
            content: 消息内容
            metadata: 消息元数据
            
        Returns:
            bool: 是否成功添加
        """
        
        # 检查对话是否存在
        if conversation_id not in self._conversations:
            self.log_error(f"对话不存在: {conversation_id}")
            return False
        
        # 获取对话状态和记忆
        conversation_state = self._conversations[conversation_id]
        memory = self._memories[conversation_id]
        
        # 创建消息
        if role == "user":
            message = HumanMessage(content=content)
        elif role == "assistant":
            message = AIMessage(content=content)
        elif role == "system":
            message = SystemMessage(content=content)
        else:
            self.log_error(f"不支持的消息角色: {role}")
            return False
        
        # 添加到LangChain记忆
        memory.chat_memory.add_message(message)
        
        # 更新对话状态
        conversation_state.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        
        # 更新对话时间
        conversation_state.updated_at = datetime.now()
        
        # 限制历史消息数量
        if len(conversation_state.messages) > self.max_history:
            # 保留最近的max_history条消息，但总是保留系统消息
            system_messages = [m for m in conversation_state.messages if m["role"] == "system"]
            other_messages = [m for m in conversation_state.messages if m["role"] != "system"]
            
            # 保留所有系统消息和最近的其他消息
            other_messages = other_messages[-(self.max_history - len(system_messages)):]
            conversation_state.messages = system_messages + other_messages
            
            # 同步更新LangChain记忆（简化处理，实际需要更复杂的逻辑）
            self._sync_memory_from_state(conversation_id)
        
        self.log_debug(f"添加消息到对话 {conversation_id}: {role}: {content[:50]}...")
        
        return True
    
    def get_memory(self, conversation_id: str) -> Optional[ConversationBufferMemory]:
        """
        获取对话的记忆实例
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            Optional[ConversationBufferMemory]: LangChain记忆实例，如果不存在则返回None
        """
        
        return self._memories.get(conversation_id)
    
    # 【新增关键方法】获取LangChain格式的对话历史消息
    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[BaseMessage]:
        """
        获取对话历史（LangChain BaseMessage格式）
        
        Args:
            conversation_id: 对话ID
            limit: 限制返回的消息数量，None表示返回所有
            
        Returns:
            List[BaseMessage]: 对话历史消息列表（LangChain格式）
        """
        
        if conversation_id not in self._memories:
            return []
        
        memory = self._memories[conversation_id]
        
        # 直接从LangChain记忆实例中获取消息
        messages = memory.chat_memory.messages
        
        if limit and limit > 0:
            # 返回最近的消息
            return messages[-limit:]
        
        return messages
    
    def get_conversation_state(self, conversation_id: str) -> Optional[ConversationState]:
        """
        获取对话状态
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            Optional[ConversationState]: 对话状态，如果不存在则返回None
        """
        
        return self._conversations.get(conversation_id)
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取对话历史（字典格式，保持向后兼容）
        
        Args:
            conversation_id: 对话ID
            limit: 限制返回的消息数量，None表示返回所有
            
        Returns:
            List[Dict]: 对话历史消息列表（字典格式）
        """
        
        if conversation_id not in self._conversations:
            return []
        
        messages = self._conversations[conversation_id].messages
        
        if limit:
            return messages[-limit:]
        
        return messages
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[str]:
        """
        获取对话摘要（使用LangChain的摘要记忆）
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            Optional[str]: 对话摘要，如果无法生成则返回None
        """
        
        if conversation_id not in self._conversations:
            return None
        
        # 获取对话历史
        messages = self.get_conversation_history(conversation_id)
        
        # 过滤系统消息
        non_system_messages = [m for m in messages if m["role"] != "system"]
        
        if len(non_system_messages) < 3:  # 消息太少，不生成摘要
            return None
        
        # 简化版摘要：统计对话信息
        user_messages = [m for m in non_system_messages if m["role"] == "user"]
        assistant_messages = [m for m in non_system_messages if m["role"] == "assistant"]
        
        summary = (
            f"对话包含 {len(user_messages)} 条用户消息和 {len(assistant_messages)} 条助手消息。"
            f"最后一条用户消息: {user_messages[-1]['content'][:100]}..."
        )
        
        return summary
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除对话
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            bool: 是否成功删除
        """
        
        if conversation_id not in self._conversations:
            return False
        
        # 从内存中删除
        del self._conversations[conversation_id]
        
        if conversation_id in self._memories:
            del self._memories[conversation_id]
        
        self.log_info(f"删除对话: {conversation_id}")
        
        return True
    
    def list_conversations(
        self,
        user_id: Optional[str] = None,
        employee_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        列出对话
        
        Args:
            user_id: 过滤用户ID
            employee_id: 过滤员工ID
            
        Returns:
            List[Dict]: 对话列表
        """
        
        conversations = []
        
        for conv_id, state in self._conversations.items():
            # 应用过滤条件
            if user_id and state.user_id != user_id:
                continue
            
            if employee_id and state.employee_id != employee_id:
                continue
            
            # 获取对话摘要
            summary = self.get_conversation_summary(conv_id)
            
            conversation_info = {
                "conversation_id": conv_id,
                "employee_id": state.employee_id,
                "user_id": state.user_id,
                "organization_id": state.organization_id,
                "message_count": len(state.messages),
                "created_at": state.created_at.isoformat(),
                "updated_at": state.updated_at.isoformat(),
                "summary": summary,
                "metadata": state.metadata
            }
            
            conversations.append(conversation_info)
        
        # 按更新时间倒序排序
        conversations.sort(key=lambda x: x["updated_at"], reverse=True)
        
        return conversations
    
    def clear_all_conversations(self) -> int:
        """
        清除所有对话
        
        Returns:
            int: 清除的对话数量
        """
        
        count = len(self._conversations)
        
        self._conversations.clear()
        self._memories.clear()
        
        self.log_info(f"清除所有对话，共 {count} 个")
        
        return count
    
    def _sync_memory_from_state(self, conversation_id: str):
        """
        从对话状态同步LangChain记忆
        
        注意：这是一个简化实现，实际可能需要更复杂的逻辑
        
        Args:
            conversation_id: 对话ID
        """
        
        if conversation_id not in self._conversations:
            return
        
        state = self._conversations[conversation_id]
        
        # 创建新的记忆实例
        memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            output_key="output"
        )
        
        # 重新添加所有消息
        for msg in state.messages:
            if msg["role"] == "user":
                memory.chat_memory.add_message(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                memory.chat_memory.add_message(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                memory.chat_memory.add_message(SystemMessage(content=msg["content"]))
        
        # 更新记忆
        self._memories[conversation_id] = memory

# 创建全局对话记忆管理器实例
conversation_memory_manager = ConversationMemoryManager()