# 🔧 MEK-AI 前后端联调问题记录与解决方案

> 记录日期：2026-02-06
> 记录人：AI Assistant
> 项目阶段：前后端联调阶段

---

## 📋 今日联调解决的问题清单

### 问题1：员工列表返回0条数据
**现象**：前端请求 `/api/v1/employees` 返回空数组，但分类接口正常返回6个分类

**根本原因**：
- 后端 `list_employees` 方法接收了 `user_id="anonymous"` 参数
- 过滤逻辑：`if user_id and emp_data.get("created_by") != user_id` 会过滤掉所有员工
- 示例员工的 `created_by` 是 `"system"` 或 `"user_001"`，不是 `"anonymous"`

**解决方案**：
```python
# app/api/v1/endpoints/employees.py
# 获取当前用户ID（可能为None或anonymous）
user_id = current_user.user_id if current_user else None
# 如果是anonymous，视为未登录，不应用用户过滤
if user_id == "anonymous":
    user_id = None
```

**经验总结**：
- 匿名用户处理要统一，不能把 `"anonymous"` 当作有效用户ID进行过滤
- 可选用户验证应该使用 `get_optional_user` 而不是 `get_current_user`

---

### 问题2：路由冲突 - `/categories` 被匹配为 `/{employee_id}`
**现象**：请求 `/api/v1/employees/categories` 返回404，被错误路由到 `/{employee_id}`

**根本原因**：
- FastAPI 路由按定义顺序匹配
- `/{employee_id}` 定义在 `/categories` 之前
- 请求 `/categories` 时，FastAPI 把 `"categories"` 当作 `employee_id` 参数

**解决方案**：
```python
# app/api/v1/endpoints/employees.py
# 路由定义顺序很重要！静态路由必须在动态路由之前

@router.get("/categories", ...)  # ✅ 先定义静态路由
async def get_employee_categories(...):
    ...

@router.get("/{employee_id}", ...)  # ✅ 后定义动态路由
async def get_employee(employee_id: str, ...):
    ...
```

**经验总结**：
- FastAPI 路由匹配是顺序的，静态路由必须在动态路由之前定义
- 通用规则：`/static` 类型的路由要在 `/{param}` 之前定义

---

### 问题3：雇佣接口返回422错误
**现象**：点击"免费招聘"按钮，后端返回422 Unprocessable Entity

**根本原因**：
- 后端 `HireRequest` 模型要求 `employee_id` 字段必填
- 前端发送的请求体是空对象 `{}`
- URL路径中已经包含 `employee_id`，但请求体中没有

**解决方案**：
```python
# app/models/schemas.py
class HireRequest(PydanticBaseModel):
    """雇佣请求模型"""
    # 修改前：employee_id: str = Field(..., description="员工ID")
    # 修改后：
    employee_id: Optional[str] = Field(None, description="员工ID（可选，URL路径中已包含）")
    organization_id: Optional[str] = Field(None, description="组织ID")
    payment_method: Optional[str] = Field(None, description="支付方式")
```

**经验总结**：
- 请求体字段如果可以从URL路径获取，应该设为 Optional
- 避免重复要求同一个参数（URL路径 + 请求体）

---

### 问题4：雇佣接口返回400错误 - "该员工已被雇佣"
**现象**：雇佣接口返回400，提示员工已被雇佣

**根本原因**：
- 示例数据 `emp_003` 的 `is_hired` 字段被设为 `True`
- 后端逻辑会检查 `if existing_employee.is_hired` 并拒绝重复雇佣

**解决方案**：
```python
# app/services/employee_service.py
# 修改示例数据
{
    "id": "emp_003",
    ...
    "is_hired": False,  # 修改前是 True
    "is_recruited": False,
    ...
}
```

**经验总结**：
- 示例数据要确保状态正确，避免初始化时设置不合理的状态
- 雇佣/试用等操作前必须检查当前状态

---

### 问题5：聊天接口返回422错误
**现象**：发送消息后，后端返回422错误

**根本原因**：
- 聊天接口使用了 `get_current_user` 依赖
- `get_current_user` 要求必须提供 `X-Employee-ID` 请求头
- 但聊天时这个头可能还没设置

