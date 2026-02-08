# MEK-AI 项目问题分析报告

## 日期：2026-02-08

---

## 一、当前存在的核心问题

### 1. 前端显示"预览功能暂时不可用"，但后端正常返回

**现象**：
- 前端显示错误消息："抱歉，预览功能暂时不可用。"
- 后端日志显示 Agent 正常执行并返回了结果
- 说明前端和后端的通信存在问题

**可能原因**：
- 响应格式不匹配
- 超时问题
- 前端错误处理逻辑有问题

---

### 2. DeepSeek API 调用失败

**现象**：
```
2026-02-08 21:47:51 - app.services.ai.chat_deepseek - ERROR - [unknown] - DeepSeek 异步调用失败:
```

**影响**：
- LLM 调用不稳定，导致 Agent 无法正常工作
- 第二次请求直接失败

---

### 3. ReAct Agent 思考过程混乱

**现象**：
Agent 的思考过程显示过度纠结：
- "我需要确认默认范围是什么..."
- "但为了更专业，我可以先搜索一下..."
- "然而，根据指令，如果我有足够信息，可以直接回答..."
- 最后又决定搜索

**根本原因**：
提示词过于复杂，给 Agent 太多条件判断，导致逻辑混乱

---

### 4. 对话历史传递问题（已部分修复）

**历史问题**：
- 配置知识库后没有对话历史
- 不配置知识库有对话历史

**根本原因**（已找到）：
- 无工具时使用 `LLMChain` 带有 `ConversationBufferMemory`
- 有工具时使用 `AgentExecutor` 没有配置 `memory`

**修复状态**：已添加 memory，但效果仍不理想

---

## 二、现有代码分析

### 2.1 ReAct Agent 提示词模板

**文件**：`app/agents/base_agent.py` (第131-154行)

```python
# 构建RAG检索的系统提示
# 允许LLM自主判断是否需要使用知识库
rag_system_prompt = self.config.system_prompt + """

INSTRUCTION: Use the knowledge_retrieval tool ONLY when you need specific information from the knowledge base to answer the question.
Do NOT search for information you already have or for simple greetings/confirmations.

Follow this workflow:
1. Start with a Thought about what the user is asking
2. If you ALREADY have enough information from previous conversation or general knowledge, go directly to Final Answer
3. If you NEED specific information from the knowledge base, use the knowledge_retrieval tool with Action/Action Input
4. Wait for the Observation (tool result)
5. After getting information (or if you already had it), provide your Final Answer

IMPORTANT: Do NOT keep searching repeatedly. Search once at most, then provide your answer.

Use the following format:
Thought: think about what to do and whether you need to search
Action: the action to take (only if you need to search)
Action Input: the input to the action
Observation: the result of the action (this will be provided to you)
Thought: I now know the final answer (or I already knew it)
Final Answer: the final answer to the original question

You have access to the following tools:"""
```

**问题**：
- 提示词给 Agent 太多选择，导致决策困难
- "If you ALREADY have enough information..." 这种条件判断让 LLM 纠结
- 缺乏明确的决策边界

---

### 2.2 AgentExecutor 配置

**文件**：`app/agents/base_agent.py` (第171-193行)

```python
# 创建LLM链
llm_chain = LLMChain(llm=self.llm, prompt=prompt)

# 使用ZeroShotAgent（ReAct代理的实现）
agent = ZeroShotAgent(
    llm_chain=llm_chain,
    tools=self.tools,
    verbose=True
)

# 为ReAct Agent创建memory来维护对话历史
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

self.agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=self.tools,
    memory=memory,
    verbose=True,
    max_iterations=self.config.max_iterations,
    handle_parsing_errors=True
)
```

---

### 2.3 对话历史格式化

**文件**：`app/agents/digital_employee_agent.py` (第151-177行)

```python
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
```

---

### 2.4 提示模板 Suffix

**文件**：`app/agents/base_agent.py` (第160-169行)

```python
prompt = ZeroShotAgent.create_prompt(
    tools=self.tools,
    prefix=rag_system_prompt,
    suffix="""Begin!

Previous conversation history:
{chat_history}

Question: {input}

{agent_scratchpad}""",
    input_variables=["chat_history", "input", "agent_scratchpad"]
)
```

---

### 2.5 前端预览组件

**文件**：`frontend/src/ui-pages/digital-employee/components/EditDigitalEmployee.tsx`

