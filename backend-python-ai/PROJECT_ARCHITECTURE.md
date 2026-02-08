# 🏗️ MEK-AI Python AI服务 - 完整架构与开发总览

## 📋 目录
1. [核心架构与铁律](#-核心架构与铁律-不可违背)
2. [项目结构全览](#-项目结构全览-完整目录树)
3. [前后端数据模型映射](#-前后端数据模型映射)
4. [当前模块状态](#-当前模块状态-已完成部分)
5. [后续开发计划](#-后续开发计划-阶段化路线图)
6. [技术栈与决策](#-技术栈与关键决策)

---

## ⚙️ 核心架构与铁律 (不可违背)

### 1. 核心模式：分层架构
```
┌─────────────────────────────────────────────────────────────┐
│                      API 层 (api/)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  endpoints/ │  │ middleware  │  │    dependencies     │  │
│  │  - chat     │  │ - CORS      │  │ - 权限验证          │  │
│  │  - health   │  │ - Logging   │  │ - 用户上下文        │  │
│  │  - files    │  │ - Exception │  │                     │  │
│  └──────┬──────┘  └─────────────┘  └─────────────────────┘  │
├─────────┼───────────────────────────────────────────────────┤
│         ▼                                                   │
│                   业务服务层 (services/)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │     ai/     │  │ processing/ │  │       memory/       │  │
│  │ - chat      │  │ - document  │  │ - conversation      │  │
│  │ - rag       │  │ - text      │  │   memory            │  │
│  │ - model     │  │ - embedding │  │                     │  │
│  │   manager   │  │ - vector    │  │                     │  │
│  │             │  │   store     │  │                     │  │
│  └──────┬──────┘  └─────────────┘  └─────────────────────┘  │
├─────────┼───────────────────────────────────────────────────┤
│         ▼                                                   │
│                    智能体层 (agents/)                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           DigitalEmployeeAgent (数字员工智能体)          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │ │
│  │  │  base_agent │  │  employee   │  │     tools/      │  │ │
│  │  │             │  │   agent     │  │ - knowledge     │  │ │
│  │  │             │  │             │  │   retrieval     │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    数据与配置层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ models/     │  │  config/    │  │       utils/        │  │
│  │ - schemas   │  │ - settings  │  │ - logger            │  │
│  │ - enums     │  │ - constants │  │ - file_utils        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2. 开发工作流 (每个模块必须遵循)
```
1. 定义 → 2. 服务实现 → 3. API端点 → 4. 集成测试
   ↓          ↓            ↓            ↓
schemas   services/     endpoints/    test_api.py
models    业务逻辑      路由处理       接口验证
```

### 3. 绝对禁止项
- ❌ **禁止** 在 `api/endpoints/` 中编写：业务逻辑、数据库操作、AI模型调用
- ❌ **禁止** 在 `services/` 中编写：HTTP响应处理、请求验证（应在schemas层）
- ❌ **禁止** 直接绕过 `services` 层从 `api` 层调用 `agents` 层
- ✅ **允许** 在 `api/endpoints/` 中：参数提取、调用服务层、返回响应
- ✅ **允许** 在 `services/` 中：业务逻辑编排、状态管理、错误处理

### 4. 数据流原则
- **单向数据流**：`Client` → `API Layer` → `Services Layer` → `Agents Layer`
- **响应流**：`Agents Layer` → `Services Layer` → `API Layer` → `Client`
- **错误处理**：
  - 业务错误 → services层抛出 → api层捕获 → HTTP响应
  - 系统错误 → 中间件统一处理

---

## 📁 项目结构全览 (完整目录树)

```
backend-python-ai/
├── app/                           # 【应用主目录】
│   ├── __init__.py
│   ├── main.py                    # FastAPI应用创建与生命周期管理
│   │
│   ├── config/                    # 【配置层】
│   │   ├── __init__.py
│   │   ├── settings.py            # 主配置 (Pydantic BaseSettings)
│   │   │                          # - 应用基础配置
│   │   │                          # - LLM API密钥 (OpenAI/Anthropic/Gemini/DeepSeek)
│   │   │                          # - 向量数据库配置 (ChromaDB)
│   │   │                          # - CORS/安全/日志配置
│   │   └── constants.py           # 枚举、常量定义
│   │                              # - ModelProvider, VectorDBType
│   │                              # - TaskStatus, FileType
│   │
│   ├── api/                       # 【API层：处理HTTP】
│   │   ├── __init__.py
│   │   ├── dependencies.py        # 依赖项注入
│   │   │                          # - get_current_user (模拟用户验证)
│   │   │                          # - get_optional_user (可选用户验证)
│   │   │                          # - UserContext 用户上下文
│   │   ├── middleware.py          # 中间件
│   │   │                          # - LoggingMiddleware (请求日志)
│   │   │                          # - RequestIDMiddleware (请求追踪)
│   │   │                          # - ExceptionHandlingMiddleware (异常处理)
│   │   │                          # - CaseConverterMiddleware (命名转换)
│   │   ├── router.py              # 全局路由聚合
│   │   │                          # - /api/v1/health
│   │   │                          # - /api/v1/chat
│   │   │                          # - /api/v1/employees
│   │   │                          # - /api/v1/knowledge-bases
│   │   │                          # - /api/v1/marketplace
│   │   └── v1/                    # API v1版本
│   │       ├── __init__.py
│   │       └── endpoints/         # 具体端点实现
│   │           ├── __init__.py
│   │           ├── health.py      # GET /health (健康检查)
│   │           ├── chat.py        # POST /chat (核心聊天API)
│   │           │                  # - 发送消息
│   │           │                  # - 获取对话列表/详情
│   │           │                  # - 删除对话
│   │           │                  # - 获取智能体列表
│   │           ├── employees.py   # 数字员工管理
│   │           │                  # - CRUD操作
│   │           │                  # - 发布/预览
│   │           │                  # - 分类列表
│   │           ├── knowledge.py   # 知识库管理 (预留)
│   │           │                  # - 知识库CRUD
│   │           │                  # - 文档上传/解析
│   │           ├── marketplace.py # 市场广场
│   │           │                  # - 员工列表
│   │           │                  # - 雇佣/试用
│   │           └── files.py       # 文件上传 (预留)
│   │
│   ├── services/                  # 【业务服务层：核心逻辑】
│   │   ├── __init__.py
│   │   ├── employee_service.py    # 员工服务 (内存存储)
│   │   │                          # - 员工CRUD
│   │   │                          # - 雇佣/试用逻辑
│   │   │                          # - 示例数据初始化
│   │   ├── ai/                    # AI核心服务
│   │   │   ├── __init__.py
│   │   │   ├── chat_service.py    # 聊天服务入口
│   │   │   │                      # - process_chat_message()
│   │   │   │                      # - 对话管理
│   │   │   │                      # - 智能体生命周期
│   │   │   ├── chat_deepseek.py   # DeepSeek模型集成
│   │   │   │                      # - ChatDeepSeek类
│   │   │   │                      # - 支持DeepSeek API
│   │   │   ├── rag_service.py     # RAG检索服务 (预留)
│   │   │   └── model_manager.py   # 多模型管理
│   │   │                          # - OpenAI/Anthropic/Gemini/DeepSeek
│   │   │                          # - 模型配置验证
│   │   │                          # - 模型切换
│   │   ├── processing/            # 数据处理
│   │   │   ├── __init__.py
│   │   │   ├── document_parser.py # 解析PDF, Word, TXT (预留)
│   │   │   ├── text_splitter.py   # 文本分割 (预留)
│   │   │   ├── embedding_service.py # 生成向量 (预留)
│   │   │   └── vector_store.py    # 向量数据库(Chroma)操作 (预留)
│   │   └── memory/                # 对话记忆管理
│   │       ├── __init__.py
│   │       └── conversation_memory.py # 基于LangChain Memory封装
│   │                              # - 对话状态管理
│   │                              # - 历史消息存储
│   │                              # - 对话摘要生成
│   │
│   ├── agents/                    # 【智能体层：LangChain编排】
│   │   ├── __init__.py
│   │   ├── base_agent.py          # 智能体基类
│   │   ├── digital_employee_agent.py # 数字员工智能体（主）
│   │   │                          # - 人设/技能配置
│   │   │                          # - 消息处理流程
│   │   │                          # - 工具调用
│   │   └── tools/                 # 工具定义
│   │       ├── __init__.py
│   │       └── knowledge_retrieval_tool.py # 知识库检索工具 (预留)
│   │
│   ├── models/                    # 【数据模型】
│   │   ├── __init__.py
│   │   ├── schemas.py             # Pydantic模型（请求/响应验证）
│   │   │                          # - ChatRequest/ChatResponse
│   │   │                          # - SuccessResponse/ErrorResponse
│   │   │                          # - Conversation/Message
│   │   │                          # - EmployeeBase/EmployeeResponse
│   │   │                          # - HireRequest/TrialRequest
│   │   └── enums.py               # 状态枚举等
│   │
│   └── utils/                     # 【工具函数】
│       ├── __init__.py
│       ├── logger.py              # 日志配置 (LoggerMixin)
│       └── file_utils.py          # 文件操作
│
├── data/                          # 本地数据存储（开发用）
│   ├── uploads/                   # 上传的文件
│   └── vector_db/                 # ChromaDB数据
│
├── logs/                          # 日志文件目录
│
├── tests/                         # 测试目录
│
├── .env                           # 环境变量配置
├── .env.example                   # 环境变量模板
├── requirements.txt               # Python依赖
├── pyproject.toml                 # 项目配置
├── README.md                      # 项目说明
├── PROJECT_ARCHITECTURE.md        # 项目架构文档
├── Dockerfile                     # Docker构建
├── docker-compose.yml             # Docker编排
├── start.bat                      # Windows启动脚本
├── simple_test.py                 # 简单测试脚本
├── test_multi_turn.py             # 多轮对话测试脚本
├── debug_agent_scratchpad.py      # Agent调试脚本
└── diagnose_routes.py             # 路由诊断脚本
```

### 关键文件说明
- **`main.py`**：FastAPI应用入口，生命周期管理，中间件注册
- **`settings.py`**：统一配置管理，支持.env文件和环境变量
- **`chat_service.py`**：聊天业务逻辑核心，协调智能体和记忆
- **`chat_deepseek.py`**：DeepSeek模型集成，支持国内大模型
- **`employee_service.py`**：员工服务，内存存储实现
- **`digital_employee_agent.py`**：数字员工智能体，基于LangChain实现
- **`conversation_memory.py`**：对话记忆管理，支持多轮对话
- **`model_manager.py`**：多LLM提供商管理(OpenAI/Anthropic/Gemini/DeepSeek)
- **`schemas.py`**：Pydantic模型定义，请求/响应验证
- **`dependencies.py`**：依赖注入，用户认证上下文
- **`marketplace.py`**：市场广场API，雇佣/试用功能
- **`employees.py`**：员工管理API，CRUD操作

---

## 🔄 前后端数据模型映射

### 概述
后端服务的核心目标是将前端Mock数据切换为真实数据。以下是前端Mock数据结构与后端Pydantic模型的映射关系。

### 1. 数字员工模型映射

#### 前端Mock数据 (TypeScript)
```typescript
// src/shared/types/employee.ts
interface Employee {
    id: string;
    name: string;
    description: string;
    avatar: string;
    category: string[];
    tags: string[];
    price: number | 'free';
    originalPrice?: number;
    trialCount: number;
    hireCount: number;
    isHired: boolean;
    isRecruited: boolean;
    isInTrial?: boolean;
    hiredAt?: string;
    createdAt?: string;
    createdBy?: string;
    status?: 'published' | 'archived' | 'active' | 'inactive' | 'draft';
    skills?: string[];
    knowledgeBaseIds?: string[];
    isHot?: boolean;
    industry?: string;
    role?: string;
    prompt?: string;
    model?: string;
}
```

#### 后端对应模型 (Python)
```python
# app/models/schemas.py (已实现)
class EmployeeBase(BaseModel):
    """员工基础模型"""
    name: str
    description: str
    avatar: Optional[str] = None
    category: List[str] = []
    tags: List[str] = []
    price: Union[int, str] = 0  # 支持数字或'free'
    original_price: Optional[int] = None
    skills: List[str] = []
    industry: Optional[str] = None
    role: Optional[str] = None
    prompt: Optional[str] = None
    model: Optional[str] = None
    knowledge_base_ids: List[str] = []
    is_hot: Optional[bool] = False

class EmployeeCreate(EmployeeBase):
    """创建员工请求"""
    pass

class EmployeeResponse(EmployeeBase):
    """员工响应模型"""
    id: str
    trial_count: int = 0
    hire_count: int = 0
    is_hired: bool = False
    is_recruited: bool = False
    status: str = "draft"
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    
    class Config:
        from_attributes = True
```

#### 字段映射表
| 前端字段 | 后端字段 | 说明 |
|---------|---------|------|
| `id` | `id` | 员工唯一标识 |
| `name` | `name` | 员工名称 |
| `description` | `description` | 员工描述 |
| `avatar` | `avatar` | 头像URL |
| `category` | `category` | 分类标签数组 |
| `tags` | `tags` | 标签数组 |
| `price` | `price` | 价格(数字或'free') |
| `originalPrice` | `original_price` | 原价 |
| `trialCount` | `trial_count` | 试用次数 |
| `hireCount` | `hire_count` | 雇佣次数 |
| `isHired` | `is_hired` | 是否已雇佣 |
| `isRecruited` | `is_recruited` | 是否已招聘 |
| `status` | `status` | 状态(published/draft/archived) |
| `skills` | `skills` | 技能列表 |
| `knowledgeBaseIds` | `knowledge_base_ids` | 关联知识库ID |
| `industry` | `industry` | 所属行业 |
| `role` | `role` | 岗位角色 |
| `prompt` | `prompt` | 系统提示词 |
| `model` | `model` | 使用的AI模型 |
| `isHot` | `is_hot` | 是否热门 |
| `createdAt` | `created_at` | 创建时间 |
| `createdBy` | `created_by` | 创建者 |

---

### 2. 聊天消息模型映射

#### 前端Mock数据 (TypeScript)
```typescript
// src/modules/marketplace/types/index.ts
interface Message {
    id: string;
    role: 'user' | 'model' | 'assistant';
    content: string;
    timestamp: number;
}

interface ChatSession {
    id: string;
    title: string;
    employeeId: string;
    lastModified: number;
}
```

#### 后端对应模型 (Python)
```python
# app/models/schemas.py (已实现)
class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., min_length=1, max_length=5000)
    employee_id: str = Field(..., description="员工ID")
    conversation_id: Optional[str] = Field(default=None)
    stream: bool = Field(default=False)
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=16000)

class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str = Field(..., description="AI回复")
    conversation_id: str = Field(..., description="对话ID")
    message_id: str = Field(..., description="消息ID")
    timestamp: datetime = Field(..., description="响应时间")

class Conversation(BaseModel):
    """对话模型"""
    conversation_id: str
    employee_id: str
    user_id: Optional[str] = None
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
```

#### 字段映射表
| 前端字段 | 后端字段 | 说明 |
|---------|---------|------|
| `id` | `conversation_id` / `message_id` | 会话/消息ID |
| `role` | `role` | 角色(user/model/assistant) |
| `content` | `content` / `message` | 消息内容 |
| `timestamp` | `timestamp` | 时间戳 |
| `employeeId` | `employee_id` | 员工ID |
| `title` | `title` | 会话标题 |
| `lastModified` | `updated_at` | 最后修改时间 |

---

### 3. API端点映射 (已实现)

#### 数字员工API
```
GET    /api/v1/employees                    # 获取员工列表 ✅
GET    /api/v1/employees/{id}               # 获取单个员工 ✅
POST   /api/v1/employees                    # 创建员工 ✅
PUT    /api/v1/employees/{id}               # 更新员工 ✅
DELETE /api/v1/employees/{id}               # 删除员工 ✅
POST   /api/v1/employees/{id}/publish       # 发布员工 ✅
GET    /api/v1/employees/categories         # 获取分类列表 ✅
```

#### 市场广场API
```
GET    /api/v1/marketplace/employees        # 获取市场员工列表 ✅
GET    /api/v1/marketplace/categories       # 获取分类列表 ✅
POST   /api/v1/marketplace/{id}/hire        # 雇佣员工 ✅
POST   /api/v1/marketplace/{id}/trial       # 试用员工 ✅
```

#### 聊天API (已实现)
```
POST   /api/v1/chat                         # 发送消息 ✅
GET    /api/v1/chat/conversations          # 获取对话列表 ✅
GET    /api/v1/chat/conversations/{id}     # 获取对话详情 ✅
DELETE /api/v1/chat/conversations/{id}     # 删除对话 ✅
GET    /api/v1/chat/agents                 # 获取智能体列表 ✅
```

#### 知识库API (预留)
```
GET    /api/v1/knowledge-bases              # 获取知识库列表 ⏳
POST   /api/v1/knowledge-bases              # 创建知识库 ⏳
GET    /api/v1/knowledge-bases/{id}         # 获取知识库详情 ⏳
PUT    /api/v1/knowledge-bases/{id}         # 更新知识库 ⏳
DELETE /api/v1/knowledge-bases/{id}         # 删除知识库 ⏳
POST   /api/v1/knowledge-bases/{id}/upload  # 上传文档 ⏳
```

---

## 📊 当前模块状态 (已完成部分)

### ✅ 核心基础设施 (完成度 100%)
- **FastAPI应用框架**：完整的应用生命周期管理
- **配置系统**：Pydantic Settings，支持多环境配置
- **日志系统**：结构化日志，支持请求追踪
- **中间件**：CORS、请求日志、异常处理、请求ID追踪
- **健康检查**：详细的健康检查端点
- **核心文件**：
  - [main.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/main.py)
  - [settings.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/config/settings.py)
  - [middleware.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/api/middleware.py)

### ✅ 聊天服务模块 (完成度 95%)
- **功能**：消息处理、对话管理、多轮对话、智能体生命周期
- **状态**：核心功能完整，支持OpenAI/Anthropic/Gemini/DeepSeek
- **特性**：
  - 对话创建/获取/删除
  - 消息历史管理
  - 智能体动态创建
  - 性能计时统计
  - 多模型支持
- **核心文件**：
  - [chat_service.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/services/ai/chat_service.py)
  - [chat_deepseek.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/services/ai/chat_deepseek.py)
  - [chat.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/api/v1/endpoints/chat.py)
  - [digital_employee_agent.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/agents/digital_employee_agent.py)

### ✅ 对话记忆模块 (完成度 85%)
- **功能**：对话状态管理、历史消息存储、对话摘要
- **状态**：内存存储实现，支持持久化扩展
- **特性**：
  - 多对话管理
  - 消息历史查询
  - 对话元数据
- **核心文件**：
  - [conversation_memory.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/services/memory/conversation_memory.py)

### ✅ 模型管理模块 (完成度 90%)
- **功能**：多LLM提供商管理、模型配置、动态切换
- **支持提供商**：OpenAI、Anthropic、Google Gemini、DeepSeek
- **特性**：
  - 统一模型接口
  - 配置验证
  - 温度/Token参数控制
- **核心文件**：
  - [model_manager.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/services/ai/model_manager.py)

### ✅ 数据模型层 (完成度 95%)
- **功能**：Pydantic模型定义、请求/响应验证
- **状态**：核心模型完整
- **包含模型**：
  - ChatRequest/ChatResponse
  - SuccessResponse/ErrorResponse
  - Conversation/Message
  - EmployeeBase/EmployeeCreate/EmployeeResponse
  - HireRequest/TrialRequest
  - UserContext
- **核心文件**：
  - [schemas.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/models/schemas.py)

### ✅ 员工服务模块 (完成度 90%)
- **功能**：员工CRUD、雇佣/试用、内存存储
- **状态**：功能完整，使用内存存储
- **特性**：
  - 员工列表/详情/创建/更新/删除
  - 雇佣/试用逻辑
  - 分类列表
  - 示例数据初始化
- **核心文件**：
  - [employee_service.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/services/employee_service.py)
  - [employees.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/api/v1/endpoints/employees.py)

### ✅ 市场广场模块 (完成度 85%)
- **功能**：市场员工列表、雇佣、试用
- **状态**：核心功能实现
- **特性**：
  - 员工列表（支持过滤）
  - 雇佣员工
  - 试用员工
  - 分类/行业列表
- **核心文件**：
  - [marketplace.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/api/v1/endpoints/marketplace.py)

### ⏳ 知识库模块 (完成度 20%)
- **功能**：文档上传、向量化、知识检索
- **状态**：目录结构创建，核心逻辑待实现
- **依赖组件**：
  - document_parser.py (预留)
  - text_splitter.py (预留)
  - embedding_service.py (预留)
  - vector_store.py (预留)

### ⏳ 文件处理模块 (完成度 10%)
- **功能**：文件上传、存储、处理任务管理
- **状态**：端点预留，实现待开发

### ⏳ RAG服务模块 (完成度 10%)
- **功能**：检索增强生成、知识库查询
- **状态**：目录结构创建，待实现

---

## 🗺️ 后续开发计划 (阶段化路线图)

### 第一阶段：知识库与RAG (预计：2周)
**目标**：实现完整的知识库管理和RAG检索

| 模块 | 核心功能 | 技术要点 |
|------|----------|----------|
| **1. 文档处理**<br>(`processing/`) | • PDF/Word/TXT解析<br>• 文本分割与清洗<br>• 向量化生成 | • unstructured库<br>• sentence-transformers<br>• tiktoken分词 |
| **2. 向量数据库**<br>(`vector_store.py`) | • ChromaDB集成<br>• 集合管理<br>• 相似度检索 | • chromadb<br>• 向量索引<br>• 元数据过滤 |
| **3. RAG服务**<br>(`rag_service.py`) | • 检索策略<br>• 上下文组装<br>• 引用溯源 | • LangChain RAG<br>• 重排序<br>• 结果融合 |

### 第二阶段：持久化与优化 (预计：1周)
**目标**：添加数据库持久化和性能优化

| 模块 | 核心功能 | 技术要点 |
|------|----------|----------|
| **1. 数据库层** | • PostgreSQL/MySQL集成<br>• SQLAlchemy ORM<br>• 数据迁移 | • SQLAlchemy 2.0<br>• Alembic迁移<br>• 连接池管理 |
| **2. 缓存层** | • Redis缓存<br>• 对话缓存<br>• 热点数据缓存 | • redis-py<br>• 缓存策略<br>• 过期策略 |
| **3. 记忆优化** | • 消息截断<br>• 对话总结<br>• 分层记忆 | • ConversationSummaryMemory<br>• Token限制 |

### 第三阶段：高级功能 (预计：2周)
**目标**：实现企业级功能和性能优化

| 模块 | 核心功能 | 技术要点 |
|------|----------|----------|
| **1. 流式响应** | • SSE流式输出<br>• 打字机效果<br>• 中断处理 | • StreamingResponse<br>• 异步生成器 |
| **2. 多模态支持** | • 图片理解<br>• 语音处理 | • GPT-4V<br>• Whisper API |
| **3. 性能优化** | • 连接池<br>• 缓存层<br>• 限流 | • Redis缓存<br>• slowapi限流 |

---

## 🛠️ 技术栈与关键决策

### 核心技术栈
```json
{
  "dependencies": {
    "fastapi": "0.104.1",           // Web框架
    "uvicorn": "0.24.0",            // ASGI服务器
    "pydantic": "2.5.0",            // 数据验证
    "pydantic-settings": "2.1.0",   // 配置管理
    "langchain": ">=0.1.0,<0.2",    // AI编排框架
    "langchain-openai": "0.0.5",    // OpenAI集成
    "openai": ">=1.10.0,<2.0.0",    // OpenAI SDK
    "anthropic": ">=0.16.0,<1",     // Claude SDK
    "google-generativeai": "0.3.1", // Gemini SDK
    "chromadb": "0.4.18",           // 向量数据库
    "sentence-transformers": "2.2.2", // 嵌入模型
    "celery": "5.3.4",              // 任务队列
    "redis": "5.0.1"                // 缓存/消息 broker
  },
  "devDependencies": {
    "black": "23.11.0",             // 代码格式化
    "flake8": "6.1.0",              // 代码检查
    "pytest": "7.4.3",              // 测试框架
    "pytest-asyncio": "0.21.1"      // 异步测试
  }
}
```

### 关键架构决策

#### 1. Web框架选择：FastAPI
**理由**：
- ✅ 原生异步支持 (async/await)
- ✅ 自动API文档生成 (/docs, /redoc)
- ✅ Pydantic集成，类型安全
- ✅ 高性能，基于Starlette和Uvicorn

#### 2. AI编排：LangChain
**理由**：
- ✅ 统一LLM接口，支持多提供商
- ✅ 丰富的组件生态 (Chains, Agents, Tools)
- ✅ Memory组件支持对话历史
- ✅ 与向量数据库集成

#### 3. 向量数据库：ChromaDB
**理由**：
- ✅ 轻量级，本地嵌入式
- ✅ 与LangChain深度集成
- ✅ 支持持久化存储
- ✅ 开发友好，易于部署

#### 4. 配置管理：Pydantic Settings
**理由**：
- ✅ 类型安全的配置验证
- ✅ 自动.env文件加载
- ✅ 环境变量优先级
- ✅ 计算属性支持

### 数据流设计原则

```
┌─────────────────────────────────────────────────────────────┐
│                        请求处理流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 请求接收                                                 │
│     Client → FastAPI → Middleware → Dependency Injection   │
│                                                             │
│  2. 请求验证                                                 │
│     Pydantic Schemas → 自动验证 → 类型转换                  │
│                                                             │
│  3. 业务处理                                                 │
│     Endpoint → Service Layer → Agent Layer                 │
│                                                             │
│  4. 响应返回                                                 │
│     Agent → Service → Endpoint → Pydantic Response → Client │
│                                                             │
│  5. 错误处理                                                 │
│     Exception → Middleware Handler → ErrorResponse          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 开发规范

#### 文件命名规范
- Python模块：`snake_case.py` (如 `chat_service.py`)
- 类名：`PascalCase` (如 `ChatService`)
- 函数/方法：`snake_case` (如 `process_message`)
- 常量：`UPPER_SNAKE_CASE` (如 `DEFAULT_MODEL`)

#### 目录组织规范
```
module_name/
├── __init__.py           # 模块导出
├── service.py            # 业务服务
├── models.py (或 schemas.py) # 数据模型
└── utils.py              # 工具函数
```

#### 代码风格规范
- 使用Black格式化代码
- 使用Flake8检查代码质量
- 类型注解必须完整
- 文档字符串使用Google风格
- 异步函数使用 `async/await`

---

## 📈 项目统计

### 代码规模
- **总文件数**：约45个Python文件
- **核心模块**：6个 (config, api, services, agents, models, utils)
- **API端点**：6个主要端点 (health, chat, employees, marketplace, knowledge, files)
- **服务层**：4个子模块 (ai, processing, memory, employee)

### 完成度统计

#### 核心基础设施
- **FastAPI框架**：100% ✅
- **配置管理**：100% ✅
- **日志系统**：100% ✅
- **中间件**：100% ✅

#### 业务模块
- **聊天服务**：95% ✅ - 核心功能完整，支持多LLM
- **对话记忆**：85% ✅ - 内存存储，需持久化
- **模型管理**：90% ✅ - 支持OpenAI/Anthropic/Gemini/DeepSeek
- **数据模型**：95% ✅ - 基础模型完整
- **员工服务**：90% ✅ - 内存存储实现
- **市场广场**：85% ✅ - 雇佣/试用功能实现

#### 待实现模块
| 模块 | 完成度 | 状态 | 说明 |
|------|-------|------|------|
| **知识库管理** | 20% | ⏳ 结构预留 | 文档处理待实现 |
| **文件上传** | 10% | ⏳ 端点预留 | 待开发 |
| **RAG服务** | 10% | ⏳ 结构预留 | 待实现 |
| **数据库持久化** | 0% | ⏳ 未开始 | 计划使用PostgreSQL |

### 技术债务
1. 知识库向量存储未实现完整CRUD
2. 文件上传端点待开发
3. 缺少数据库持久化层 (当前内存存储)
4. 缺少完整的单元测试覆盖
5. 需要添加API限流和认证
6. 流式响应(SSE)待实现
7. 对话记忆需要优化（Token限制、消息截断）

---

## 📝 总结

MEK-AI Python AI服务采用 **分层架构** 设计，严格遵循关注点分离原则。项目已完成核心基础设施、聊天服务、员工服务和市场广场模块，实现了基于LangChain的数字员工智能体，支持多LLM提供商(OpenAI/Anthropic/Gemini/DeepSeek)。

### 核心优势
- ✅ 清晰的分层架构，易于维护和扩展
- ✅ 完整的类型系统，Pydantic数据验证
- ✅ 多LLM提供商支持，灵活切换
- ✅ 模块化设计，便于团队协作
- ✅ 异步架构，高性能并发处理

### 下一步行动
1. 实现知识库文档处理和向量化
2. 完成RAG检索增强生成服务
3. 添加数据库持久化层 (PostgreSQL)
4. 优化对话记忆（Token限制、消息截断）
5. 实现流式响应(SSE)
6. 完善单元测试和集成测试

---

## 🔄 Mock数据切换路线图

### 切换策略
前端目前使用Mock数据，后端需要逐步实现真实API来替换Mock。切换过程遵循"渐进式替换"原则：

1. **保持接口兼容**：后端API的URL、请求参数、响应格式与前端Mock API保持一致
2. **字段命名转换**：后端使用蛇形命名(snake_case)，前端使用驼峰命名(camelCase)，通过中间件自动转换
3. **增量替换**：按模块逐个替换，确保每个模块替换后前端功能正常

### 切换状态

| 模块 | 前端Mock文件 | 后端状态 | 切换进度 |
|------|-------------|---------|---------|
| **聊天服务** | `marketplace/mockData.ts` | ✅ 已实现 | 100% |
| **数字员工CRUD** | `digital-employee/mockData.ts` | ✅ 已实现 | 100% |
| **市场广场** | `marketplace/mockData.ts` | ✅ 已实现 | 100% |
| **知识库管理** | `knowledge-base/mockData.ts` | ⏳ 需实现 | 0% |
| **文件上传** | `knowledge-base/mockData.ts` | ⏳ 需实现 | 0% |
| **RAG检索** | - | ⏳ 需实现 | 0% |

### 前端适配要点

#### 1. API基础URL配置
```typescript
// src/core/config/api.ts
const API_BASE_URL = 'http://localhost:8000';

// API端点定义
export const API_ENDPOINTS = {
  EMPLOYEES: {
    LIST: '/employees',
    DETAIL: (id: string) => `/employees/${id}`,
    CREATE: '/employees',
    UPDATE: (id: string) => `/employees/${id}`,
    DELETE: (id: string) => `/employees/${id}`,
    PUBLISH: (id: string) => `/employees/${id}/publish`,
    CATEGORIES: '/employees/categories',
  },
  MARKETPLACE: {
    LIST: '/marketplace/employees',
    HIRE: (id: string) => `/marketplace/${id}/hire`,
    TRIAL: (id: string) => `/marketplace/${id}/trial`,
    CATEGORIES: '/marketplace/categories',
  },
  CHAT: {
    SEND: '/chat',
    SESSIONS: '/chat/conversations',
    SESSION_MESSAGES: (id: string) => `/chat/conversations/${id}`,
    DELETE_SESSION: (id: string) => `/chat/conversations/${id}`,
  },
};
```

#### 2. 响应数据转换
```typescript
// 后端返回蛇形命名，前端需要转换为驼峰命名
const adaptEmployee = (backendData: any): Employee => ({
  id: backendData.id,
  name: backendData.name,
  description: backendData.description,
  // 字段名映射
  trialCount: backendData.trial_count,
  hireCount: backendData.hire_count,
  isHired: backendData.is_hired,
  knowledgeBaseIds: backendData.knowledge_base_ids,
  createdAt: backendData.created_at,
  createdBy: backendData.created_by,
  // ...
});
```

#### 3. 错误处理统一
后端统一返回格式：
```json
{
  "success": false,
  "message": "错误描述",
  "data": null,
  "timestamp": "2024-01-01T00:00:00"
}
```

### 数据库设计建议

#### 员工表 (employees)
```sql
CREATE TABLE employees (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    avatar VARCHAR(500),
    category JSON,  -- ["strategy", "marketing"]
    tags JSON,      -- ["expert", "pro"]
    price INT,      -- 0表示free
    trial_count INT DEFAULT 0,
    hire_count INT DEFAULT 0,
    is_hired BOOLEAN DEFAULT FALSE,
    is_recruited BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'draft',  -- published/draft/archived
    skills JSON,
    knowledge_base_ids JSON,
    industry VARCHAR(50),
    role VARCHAR(50),
    prompt TEXT,
    model VARCHAR(50),
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 知识库表 (knowledge_bases)
```sql
CREATE TABLE knowledge_bases (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    doc_count INT DEFAULT 0,
    created_by VARCHAR(36),
    status VARCHAR(20) DEFAULT 'active',
    tags JSON,
    is_public BOOLEAN DEFAULT TRUE,
    vectorized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 知识条目表 (knowledge_items)
```sql
CREATE TABLE knowledge_items (
    id VARCHAR(36) PRIMARY KEY,
    knowledge_base_id VARCHAR(36),
    serial_no INT,
    content TEXT,
    word_count INT,
    source_file VARCHAR(200),
    metadata JSON,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id)
);
```

#### 对话表 (conversations)
```sql
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36),
    title VARCHAR(200),
    message_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 消息表 (messages)
```sql
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36),
    role VARCHAR(20),  -- user/assistant/system
    content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```
