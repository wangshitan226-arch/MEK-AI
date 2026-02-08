"""
聊天API端点
处理聊天相关的HTTP请求
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.api.dependencies import get_current_user, get_optional_user, UserContext
from app.services.ai.chat_service import chat_service
from app.models.schemas import (
    ChatRequest,
    SuccessResponse
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 创建路由器
router = APIRouter()

@router.post(
    "/",
    response_model=SuccessResponse,
    summary="发送聊天消息",
    description="向指定的数字员工发送消息并获取回复"
)
async def send_chat_message(
    chat_request: ChatRequest,
    current_user: Optional[UserContext] = Depends(get_optional_user)
) -> SuccessResponse:
    """
    发送聊天消息端点
    
    Args:
        chat_request: 聊天请求数据
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含AI回复
    """
    
    try:
        # 处理未登录用户
        user_id = current_user.user_id if current_user else "anonymous"
        organization_id = current_user.organization_id if current_user else None
        permissions = current_user.permissions if current_user else []
        is_mock = current_user.is_mock if current_user else True

        # 记录请求信息
        logger.info(f"收到聊天请求 - "
                   f"用户: {user_id}, "
                   f"员工: {chat_request.employee_id}, "
                   f"对话: {chat_request.conversation_id or '新对话'}")

        # 准备用户上下文
        user_context = {
            "user_id": user_id,
            "organization_id": organization_id,
            "employee_id": chat_request.employee_id,
            "permissions": permissions,
            "is_mock": is_mock
        }
        
        # 准备模型配置（从请求中提取）
        model_config = {}
        
        if chat_request.temperature is not None:
            model_config["temperature"] = chat_request.temperature
        
        if chat_request.max_tokens is not None:
            model_config["max_tokens"] = chat_request.max_tokens
        
        # 调用聊天服务处理消息
        result = await chat_service.process_chat_message(
            message=chat_request.message,
            employee_id=chat_request.employee_id,
            conversation_id=chat_request.conversation_id,
            user_context=user_context,
            model_config=model_config
        )
        
        # 检查处理结果
        if not result.get("success", False):
            error_info = result.get("error", {})
            error_message = error_info.get("message", "未知错误")
            
            logger.error(f"聊天处理失败 - "
                        f"员工: {chat_request.employee_id}, "
                        f"错误: {error_message}")
            
            return SuccessResponse(
                success=False,
                message=error_message,
                data=result
            )
        
        # 构建响应数据
        response_data = {
            "response": result.get("response", ""),
            "conversation_id": result.get("conversation_id"),
            "message_id": result.get("message_id", str(uuid.uuid4())),
            "employee_id": chat_request.employee_id,
            "user_id": user_id,
            "processing_time": result.get("processing_time"),
            "total_processing_time": result.get("total_processing_time"),
            "timestamp": result.get("timestamp"),
            "model_info": result.get("model_info", {}),
            "metadata": result.get("metadata", {})
        }
        
        logger.info(f"聊天处理成功 - "
                   f"员工: {chat_request.employee_id}, "
                   f"对话: {response_data['conversation_id']}, "
                   f"耗时: {response_data.get('total_processing_time', 0):.3f}s")
        
        return SuccessResponse(
            success=True,
            message="消息处理成功",
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"聊天端点处理异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理聊天消息时发生错误: {str(e)}"
        )

@router.get(
    "/conversations",
    response_model=SuccessResponse,
    summary="获取对话列表",
    description="获取当前用户的对话列表"
)
async def get_conversations(
    employee_id: Optional[str] = None,
    limit: int = 20,
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    获取对话列表端点
    
    Args:
        employee_id: 员工ID过滤（可选）
        limit: 返回数量限制
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含对话列表
    """
    
    try:
        # 获取对话列表
        from app.services.memory.conversation_memory import conversation_memory_manager
        
        conversations = conversation_memory_manager.list_conversations(
            user_id=current_user.user_id,
            employee_id=employee_id
        )
        
        # 应用数量限制
        if limit > 0:
            conversations = conversations[:limit]
        
        logger.info(f"获取对话列表 - "
                   f"用户: {current_user.user_id}, "
                   f"员工过滤: {employee_id}, "
                   f"数量: {len(conversations)}")
        
        return SuccessResponse(
            success=True,
            message="获取对话列表成功",
            data={
                "conversations": conversations,
                "total": len(conversations),
                "user_id": current_user.user_id,
                "employee_filter": employee_id
            }
        )
        
    except Exception as e:
        logger.error(f"获取对话列表异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取对话列表时发生错误: {str(e)}"
        )