**消息列表渲染** (第477-512行)：
```tsx
<div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-5 space-y-6">
    {previewMessages.map((msg, idx) => (
        <div key={idx} className={`flex group ${msg.role === 'user' ? 'justify-end' : 'justify-start'} items-start space-x-3`}>
            {/* Bot Avatar */}
            {msg.role === 'model' && (
                <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0 mt-1 border border-slate-100 shadow-sm">
                    <img
                        src={formData.avatar || `https://ui-avatars.com/api/?name=${formData.name || 'Bot'}&background=random`}
                        alt="Bot"
                        className="w-full h-full object-cover"
                    />
                </div>
            )}

            <div className={`flex flex-col max-w-[80%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div 
                    className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm transition-shadow hover:shadow-md ${
                    msg.role === 'user' 
                        ? 'bg-blue-600 text-white rounded-tr-none' 
                        : 'bg-slate-50 border border-slate-100 text-slate-800 rounded-tl-none'
                    }`}
                >
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>
            </div>

            {/* User Avatar */}
            {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0 mt-1 text-slate-400 border border-slate-200">
                    <User size={16} />
                </div>
            )}
        </div>
    ))}
    {/* 用于自动滚动的锚点 */}
    <div ref={messagesEndRef} />
</div>
```

**自动滚动逻辑** (第75-82行)：
```tsx
const messagesEndRef = useRef<HTMLDivElement>(null);
const messagesContainerRef = useRef<HTMLDivElement>(null);

// 自动滚动到最新消息
useEffect(() => {
  if (messagesEndRef.current) {
    messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
  }
}, [previewMessages]);
```

---

## 三、问题根因总结

### 1. 架构设计问题

**ReAct Agent 不适合当前场景**：
- ReAct 设计用于需要多步推理和工具调用的复杂任务
- 当前场景主要是问答和简单游戏，ReAct 过于复杂
- 提示词工程难度高，很难平衡"强制使用工具"和"自主决策"

### 2. 提示词工程问题

**当前提示词的问题**：
```
INSTRUCTION: Use the knowledge_retrieval tool ONLY when you need specific information...
If you ALREADY have enough information... go directly to Final Answer
If you NEED specific information... use the knowledge_retrieval tool
```

- 给 LLM 太多选择，导致决策困难
- 缺乏明确的触发条件
- LLM 无法准确判断"是否有足够信息"

### 3. 错误处理问题

**前端错误**：
- 后端正常返回但前端显示"暂时不可用"
- 可能是响应格式不匹配或超时

**后端错误**：
- DeepSeek API 调用偶发失败
- 缺乏重试机制

### 4. 对话历史问题

**虽然已添加 memory，但仍有问题**：
- `AgentExecutor` 的 memory 和手动传入的 `chat_history` 可能冲突
- 提示模板中同时存在 `{chat_history}` 和 memory 管理的 history

---

## 四、建议的解决方案

### 方案1：简化架构（推荐）

**放弃 ReAct Agent，改用简单方案**：
1. 先判断用户问题是否需要查询知识库（用一个简单的分类器）
2. 如果需要，先查询知识库获取上下文
3. 将上下文 + 用户问题 + 对话历史一起传给 LLM
4. 直接获取回答

**优点**：
- 逻辑清晰，易于控制
- 提示词简单，不会搞糊涂 LLM
- 更容易调试和优化

### 方案2：优化 ReAct 提示词

**明确工具使用条件**：
```
You have access to the knowledge_retrieval tool.

RULES:
1. For greetings, simple questions, or when you already know the answer: respond directly with Final Answer
2. ONLY use knowledge_retrieval when the question specifically asks about information in the knowledge base
3. After using knowledge_retrieval once, you MUST provide Final Answer, do not search again
```

### 方案3：混合模式

**保留 ReAct，但添加预处理器**：
1. 先检查用户意图
2. 如果是简单问候/确认，直接回复，不走 ReAct
3. 只有复杂查询才走 ReAct Agent

---

## 五、需要进一步调查的问题

1. **前端错误处理逻辑** - 为什么后端正常返回但前端显示错误？
2. **DeepSeek API 稳定性** - 调用失败的具体原因是什么？
3. **响应时间** - 是否因为响应太慢导致前端超时？
4. **AgentExecutor memory 和 chat_history 的冲突** - 两者如何正确配合？

---

## 六、已完成的修复

1. ✅ 修复了员工列表不显示问题（前端数据结构处理）
2. ✅ 修复了后端重复添加 `created` 标签问题
3. ✅ 修复了知识库检索工具只返回前50字符的问题
4. ✅ 修复了前端预览框不能下拉的问题
5. ✅ 修复了前端预览框自动滚动问题
6. ✅ 添加了 ReAct Agent 的 memory 配置
7. ✅ 修改了 ReAct 提示词，减少强制搜索

---

## 七、待修复问题

1. ❌ 前端显示"暂时不可用"但后端正常
2. ❌ DeepSeek API 调用偶发失败
3. ❌ ReAct Agent 思考过程混乱
4. ❌ 对话历史效果不理想
5. ❌ 整体响应效果差

---

*文档生成时间：2026-02-08*
*最后更新：2026-02-08*
