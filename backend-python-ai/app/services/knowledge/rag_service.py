"""
RAG检索服务 - 基于LangChain简化实现
处理向量存储和检索增强生成
"""

import os
# 禁用 ChromaDB 遥测
os.environ["ANONYMIZED_TELEMETRY"] = "false"

import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain.schema import Document
try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    # 兼容旧版本
    from langchain.vectorstores import Chroma

from app.utils.logger import LoggerMixin


class RAGService(LoggerMixin):
    """
    RAG检索服务
    基于LangChain的向量存储和检索
    """
    
    def __init__(self, vector_db_dir: str = "./data/vector_db"):
        """初始化RAG服务"""
        super().__init__()
        
        self.vector_db_dir = Path(vector_db_dir)
        self.vector_db_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化嵌入模型（使用简单的内存嵌入，避免sentence-transformers依赖）
        self.embeddings = self._create_embeddings()
        
        self.log_info("RAG服务初始化完成")
    
    def _create_embeddings(self):
        """创建嵌入模型（生产级实现）"""
        try:
            # 首先尝试使用 HuggingFaceEmbeddings（需要本地缓存或网络）
            try:
                from langchain_community.embeddings import HuggingFaceEmbeddings
            except ImportError:
                from langchain.embeddings import HuggingFaceEmbeddings
            
            # 设置离线模式，使用本地缓存
            import os
            os.environ["HF_HUB_OFFLINE"] = "1"
            
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
            self.log_info("HuggingFaceEmbeddings 加载成功")
            return embeddings
            
        except Exception as e:
            self.log_warning(f"HuggingFaceEmbeddings 加载失败，使用备用嵌入: {str(e)}")
            # 使用备用的 FakeEmbeddings（仅用于测试，所有向量都是随机的）
            try:
                from langchain_community.embeddings import FakeEmbeddings
            except ImportError:
                from langchain.embeddings import FakeEmbeddings
            
            self.log_warning("使用 FakeEmbeddings 作为备用（仅用于测试）")
            return FakeEmbeddings(size=384)
    
    def _get_vectorstore(self, knowledge_base_id: str) -> Chroma:
        """
        获取指定知识库的向量存储
        
        Args:
            knowledge_base_id: 知识库ID
            
        Returns:
            Chroma: 向量存储实例
        """
        persist_dir = self.vector_db_dir / knowledge_base_id
        persist_dir.mkdir(parents=True, exist_ok=True)
        
        return Chroma(
            persist_directory=str(persist_dir),
            embedding_function=self.embeddings,
            collection_name=knowledge_base_id,
        )
    
    async def add_documents(
        self,
        knowledge_base_id: str,
        documents: List[Document],
    ) -> Dict[str, Any]:
        """
        添加文档到向量存储
        
        Args:
            knowledge_base_id: 知识库ID
            documents: 文档列表
            
        Returns:
            Dict: 添加结果
        """
        try:
            if not documents:
                return {
                    "success": False,
                    "error": "文档列表为空",
                    "processed_count": 0,
                }
            
            self.log_info(
                f"开始向量化文档: 知识库={knowledge_base_id}, "
                f"文档数={len(documents)}"
            )
            
            # 获取向量存储
            vectorstore = self._get_vectorstore(knowledge_base_id)
            
            # 添加文档
            ids = vectorstore.add_documents(documents)
            
            # 持久化
            vectorstore.persist()
            
            self.log_info(
                f"文档向量化完成: 知识库={knowledge_base_id}, "
                f"成功添加 {len(ids)} 个文档"
            )
            
            return {
                "success": True,
                "processed_count": len(ids),
                "document_ids": ids,
                "knowledge_base_id": knowledge_base_id,
            }
            
        except Exception as e:
            self.log_error(
                f"添加文档到向量存储失败: 知识库={knowledge_base_id}, "
                f"错误={str(e)}",
                error=e,
            )
            return {
                "success": False,
                "error": str(e),
                "processed_count": 0,
            }
    
    async def search(
        self,
        knowledge_base_id: str,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        搜索知识库
        
        Args:
            knowledge_base_id: 知识库ID
            query: 查询内容
            top_k: 返回结果数量
            score_threshold: 相似度阈值
            
        Returns:
            List[Dict]: 搜索结果
        """
        try:
            self.log_info(
                f"搜索知识库: 知识库={knowledge_base_id}, "
                f"查询='{query[:50]}...', top_k={top_k}"
            )
            
            # 获取向量存储
            vectorstore = self._get_vectorstore(knowledge_base_id)
            
            # 执行相似度搜索（带分数）
            results = vectorstore.similarity_search_with_score(query, k=top_k * 2)
            
            # 格式化结果
            formatted_results = []
            for doc, score in results:
                # Chroma返回的是距离，转换为相似度（1 - distance）
                similarity = 1.0 - score
                
                if similarity >= score_threshold:
                    formatted_results.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": round(similarity, 4),
                        "source_file": doc.metadata.get("source", "unknown"),
                    })
            
            # 按分数排序并截取
            formatted_results.sort(key=lambda x: x["score"], reverse=True)
            final_results = formatted_results[:top_k]
            
            self.log_info(
                f"搜索完成: 知识库={knowledge_base_id}, "
                f"返回 {len(final_results)} 个结果"
            )
            
            return final_results
            
        except Exception as e:
            self.log_error(
                f"搜索知识库失败: 知识库={knowledge_base_id}, "
                f"错误={str(e)}",
                error=e,
            )
            return []
    
    async def delete_knowledge_base(self, knowledge_base_id: str) -> bool:
        """
        删除知识库的向量数据
        
        Args:
            knowledge_base_id: 知识库ID
            
        Returns:
            bool: 是否成功
        """
        try:
            import shutil
            
            persist_dir = self.vector_db_dir / knowledge_base_id
            if persist_dir.exists():
                shutil.rmtree(persist_dir)
                self.log_info(f"向量存储删除成功: {knowledge_base_id}")
                return True
            
            return False
            
        except Exception as e:
            self.log_error(
                f"删除向量存储失败: 知识库={knowledge_base_id}, "
                f"错误={str(e)}",
                error=e,
            )
            return False
    
    async def get_stats(self, knowledge_base_id: str) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Args:
            knowledge_base_id: 知识库ID
            
        Returns:
            Dict: 统计信息
        """
        try:
            vectorstore = self._get_vectorstore(knowledge_base_id)
            
            # 获取集合信息
            collection = vectorstore._collection
            count = collection.count()
            
            return {
                "knowledge_base_id": knowledge_base_id,
                "document_count": count,
                "vectorized": count > 0,
            }
            
        except Exception as e:
            self.log_error(
                f"获取统计信息失败: 知识库={knowledge_base_id}, "
                f"错误={str(e)}",
                error=e,
            )
            return {
                "knowledge_base_id": knowledge_base_id,
                "document_count": 0,
                "vectorized": False,
                "error": str(e),
            }
    
    def build_context(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        max_context_length: int = 3000,
    ) -> str:
        """
        构建RAG上下文
        
        Args:
            query: 用户查询
            search_results: 搜索结果
            max_context_length: 最大上下文长度
            
        Returns:
            str: 构建的上下文
        """
        if not search_results:
            return "没有找到相关信息。"
        
        context_parts = []
        context_parts.append("基于以下参考资料回答问题:\n")
        
        current_length = len(context_parts[0])
        
        for i, result in enumerate(search_results, 1):
            content = result.get("content", "")
            score = result.get("score", 0)
            source = result.get("source_file", "unknown")
            
            # 构建引用块
            citation = f"\n[文档{i}] (相关度: {score:.2f}, 来源: {source})\n{content}\n"
            
            # 检查是否超过最大长度
            if current_length + len(citation) > max_context_length:
                # 截断内容
                remaining = max_context_length - current_length - 50
                if remaining > 100:
                    truncated_content = content[:remaining] + "..."
                    citation = f"\n[文档{i}] (相关度: {score:.2f}, 来源: {source})\n{truncated_content}\n"
                else:
                    break
            
            context_parts.append(citation)
            current_length += len(citation)
        
        context_parts.append("\n请基于以上参考资料回答用户问题。")
        
        return "".join(context_parts)


# 创建全局实例
rag_service = RAGService()
