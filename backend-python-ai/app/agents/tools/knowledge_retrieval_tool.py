"""
知识库检索工具
用于从知识库中检索相关信息 - 支持增强式RAG检索
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.services.knowledge.knowledge_service import knowledge_service
from app.db.database import get_db
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 创建线程池用于执行异步操作
_executor = ThreadPoolExecutor(max_workers=4)


class KnowledgeRetrievalInput(BaseModel):
    """知识库检索输入"""
    query: str = Field(description="搜索查询语句")


class KnowledgeRetrievalTool(BaseTool):
    """
    知识库检索工具
    从指定的知识库中检索相关信息，支持增强式RAG检索
    """
    
    name: str = "knowledge_retrieval"
    description: str = """Retrieve relevant information from the knowledge base to answer user questions.
    
    Use this tool to search for information in the knowledge base before answering any question.
    This ensures your responses are based on the knowledge base content.
    
    Parameters:
    - query: The search query to find relevant information
    
    Example: "What are the rules of this game?" or "Tell me about the company policy"
    """
    
    args_schema: type[BaseModel] = KnowledgeRetrievalInput
    
    # Pydantic 字段声明
    default_kb_ids: List[str] = Field(default=[], description="默认知识库ID列表")
    
    def __init__(self, knowledge_base_ids: Optional[List[str]] = None, **kwargs):
        """
        初始化知识库检索工具
        
        Args:
            knowledge_base_ids: 默认知识库ID列表
        """
        super().__init__(default_kb_ids=knowledge_base_ids or [], **kwargs)
    
    def _run(
        self,
        query: str,
    ) -> str:
        """
        执行知识库检索（同步入口）
        
        Args:
            query: 搜索查询
            
        Returns:
            str: 检索结果文本
        """
        try:
            # 使用提供的知识库ID或默认ID
            kb_ids = self.default_kb_ids
            
            if not kb_ids:
                return "No knowledge base specified. Cannot retrieve relevant information."
            
            logger.info(f"Knowledge retrieval - Query: {query}, KBs: {kb_ids}")
            
            # 使用线程池执行异步操作
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self._async_retrieve(query, kb_ids))
            finally:
                loop.close()
            
        except Exception as e:
            logger.error(f"Knowledge retrieval failed: {str(e)}")
            return f"Knowledge retrieval failed: {str(e)}"
    
    async def _async_retrieve(self, query: str, kb_ids: List[str]) -> str:
        """
        异步执行知识库检索
        
        Args:
            query: 搜索查询
            kb_ids: 知识库ID列表
            
        Returns:
            str: 检索结果文本
        """
        # 获取数据库会话
        db = next(get_db())
        try:
            # 获取知识库信息
            results = []
            for kb_id in kb_ids:
                try:
                    kb = await knowledge_service.get_knowledge_base(db, kb_id)
                    if kb:
                        results.append(f"Knowledge Base '{kb.name}': Contains {kb.doc_count} documents")
                        
                        # TODO: 实现真正的向量检索
                        # 这里应该调用向量数据库进行相似度搜索
                        # 目前返回知识库基本信息作为示例
                        
                        # 获取知识库中的文档列表
                        items = await knowledge_service.get_knowledge_items(db, kb_id)
                        if items:
                            results.append(f"  Available documents: {len(items)}")
                            for item in items[:3]:  # 只显示前3个文档
                                # 返回完整的文档内容，不要截断
                                results.append(f"  Document {item.serial_no}:")
                                results.append(f"    {item.content}")
                except Exception as kb_error:
                    logger.error(f"Error retrieving knowledge base {kb_id}: {str(kb_error)}")
                    results.append(f"Knowledge Base '{kb_id}': Error - {str(kb_error)}")
            
            if not results:
                return "No knowledge bases found or no access to specified knowledge bases."
            
            # 构建检索结果
            result_text = f"Retrieved information for query '{query}':\n\n"
            result_text += "\n".join(results)
            result_text += "\n\nPlease use this information to answer the user's question."
            
            return result_text
            
        except Exception as e:
            logger.error(f"Async knowledge retrieval failed: {str(e)}")
            return f"Knowledge retrieval failed: {str(e)}"
        finally:
            db.close()
    
    async def _arun(
        self,
        query: str,
    ) -> str:
        """异步执行知识库检索"""
        kb_ids = self.default_kb_ids
        if not kb_ids:
            return "No knowledge base specified. Cannot retrieve relevant information."
        return await self._async_retrieve(query, kb_ids)


def create_knowledge_retrieval_tool(knowledge_base_ids: Optional[List[str]] = None) -> KnowledgeRetrievalTool:
    """
    创建知识库检索工具
    
    Args:
        knowledge_base_ids: 知识库ID列表
        
    Returns:
        KnowledgeRetrievalTool: 知识库检索工具实例
    """
    return KnowledgeRetrievalTool(knowledge_base_ids=knowledge_base_ids)