**解决方案**：
```python
# app/api/v1/endpoints/chat.py
# 修改前：
current_user: UserContext = Depends(get_current_user)

# 修改后：
current_user: Optional[UserContext] = Depends(get_optional_user)

# 并在代码中处理 current_user 为 None 的情况
user_id = current_user.user_id if current_user else "anonymous"
```

**经验总结**：
- 不是所有接口都需要强制登录，聊天等场景应该支持匿名用户
- 使用 `get_optional_user` 代替 `get_current_user` 来支持可选认证

---

### 问题6：前端只显示"消息处理成功"，不显示AI回复
**现象**：后端返回200成功，但前端只显示"消息处理成功"，没有AI的实际回复内容

**根本原因**：
- 后端返回格式：`{ success: true, message: "消息处理成功", data: { response: "AI回复" } }`
- 前端期望格式：`{ message: "AI回复" }`
- 前端直接使用了 `response.message` 而不是 `response.data.response`

**解决方案**：
```typescript
// frontend/src/modules/marketplace/logic/services/employeeApi.ts
// 修改前：
const response = await apiClient.post<{
  message: string;
  conversation_id?: string;
}>(API_ENDPOINTS.CHAT.SEND, {...});
return response;

// 修改后：
const response = await apiClient.post<ApiResponse<any>>(API_ENDPOINTS.CHAT.SEND, {...});

// 后端返回格式: { success: true, message: "消息处理成功", data: { response: "AI回复", ... } }
if (!response.success || !response.data) {
  throw new Error(response.message || '聊天请求失败');
}

return {
  message: response.data.response || response.data.message || '无回复',
  conversation_id: response.data.conversation_id,
};
```

**经验总结**：
- 前后端要统一响应格式，后端使用 `SuccessResponse` 包装时，前端要正确解析 `data` 字段
- 不要直接返回后端的 `message` 字段（那是给用户的提示信息），要返回 `data.response`（实际的AI回复）

---

## 🔄 数据流向说明

### 1. 员工列表查询流程
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   前端请求   │────▶│  employees  │────▶│   依赖注入   │────▶│   服务层    │
│  GET /employees │  │   端点      │     │ get_optional_user │  │ list_employees │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                    │
                                                                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   前端展示   │◀────│  响应转换    │◀────│ SuccessResponse│◀────│  内存存储   │
│  Employee[]  │     │ snake→camel │     │ {success, data}│     │ _employees  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**关键注意点**：
- `user_id="anonymous"` 要转换为 `None`，避免过滤掉所有数据
- 响应数据需要从 snake_case 转换为 camelCase

---

### 2. 雇佣员工流程
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   前端点击   │────▶│  marketplace│────▶│   依赖注入   │────▶│   服务层    │
│  "免费招聘"  │     │ /{id}/hire  │     │ get_optional_user │  │ hire_employee │
│  POST {}    │     │  端点       │     │               │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                    │
                                                                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   前端提示   │◀────│  SuccessResponse│◀────│  状态更新    │◀────│  内存存储   │
│  "雇佣成功"  │     │ {success, data}│     │ is_hired=True │     │ _employees  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**关键注意点**：
- 请求体可以为空 `{}`，因为 `employee_id` 已经在URL路径中
- 要检查员工当前状态，避免重复雇佣
- 匿名用户也要支持雇佣操作

---

### 3. 聊天消息流程
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   前端发送   │────▶│    chat     │────▶│   依赖注入   │────▶│   服务层    │
│  "你好"     │     │   端点      │     │ get_optional_user │  │ chat_service │
│  POST {msg} │     │             │     │               │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                    │
                                                                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   前端展示   │◀────│  响应解析    │◀────│ SuccessResponse│◀────│    Agent    │
│  AI回复内容  │     │ data.response│     │ {success, data}│     │  LangChain  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**关键注意点**：
- 前端要解析 `response.data.response`，不是 `response.message`
- `response.message` 是状态提示（如"消息处理成功"）
- `response.data.response` 才是AI的实际回复内容
- 支持匿名用户聊天

