"""
Pydantic模型定义
用于请求/响应数据验证
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel as PydanticBaseModel, Field, validator

from app.config.constants import (
    TaskStatus,
    FileType,
    ModelProvider,
    ErrorCode,
    Constants
)

# ==================== 员工相关模型 ====================

class EmployeeBase(PydanticBaseModel):
    """员工基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="员工名称")
    description: str = Field(..., min_length=1, max_length=500, description="员工描述")
    avatar: Optional[str] = Field(None, description="头像URL")
    category: List[str] = Field(default_factory=list, description="分类标签数组")
    tags: List[str] = Field(default_factory=list, description="标签数组")
    price: Union[int, str] = Field(default=0, description="价格(数字或'free')")
    skills: List[str] = Field(default_factory=list, description="技能列表")
    industry: Optional[str] = Field(None, description="所属行业")
    role: Optional[str] = Field(None, description="岗位角色")
    prompt: Optional[str] = Field(None, description="系统提示词")
    model: Optional[str] = Field(None, description="使用的AI模型")
    knowledge_base_ids: List[str] = Field(default_factory=list, description="关联知识库ID列表")

    @validator("price")
    def validate_price(cls, v):
        """验证价格字段"""
        if isinstance(v, str) and v != "free":
            try:
                return int(v)
            except ValueError:
                raise ValueError("价格必须是数字或'free'")
        elif isinstance(v, int) and v < 0:
            raise ValueError("价格不能为负数")
        return v

class EmployeeCreate(EmployeeBase):
    """创建员工请求模型"""
    pass

