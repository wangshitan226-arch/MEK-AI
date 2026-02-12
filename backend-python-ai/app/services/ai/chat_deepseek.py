"""
DeepSeek 聊天模型自定义实现
直接与 DeepSeek API 通信，绕过 langchain-openai 的兼容层问题
"""

import json
import aiohttp
import requests
import logging
import time
from typing import Any, Dict, List, Optional, AsyncIterator, Iterator
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from pydantic import Field

from app.config.settings import settings

# 创建模块级别的日志记录器
logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0):
    """
    重试装饰器 - 带指数退避
    
    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # 检查是否应该重试
                    error_str = str(e).lower()
                    
                    # 这些错误不重试
                    if any(err in error_str for err in [
                        'invalid api key',
                        'authentication',
                        'unauthorized',
                        'bad request',
                        'invalid request'
                    ]):
                        logger.error(f"请求错误，不重试: {e}")
                        raise
                    
                    # 最后一次尝试，抛出异常
                    if attempt == max_retries - 1:
                        logger.error(f"达到最大重试次数 ({max_retries})，最后错误: {e}")
                        raise
                    
                    # 计算延迟时间（指数退避）
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    
                    # 添加随机抖动，避免同时重试
                    import random
                    delay = delay * (0.5 + random.random())
                    
                    logger.warning(f"API调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    logger.info(f"等待 {delay:.2f} 秒后重试...")
                    
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # 检查是否应该重试
                    error_str = str(e).lower()
                    
                    # 这些错误不重试
                    if any(err in error_str for err in [
                        'invalid api key',
                        'authentication',
                        'unauthorized',
                        'bad request',
                        'invalid request'
                    ]):
                        logger.error(f"请求错误，不重试: {e}")
                        raise
                    
                    # 最后一次尝试，抛出异常
                    if attempt == max_retries - 1:
                        logger.error(f"达到最大重试次数 ({max_retries})，最后错误: {e}")
                        raise
                    
                    # 计算延迟时间（指数退避）
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    
                    # 添加随机抖动
                    import random
                    delay = delay * (0.5 + random.random())
                    
                    logger.warning(f"API调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    logger.info(f"等待 {delay:.2f} 秒后重试...")
                    
                    time.sleep(delay)
            
            raise last_exception
        
        import asyncio
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if asyncio.iscoroutinefunction(func):
                return async_wrapper(*args, **kwargs)
            else:
                return sync_wrapper(*args, **kwargs)
        
        return wrapper
    
    return decorator


class ChatDeepSeek(BaseChatModel):
    """
    自定义 DeepSeek 聊天模型
    直接与 DeepSeek API 通信，解决兼容性问题
    """
    
    model: str = Field(default="deepseek-chat", description="模型名称")
    temperature: float = Field(default=0.7, description="温度参数")
    max_tokens: Optional[int] = Field(default=None, description="最大token数")
    api_key: str = Field(description="DeepSeek API 密钥")
    base_url: str = Field(default="https://api.deepseek.com", description="API基础URL")
    timeout: int = Field(default=30, description="请求超时时间")
    max_retries: int = Field(default=3, description="最大重试次数")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        """初始化 DeepSeek 模型 - 在父类初始化前处理 base_url"""
        
        # 处理 base_url，确保以 /v1 结尾
        if "base_url" in kwargs:
            base_url = kwargs["base_url"]
        elif hasattr(settings, "DEEPSEEK_BASE_URL"):
            base_url = settings.DEEPSEEK_BASE_URL
            kwargs["base_url"] = base_url
        else:
            base_url = "https://api.deepseek.com"
            kwargs["base_url"] = base_url
        
        # 确保 base_url 以 /v1 结尾
        if not base_url.endswith('/v1'):
            if base_url.endswith('/'):
                kwargs["base_url"] = f"{base_url}v1"
            else:
                kwargs["base_url"] = f"{base_url}/v1"
        
        # 确保 api_key 存在
        if "api_key" not in kwargs and hasattr(settings, "DEEPSEEK_API_KEY"):
            kwargs["api_key"] = settings.DEEPSEEK_API_KEY
        
        # 调用父类初始化 - 只传递定义的字段
        super().__init__(**kwargs)
        
        # 使用模块级别的 logger，不在实例上设置属性
        logger.info(f"初始化 ChatDeepSeek: {self.model}, base_url: {self.base_url}")
    
    @property
    def _llm_type(self) -> str:
        """返回语言模型类型"""
        return "deepseek-chat"
    
    def _convert_message_to_dict(self, message: BaseMessage) -> Dict[str, Any]:
        """将 LangChain 消息转换为 DeepSeek API 格式"""
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "assistant"
        elif isinstance(message, SystemMessage):
            role = "system"
        else:
            raise ValueError(f"不支持的消息类型: {type(message)}")
        
        return {
            "role": role,
            "content": message.content,
            "name": getattr(message, 'name', None)
        }
    
    def _create_request_body(self, messages: List[BaseMessage], **kwargs) -> Dict[str, Any]:
        """创建请求体"""
        message_dicts = [self._convert_message_to_dict(msg) for msg in messages]
        
        body = {
            "model": self.model,
            "messages": message_dicts,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "stream": False
        }
        
        # 移除 None 值
        body = {k: v for k, v in body.items() if v is not None}
        return body
    
    def _create_headers(self) -> Dict[str, str]:
        """创建请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
    
    @retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        同步生成回复（带重试机制）
        """
        # 构建请求
        url = f"{self.base_url}/chat/completions"
        headers = self._create_headers()
        body = self._create_request_body(messages, **kwargs)
        
        # 添加停止词
        if stop:
            body["stop"] = stop
        
        logger.debug(f"发送请求到 DeepSeek: {url}")
        
        # 发送请求
        response = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=self.timeout
        )
        
        # 检查响应
        if response.status_code != 200:
            error_msg = f"DeepSeek API 错误: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # 解析响应
        result = response.json()
        
        # 提取消息内容
        if "choices" in result and len(result["choices"]) > 0:
            message_content = result["choices"][0]["message"]["content"]
            message = AIMessage(content=message_content)
            
            # 构建 ChatResult
            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])
        else:
            raise ValueError(f"响应格式异常: {result}")
    
    @retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        异步生成回复（带重试机制）
        """
        # 构建请求
        url = f"{self.base_url}/chat/completions"
        headers = self._create_headers()
        body = self._create_request_body(messages, **kwargs)
        
        # 添加停止词
        if stop:
            body["stop"] = stop
        
        logger.debug(f"异步发送请求到 DeepSeek: {url}")
        
        # 异步发送请求
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=body,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    error_msg = f"DeepSeek API 错误: {response.status} - {error_text}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # 解析响应
                result = await response.json()
                
                # 提取消息内容
                if "choices" in result and len(result["choices"]) > 0:
                    message_content = result["choices"][0]["message"]["content"]
                    message = AIMessage(content=message_content)
                    
                    # 构建 ChatResult
                    generation = ChatGeneration(message=message)
                    return ChatResult(generations=[generation])
                else:
                    raise ValueError(f"响应格式异常: {result}")
    
    def get_num_tokens(self, text: str) -> int:
        """
        估算 token 数量（简化版）
        """
        # 简单估算：英文大约 1 token = 4 字符，中文大约 1 token = 2 字符
        return len(text) // 3
    
    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        """
        估算消息列表的 token 数量
        """
        total = 0
        for message in messages:
            total += self.get_num_tokens(message.content)
        return total