---

## 📝 联调最佳实践

### 1. 路由定义顺序
```python
# ✅ 正确：静态路由在前，动态路由在后
@router.get("/categories", ...)
@router.get("/industries", ...)
@router.get("/{employee_id}", ...)

# ❌ 错误：动态路由会拦截静态路由
@router.get("/{employee_id}", ...)
@router.get("/categories", ...)  # 永远不会被匹配
```

### 2. 匿名用户处理
```python
# ✅ 正确：处理 anonymous 为未登录
user_id = current_user.user_id if current_user else None
if user_id == "anonymous":
    user_id = None

# ❌ 错误：anonymous 会被当作有效用户ID
user_id = current_user.user_id if current_user else "anonymous"
```

### 3. 响应格式统一
```python
# 后端统一返回格式
return SuccessResponse(
    success=True,
    message="操作成功提示",  # 给用户看的提示
    data={
        "response": "AI实际回复内容",  # 实际业务数据
        "conversation_id": "xxx"
    }
)
```

```typescript
// 前端统一解析
const response = await apiClient.post<ApiResponse<any>>(url, data);
if (!response.success) {
  throw new Error(response.message);
}
// 使用 response.data.xxx 获取实际数据
return {
  message: response.data.response,
  conversation_id: response.data.conversation_id
};
```

### 4. 请求体验证
```python
# ✅ 正确：URL路径中的参数设为 Optional
class HireRequest(BaseModel):
    employee_id: Optional[str] = None  # URL路径中已提供
    organization_id: Optional[str] = None

# ❌ 错误：重复要求必填
class HireRequest(BaseModel):
    employee_id: str = Field(..., description="员工ID")  # 必填，但URL中已提供
```

---

## 🐛 调试技巧

### 1. 查看后端日志
```bash
# 实时查看日志
tail -f logs/app.log

# 过滤特定接口
tail -f logs/app.log | grep "hire"
```

### 2. 检查路由注册
```python
# diagnose_routes.py
from app.main import app

for route in app.routes:
    print(f"{route.methods} {route.path}")
```

### 3. 验证请求响应
```python
# 在关键位置添加日志
logger.info(f"收到请求: {method} {path}, 参数: {params}")
logger.info(f"处理结果: {result}")
logger.info(f"返回响应: {response}")
```

---

## 📚 知识库模块联调记录 (2026-02-07)

### 问题1：FastAPI Body 参数解析问题
**现象**：创建知识库时返回 422，提示 `Field required: kb_data`

**根本原因**：
- FastAPI 对于 POST/PUT 请求的 Body 参数，默认会尝试将参数名作为 JSON 的 key
- 后端定义 `kb_data: KnowledgeBaseCreate`，FastAPI 期望请求体是 `{"kb_data": {...}}`
- 但前端直接发送了 `{...}`，导致验证失败

**解决方案**：
```python
# 后端：使用 Body(...) 明确指定参数来源
@router.post("/knowledge-bases")
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate = Body(...),  # 明确使用 Body
    current_user: UserContext = Depends(get_current_user),
) -> SuccessResponse:
    ...

# 前端：按照后端期望的格式发送
const response = await apiClient.post('/knowledge-bases', {
    kb_data: {
        name: data.name,
        description: data.description,
        is_public: data.isPublic,
        tags: data.tags,
    }
});
```

**经验总结**：
- FastAPI 的 Body 参数默认会尝试从请求体中解析与参数名相同的 key
- 如果后端参数名是 `kb_data`，前端必须发送 `{"kb_data": {...}}`
- 或者后端使用 `Body(..., embed=True)` 来支持直接发送数据

---

### 问题2：数据格式转换（snake_case ↔ camelCase）
**现象**：后端返回的数据字段名是 snake_case，前端期望 camelCase

**根本原因**：
- Python 后端使用 snake_case（`doc_count`, `created_at`）
- TypeScript 前端使用 camelCase（`docCount`, `createdAt`）