class EmployeeUpdate(PydanticBaseModel):
    """更新员工请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="员工名称")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="员工描述")
    avatar: Optional[str] = Field(None, description="头像URL")
    category: Optional[List[str]] = Field(None, description="分类标签数组")
    tags: Optional[List[str]] = Field(None, description="标签数组")
    price: Optional[Union[int, str]] = Field(None, description="价格(数字或'free')")
    skills: Optional[List[str]] = Field(None, description="技能列表")
    industry: Optional[str] = Field(None, description="所属行业")
    role: Optional[str] = Field(None, description="岗位角色")
    prompt: Optional[str] = Field(None, description="系统提示词")
    model: Optional[str] = Field(None, description="使用的AI模型")
    knowledge_base_ids: Optional[List[str]] = Field(None, description="关联知识库ID列表")
    status: Optional[str] = Field(None, description="状态")

class EmployeeResponse(EmployeeBase):
    """员工响应模型"""
    id: str = Field(..., description="员工ID")
    trial_count: int = Field(default=0, description="试用次数")
    hire_count: int = Field(default=0, description="雇佣次数")
    is_hired: bool = Field(default=False, description="是否已雇佣")
    is_recruited: bool = Field(default=False, description="是否已招聘")
    status: str = Field(default="draft", description="状态: draft/published/archived")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者ID")
    is_hot: Optional[bool] = Field(None, description="是否热门")
    original_price: Optional[int] = Field(None, description="原价")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class BaseModel(PydanticBaseModel):
    """
    基础模型类
    
    所有模型都继承此类，提供通用配置
    """
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        from_attributes = True  # 用于ORM模型
        populate_by_name = True  # 允许使用别名
        arbitrary_types_allowed = True

class SuccessResponse(BaseModel):
    """
    成功响应模型
    
    所有成功响应都应遵循此格式
    """
    
    success: bool = Field(default=True, description="是否成功")
    message: Optional[str] = Field(default=None, description="成功消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")

class ErrorResponse(BaseModel):
    """
    错误响应模型
    
    所有错误响应都应遵循此格式
    """
    
    success: bool = Field(default=False, description="是否成功")
    error_code: int = Field(..., description="错误码")
    error_message: str = Field(..., description="错误消息")
    detail: Optional[Any] = Field(default=None, description="错误详情")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间戳")

# ==================== 健康检查模型 ====================

class HealthResponse(BaseModel):
    """健康检查响应模型"""
    
    status: str = Field(..., description="服务状态")
    service: str = Field(..., description="服务名称")
    version: str = Field(..., description="服务版本")
    environment: str = Field(..., description="运行环境")
    timestamp: datetime = Field(..., description="检查时间")

class SystemInfo(BaseModel):
    """系统信息模型"""
    
    platform: str = Field(..., description="操作系统平台")
    python_version: str = Field(..., description="Python版本")
    processor: str = Field(..., description="处理器信息")
    machine: str = Field(..., description="机器类型")
    system: str = Field(..., description="操作系统")
    release: str = Field(..., description="系统版本")

class AppInfo(BaseModel):
    """应用信息模型"""
    
    name: str = Field(..., description="应用名称")
    version: str = Field(..., description="应用版本")
    environment: str = Field(..., description="运行环境")
    debug: bool = Field(..., description="是否调试模式")
    log_level: str = Field(..., description="日志级别")

class ServiceStatus(BaseModel):
    """服务状态模型"""
    
    status: str = Field(..., description="服务状态")
    response_time: Optional[str] = Field(default=None, description="响应时间")
    details: Optional[str] = Field(default=None, description="状态详情")

class DetailedHealthResponse(BaseModel):
    """详细健康检查响应模型"""
    
    status: str = Field(..., description="整体状态")
    timestamp: datetime = Field(..., description="检查时间")
    app: AppInfo = Field(..., description="应用信息")
    system: SystemInfo = Field(..., description="系统信息")
    config: Dict[str, Any] = Field(..., description="配置检查")
    services: Dict[str, ServiceStatus] = Field(..., description="服务状态")

# ==================== 用户相关模型 ====================

class UserInfo(BaseModel):
    """用户信息模型"""
    
    user_id: str = Field(..., description="用户ID")
    employee_id: str = Field(..., description="员工ID")
    organization_id: Optional[str] = Field(default=None, description="组织ID")
    is_authenticated: bool = Field(..., description="是否已认证")
    is_mock: bool = Field(..., description="是否为模拟用户")
    permissions: List[str] = Field(default_factory=list, description="用户权限")

class UserContext(BaseModel):
    """用户上下文模型（用于内部传递）"""
    
    user_id: str = Field(..., description="用户ID")
    employee_id: str = Field(..., description="员工ID")
    organization_id: Optional[str] = Field(default=None, description="组织ID")
    is_authenticated: bool = Field(default=True, description="是否已认证")
    is_mock: bool = Field(default=False, description="是否为模拟用户")
    permissions: List[str] = Field(default_factory=lambda: ["chat", "read"], description="用户权限")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

# ==================== 聊天相关模型（占位） ====================

class Message(BaseModel):
    """消息模型"""
    
    role: str = Field(..., description="消息角色（system/user/assistant/tool）")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="消息时间")
    
    @validator("role")
    def validate_role(cls, v):
        """验证消息角色"""
        allowed_roles = ["system", "user", "assistant", "tool"]
        if v not in allowed_roles:
            raise ValueError(f"角色必须是以下之一: {allowed_roles}")
        return v

class ChatRequest(BaseModel):
    """聊天请求模型"""
    
    message: str = Field(..., min_length=1, max_length=5000, description="用户消息")
    employee_id: str = Field(..., description="员工ID（业务必需）")
    conversation_id: Optional[str] = Field(default=None, description="对话ID（为空时创建新对话）")
    user_id: Optional[str] = Field(default=None, description="用户ID（预留字段）")
    organization_id: Optional[str] = Field(default=None, description="组织ID（预留字段）")
    stream: bool = Field(default=False, description="是否流式响应")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="温度参数")
    max_tokens: Optional[int] = Field(default=None, ge=1, le=16000, description="最大Token数")

class ChatResponse(BaseModel):
    """聊天响应模型"""
    
    response: str = Field(..., description="AI回复")
    conversation_id: str = Field(..., description="对话ID")
    message_id: str = Field(..., description="消息ID")
    timestamp: datetime = Field(..., description="响应时间")
    token_usage: Optional[Dict[str, int]] = Field(default=None, description="Token使用统计")
    model: Optional[str] = Field(default=None, description="使用的模型")
    finish_reason: Optional[str] = Field(default=None, description="完成原因")

class Conversation(BaseModel):
    """对话模型"""
    
    conversation_id: str = Field(..., description="对话ID")
    employee_id: str = Field(..., description="员工ID")
    user_id: Optional[str] = Field(default=None, description="用户ID")
    organization_id: Optional[str] = Field(default=None, description="组织ID")
    title: Optional[str] = Field(default=None, description="对话标题")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    message_count: int = Field(default=0, description="消息数量")
    is_active: bool = Field(default=True, description="是否活跃")

# ==================== 知识库相关模型 ====================

class KnowledgeBaseCreate(PydanticBaseModel):
    """知识库创建模型"""
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签")
    is_public: bool = Field(default=True, description="是否公开")
    category: Optional[str] = Field(None, description="分类")

class KnowledgeBaseUpdate(PydanticBaseModel):
    """知识库更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    tags: Optional[List[str]] = Field(None, description="标签")
    is_public: Optional[bool] = Field(None, description="是否公开")
    status: Optional[str] = Field(None, description="状态")

