"""
AI模型管理器
负责管理不同LLM提供商的模型实例和配置
"""

import os
import json
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict

try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from app.services.ai.chat_deepseek import ChatDeepSeek 
from app.config.settings import settings
from app.config.constants import ModelProvider
from app.utils.logger import LoggerMixin
# 在现有的导入之后添加
try:
    from langchain_deepseek import ChatDeepSeek
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False
@dataclass
class ModelConfig:
    """模型配置数据类"""
    
    provider: ModelProvider
    model_name: str
    temperature: float
    max_tokens: Optional[int]
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

class ModelManager(LoggerMixin):
    """
    AI模型管理器
    统一管理不同提供商的LLM实例
    """
    
    def __init__(self):
        """初始化模型管理器"""
        super().__init__()
        
        # 存储已创建的模型实例
        self._chat_models: Dict[str, BaseChatModel] = {}
        self._embedding_models: Dict[str, Embeddings] = {}
        
        # 初始化默认模型
        self._init_default_models()
        
        self.log_info("AI模型管理器初始化完成")
    
    def _init_default_models(self):
        """初始化默认模型"""
        
        # 创建默认聊天模型配置
        default_config = ModelConfig(
            provider=settings.DEFAULT_MODEL_PROVIDER,
            model_name=settings.DEFAULT_MODEL_NAME,
            temperature=settings.MODEL_TEMPERATURE,
            max_tokens=settings.MODEL_MAX_TOKENS
        )
        print(f"DEBUG: 创建默认模型配置: provider={default_config.provider}, model={default_config.model_name}")  # 添加调试
        # 创建默认聊天模型
        default_chat_model = self.create_chat_model(default_config)
        self._chat_models["default"] = default_chat_model
        print(f"DEBUG: 默认模型创建成功: {type(default_chat_model).__name__}")
        # 创建默认嵌入模型
        default_embedding = self.create_embedding_model()
        self._embedding_models["default"] = default_embedding
        
        self.log_info(f"已创建默认模型: {settings.DEFAULT_MODEL_PROVIDER}/{settings.DEFAULT_MODEL_NAME}")
    
    def create_chat_model(self, config: ModelConfig) -> BaseChatModel:
        """
        创建聊天模型实例
        
        Args:
            config: 模型配置
            
        Returns:
            BaseChatModel: LangChain聊天模型实例
            
        Raises:
            ValueError: 当不支持的模型提供商或缺少API密钥时
        """
        
        # 优先使用配置中的API密钥，如果没有则使用环境变量
        api_key = config.api_key or self._get_api_key(config.provider)
        
        if not api_key:
            raise ValueError(f"{config.provider} API密钥未配置")
        
        model_kwargs = {
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "timeout": config.timeout,
            "max_retries": config.max_retries,
        }
        
        # 根据提供商创建不同的模型实例
        if config.provider == ModelProvider.OPENAI:
            base_url = config.base_url or settings.DEEPSEEK_BASE_URL or "https://api.deepseek.com"
            return ChatOpenAI(
                model=config.model_name,
                api_key=api_key,  # 统一使用 api_key 参数名
                base_url=config.base_url,
                **model_kwargs
            )
            
        elif config.provider == ModelProvider.ANTHROPIC:
            # 注意：根据实际库调整
            return ChatAnthropicMessages(
                model=config.model_name,
                api_key=api_key,
                **model_kwargs
            )
            
        elif config.provider == ModelProvider.GEMINI:
            return ChatGoogleGenerativeAI(
                model=config.model_name,
                api_key=api_key,
                **model_kwargs
            )
            
        elif config.provider == ModelProvider.DEEPSEEK:
            # 使用自定义的 ChatDeepSeek，直接与 DeepSeek API 通信
            base_url = config.base_url or settings.DEEPSEEK_BASE_URL
            
            return ChatDeepSeek(
                model=config.model_name,
                api_key=api_key,
                base_url=base_url,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout,
                max_retries=config.max_retries,
            )
            
        elif config.provider == ModelProvider.LOCAL:
            # 本地模型支持（后续实现）
            raise NotImplementedError("本地模型支持尚未实现")
            
        else:
            raise ValueError(f"不支持的模型提供商: {config.provider}")
    
    def create_embedding_model(self) -> Embeddings:
        """
        创建嵌入模型实例
        
        Returns:
            Embeddings: LangChain嵌入模型实例
        """
        
        api_key = self._get_api_key(ModelProvider.OPENAI)
        
        if not api_key:
            self.log_warning("OpenAI API密钥未配置，无法创建嵌入模型")
            # 返回一个模拟嵌入模型（开发用）
            return self._create_mock_embedding_model()
        
        if not OPENAI_AVAILABLE:
            self.log_warning("OpenAI 模块不可用，使用模拟嵌入模型")
            return self._create_mock_embedding_model()
        
        return OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=api_key
        )
    
    def _create_mock_embedding_model(self):
        """创建模拟嵌入模型（开发用）"""
        
        from langchain_core.embeddings import Embeddings
        
        class MockEmbeddings(Embeddings):
            """模拟嵌入模型，返回随机向量"""
            
            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                import random
                return [[random.random() for _ in range(1536)] for _ in texts]
            
            def embed_query(self, text: str) -> List[float]:
                import random
                return [random.random() for _ in range(1536)]
        
        self.log_warning("使用模拟嵌入模型（仅限开发）")
        return MockEmbeddings()
    
    def _get_api_key(self, provider: ModelProvider) -> Optional[str]:
        """
        获取指定提供商的API密钥
        
        Args:
            provider: 模型提供商
            
        Returns:
            Optional[str]: API密钥，如果未配置则返回None
        """
        
        if provider == ModelProvider.OPENAI:
            return settings.OPENAI_API_KEY
        elif provider == ModelProvider.ANTHROPIC:
            return settings.ANTHROPIC_API_KEY
        elif provider == ModelProvider.GEMINI:
            return settings.GEMINI_API_KEY
        elif provider == ModelProvider.DEEPSEEK:
            return settings.DEEPSEEK_API_KEY
    
    def get_chat_model(self, model_key: str = "default") -> BaseChatModel:
        """
        获取聊天模型实例
        
        Args:
            model_key: 模型键名，默认为"default"
            
        Returns:
            BaseChatModel: 聊天模型实例
            
        Raises:
            KeyError: 当模型不存在时
        """
        
        if model_key not in self._chat_models:
            raise KeyError(f"模型不存在: {model_key}")
        
        return self._chat_models[model_key]
    
    def get_embedding_model(self, model_key: str = "default") -> Embeddings:
        """
        获取嵌入模型实例
        
        Args:
            model_key: 模型键名，默认为"default"
            
        Returns:
            Embeddings: 嵌入模型实例
            
        Raises:
            KeyError: 当模型不存在时
        """
        
        if model_key not in self._embedding_models:
            raise KeyError(f"嵌入模型不存在: {model_key}")
        
        return self._embedding_models[model_key]
    
    def register_chat_model(self, model_key: str, model: BaseChatModel):
        """
        注册聊天模型实例
        
        Args:
            model_key: 模型键名
            model: 聊天模型实例
        """
        
        self._chat_models[model_key] = model
        self.log_info(f"已注册聊天模型: {model_key}")
    
    def register_embedding_model(self, model_key: str, model: Embeddings):
        """
        注册嵌入模型实例
        
        Args:
            model_key: 模型键名
            model: 嵌入模型实例
        """
        
        self._embedding_models[model_key] = model
        self.log_info(f"已注册嵌入模型: {model_key}")
    
    def list_chat_models(self) -> List[Dict[str, Any]]:
        """
        列出所有可用的聊天模型
        
        Returns:
            List[Dict]: 模型信息列表
        """
        
        models = []
        
        for key, model in self._chat_models.items():
            model_info = {
                "key": key,
                "provider": str(type(model).__name__),
                "model_name": getattr(model, "model_name", "unknown"),
                "temperature": getattr(model, "temperature", None),
                "max_tokens": getattr(model, "max_tokens", None),
            }
            models.append(model_info)
        
        return models
    
    def create_model_config_from_request(
        self,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> ModelConfig:
        """
        从请求参数创建模型配置
        
        Args:
            provider: 模型提供商
            model_name: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            ModelConfig: 模型配置
        """
        
        # 使用请求参数或默认值
        final_provider = ModelProvider(provider) if provider else settings.DEFAULT_MODEL_PROVIDER
        final_model_name = model_name or settings.DEFAULT_MODEL_NAME
        final_temperature = temperature if temperature is not None else settings.MODEL_TEMPERATURE
        final_max_tokens = max_tokens or settings.MODEL_MAX_TOKENS
        
        return ModelConfig(
            provider=final_provider,
            model_name=final_model_name,
            temperature=final_temperature,
            max_tokens=final_max_tokens
        )
    
    def validate_model_config(self, config: ModelConfig) -> bool:
        """
        验证模型配置是否有效
        
        Args:
            config: 模型配置
            
        Returns:
            bool: 配置是否有效
        """
        
        # 检查API密钥
        api_key = self._get_api_key(config.provider)
        if not api_key:
            self.log_error(f"{config.provider} API密钥未配置")
            return False
        
        # 检查模型参数
        if config.temperature < 0 or config.temperature > 2:
            self.log_error(f"温度参数必须在0-2之间: {config.temperature}")
            return False
        
        if config.max_tokens and config.max_tokens < 1:
            self.log_error(f"最大token数必须大于0: {config.max_tokens}")
            return False
        
        return True

# 创建全局模型管理器实例
model_manager = ModelManager()