**解决方案**：
```typescript
// 定义后端返回的格式
interface BackendKnowledgeBase {
    id: string;
    name: string;
    doc_count: number;  // snake_case
    created_at: string; // snake_case
    ...
}

// 转换函数
const transformKnowledgeBase = (kb: BackendKnowledgeBase): KnowledgeBase => ({
    id: kb.id,
    name: kb.name,
    docCount: kb.doc_count || 0,  // 转换并设置默认值
    createdAt: kb.created_at,
    ...
});

// apiClient 已经集成了自动转换（keysToSnake/keysToCamel）
```

**经验总结**：
- 在 apiClient 层统一处理大小写转换
- 为每个后端接口定义对应的 BackendXXX 类型
- 转换时设置合理的默认值，避免 undefined

---

### 问题3：文件上传进度监控
**现象**：需要显示文件上传进度条

**解决方案**：
```typescript
uploadDocument: async (
    kbId: string,
    file: File,
    onProgress?: (progress: number) => void
) => {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        
        // 监听上传进度
        xhr.upload.addEventListener('progress', (event) => {
            if (event.lengthComputable && onProgress) {
                const progress = Math.round((event.loaded * 100) / event.total);
                onProgress(progress);
            }
        });
        
        xhr.addEventListener('load', () => {
            const response = JSON.parse(xhr.responseText);
            if (response.success) {
                resolve(response.data);
            } else {
                reject(new Error(response.message));
            }
        });
        
        xhr.open('POST', url);
        xhr.send(formData);
    });
}
```

---

### 问题4：API 响应格式统一处理
**现象**：后端返回 `{ success, message, data }`，前端需要统一解析

**解决方案**：
```typescript
// 统一响应类型
interface ApiResponse<T> {
    success: boolean;
    message: string;
    data: T;
}

// 统一处理函数
const handleResponse = <T>(response: ApiResponse<T>): T => {
    if (!response.success || !response.data) {
        throw new Error(response.message || '请求失败');
    }
    return response.data;
};

// 使用示例
const response = await apiClient.get<ApiResponse<{ items: KnowledgeBase[] }>>(url);
const data = handleResponse(response);
return data.items;
```

**经验总结**：
- 不要直接使用 `response.message`（这是状态提示）
- 业务数据在 `response.data` 中
- 统一封装错误处理逻辑

---

### 问题5：依赖注入和虚拟环境
**现象**：启动后端时出现 `ModuleNotFoundError: No module named 'langchain'`

**根本原因**：
- 终端没有激活 Python 虚拟环境
- 全局 Python 环境没有安装依赖

**解决方案**：
```bash
# Windows PowerShell
venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000

# 或者使用完整路径
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

**经验总结**：
- 每次启动后端前必须激活虚拟环境
- 建议在项目根目录创建启动脚本（start_backend.ps1）

---

## 🎯 后续优化建议

1. **统一匿名用户处理**：封装 `get_effective_user_id()` 函数统一处理
2. **添加请求验证中间件**：自动验证必填字段
3. **完善错误码体系**：区分业务错误和系统错误
4. **添加接口文档**：使用 FastAPI 的 `/docs` 自动生成文档
5. **性能监控**：添加接口耗时统计和慢查询告警
6. **前端类型生成**：根据后端 OpenAPI 自动生成 TypeScript 类型

---

## 📚 相关文件

- [PROJECT_ARCHITECTURE.md](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/PROJECT_ARCHITECTURE.md) - 项目架构文档
- [app/api/dependencies.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/api/dependencies.py) - 依赖注入
- [app/models/schemas.py](file:///d:/Project/MEK-AI/MEK-AI-V2/backend-python-ai/app/models/schemas.py) - 数据模型
- [frontend/src/core/config/api.ts](file:///d:/Project/MEK-AI/MEK-AI-V2/frontend/src/core/config/api.ts) - 前端API配置
- [frontend/src/modules/knowledge-base/logic/services/knowledgeBaseApi.ts](file:///d:/Project/MEK-AI/MEK-AI-V2/frontend/src/modules/knowledge-base/logic/services/knowledgeBaseApi.ts) - 知识库API服务

---

*最后更新：2026-02-07*
