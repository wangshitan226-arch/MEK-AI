"""
应用常量定义
所有枚举和常量集中管理
"""

from enum import Enum
from typing import Final

# ==================== 环境枚举 ====================
class Environment(str, Enum):
    """运行环境枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

# ==================== 日志级别枚举 ====================
class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# ==================== 模型提供商枚举 ====================
class ModelProvider(str, Enum):
    """AI模型提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    LOCAL = "local"
    DEEPSEEK = "deepseek"  # 添加DeepSeek

# ==================== 向量数据库类型枚举 ====================
class VectorDBType(str, Enum):
    """向量数据库类型枚举"""
    CHROMA = "chroma"
    QDRANT = "qdrant"
    PINECONE = "pinecone"

# ==================== 文件类型枚举 ====================
class FileType(str, Enum):
    """文件类型枚举"""
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"
    MD = "md"
    JSON = "json"

# ==================== 任务状态枚举 ====================
class TaskStatus(str, Enum):
    """异步任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# ==================== 对话角色枚举 ====================
class MessageRole(str, Enum):
    """消息角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

# ==================== 全局常量 ====================
class Constants:
    """全局常量类"""
    
    # API版本
    API_V1_PREFIX: Final[str] = "/api/v1"
    
    # 默认分页参数
    DEFAULT_PAGE_SIZE: Final[int] = 20
    DEFAULT_PAGE_NUMBER: Final[int] = 1
    
    # 时间格式
    DATETIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT: Final[str] = "%Y-%m-%d"
    
    # 文件大小限制（字节）
    FILE_SIZE_1MB: Final[int] = 1024 * 1024
    FILE_SIZE_10MB: Final[int] = 10 * 1024 * 1024
    FILE_SIZE_100MB: Final[int] = 100 * 1024 * 1024
    
    # 文本分块参数
    DEFAULT_CHUNK_SIZE: Final[int] = 1000
    DEFAULT_CHUNK_OVERLAP: Final[int] = 200
    
    # 向量维度
    EMBEDDING_DIMENSION: Final[int] = 1536  # OpenAI ada-002
    
    # HTTP状态码
    HTTP_200_OK: Final[int] = 200
    HTTP_201_CREATED: Final[int] = 201
    HTTP_400_BAD_REQUEST: Final[int] = 400
    HTTP_401_UNAUTHORIZED: Final[int] = 401
    HTTP_403_FORBIDDEN: Final[int] = 403
    HTTP_404_NOT_FOUND: Final[int] = 404
    HTTP_500_INTERNAL_SERVER_ERROR: Final[int] = 500

# ==================== 错误码定义 ====================
class ErrorCode:
    """错误码定义"""
    
    # 通用错误
    SUCCESS: Final[int] = 0
    UNKNOWN_ERROR: Final[int] = 1000
    VALIDATION_ERROR: Final[int] = 1001
    AUTHENTICATION_ERROR: Final[int] = 1002
    AUTHORIZATION_ERROR: Final[int] = 1003
    RESOURCE_NOT_FOUND: Final[int] = 1004
    
    # 模型相关错误
    MODEL_NOT_AVAILABLE: Final[int] = 2001
    MODEL_API_ERROR: Final[int] = 2002
    MODEL_RATE_LIMIT: Final[int] = 2003
    MODEL_TIMEOUT: Final[int] = 2004
    
    # 文件相关错误
    FILE_TOO_LARGE: Final[int] = 3001
    FILE_TYPE_NOT_ALLOWED: Final[int] = 3002
    FILE_UPLOAD_FAILED: Final[int] = 3003
    FILE_PROCESSING_FAILED: Final[int] = 3004
    
    # 向量数据库错误
    VECTOR_DB_ERROR: Final[int] = 4001
    VECTOR_DB_CONNECTION_ERROR: Final[int] = 4002
    VECTOR_DB_QUERY_ERROR: Final[int] = 4003

# ==================== 默认值 ====================
DEFAULT_MODEL_NAME_MAPPING = {
    ModelProvider.OPENAI: "deepseek",
    ModelProvider.ANTHROPIC: "claude-3-opus-20240229",
    ModelProvider.GEMINI: "gemini-pro",
    ModelProvider.LOCAL: "llama2"
}

# 文件扩展名到类型的映射
FILE_EXTENSION_MAPPING = {
    ".pdf": FileType.PDF,
    ".txt": FileType.TXT,
    ".docx": FileType.DOCX,
    ".doc": FileType.DOCX,
    ".md": FileType.MD,
    ".json": FileType.JSON
}

# 允许的HTTP方法
ALLOWED_HTTP_METHODS = [
    "GET", "POST", "PUT", "DELETE", "PATCH", 
    "OPTIONS", "HEAD", "TRACE", "CONNECT"
]