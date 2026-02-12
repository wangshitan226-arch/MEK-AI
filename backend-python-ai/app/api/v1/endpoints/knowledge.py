"""
知识库管理API端点 - MySQL版本
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks, Body
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_optional_user, UserContext
from app.db import get_db
from app.services.knowledge.knowledge_service import knowledge_service
from app.services.knowledge.document_processor import document_processor
from app.services.knowledge.rag_service import rag_service
from app.db.repositories import knowledge_repository
from app.db.models import KnowledgeBase
from app.models.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeItemCreate,
    KnowledgeItemResponse,
    KnowledgeSaveRequest,
    KnowledgeSearchRequest,
    DocumentUploadConfig,
    DocumentParseResponse,
    SuccessResponse,
)
from app.utils.logger import get_logger
from langchain.schema import Document

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])


# ========== 知识库管理 ==========

@router.get(
    "",
    response_model=SuccessResponse,
    summary="获取知识库列表",
    description="获取知识库列表，支持分页和过滤"
)
async def get_knowledge_bases(
    status: Optional[str] = None,
    is_public: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: Optional[UserContext] = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """获取知识库列表"""
    try:
        user_id = current_user.user_id if current_user else None
        
        # 获取知识库列表
        knowledge_bases = await knowledge_service.list_knowledge_bases(
            db=db,
            user_id=user_id,
            status=status,
            is_public=is_public,
            limit=page_size,
            offset=(page - 1) * page_size,
        )
        
        # 获取总数
        total = knowledge_repository.kb_repo.count(db)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        
        items = [kb.dict() for kb in knowledge_bases]
        logger.info(f"返回知识库列表: {len(items)} 个")
        
        return SuccessResponse(
            success=True,
            message="获取知识库列表成功",
            data={
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            }
        )
        
    except Exception as e:
        logger.error(f"获取知识库列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识库列表失败: {str(e)}"
        )


@router.post(
    "",
    response_model=SuccessResponse,
    summary="创建知识库",
    description="创建新的知识库"
)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate = Body(...),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """创建知识库"""
    try:
        knowledge_base = await knowledge_service.create_knowledge_base(
            db=db,
            kb_data=kb_data,
            user_id=current_user.user_id,
            organization_id=current_user.organization_id,
        )
        
        if not knowledge_base:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建知识库失败"
            )
        
        return SuccessResponse(
            success=True,
            message="知识库创建成功",
            data=knowledge_base.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建知识库失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建知识库失败: {str(e)}"
        )


@router.get(
    "/{knowledge_base_id}",
    response_model=SuccessResponse,
    summary="获取知识库详情",
    description="获取指定知识库的详细信息"
)
async def get_knowledge_base_detail(
    knowledge_base_id: str,
    current_user: Optional[UserContext] = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """获取知识库详情"""
    try:
        user_id = current_user.user_id if current_user else None
        
        knowledge_base = await knowledge_service.get_knowledge_base(
            db=db,
            kb_id=knowledge_base_id,
            user_id=user_id,
        )
        
        if not knowledge_base:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在: {knowledge_base_id}"
            )
        
        return SuccessResponse(
            success=True,
            message="获取知识库详情成功",
            data=knowledge_base.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识库详情失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识库详情失败: {str(e)}"
        )


@router.put(
    "/{knowledge_base_id}",
    response_model=SuccessResponse,
    summary="更新知识库",
    description="更新指定知识库的信息"
)
async def update_knowledge_base(
    knowledge_base_id: str,
    update_data: KnowledgeBaseUpdate = Body(...),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """更新知识库"""
    try:
        knowledge_base = await knowledge_service.update_knowledge_base(
            db=db,
            kb_id=knowledge_base_id,
            update_data=update_data,
            user_id=current_user.user_id,
        )
        
        if not knowledge_base:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在或无权限: {knowledge_base_id}"
            )
        
        return SuccessResponse(
            success=True,
            message="知识库更新成功",
            data=knowledge_base.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新知识库失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新知识库失败: {str(e)}"
        )


@router.delete(
    "/{knowledge_base_id}",
    response_model=SuccessResponse,
    summary="删除知识库",
    description="删除指定的知识库"
)
async def delete_knowledge_base(
    knowledge_base_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """删除知识库"""
    try:
        # 删除向量数据
        await rag_service.delete_knowledge_base(knowledge_base_id)
        
        # 删除知识库记录
        success = await knowledge_service.delete_knowledge_base(
            db=db,
            kb_id=knowledge_base_id,
            user_id=current_user.user_id,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在或无权限: {knowledge_base_id}"
            )
        
        return SuccessResponse(
            success=True,
            message="知识库删除成功",
            data={"knowledge_base_id": knowledge_base_id, "deleted": True}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除知识库失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除知识库失败: {str(e)}"
        )


# ========== 文档管理 ==========

@router.post(
    "/{knowledge_base_id}/upload",
    response_model=SuccessResponse,
    summary="上传文档",
    description="上传文档到知识库"
)
async def upload_document(
    knowledge_base_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """上传文档"""
    logger.info(f"上传文档参数: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    try:
        # 检查知识库是否存在
        kb = await knowledge_service.get_knowledge_base(
            db=db,
            kb_id=knowledge_base_id,
            user_id=current_user.user_id,
        )
        
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在: {knowledge_base_id}"
            )
        
        # 读取文件内容
        content = await file.read()
        
        # 处理文件
        config = {
            "knowledge_length": chunk_size,
            "overlap_length": chunk_overlap,
        }
        
        result = await document_processor.process_file(
            file_content=content,
            filename=file.filename,
            knowledge_base_id=knowledge_base_id,
            config=config,
        )
        
        if result.get("parse_status") == "failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文档处理失败: {result.get('error')}"
            )
        
        # 后台向量化处理
        if result.get("chunks"):
            chunks = result["chunks"]
            documents = [
                Document(
                    page_content=chunk["content"],
                    metadata={
                        **chunk["metadata"],
                        "source": file.filename,
                        "knowledge_base_id": knowledge_base_id,
                    }
                )
                for chunk in chunks
            ]
            
            background_tasks.add_task(
                rag_service.add_documents,
                knowledge_base_id,
                documents,
            )
            
            # 更新向量化状态
            await knowledge_service.update_vectorized_status(
                db=db,
                kb_id=knowledge_base_id,
                vectorized=True
            )
        
        return SuccessResponse(
            success=True,
            message=f"文档上传成功，生成了 {result.get('total_chunks', 0)} 个知识块",
            data={
                "knowledge_base_id": knowledge_base_id,
                "file_name": file.filename,
                "file_size": len(content),
                "chunks_processed": result.get("total_chunks", 0),
                "vectorization_queued": True,
                "chunks": result.get("chunks", []),
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传文档失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文档失败: {str(e)}"
        )


@router.get(
    "/{knowledge_base_id}/documents",
    response_model=SuccessResponse,
    summary="获取知识库文档列表",
    description="获取指定知识库的文档（知识点）列表"
)
async def get_knowledge_base_documents(
    knowledge_base_id: str,
    page: int = 1,
    page_size: int = 20,
    current_user: Optional[UserContext] = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """获取知识库文档列表"""
    try:
        user_id = current_user.user_id if current_user else None
        
        items = await knowledge_service.get_knowledge_items(
            db=db,
            kb_id=knowledge_base_id,
            user_id=user_id,
            limit=page_size,
            offset=(page - 1) * page_size,
        )
        
        # 获取总数
        total = len(items)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        
        return SuccessResponse(
            success=True,
            message="获取文档列表成功",
            data={
                "items": [item.dict() for item in items],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            }
        )
        
    except Exception as e:
        logger.error(f"获取文档列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档列表失败: {str(e)}"
        )


# ========== 补充前端需要的接口 ==========

@router.post(
    "/{knowledge_base_id}/documents/{file_id}/parse",
    response_model=SuccessResponse,
    summary="解析文档",
    description="解析已上传的文档（前端需要）"
)
async def parse_document(
    knowledge_base_id: str,
    file_id: str,
    config: DocumentUploadConfig,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """解析文档"""
    try:
        # 获取文件路径
        file_path = document_processor.get_file_path(file_id, knowledge_base_id)
        
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"文件不存在: {file_id}"
            )
        
        # 解析文档
        documents = await document_processor.parse_document(str(file_path))
        
        # 分割文档
        chunks = await document_processor.split_documents(
            documents,
            chunk_size=config.knowledge_length,
            chunk_overlap=config.overlap_length,
        )
        
        # 构建响应
        knowledge_list = [
            {
                "id": f"ki_{i}",
                "knowledge_base_id": knowledge_base_id,
                "serial_no": i + 1,
                "content": chunk.page_content,
                "word_count": len(chunk.page_content),
                "create_time": datetime.now().isoformat(),
                "source_file": file_path.name,
                "metadata": chunk.metadata,
            }
            for i, chunk in enumerate(chunks)
        ]
        
        return SuccessResponse(
            success=True,
            message="文档解析成功",
            data={
                "file_id": file_id,
                "file_name": file_path.name,
                "knowledge_list": knowledge_list,
                "parse_status": "completed",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"解析文档失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解析文档失败: {str(e)}"
        )


@router.post(
    "/{knowledge_base_id}/knowledge",
    response_model=SuccessResponse,
    summary="保存知识点",
    description="保存解析后的知识点到知识库（前端需要）"
)
async def save_knowledge_items(
    knowledge_base_id: str,
    items: List[KnowledgeItemCreate] = Body(...),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """保存知识点"""
    try:
        success = await knowledge_service.add_knowledge_items(
            db=db,
            kb_id=knowledge_base_id,
            items=[item.dict() for item in items],
            user_id=current_user.user_id,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限添加知识点"
            )

        return SuccessResponse(
            success=True,
            message=f"成功保存 {len(items)} 个知识点",
            data={
                "knowledge_base_id": knowledge_base_id,
                "saved_count": len(items),
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存知识点失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存知识点失败: {str(e)}"
        )


@router.get(
    "/config/document-processing",
    response_model=SuccessResponse,
    summary="获取文档处理配置",
    description="获取默认的文档处理配置（前端需要）"
)
async def get_document_config(
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """获取文档处理配置"""
    try:
        config = await knowledge_service.get_document_config()
        
        return SuccessResponse(
            success=True,
            message="获取配置成功",
            data=config.dict()
        )
        
    except Exception as e:
        logger.error(f"获取配置失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取配置失败: {str(e)}"
        )


@router.put(
    "/config/document-processing",
    response_model=SuccessResponse,
    summary="更新文档处理配置",
    description="更新文档处理配置（前端需要，当前仅返回传入配置）"
)
async def update_document_config(
    config: DocumentUploadConfig,
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """更新文档处理配置"""
    try:
        # 当前仅返回传入的配置（内存存储，不持久化）
        return SuccessResponse(
            success=True,
            message="配置更新成功",
            data=config.dict()
        )
        
    except Exception as e:
        logger.error(f"更新配置失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新配置失败: {str(e)}"
        )


@router.delete(
    "/{knowledge_base_id}/knowledge/{item_id}",
    response_model=SuccessResponse,
    summary="删除知识点",
    description="删除知识库中的单个知识点"
)
async def delete_knowledge_item(
    knowledge_base_id: str,
    item_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """删除知识点"""
    try:
        success = await knowledge_service.delete_knowledge_item(
            db=db,
            kb_id=knowledge_base_id,
            item_id=item_id,
            user_id=current_user.user_id,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识点不存在或无权限: {item_id}"
            )
        
        return SuccessResponse(
            success=True,
            message="删除知识点成功",
            data={"item_id": item_id, "deleted": True}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除知识点失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除知识点失败: {str(e)}"
        )


@router.delete(
    "/{knowledge_base_id}/knowledge",
    response_model=SuccessResponse,
    summary="清空知识库",
    description="清空知识库中的所有知识点"
)
async def clear_knowledge_items(
    knowledge_base_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """清空知识库"""
    try:
        success = await knowledge_service.clear_knowledge_items(
            db=db,
            kb_id=knowledge_base_id,
            user_id=current_user.user_id,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在或无权限: {knowledge_base_id}"
            )
        
        return SuccessResponse(
            success=True,
            message="清空知识库成功",
            data={"knowledge_base_id": knowledge_base_id, "cleared": True}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清空知识库失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清空知识库失败: {str(e)}"
        )


# ========== 搜索和查询 ==========

@router.post(
    "/{knowledge_base_id}/search",
    response_model=SuccessResponse,
    summary="搜索知识库",
    description="在指定知识库中搜索相关内容"
)
async def search_knowledge_base(
    knowledge_base_id: str,
    request: KnowledgeSearchRequest,
    current_user: Optional[UserContext] = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """搜索知识库"""
    try:
        user_id = current_user.user_id if current_user else None
        
        # 检查知识库权限
        kb = await knowledge_service.get_knowledge_base(
            db=db,
            kb_id=knowledge_base_id,
            user_id=user_id,
        )
        
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在: {knowledge_base_id}"
            )
        
        # 执行搜索
        results = await rag_service.search(
            knowledge_base_id=knowledge_base_id,
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
        )
        
        return SuccessResponse(
            success=True,
            message="搜索成功",
            data={
                "query": request.query,
                "knowledge_base_id": knowledge_base_id,
                "results": results,
                "total": len(results),
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索知识库失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索知识库失败: {str(e)}"
        )


@router.get(
    "/{knowledge_base_id}/stats",
    response_model=SuccessResponse,
    summary="获取知识库统计",
    description="获取知识库的向量化和文档统计信息"
)
async def get_knowledge_base_stats(
    knowledge_base_id: str,
    current_user: Optional[UserContext] = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """获取知识库统计"""
    try:
        user_id = current_user.user_id if current_user else None
        
        # 检查知识库权限
        kb = await knowledge_service.get_knowledge_base(
            db=db,
            kb_id=knowledge_base_id,
            user_id=user_id,
        )
        
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在: {knowledge_base_id}"
            )
        
        # 获取向量统计
        vector_stats = await rag_service.get_stats(knowledge_base_id)
        
        return SuccessResponse(
            success=True,
            message="获取统计成功",
            data={
                "knowledge_base_id": knowledge_base_id,
                "name": kb.name,
                "doc_count": kb.doc_count,
                "vectorized": vector_stats.get("vectorized", False),
                "vector_count": vector_stats.get("document_count", 0),
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取统计失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计失败: {str(e)}"
        )


# 导出路由器
__all__ = ["router"]