class KnowledgeBaseResponse(PydanticBaseModel):
    """知识库响应模型"""
    id: str = Field(..., description="知识库ID")
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(None, description="描述")
    doc_count: int = Field(default=0, description="文档数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: str = Field(..., description="创建者ID")
    status: str = Field(default="active", description="状态: active/inactive/processing")
    tags: List[str] = Field(default_factory=list, description="标签")
    is_public: bool = Field(default=True, description="是否公开")
    vectorized: bool = Field(default=False, description="是否已向量化")
    category: Optional[str] = Field(None, description="分类")

    class Config:
        from_attributes = True

class KnowledgeItemCreate(PydanticBaseModel):
    """知识条目创建模型"""
    content: str = Field(..., min_length=1, description="内容")
    serial_no: int = Field(default=1, description="序号")
    source_file: Optional[str] = Field(None, description="源文件")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

class KnowledgeItemResponse(PydanticBaseModel):
    """知识条目响应模型"""
    id: str = Field(..., description="条目ID")
    knowledge_base_id: str = Field(..., description="知识库ID")
    serial_no: int = Field(..., description="序号")
    content: str = Field(..., description="内容")
    word_count: int = Field(..., description="字数")
    create_time: datetime = Field(..., description="创建时间")
    source_file: Optional[str] = Field(None, description="源文件")
    embeddings: Optional[List[float]] = Field(None, description="向量嵌入")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    class Config:
        from_attributes = True

class DocumentUploadConfig(PydanticBaseModel):
    """文档上传配置模型"""
    file_type: str = Field(default="text", description="文件类型")
    knowledge_length: int = Field(default=2000, description="知识点长度")
    overlap_length: int = Field(default=30, description="重叠长度")
    line_break_segment: bool = Field(default=True, description="换行自动分段")
    max_segment_length: int = Field(default=500, description="最大分段长度")

class DocumentParseRequest(PydanticBaseModel):
    """文档解析请求模型"""
    file_id: str = Field(..., description="文件ID")
    config: DocumentUploadConfig = Field(default_factory=DocumentUploadConfig, description="解析配置")

class DocumentParseResponse(PydanticBaseModel):
    """文档解析响应模型"""
    file_id: str = Field(..., description="文件ID")
    file_name: str = Field(..., description="文件名")
    knowledge_list: List[KnowledgeItemResponse] = Field(default_factory=list, description="知识点列表")
    parse_status: str = Field(default="completed", description="解析状态")

class KnowledgeSaveRequest(PydanticBaseModel):
    """保存知识点请求模型"""
    items: List[KnowledgeItemCreate] = Field(..., description="知识点列表")

class KnowledgeSearchRequest(PydanticBaseModel):
    """知识搜索请求模型"""
    query: str = Field(..., min_length=1, max_length=1000, description="查询内容")
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量")
    score_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="相似度阈值")