@router.get(
    "/conversations/{conversation_id}",
    response_model=SuccessResponse,
    summary="获取对话详情",
    description="获取指定对话的详细信息和历史消息"
)
async def get_conversation_detail(
    conversation_id: str,
    limit: int = 50,
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    获取对话详情端点
    
    Args:
        conversation_id: 对话ID
        limit: 消息数量限制
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含对话详情
    """
    
    try:
        # 获取对话状态
        from app.services.memory.conversation_memory import conversation_memory_manager
        
        conversation_state = conversation_memory_manager.get_conversation_state(conversation_id)
        
        if not conversation_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"对话不存在: {conversation_id}"
            )
        
        # 检查权限（仅允许对话创建者访问）
        if conversation_state.user_id != current_user.user_id:
            logger.warning(f"权限拒绝 - "
                          f"用户: {current_user.user_id} 尝试访问对话: {conversation_id}, "
                          f"对话所有者: {conversation_state.user_id}")
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此对话"
            )
        
        # 获取对话历史
        messages = conversation_memory_manager.get_conversation_history(
            conversation_id,
            limit=limit
        )
        
        # 获取对话摘要
        summary = conversation_memory_manager.get_conversation_summary(conversation_id)
        
        logger.info(f"获取对话详情 - "
                   f"对话: {conversation_id}, "
                   f"消息数量: {len(messages)}")
        
        return SuccessResponse(
            success=True,
            message="获取对话详情成功",
            data={
                "conversation_id": conversation_id,
                "employee_id": conversation_state.employee_id,
                "user_id": conversation_state.user_id,
                "organization_id": conversation_state.organization_id,
                "created_at": conversation_state.created_at.isoformat(),
                "updated_at": conversation_state.updated_at.isoformat(),
                "message_count": len(messages),
                "summary": summary,
                "messages": messages,
                "metadata": conversation_state.metadata
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取对话详情异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取对话详情时发生错误: {str(e)}"
        )

@router.delete(
    "/conversations/{conversation_id}",
    response_model=SuccessResponse,
    summary="删除对话",
    description="删除指定的对话"
)
async def delete_conversation(
    conversation_id: str,
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    删除对话端点
    
    Args:
        conversation_id: 对话ID
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应
    """
    
    try:
        # 获取对话状态
        from app.services.memory.conversation_memory import conversation_memory_manager
        
        conversation_state = conversation_memory_manager.get_conversation_state(conversation_id)
        
        if not conversation_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"对话不存在: {conversation_id}"
            )
        
        # 检查权限（仅允许对话创建者删除）
        if conversation_state.user_id != current_user.user_id:
            logger.warning(f"权限拒绝 - "
                          f"用户: {current_user.user_id} 尝试删除对话: {conversation_id}, "
                          f"对话所有者: {conversation_state.user_id}")
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此对话"
            )
        
        # 删除对话
        success = conversation_memory_manager.delete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除对话失败: {conversation_id}"
            )
        
        logger.info(f"删除对话 - "
                   f"对话: {conversation_id}, "
                   f"用户: {current_user.user_id}")
        
        return SuccessResponse(
            success=True,
            message="对话删除成功",
            data={
                "conversation_id": conversation_id,
                "deleted": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除对话异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除对话时发生错误: {str(e)}"
        )

@router.get(
    "/agents",
    response_model=SuccessResponse,
    summary="获取智能体列表",
    description="获取所有可用的数字员工智能体"
)
async def get_agents(
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    获取智能体列表端点
    
    Args:
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含智能体列表
    """
    
    try:
        # 获取智能体列表
        agents_info = chat_service.list_employee_agents()
        
        # 获取模型列表
        from app.services.ai.model_manager import model_manager
        models_info = model_manager.list_chat_models()
        
        logger.info(f"获取智能体列表 - "
                   f"用户: {current_user.user_id}, "
                   f"智能体数量: {agents_info['total']}")
        
        return SuccessResponse(
            success=True,
            message="获取智能体列表成功",
            data={
                "agents": agents_info,
                "models": models_info,
                "available_providers": ["openai", "anthropic", "gemini"],
                "default_provider": "openai"
            }
        )
        
    except Exception as e:
        logger.error(f"获取智能体列表异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取智能体列表时发生错误: {str(e)}"
        )

# 导出路由器
__all__ = ["router"]