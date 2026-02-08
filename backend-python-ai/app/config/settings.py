"""
应用配置管理
使用Pydantic BaseSettings管理环境变量
"""

import secrets
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings

from app.config.constants import (
    ModelProvider,
    VectorDBType,
    Environment,
    LogLevel
)

class Settings(BaseSettings):
    """
    应用配置类
    
    注意：所有配置都可以通过环境变量或.env文件设置
    优先级：环境变量 > .env文件 > 默认值
    """
    
    # ==================== 应用基础配置 ====================
    APP_NAME: str = Field(default="MEK-AI Python服务", description="应用名称")
    APP_VERSION: str = Field(default="1.0.0", description="应用版本")
    APP_ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT, description="运行环境")
    APP_DEBUG: bool = Field(default=False, description="是否启用调试模式")
    APP_HOST: str = Field(default="0.0.0.0", description="监听主机")
    APP_PORT: int = Field(default=8000, description="监听端口")
    APP_RELOAD: bool = Field(default=False, description="是否启用热重载")
    APP_WORKERS: int = Field(default=4, description="工作进程数")
    APP_LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, description="日志级别")
    
    # ==================== 安全配置 ====================
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="应用密钥，用于签名等"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT算法")
    JWT_EXPIRE_MINUTES: int = Field(default=30, description="JWT过期时间（分钟）")
    
    # ==================== CORS配置 ====================
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="允许的跨域源"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="是否允许凭据")
    CORS_ALLOW_METHODS: List[str] = Field(default=["*"], description="允许的HTTP方法")
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"], description="允许的HTTP头部")
    
    # ==================== LLM API密钥配置 ====================
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API密钥")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API密钥")
    GEMINI_API_KEY: Optional[str] = Field(default=None, description="Google Gemini API密钥")

    DEEPSEEK_API_KEY: Optional[str] = Field(default="sk-751d8945ad1d4a31a7d5f6ff5716ba4a", description="DeepSeek API密钥")
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com", description="DeepSeek API基础URL")
    
    # ==================== 模型配置 ====================
    # 修改默认模型提供者为DeepSeek（测试用）
    DEFAULT_MODEL_PROVIDER: ModelProvider = Field(
        default=ModelProvider.DEEPSEEK,  # 改为DeepSeek
        description="默认模型提供商"
    )
    DEFAULT_MODEL_NAME: str = Field(
        default="deepseek-chat",
        description="默认模型名称"
    )
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-ada-002",
        description="嵌入模型名称"
    )
    MODEL_TEMPERATURE: float = Field(default=0.7, description="模型温度参数")
    MODEL_MAX_TOKENS: int = Field(default=4096, description="模型最大Token数")
    
    # ==================== 向量数据库配置 ====================
    VECTOR_DB_TYPE: VectorDBType = Field(
        default=VectorDBType.CHROMA,
        description="向量数据库类型"
    )
    CHROMA_PERSIST_DIR: str = Field(
        default="./data/vector_db",
        description="ChromaDB持久化目录"
    )
    CHROMA_COLLECTION_NAME: str = Field(
        default="mek_ai_documents",
        description="ChromaDB集合名称"
    )
    
    # ==================== 文件存储配置 ====================
    UPLOAD_DIR: str = Field(default="./data/uploads", description="上传文件目录")
    MAX_UPLOAD_SIZE: int = Field(default=104857600, description="最大上传大小（字节）")
    ALLOWED_EXTENSIONS: str = Field(
        default=".pdf,.txt,.docx,.md,.json",
        description="允许的文件扩展名"
    )
    
    # ==================== Redis配置 ====================
    REDIS_HOST: str = Field(default="localhost", description="Redis主机")
    REDIS_PORT: int = Field(default=6379, description="Redis端口")
    REDIS_DB: int = Field(default=0, description="Redis数据库编号")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis密码")
    
    # ==================== 日志配置 ====================
    LOG_FILE: str = Field(default="./logs/app.log", description="日志文件路径")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    LOG_MAX_SIZE: int = Field(default=10485760, description="日志文件最大大小（字节）")
    LOG_BACKUP_COUNT: int = Field(default=5, description="日志备份数量")
    
    # ==================== 监控配置 ====================
    ENABLE_METRICS: bool = Field(default=True, description="是否启用指标收集")
    METRICS_PORT: int = Field(default=9090, description="指标服务器端口")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, description="健康检查间隔（秒）")
    
    # ==================== 开发配置 ====================
    MOCK_USER_ID: str = Field(default="mock_user_001", description="模拟用户ID")
    MOCK_ORGANIZATION_ID: str = Field(default="mock_org_001", description="模拟组织ID")
    MOCK_EMPLOYEE_ID: str = Field(default="mock_emp_001", description="模拟员工ID")
    
    # ==================== 计算属性 ====================
    @property
    def redis_url(self) -> str:
        """获取Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """获取允许的文件扩展名列表"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    @property
    def is_development(self) -> bool:
        """检查是否为开发环境"""
        return self.APP_ENVIRONMENT == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """检查是否为生产环境"""
        return self.APP_ENVIRONMENT == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """检查是否为测试环境"""
        return self.APP_ENVIRONMENT == Environment.TESTING
    
    class Config:
        """Pydantic配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # 忽略未定义的额外字段

# 创建全局配置实例
settings = Settings()