# ==================== 市场广场模型 ====================

class MarketplaceFilter(PydanticBaseModel):
    """市场广场筛选参数"""
    category: Optional[str] = Field(None, description="分类")
    industry: Optional[str] = Field(None, description="行业")
    min_price: Optional[int] = Field(None, ge=0, description="最低价格")
    max_price: Optional[int] = Field(None, ge=0, description="最高价格")
    tags: Optional[List[str]] = Field(None, description="标签")
    search: Optional[str] = Field(None, description="搜索关键词")
    sort_by: Optional[str] = Field(None, description="排序字段")
    sort_order: Optional[str] = Field(default="desc", description="排序方向")

    @validator("sort_order")
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("排序方向必须是 'asc' 或 'desc'")
        return v

class HireRequest(PydanticBaseModel):
    """雇佣请求模型"""
    employee_id: Optional[str] = Field(None, description="员工ID（可选，URL路径中已包含）")
    organization_id: Optional[str] = Field(None, description="组织ID")
    payment_method: Optional[str] = Field(None, description="支付方式")

class TrialRequest(PydanticBaseModel):
    """试用请求模型"""
    employee_id: Optional[str] = Field(None, description="员工ID（可选，URL路径中已包含）")
    organization_id: Optional[str] = Field(None, description="组织ID")


# ==================== 文件相关模型（占位） ====================

class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    
    file_id: str = Field(..., description="文件ID")
    filename: str = Field(..., description="文件名")
    content_type: str = Field(..., description="文件类型")
    size: int = Field(..., description="文件大小（字节）")
    upload_time: datetime = Field(..., description="上传时间")
    task_id: str = Field(..., description="处理任务ID")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="处理状态")

class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="进度（0-1）")
    message: Optional[str] = Field(default=None, description="状态消息")
    result: Optional[Any] = Field(default=None, description="处理结果")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    estimated_completion: Optional[datetime] = Field(default=None, description="预计完成时间")

# ==================== 分页模型 ====================

class PaginationParams(BaseModel):
    """分页参数模型"""
    
    page: int = Field(default=Constants.DEFAULT_PAGE_NUMBER, ge=1, description="页码")
    page_size: int = Field(default=Constants.DEFAULT_PAGE_SIZE, ge=1, le=100, description="每页大小")
    sort_by: Optional[str] = Field(default=None, description="排序字段")
    sort_order: Optional[str] = Field(default="desc", description="排序方向（asc/desc）")
    
    @validator("sort_order")
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("排序方向必须是 'asc' 或 'desc'")
        return v

class PaginatedResponse(BaseModel):
    """分页响应模型"""
    
    items: List[Any] = Field(..., description="数据项列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")

# 导出所有模型
__all__ = [
    # 基础模型
    "BaseModel",
    "SuccessResponse",
    "ErrorResponse",
    
    # 健康检查模型
    "HealthResponse",
    "SystemInfo",
    "AppInfo",
    "ServiceStatus",
    "DetailedHealthResponse",
    
    # 用户相关模型
    "UserInfo",
    "UserContext",
    
    # 聊天相关模型
    "Message",
    "ChatRequest",
    "ChatResponse",
    "Conversation",
    
    # 知识库相关模型
    "KnowledgeBaseCreate",
    "KnowledgeBase",
    
    # 文件相关模型
    "FileUploadResponse",
    "TaskStatusResponse",
    
    # 分页模型
    "PaginationParams",
    "PaginatedResponse",

    # 新增员工相关模型
    "EmployeeBase",
    "EmployeeCreate", 
    "EmployeeUpdate",
    "EmployeeResponse",
    
    # 新增知识库模型
    "KnowledgeBaseCreate",
    "KnowledgeBaseUpdate", 
    "KnowledgeBaseResponse",
    "KnowledgeItemResponse",
    
    # 新增市场广场模型
    "MarketplaceFilter",
    "HireRequest",
    "TrialRequest",
]