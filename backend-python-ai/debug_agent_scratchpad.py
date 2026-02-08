"""
深度调试 agent_scratchpad 错误
此脚本将逐步跟踪数据流，定位问题根源。
"""

import asyncio
from app.services.ai.model_manager import model_manager
from app.agents.digital_employee_agent import DigitalEmployeeAgent
from app.services.memory.conversation_memory import conversation_memory_manager

async def debug_agent_scratchpad():
    print("=" * 60)
    print("深度调试: agent_scratchpad 错误")
    print("=" * 60)
    
    # 1. 创建模型和基础智能体
    print("\n1. 创建模型和基础智能体...")
    config = model_manager.create_model_config_from_request(
        provider="openai",
        model_name="gpt-4-turbo-preview",
        temperature=0.7
    )
    llm = model_manager.create_chat_model(config)
    
    employee_config = {
        "name": "Debug助手",
        "persona": "用于调试的AI助手",
        "skills": ["调试", "分析"],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    agent = DigitalEmployeeAgent(
        employee_id="debug_emp_001",
        employee_config=employee_config,
        llm=llm,
        tools=[]
    )
    
    print(f"✅ 智能体创建，执行器状态: {agent.agent_executor is not None}")
    
    # 2. 创建一个新的对话，并添加一些测试消息
    print("\n2. 创建测试对话和历史...")
    conv_id = conversation_memory_manager.create_conversation(
        employee_id="debug_emp_001",
        user_id="debug_user"
    )
    
    # 添加示例对话
    conversation_memory_manager.add_message(conv_id, "user", "你好，你是谁？")
    conversation_memory_manager.add_message(conv_id, "assistant", "我是Debug助手，专门帮你解决问题。")
    conversation_memory_manager.add_message(conv_id, "user", "什么是Python？")
    
    print(f"✅ 对话创建: {conv_id}")
    
    # 3. 【关键测试点】检查 get_conversation_messages 返回的格式
    print("\n3. 检查 conversation_memory 返回的消息格式...")
    langchain_messages = conversation_memory_manager.get_conversation_messages(conv_id)
    print(f"   返回的消息列表类型: {type(langchain_messages)}")
    print(f"   消息数量: {len(langchain_messages)}")
    
    if langchain_messages:
        for i, msg in enumerate(langchain_messages[-2:]):  # 看最后两条
            print(f"   消息[{i}] -> 类型: {type(msg).__name__}, 内容: {msg.content[:50]}...")
            # 检查是否是 BaseMessage 子类
            from langchain_core.messages import BaseMessage
            print(f"     是 BaseMessage 吗？ -> {isinstance(msg, BaseMessage)}")
    
    # 4. 【关键测试点】模拟智能体内 _prepare_agent_inputs 方法的输出
    print("\n4. 模拟智能体内部准备的输入参数...")
    # 模拟 context
    test_context = {
        "conversation_id": conv_id,
        "employee_id": "debug_emp_001",
        "user_id": "debug_user"
    }
    
    # 调用内部的 _prepare_agent_inputs 方法（我们需要临时访问它）
    # 为了测试，我们直接复制其逻辑
    chat_history_for_agent = []
    if conv_id:
        chat_history_for_agent = conversation_memory_manager.get_conversation_messages(conv_id, limit=10)
    
    simulated_inputs = {
        "input": "请解释一下机器学习。",
        "chat_history": chat_history_for_agent,
        "agent_scratchpad": []  # 按你当前代码的版本
    }
    
    print(f"   模拟的输入字典键: {list(simulated_inputs.keys())}")
    print(f"   'chat_history' 值的类型: {type(simulated_inputs['chat_history'])}")
    print(f"   'agent_scratchpad' 值的类型: {type(simulated_inputs['agent_scratchpad'])}")
    
    # 5. 【关键测试点】直接测试 LangChain 提示模板格式化
    print("\n5. 直接测试 LangChain 提示模板...")
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    # 使用与你 base_agent.py 中 _create_prompt 方法完全相同的逻辑
    test_system_prompt = "你是Debug助手。"
    test_tools = []
    
    tools_description = "\n".join([f"{tool.name}: {tool.description}" for tool in test_tools]) if test_tools else "没有可用的工具"
    tool_names = ", ".join([tool.name for tool in test_tools]) if test_tools else "无"
    
    # 构建提示模板
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", f"""{test_system_prompt}

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

注意：如果用户的问题不需要使用工具，请直接回答。
"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    print(f"✅ 提示模板创建成功")
    
    # 尝试格式化提示（这是报错的源头）
    print("   尝试格式化提示模板（模拟代理内部操作）...")
    try:
        # 准备格式化参数
        format_kwargs = {
            "input": "请解释一下机器学习。",
            "chat_history": simulated_inputs['chat_history'],
            "agent_scratchpad": []  # 关键：这里传入空列表
        }
        
        # 尝试部分格式化（填充 system_prompt 等）
        partial_kwargs = {
            "system_prompt": test_system_prompt,
            "tools": tools_description,
            "tool_names": tool_names
        }
        prompt_template = prompt_template.partial(**partial_kwargs)
        
        # 尝试格式化消息
        messages = prompt_template.format_messages(**format_kwargs)
        print(f"   ✅ 提示模板格式化成功！生成 {len(messages)} 条消息。")
        
    except Exception as e:
        print(f"   ❌ 提示模板格式化失败！")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {e}")
        print(f"   此时传入的 agent_scratchpad 值为: {format_kwargs.get('agent_scratchpad')}")
        print(f"   其类型为: {type(format_kwargs.get('agent_scratchpad'))}")
        
        # 额外诊断：如果 agent_scratchpad 是空列表，为什么还会出错？
        if format_kwargs.get('agent_scratchpad') == []:
            print("\n   ⚠️  重要发现: agent_scratchpad 是空列表 []，但格式化仍失败。")
            print("      这可能意味着 LangChain 内部期望一个不同的结构。")
            print("      尝试传入一个空的 BaseMessage 列表而不是普通空列表。")
            
            # 测试：使用空的 BaseMessage 列表
            from langchain_core.messages import BaseMessage
            format_kwargs["agent_scratchpad"] = []  # 已经是空列表
            
            # 检查 chat_history 的每个元素
            print(f"\n      检查 chat_history 的每个元素:")
            for i, msg in enumerate(format_kwargs["chat_history"]):
                print(f"      元素[{i}]: 类型={type(msg).__name__}, 是BaseMessage?={isinstance(msg, BaseMessage)}")
    
    # 6. 如果以上都通过，尝试实际调用一次智能体（可能失败）
    print("\n6. 尝试实际调用智能体处理消息...")
    if agent.agent_executor:
        try:
            print(f"   使用 conversation_id: {conv_id}")
            test_context = {
                "conversation_id": conv_id,
                "employee_id": "debug_emp_001",
                "user_id": "debug_user",
                "chat_history": chat_history_for_agent  # 确保上下文中有正确格式的历史
            }
            
            result = await agent.process_message("请解释一下机器学习。", test_context)
            if result.get("success"):
                print(f"   ✅ 智能体调用成功！")
                print(f"   响应: {result.get('response', '')[:100]}...")
            else:
                print(f"   ❌ 智能体调用失败！")
                print(f"   错误: {result.get('error', {}).get('message')}")
        except Exception as e:
            print(f"   ❌ 调用过程中抛出异常: {type(e).__name__}: {e}")
    else:
        print("   ⚠️  智能体执行器未初始化，跳过实际调用。")
    
    print("\n" + "=" * 60)
    print("调试完成。请将上方输出完整复制。")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(debug_agent_scratchpad())