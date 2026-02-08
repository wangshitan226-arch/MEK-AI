很好！知识库服务开发是AI系统的核心功能。让我为你制定详细的开发步骤：

## 📋 知识库服务开发详细步骤

### 🎯 第一阶段：基础架构与数据模型（1-2天）

#### 1. 完善数据模型
**文件：`app/models/schemas.py`（补充）**

```python
# ==================== 知识库相关模型补充 ====================

class KnowledgeBaseCreate(BaseModel):
    """知识库创建模型"""
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签")
    is_public: bool = Field(default=True, description="是否公开")
    category: Optional[str] = Field(None, description="分类")

class KnowledgeBaseUpdate(BaseModel):
    """知识库更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    tags: Optional[List[str]] = Field(None, description="标签")
    is_public: Optional[bool] = Field(None, description="是否公开")
    status: Optional[str] = Field(None, description="状态")

class KnowledgeBaseResponse(BaseModel):
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

class DocumentUploadRequest(BaseModel):
    """文档上传请求模型"""
    knowledge_base_id: str = Field(..., description="知识库ID")
    file_name: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")
    chunk_size: int = Field(default=1000, description="分块大小")
    chunk_overlap: int = Field(default=200, description="分块重叠")

class DocumentItem(BaseModel):
    """文档项模型"""
    id: str = Field(..., description="文档项ID")
    knowledge_base_id: str = Field(..., description="知识库ID")
    content: str = Field(..., description="内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    source_file: Optional[str] = Field(None, description="源文件")
    page_number: Optional[int] = Field(None, description="页码")
    chunk_index: int = Field(..., description="分块索引")
    total_chunks: int = Field(..., description="总分块数")
    vector_id: Optional[str] = Field(None, description="向量ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

class KnowledgeQuery(BaseModel):
    """知识查询模型"""
    query: str = Field(..., min_length=1, max_length=1000, description="查询内容")
    knowledge_base_id: str = Field(..., description="知识库ID")
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量")
    score_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="相似度阈值")
    include_metadata: bool = Field(default=True, description="是否包含元数据")

class SearchResult(BaseModel):
    """搜索结果模型"""
    content: str = Field(..., description="内容")
    score: float = Field(..., description="相似度分数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    source_file: Optional[str] = Field(None, description="源文件")
    page_number: Optional[int] = Field(None, description="页码")
```

#### 2. 创建知识库服务
**文件：`app/services/knowledge_service.py`**

```python
"""
知识库管理服务
处理知识库的创建、文档上传、向量化等业务逻辑
"""

import uuid
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from app.utils.logger import LoggerMixin
from app.models.schemas import (
    KnowledgeBaseCreate, 
    KnowledgeBaseUpdate, 
    KnowledgeBaseResponse,
    DocumentItem
)

class KnowledgeService(LoggerMixin):
    """
    知识库管理服务
    处理知识库的CRUD、文档管理、向量化等
    """
    
    def __init__(self, data_dir: str = "./data"):
        """初始化知识库服务"""
        super().__init__()
        
        # 内存存储（后续替换为数据库）
        self._knowledge_bases: Dict[str, Dict[str, Any]] = {}
        self._documents: Dict[str, List[Dict[str, Any]]] = {}
        
        # 文件存储目录
        self.data_dir = Path(data_dir)
        self.upload_dir = self.data_dir / "uploads"
        self.vector_db_dir = self.data_dir / "vector_db"
        
        # 创建必要的目录
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.vector_db_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化示例数据
        self._init_sample_data()
        
        self.log_info("知识库服务初始化完成")
    
    def _init_sample_data(self):
        """初始化示例知识库数据"""
        
        sample_knowledge_bases = [
            {
                "id": "kb_001",
                "name": "产品手册",
                "description": "包含所有产品功能和使用说明",
                "doc_count": 3,
                "created_by": "system",
                "created_at": datetime(2024, 1, 1, 10, 0, 0),
                "updated_at": datetime(2024, 1, 15, 14, 30, 0),
                "status": "active",
                "tags": ["产品", "手册", "使用说明"],
                "is_public": True,
                "vectorized": True,
                "category": "产品文档"
            },
            {
                "id": "kb_002",
                "name": "技术支持文档",
                "description": "常见技术问题和解决方案",
                "doc_count": 2,
                "created_by": "system",
                "created_at": datetime(2024, 1, 5, 9, 0, 0),
                "updated_at": datetime(2024, 1, 20, 11, 0, 0),
                "status": "active",
                "tags": ["技术", "支持", "FAQ"],
                "is_public": True,
                "vectorized": False,
                "category": "技术支持"
            }
        ]
        
        for kb in sample_knowledge_bases:
            self._knowledge_bases[kb["id"]] = kb
            self._documents[kb["id"]] = []
        
        # 添加示例文档
        sample_documents = [
            {
                "id": "doc_001",
                "knowledge_base_id": "kb_001",
                "content": "产品功能介绍：我们的AI助手提供智能对话、文档分析、知识检索等功能。",
                "metadata": {"type": "介绍", "importance": "高"},
                "source_file": "产品介绍.pdf",
                "page_number": 1,
                "chunk_index": 0,
                "total_chunks": 1,
                "vector_id": "vec_001",
                "created_at": datetime(2024, 1, 2, 10, 0, 0),
                "updated_at": datetime(2024, 1, 2, 10, 0, 0)
            },
            {
                "id": "doc_002",
                "knowledge_base_id": "kb_001",
                "content": "安装步骤：1. 下载安装包 2. 运行安装程序 3. 配置基本设置 4. 开始使用。",
                "metadata": {"type": "指南", "difficulty": "简单"},
                "source_file": "安装指南.pdf",
                "page_number": 1,
                "chunk_index": 0,
                "total_chunks": 1,
                "vector_id": "vec_002",
                "created_at": datetime(2024, 1, 3, 11, 0, 0),
                "updated_at": datetime(2024, 1, 3, 11, 0, 0)
            }
        ]
        
        for doc in sample_documents:
            kb_id = doc["knowledge_base_id"]
            if kb_id in self._documents:
                self._documents[kb_id].append(doc)
    
    def create_knowledge_base(self, kb_data: KnowledgeBaseCreate, created_by: str) -> KnowledgeBaseResponse:
        """
        创建新知识库
        
        Args:
            kb_data: 知识库数据
            created_by: 创建者ID
            
        Returns:
            KnowledgeBaseResponse: 创建的知识库
        """
        
        try:
            # 生成知识库ID
            kb_id = f"kb_{str(uuid.uuid4())[:8]}"
            
            now = datetime.now()
            
            # 创建知识库记录
            kb_record = {
                "id": kb_id,
                **kb_data.dict(),
                "doc_count": 0,
                "created_by": created_by,
                "created_at": now,
                "updated_at": now,
                "status": "active",
                "vectorized": False
            }
            
            # 保存到内存存储
            self._knowledge_bases[kb_id] = kb_record
            self._documents[kb_id] = []
            
            # 创建知识库目录
            kb_dir = self.upload_dir / kb_id
            kb_dir.mkdir(parents=True, exist_ok=True)
            
            self.log_info(f"创建知识库成功: {kb_id}, 名称: {kb_data.name}")
            
            return KnowledgeBaseResponse(**kb_record)
            
        except Exception as e:
            self.log_error(f"创建知识库失败: {str(e)}", error=e)
            raise
    
    def get_knowledge_base(self, kb_id: str) -> Optional[KnowledgeBaseResponse]:
        """
        获取知识库详情
        
        Args:
            kb_id: 知识库ID
            
        Returns:
            Optional[KnowledgeBaseResponse]: 知识库信息
        """
        
        if kb_id not in self._knowledge_bases:
            self.log_warning(f"知识库不存在: {kb_id}")
            return None
        
        return KnowledgeBaseResponse(**self._knowledge_bases[kb_id])
    
    def update_knowledge_base(self, kb_id: str, update_data: KnowledgeBaseUpdate) -> Optional[KnowledgeBaseResponse]:
        """
        更新知识库信息
        
        Args:
            kb_id: 知识库ID
            update_data: 更新数据
            
        Returns:
            Optional[KnowledgeBaseResponse]: 更新后的知识库信息
        """
        
        if kb_id not in self._knowledge_bases:
            self.log_warning(f"知识库不存在，无法更新: {kb_id}")
            return None
        
        try:
            # 获取现有知识库数据
            kb = self._knowledge_bases[kb_id]
            
            # 应用更新
            update_dict = update_data.dict(exclude_unset=True)
            
            for key, value in update_dict.items():
                if value is not None:
                    kb[key] = value
            
            # 更新更新时间
            kb["updated_at"] = datetime.now()
            
            self.log_info(f"更新知识库成功: {kb_id}")
            
            return KnowledgeBaseResponse(**kb)
            
        except Exception as e:
            self.log_error(f"更新知识库失败: {kb_id}, 错误: {str(e)}", error=e)
            return None
    
    def delete_knowledge_base(self, kb_id: str, user_id: str) -> bool:
        """
        删除知识库
        
        Args:
            kb_id: 知识库ID
            user_id: 用户ID（用于权限检查）
            
        Returns:
            bool: 是否成功删除
        """
        
        if kb_id not in self._knowledge_bases:
            self.log_warning(f"知识库不存在，无法删除: {kb_id}")
            return False
        
        try:
            # 检查权限（仅创建者可以删除）
            kb = self._knowledge_bases[kb_id]
            if kb["created_by"] != user_id:
                self.log_warning(f"用户 {user_id} 无权删除知识库 {kb_id}")
                return False
            
            # 删除知识库目录
            kb_dir = self.upload_dir / kb_id
            if kb_dir.exists():
                import shutil
                shutil.rmtree(kb_dir)
            
            # 删除内存中的数据
            del self._knowledge_bases[kb_id]
            if kb_id in self._documents:
                del self._documents[kb_id]
            
            self.log_info(f"删除知识库成功: {kb_id}")
            return True
            
        except Exception as e:
            self.log_error(f"删除知识库失败: {kb_id}, 错误: {str(e)}", error=e)
            return False
    
    def list_knowledge_bases(
        self, 
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        is_public: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[KnowledgeBaseResponse]:
        """
        列出知识库
        
        Args:
            user_id: 用户ID过滤（创建者）
            status: 状态过滤
            is_public: 是否公开过滤
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[KnowledgeBaseResponse]: 知识库列表
        """
        
        try:
            filtered_kbs = []
            
            for kb_id, kb_data in self._knowledge_bases.items():
                # 应用过滤条件
                if user_id and kb_data.get("created_by") != user_id:
                    # 如果用户不是创建者，只显示公开的知识库
                    if not kb_data.get("is_public", True):
                        continue
                
                if status and kb_data.get("status") != status:
                    continue
                
                if is_public is not None and kb_data.get("is_public") != is_public:
                    continue
                
                filtered_kbs.append(KnowledgeBaseResponse(**kb_data))
            
            # 按更新时间倒序排序
            filtered_kbs.sort(key=lambda x: x.updated_at, reverse=True)
            
            # 应用分页
            start_idx = offset
            end_idx = offset + limit
            paginated_kbs = filtered_kbs[start_idx:end_idx]
            
            self.log_debug(f"列出知识库 - 过滤后数量: {len(filtered_kbs)}, 分页后: {len(paginated_kbs)}")
            
            return paginated_kbs
            
        except Exception as e:
            self.log_error(f"列出知识库失败: {str(e)}", error=e)
            return []
    
    def add_document(self, kb_id: str, document_data: Dict[str, Any]) -> Optional[DocumentItem]:
        """
        添加文档到知识库
        
        Args:
            kb_id: 知识库ID
            document_data: 文档数据
            
        Returns:
            Optional[DocumentItem]: 添加的文档项
        """
        
        if kb_id not in self._knowledge_bases:
            self.log_warning(f"知识库不存在，无法添加文档: {kb_id}")
            return None
        
        try:
            # 生成文档ID
            doc_id = f"doc_{str(uuid.uuid4())[:8]}"
            now = datetime.now()
            
            # 创建文档记录
            document_record = {
                "id": doc_id,
                "knowledge_base_id": kb_id,
                "created_at": now,
                "updated_at": now,
                **document_data
            }
            
            # 添加到内存存储
            self._documents[kb_id].append(document_record)
            
            # 更新知识库文档计数
            self._knowledge_bases[kb_id]["doc_count"] = len(self._documents[kb_id])
            self._knowledge_bases[kb_id]["updated_at"] = now
            
            self.log_info(f"添加文档成功: {doc_id}, 知识库: {kb_id}")
            
            return DocumentItem(**document_record)
            
        except Exception as e:
            self.log_error(f"添加文档失败: {kb_id}, 错误: {str(e)}", error=e)
            return None
    
    def get_documents(self, kb_id: str, limit: int = 50, offset: int = 0) -> List[DocumentItem]:
        """
        获取知识库的文档列表
        
        Args:
            kb_id: 知识库ID
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[DocumentItem]: 文档列表
        """
        
        if kb_id not in self._documents:
            return []
        
        try:
            documents = self._documents[kb_id]
            
            # 按创建时间倒序排序
            documents.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
            
            # 应用分页
            start_idx = offset
            end_idx = offset + limit
            paginated_docs = documents[start_idx:end_idx]
            
            return [DocumentItem(**doc) for doc in paginated_docs]
            
        except Exception as e:
            self.log_error(f"获取文档列表失败: {kb_id}, 错误: {str(e)}", error=e)
            return []
    
    def search_documents(self, kb_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索文档（简单文本匹配，后续替换为向量搜索）
        
        Args:
            kb_id: 知识库ID
            query: 查询内容
            top_k: 返回结果数量
            
        Returns:
            List[Dict]: 搜索结果
        """
        
        if kb_id not in self._documents:
            return []
        
        try:
            results = []
            query_lower = query.lower()
            
            for doc in self._documents[kb_id]:
                content = doc.get("content", "")
                if query_lower in content.lower():
                    # 简单的匹配分数计算
                    score = min(1.0, len(query) / len(content) * 10) if content else 0.0
                    
                    results.append({
                        "content": content[:200] + "..." if len(content) > 200 else content,
                        "score": score,
                        "metadata": doc.get("metadata", {}),
                        "source_file": doc.get("source_file"),
                        "page_number": doc.get("page_number")
                    })
            
            # 按分数排序
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            self.log_error(f"搜索文档失败: {kb_id}, 错误: {str(e)}", error=e)
            return []

# 创建全局知识库服务实例
knowledge_service = KnowledgeService()
```

### 🎯 第二阶段：文档处理服务（2-3天）

#### 3. 创建文档解析器
**文件：`app/services/processing/document_parser.py`**

```python
"""
文档解析服务
解析PDF、Word、TXT等格式的文档
"""

import io
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    from docx import Document as DocxDocument
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

from app.utils.logger import LoggerMixin

class DocumentParser(LoggerMixin):
    """
    文档解析器
    支持多种文档格式的解析
    """
    
    def __init__(self):
        """初始化文档解析器"""
        super().__init__()
        self.log_info("文档解析器初始化完成")
    
    def parse_document(self, file_path: Path, file_type: str) -> Dict[str, Any]:
        """
        解析文档
        
        Args:
            file_path: 文件路径
            file_type: 文件类型 (pdf, docx, txt, md)
            
        Returns:
            Dict: 解析结果，包含内容和元数据
        """
        
        self.log_info(f"开始解析文档: {file_path}, 类型: {file_type}")
        
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            if file_type.lower() == 'pdf':
                return self._parse_pdf(file_path)
            elif file_type.lower() == 'docx':
                return self._parse_docx(file_path)
            elif file_type.lower() in ['txt', 'md', 'markdown']:
                return self._parse_text(file_path)
            else:
                raise ValueError(f"不支持的文件类型: {file_type}")
                
        except Exception as e:
            self.log_error(f"解析文档失败: {file_path}, 错误: {str(e)}", error=e)
            raise
    
    def _parse_pdf(self, file_path: Path) -> Dict[str, Any]:
        """解析PDF文件"""
        
        if not HAS_PYPDF2:
            raise ImportError("请安装 PyPDF2: pip install PyPDF2")
        
        try:
            content_parts = []
            metadata = {}
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # 获取文档信息
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                        'modification_date': pdf_reader.metadata.get('/ModDate', ''),
                    }
                
                # 提取每页文本
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    
                    # 清理文本
                    cleaned_text = self._clean_text(page_text)
                    if cleaned_text:
                        content_parts.append({
                            'page_number': page_num,
                            'content': cleaned_text
                        })
            
            # 合并所有页面内容
            full_content = "\n\n".join([p['content'] for p in content_parts])
            
            return {
                'content': full_content,
                'metadata': metadata,
                'page_count': len(pdf_reader.pages),
                'sections': content_parts,
                'file_type': 'pdf',
                'file_size': file_path.stat().st_size
            }
            
        except Exception as e:
            self.log_error(f"解析PDF失败: {file_path}, 错误: {str(e)}", error=e)
            raise
    
    def _parse_docx(self, file_path: Path) -> Dict[str, Any]:
        """解析Word文档"""
        
        if not HAS_DOCX:
            raise ImportError("请安装 python-docx: pip install python-docx")
        
        try:
            content_parts = []
            doc = DocxDocument(file_path)
            
            # 提取段落
            for para_num, paragraph in enumerate(doc.paragraphs, 1):
                if paragraph.text.strip():
                    content_parts.append({
                        'paragraph_number': para_num,
                        'content': paragraph.text.strip(),
                        'style': paragraph.style.name if paragraph.style else 'Normal'
                    })
            
            # 提取表格
            tables = []
            for table_num, table in enumerate(doc.tables, 1):
                table_data = []
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    table_data.append(row_data)
                tables.append(table_data)
            
            # 合并内容
            full_content = "\n".join([p['content'] for p in content_parts])
            
            # 添加表格内容
            for table in tables:
                table_text = "\n".join(["\t".join(row) for row in table])
                full_content += "\n\n表格:\n" + table_text
            
            return {
                'content': full_content,
                'metadata': {
                    'paragraph_count': len(content_parts),
                    'table_count': len(tables)
                },
                'sections': content_parts,
                'tables': tables,
                'file_type': 'docx',
                'file_size': file_path.stat().st_size
            }
            
        except Exception as e:
            self.log_error(f"解析Word文档失败: {file_path}, 错误: {str(e)}", error=e)
            raise
    
    def _parse_text(self, file_path: Path) -> Dict[str, Any]:
        """解析文本文件"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 清理文本
            cleaned_content = self._clean_text(content)
            
            # 分析文本结构
            lines = content.split('\n')
            sections = []
            current_section = []
            section_num = 1
            
            for line_num, line in enumerate(lines, 1):
                if line.strip():
                    current_section.append(line.strip())
                else:
                    if current_section:
                        sections.append({
                            'section_number': section_num,
                            'line_start': line_num - len(current_section),
                            'content': '\n'.join(current_section)
                        })
                        section_num += 1
                        current_section = []
            
            # 添加最后一个段落
            if current_section:
                sections.append({
                    'section_number': section_num,
                    'line_start': len(lines) - len(current_section) + 1,
                    'content': '\n'.join(current_section)
                })
            
            return {
                'content': cleaned_content,
                'metadata': {
                    'line_count': len(lines),
                    'section_count': len(sections),
                    'word_count': len(cleaned_content.split())
                },
                'sections': sections,
                'file_type': 'txt',
                'file_size': file_path.stat().st_size
            }
            
        except Exception as e:
            self.log_error(f"解析文本文件失败: {file_path}, 错误: {str(e)}", error=e)
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理后的文本
        """
        
        if not text:
            return ""
        
        # 移除多余的空格和换行
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符但保留中文、英文、数字和常用标点
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()\[\]{}\'"-]', ' ', text)
        
        # 标准化空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        提取文件元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: 文件元数据
        """
        
        try:
            stat = file_path.stat()
            
            metadata = {
                'file_name': file_path.name,
                'file_size': stat.st_size,
                'file_type': file_path.suffix.lower().lstrip('.'),
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'absolute_path': str(file_path.absolute())
            }
            
            return metadata
            
        except Exception as e:
            self.log_error(f"提取文件元数据失败: {file_path}, 错误: {str(e)}", error=e)
            return {}

# 创建全局文档解析器实例
document_parser = DocumentParser()
```

#### 4. 创建文本分割器
**文件：`app/services/processing/text_splitter.py`**

```python
"""
文本分割服务
将长文本分割为适合处理的块
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.utils.logger import LoggerMixin

@dataclass
class TextChunk:
    """文本块数据类"""
    content: str
    metadata: Dict[str, Any]
    chunk_index: int
    total_chunks: int

class TextSplitter(LoggerMixin):
    """
    文本分割器
    将长文本分割为适合向量化的块
    """
    
    def __init__(
        self, 
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None
    ):
        """
        初始化文本分割器
        
        Args:
            chunk_size: 每个块的大小（字符数）
            chunk_overlap: 块之间的重叠大小
            separators: 分隔符列表
        """
        super().__init__()
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if separators is None:
            separators = [
                "\n\n",  # 双换行（段落分隔）
                "\n",    # 单换行
                "。",    # 中文句号
                "！",    # 中文感叹号
                "？",    # 中文问号
                "；",    # 中文分号
                "，",    # 中文逗号
                ". ",    # 英文句号+空格
                "! ",    # 英文感叹号+空格
                "? ",    # 英文问号+空格
                "; ",    # 英文分号+空格
                ", ",    # 英文逗号+空格
                " ",     # 空格
                ""       # 最后按字符分割
            ]
        
        self.separators = separators
        
        self.log_info(f"文本分割器初始化完成 - 块大小: {chunk_size}, 重叠: {chunk_overlap}")
    
    def split_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[TextChunk]:
        """
        分割文本
        
        Args:
            text: 要分割的文本
            metadata: 原始元数据
            
        Returns:
            List[TextChunk]: 分割后的文本块列表
        """
        
        if metadata is None:
            metadata = {}
        
        self.log_debug(f"开始分割文本，长度: {len(text)} 字符")
        
        try:
            # 如果文本很短，直接返回
            if len(text) <= self.chunk_size:
                return [TextChunk(
                    content=text,
                    metadata=metadata,
                    chunk_index=0,
                    total_chunks=1
                )]
            
            # 尝试用不同的分隔符分割
            chunks = self._split_by_separators(text)
            
            # 如果分割后的块仍然太大，进一步分割
            final_chunks = []
            for i, chunk_text in enumerate(chunks):
                if len(chunk_text) > self.chunk_size:
                    # 递归分割
                    sub_chunks = self._recursive_split(chunk_text)
                    for j, sub_chunk in enumerate(sub_chunks):
                        chunk_metadata = metadata.copy()
                        chunk_metadata['original_chunk_index'] = i
                        chunk_metadata['sub_chunk_index'] = j
                        
                        final_chunks.append(TextChunk(
                            content=sub_chunk,
                            metadata=chunk_metadata,
                            chunk_index=len(final_chunks),
                            total_chunks=0  # 稍后更新
                        ))
                else:
                    chunk_metadata = metadata.copy()
                    chunk_metadata['original_chunk_index'] = i
                    
                    final_chunks.append(TextChunk(
                        content=chunk_text,
                        metadata=chunk_metadata,
                        chunk_index=len(final_chunks),
                        total_chunks=0  # 稍后更新
                    ))
            
            # 更新总数
            for i, chunk in enumerate(final_chunks):
                chunk.total_chunks = len(final_chunks)
                # 更新索引以反映最终位置
                chunk.chunk_index = i
            
            self.log_debug(f"文本分割完成，共 {len(final_chunks)} 个块")
            
            return final_chunks
            
        except Exception as e:
            self.log_error(f"分割文本失败: {str(e)}", error=e)
            # 失败时返回整个文本作为一个块
            return [TextChunk(
                content=text,
                metadata=metadata,
                chunk_index=0,
                total_chunks=1
            )]
    
    def _split_by_separators(self, text: str) -> List[str]:
        """使用分隔符分割文本"""
        
        chunks = [text]
        
        for separator in self.separators:
            if separator == "":
                # 最后的分隔符，按字符分割
                final_chunks = []
                for chunk in chunks:
                    if len(chunk) > self.chunk_size:
                        # 按字符分割
                        char_chunks = self._split_by_characters(chunk)
                        final_chunks.extend(char_chunks)
                    else:
                        final_chunks.append(chunk)
                return final_chunks
            
            new_chunks = []
            for chunk in chunks:
                if len(chunk) <= self.chunk_size:
                    new_chunks.append(chunk)
                else:
                    # 使用当前分隔符分割
                    split_chunks = self._split_by_separator(chunk, separator)
                    new_chunks.extend(split_chunks)
            
            chunks = new_chunks
            
            # 检查是否所有块都已足够小
            if all(len(chunk) <= self.chunk_size for chunk in chunks):
                return chunks
        
        return chunks
    
    def _split_by_separator(self, text: str, separator: str) -> List[str]:
        """使用特定分隔符分割文本"""
        
        if separator == "":
            return [text]
        
        # 分割文本
        parts = text.split(separator)
        
        # 重新添加分隔符（除了最后一部分）
        result = []
        for i, part in enumerate(parts):
            if i < len(parts) - 1:
                result.append(part + separator)
            else:
                result.append(part)
        
        # 合并小片段
        merged_result = []
        current_chunk = ""
        
        for part in result:
            if len(current_chunk) + len(part) <= self.chunk_size:
                current_chunk += part
            else:
                if current_chunk:
                    merged_result.append(current_chunk)
                # 如果单个部分就超过块大小，需要进一步分割
                if len(part) > self.chunk_size:
                    # 递归分割
                    sub_parts = self._recursive_split(part)
                    merged_result.extend(sub_parts)
                    current_chunk = ""
                else:
                    current_chunk = part
        
        if current_chunk:
            merged_result.append(current_chunk)
        
        return merged_result
    
    def _split_by_characters(self, text: str) -> List[str]:
        """按字符分割文本"""
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # 尝试在句子边界处结束
            if end < len(text):
                # 查找最近的句子结束符
                sentence_end = max(
                    text.rfind('。', start, end),
                    text.rfind('！', start, end),
                    text.rfind('？', start, end),
                    text.rfind('. ', start, end),
                    text.rfind('! ', start, end),
                    text.rfind('? ', start, end),
                    text.rfind('\n', start, end)
                )
                
                if sentence_end != -1 and sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # 更新起始位置，考虑重叠
            start = end - self.chunk_overlap if end - self.chunk_overlap > start else end
        
        return chunks
    
    def _recursive_split(self, text: str) -> List[str]:
        """递归分割文本"""
        
        if len(text) <= self.chunk_size:
            return [text]
        
        # 在中间位置查找分割点
        mid = len(text) // 2
        
        # 查找附近的分隔符
        best_split = -1
        for offset in range(0, min(100, len(text) - mid)):
            # 向前查找
            forward_pos = mid + offset
            if forward_pos < len(text):
                if self._is_good_split_point(text, forward_pos):
                    best_split = forward_pos
                    break
            
            # 向后查找
            backward_pos = mid - offset
            if backward_pos > 0:
                if self._is_good_split_point(text, backward_pos):
                    best_split = backward_pos
                    break
        
        # 如果没有找到好的分割点，在中间分割
        if best_split == -1:
            best_split = mid
        
        # 递归分割
        left_part = text[:best_split].strip()
        right_part = text[best_split:].strip()
        
        left_chunks = self._recursive_split(left_part) if left_part else []
        right_chunks = self._recursive_split(right_part) if right_part else []
        
        return left_chunks + right_chunks
    
    def _is_good_split_point(self, text: str, position: int) -> bool:
        """检查是否是好的分割点"""
        
        if position <= 0 or position >= len(text):
            return False
        
        # 检查位置前后字符
        prev_char = text[position - 1] if position > 0 else ''
        curr_char = text[position] if position < len(text) else ''
        
        # 好的分割点：句子结束符后
        if prev_char in '。！？.!?':
            return True
        
        # 段落分隔
        if position >= 2 and text[position-2:position] == '\n\n':
            return True
        
        # 在空格处分隔
        if prev_char == ' ' and curr_char != ' ':
            return True
        
        return False
    
    def split_documents(self, documents: List[Dict[str, Any]]) -> List[TextChunk]:
        """
        分割多个文档
        
        Args:
            documents: 文档列表，每个文档包含content和metadata
            
        Returns:
            List[TextChunk]: 所有文档的分割结果
        """
        
        all_chunks = []
        
        for doc_idx, doc in enumerate(documents):
            content = doc.get('content', '')
            metadata = doc.get('metadata', {}).copy()
            
            # 添加文档信息到元数据
            metadata['document_index'] = doc_idx
            metadata['document_source'] = doc.get('source', 'unknown')
            
            chunks = self.split_text(content, metadata)
            all_chunks.extend(chunks)
        
        # 更新总数和索引
        for i, chunk in enumerate(all_chunks):
            chunk.chunk_index = i
            chunk.total_chunks = len(all_chunks)
        
        self.log_info(f"分割 {len(documents)} 个文档，生成 {len(all_chunks)} 个文本块")
        
        return all_chunks

# 创建全局文本分割器实例
text_splitter = TextSplitter()
```

### 🎯 第三阶段：向量化与存储（2-3天）

#### 5. 创建嵌入服务
**文件：`app/services/processing/embedding_service.py`**

```python
"""
嵌入服务
生成文本的向量嵌入
"""

import numpy as np
from typing import List, Dict, Any, Optional, Union
from sentence_transformers import SentenceTransformer

from app.config.settings import settings
from app.utils.logger import LoggerMixin

class EmbeddingService(LoggerMixin):
    """
    嵌入服务
    使用Sentence Transformers生成文本向量
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        初始化嵌入服务
        
        Args:
            model_name: 嵌入模型名称
        """
        super().__init__()
        
        self.model_name = model_name or settings.EMBEDDING_MODEL
        
        try:
            self.log_info(f"正在加载嵌入模型: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.model.eval()  # 设置为评估模式
            
            # 获取模型维度
            self.dimension = self.model.get_sentence_embedding_dimension()
            
            self.log_info(f"嵌入模型加载完成 - 维度: {self.dimension}")
            
        except Exception as e:
            self.log_error(f"加载嵌入模型失败: {self.model_name}, 错误: {str(e)}", error=e)
            raise
    
    def encode(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """
        编码文本为向量
        
        Args:
            texts: 单个文本或文本列表
            **kwargs: 额外的编码参数
            
        Returns:
            np.ndarray: 向量数组
        """
        
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            self.log_debug(f"编码 {len(texts)} 个文本，模型: {self.model_name}")
            
            # 编码文本
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False,
                **kwargs
            )
            
            return embeddings
            
        except Exception as e:
            self.log_error(f"编码文本失败: {str(e)}", error=e)
            raise
    
    def encode_batch(self, texts: List[str], batch_size: int = 32, **kwargs) -> List[np.ndarray]:
        """
        批量编码文本
        
        Args:
            texts: 文本列表
            batch_size: 批次大小
            **kwargs: 额外的编码参数
            
        Returns:
            List[np.ndarray]: 向量列表
        """
        
        try:
            self.log_debug(f"批量编码 {len(texts)} 个文本，批次大小: {batch_size}")
            
            all_embeddings = []
            
            # 分批处理
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                batch_embeddings = self.encode(batch_texts, **kwargs)
                all_embeddings.extend(batch_embeddings)
                
                self.log_debug(f"处理批次 {i//batch_size + 1}/{(len(texts)+batch_size-1)//batch_size}")
            
            return all_embeddings
            
        except Exception as e:
            self.log_error(f"批量编码失败: {str(e)}", error=e)
            raise
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        计算两个向量的相似度（余弦相似度）
        
        Args:
            embedding1: 第一个向量
            embedding2: 第二个向量
            
        Returns:
            float: 相似度分数（0-1）
        """
        
        try:
            # 归一化向量
            embedding1_norm = embedding1 / np.linalg.norm(embedding1)
            embedding2_norm = embedding2 / np.linalg.norm(embedding2)
            
            # 计算余弦相似度
            similarity = np.dot(embedding1_norm, embedding2_norm)
            
            # 确保在0-1范围内
            similarity = max(0.0, min(1.0, similarity))
            
            return similarity
            
        except Exception as e:
            self.log_error(f"计算相似度失败: {str(e)}", error=e)
            return 0.0
    
    def similarity_batch(self, query_embedding: np.ndarray, embeddings: List[np.ndarray]) -> List[float]:
        """
        批量计算相似度
        
        Args:
            query_embedding: 查询向量
            embeddings: 目标向量列表
            
        Returns:
            List[float]: 相似度分数列表
        """
        
        try:
            # 归一化查询向量
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            
            similarities = []
            
            for emb in embeddings:
                # 归一化目标向量
                emb_norm = emb / np.linalg.norm(emb)
                
                # 计算余弦相似度
                sim = np.dot(query_norm, emb_norm)
                sim = max(0.0, min(1.0, sim))
                
                similarities.append(sim)
            
            return similarities
            
        except Exception as e:
            self.log_error(f"批量计算相似度失败: {str(e)}", error=e)
            return [0.0] * len(embeddings)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            Dict: 模型信息
        """
        
        return {
            'model_name': self.model_name,
            'dimension': self.dimension,
            'max_seq_length': self.model.max_seq_length,
            'device': str(self.model.device)
        }

# 创建全局嵌入服务实例
embedding_service = EmbeddingService()
```

#### 6. 创建向量存储
**文件：`app/services/processing/vector_store.py`**

```python
"""
向量存储服务
使用ChromaDB存储和检索向量
"""

import chromadb
import uuid
import json
from typing import List, Dict, Any, Optional, Tuple
from chromadb.config import Settings

from app.config.settings import settings
from app.utils.logger import LoggerMixin

class VectorStore(LoggerMixin):
    """
    向量存储管理器
    基于ChromaDB的向量存储和检索
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        初始化向量存储
        
        Args:
            persist_directory: 持久化目录
        """
        super().__init__()
        
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIR
        self.collection_name = settings.CHROMA_COLLECTION_NAME
        
        try:
            # 创建ChromaDB客户端
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            self.log_info(f"向量存储初始化完成 - 目录: {self.persist_directory}")
            
            # 创建或获取默认集合
            self.collection = self._get_or_create_collection()
            
            self.log_info(f"集合 '{self.collection_name}' 就绪")
            
        except Exception as e:
            self.log_error(f"初始化向量存储失败: {str(e)}", error=e)
            raise
    
    def _get_or_create_collection(self) -> chromadb.Collection:
        """
        获取或创建集合
        
        Returns:
            chromadb.Collection: 集合对象
        """
        
        try:
            # 尝试获取现有集合
            collection = self.client.get_collection(self.collection_name)
            self.log_debug(f"获取现有集合: {self.collection_name}")
            return collection
            
        except Exception:
            # 创建新集合
            self.log_info(f"创建新集合: {self.collection_name}")
            return self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
            )
    
    def add_documents(
        self, 
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        添加文档到向量存储
        
        Args:
            documents: 文档内容列表
            embeddings: 向量列表
            metadatas: 元数据列表
            ids: ID列表
            
        Returns:
            List[str]: 添加的文档ID列表
        """
        
        try:
            if not documents or not embeddings:
                self.log_warning("文档或向量为空")
                return []
            
            if len(documents) != len(embeddings):
                raise ValueError(f"文档数量({len(documents)})和向量数量({len(embeddings)})不匹配")
            
            # 生成ID
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in range(len(documents))]
            
            # 准备元数据
            if metadatas is None:
                metadatas = [{} for _ in range(len(documents))]
            
            # 添加文档
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            self.log_info(f"添加 {len(documents)} 个文档到向量存储")
            
            return ids
            
        except Exception as e:
            self.log_error(f"添加文档失败: {str(e)}", error=e)
            raise
    
    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索相似文档
        
        Args:
            query_embedding: 查询向量
            n_results: 返回结果数量
            where: 元数据过滤条件
            where_document: 文档内容过滤条件
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        
        try:
            self.log_debug(f"向量搜索 - 查询向量维度: {len(query_embedding)}, 返回数量: {n_results}")
            
            # 执行搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document,
                include=["documents", "metadatas", "distances"]
            )
            
            # 整理结果
            search_results = []
            
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    # 将距离转换为相似度分数（ChromaDB返回的是距离，需要转换为相似度）
                    distance = results['distances'][0][i]
                    similarity = 1.0 - distance  # 假设使用余弦距离
                    
                    result = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'score': similarity,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': distance
                    }
                    
                    search_results.append(result)
            
            self.log_debug(f"搜索完成，返回 {len(search_results)} 个结果")
            
            return search_results
            
        except Exception as e:
            self.log_error(f"搜索失败: {str(e)}", error=e)
            return []
    
    def search_by_text(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        通过文本搜索
        
        Args:
            query_text: 查询文本
            n_results: 返回结果数量
            where: 元数据过滤条件
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        
        try:
            self.log_debug(f"文本搜索 - 查询: '{query_text[:50]}...', 返回数量: {n_results}")
            
            # 使用ChromaDB的文本搜索
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            # 整理结果
            search_results = []
            
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    distance = results['distances'][0][i]
                    similarity = 1.0 - distance
                    
                    result = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'score': similarity,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': distance
                    }
                    
                    search_results.append(result)
            
            self.log_debug(f"文本搜索完成，返回 {len(search_results)} 个结果")
            
            return search_results
            
        except Exception as e:
            self.log_error(f"文本搜索失败: {str(e)}", error=e)
            return []
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            Optional[Dict]: 文档信息
        """
        
        try:
            results = self.collection.get(
                ids=[document_id],
                include=["documents", "metadatas", "embeddings"]
            )
            
            if results['ids']:
                return {
                    'id': results['ids'][0],
                    'content': results['documents'][0],
                    'metadata': results['metadatas'][0] if results['metadatas'] else {},
                    'embedding': results['embeddings'][0] if results['embeddings'] else None
                }
            
            return None
            
        except Exception as e:
            self.log_error(f"获取文档失败: {document_id}, 错误: {str(e)}", error=e)
            return None
    
    def delete_documents(self, document_ids: List[str]) -> bool:
        """
        删除文档
        
        Args:
            document_ids: 文档ID列表
            
        Returns:
            bool: 是否成功删除
        """
        
        try:
            self.collection.delete(ids=document_ids)
            self.log_info(f"删除 {len(document_ids)} 个文档")
            return True
            
        except Exception as e:
            self.log_error(f"删除文档失败: {str(e)}", error=e)
            return False
    
    def delete_by_filter(self, where: Dict[str, Any]) -> bool:
        """
        根据过滤条件删除文档
        
        Args:
            where: 过滤条件
            
        Returns:
            bool: 是否成功删除
        """
        
        try:
            self.collection.delete(where=where)
            self.log_info(f"根据过滤条件删除文档: {where}")
            return True
            
        except Exception as e:
            self.log_error(f"根据过滤条件删除文档失败: {str(e)}", error=e)
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        获取集合信息
        
        Returns:
            Dict: 集合信息
        """
        
        try:
            count = self.collection.count()
            
            return {
                'collection_name': self.collection_name,
                'document_count': count,
                'persist_directory': self.persist_directory
            }
            
        except Exception as e:
            self.log_error(f"获取集合信息失败: {str(e)}", error=e)
            return {}
    
    def reset_collection(self) -> bool:
        """
        重置集合（删除所有数据）
        
        Returns:
            bool: 是否成功重置
        """
        
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self._get_or_create_collection()
            
            self.log_info("集合重置完成")
            return True
            
        except Exception as e:
            self.log_error(f"重置集合失败: {str(e)}", error=e)
            return False

# 创建全局向量存储实例
vector_store = VectorStore()
```

### 🎯 第四阶段：RAG服务与API（2-3天）

#### 7. 创建RAG服务
**文件：`app/services/ai/rag_service.py`**

```python
"""
RAG检索服务
检索增强生成的核心服务
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from app.services.processing.embedding_service import embedding_service
from app.services.processing.vector_store import vector_store
from app.services.knowledge_service import knowledge_service
from app.utils.logger import LoggerMixin

class RAGService(LoggerMixin):
    """
    RAG检索服务
    处理知识检索和上下文构建
    """
    
    def __init__(self):
        """初始化RAG服务"""
        super().__init__()
        self.log_info("RAG服务初始化完成")
    
    def retrieve(
        self, 
        query: str, 
        knowledge_base_id: str, 
        top_k: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        检索相关知识
        
        Args:
            query: 查询内容
            knowledge_base_id: 知识库ID
            top_k: 返回结果数量
            score_threshold: 相似度阈值
            
        Returns:
            List[Dict]: 检索结果列表
        """
        
        try:
            self.log_info(f"RAG检索 - 知识库: {knowledge_base_id}, 查询: '{query[:50]}...'")
            
            # 1. 编码查询
            query_embedding = embedding_service.encode(query)
            
            # 2. 构建过滤条件（按知识库ID过滤）
            where_filter = {"knowledge_base_id": knowledge_base_id}
            
            # 3. 向量搜索
            vector_results = vector_store.search(
                query_embedding=query_embedding.tolist(),
                n_results=top_k * 2,  # 多取一些，方便后续过滤
                where=where_filter
            )
            
            # 4. 文本搜索（作为补充）
            text_results = vector_store.search_by_text(
                query_text=query,
                n_results=top_k,
                where=where_filter
            )
            
            # 5. 合并和去重结果
            all_results = self._merge_results(vector_results, text_results)
            
            # 6. 过滤低分结果
            filtered_results = [
                result for result in all_results 
                if result.get('score', 0) >= score_threshold
            ]
            
            # 7. 排序和截断
            filtered_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            final_results = filtered_results[:top_k]
            
            self.log_info(f"RAG检索完成，返回 {len(final_results)} 个结果")
            
            return final_results
            
        except Exception as e:
            self.log_error(f"RAG检索失败: {str(e)}", error=e)
            return []
    
    def _merge_results(self, vector_results: List[Dict], text_results: List[Dict]) -> List[Dict]:
        """
        合并向量搜索和文本搜索结果
        
        Args:
            vector_results: 向量搜索结果
            text_results: 文本搜索结果
            
        Returns:
            List[Dict]: 合并后的结果
        """
        
        merged = []
        seen_ids = set()
        
        # 添加向量搜索结果
        for result in vector_results:
            result_id = result.get('id')
            if result_id and result_id not in seen_ids:
                merged.append(result)
                seen_ids.add(result_id)
        
        # 添加文本搜索结果（去重）
        for result in text_results:
            result_id = result.get('id')
            if result_id and result_id not in seen_ids:
                merged.append(result)
                seen_ids.add(result_id)
        
        return merged
    
    def build_context(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        """
        构建上下文
        
        Args:
            query: 原始查询
            search_results: 检索结果
            
        Returns:
            str: 构建的上下文
        """
        
        if not search_results:
            return "没有找到相关信息。"
        
        try:
            context_parts = []
            context_parts.append(f"用户查询: {query}\n\n")
            context_parts.append("相关文档内容:\n")
            
            for i, result in enumerate(search_results, 1):
                content = result.get('content', '')
                metadata = result.get('metadata', {})
                score = result.get('score', 0)
                
                # 格式化元数据
                metadata_str = ""
                if metadata:
                    metadata_items = []
                    for key, value in metadata.items():
                        if key not in ['knowledge_base_id', 'embedding']:
                            metadata_items.append(f"{key}: {value}")
                    if metadata_items:
                        metadata_str = f" ({', '.join(metadata_items)})"
                
                context_parts.append(f"\n--- 文档 {i} (相关度: {score:.2f}){metadata_str} ---\n")
                context_parts.append(f"{content}\n")
            
            # 添加引用说明
            context_parts.append("\n--- 请基于以上信息回答用户问题 ---")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            self.log_error(f"构建上下文失败: {str(e)}", error=e)
            return "上下文构建失败，请直接回答问题。"
    
    def answer_with_rag(
        self, 
        query: str, 
        knowledge_base_id: str,
        conversation_context: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        使用RAG回答问题
        
        Args:
            query: 用户问题
            knowledge_base_id: 知识库ID
            conversation_context: 对话上下文
            top_k: 检索数量
            
        Returns:
            Dict: 回答结果
        """
        
        try:
            self.log_info(f"RAG问答 - 知识库: {knowledge_base_id}, 问题: '{query[:50]}...'")
            
            # 1. 检索相关知识
            search_results = self.retrieve(
                query=query, 
                knowledge_base_id=knowledge_base_id,
                top_k=top_k
            )
            
            # 2. 构建上下文
            context = self.build_context(query, search_results)
            
            # 3. 如果有对话上下文，合并
            if conversation_context:
                full_context = f"对话历史:\n{conversation_context}\n\n{context}"
            else:
                full_context = context
            
            # 4. 构建提示词
            prompt = self._build_prompt(query, full_context)
            
            # 5. 返回结果
            return {
                'success': True,
                'query': query,
                'context': full_context,
                'prompt': prompt,
                'search_results': search_results,
                'result_count': len(search_results)
            }
            
        except Exception as e:
            self.log_error(f"RAG问答失败: {str(e)}", error=e)
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'context': "检索失败",
                'search_results': []
            }
    
    def _build_prompt(self, query: str, context: str) -> str:
        """
        构建提示词
        
        Args:
            query: 用户问题
            context: 检索到的上下文
            
        Returns:
            str: 提示词
        """
        
        prompt = f"""你是一个专业的AI助手，请基于以下提供的相关文档内容来回答用户的问题。

{context}

请按照以下要求回答：
1. 基于提供的文档内容回答问题
2. 如果文档中没有相关信息，请诚实地告知用户
3. 回答要准确、简洁、有帮助
4. 可以引用文档中的具体信息，但不要直接复制大段原文
5. 使用中文回答

用户问题：{query}

请开始回答："""
        
        return prompt
    
    def add_documents_to_knowledge_base(
        self, 
        knowledge_base_id: str,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        将文档添加到知识库并向量化
        
        Args:
            knowledge_base_id: 知识库ID
            documents: 文档列表
            
        Returns:
            Dict: 处理结果
        """
        
        try:
            if not documents:
                return {
                    'success': False,
                    'error': '文档列表为空',
                    'processed_count': 0
                }
            
            self.log_info(f"开始处理 {len(documents)} 个文档到知识库 {knowledge_base_id}")
            
            # 1. 准备文档内容
            texts = []
            metadatas = []
            
            for doc in documents:
                content = doc.get('content', '')
                metadata = doc.get('metadata', {}).copy()
                
                # 添加知识库ID到元数据
                metadata['knowledge_base_id'] = knowledge_base_id
                
                texts.append(content)
                metadatas.append(metadata)
            
            # 2. 生成向量
            embeddings = embedding_service.encode(texts)
            
            # 3. 添加到向量存储
            document_ids = vector_store.add_documents(
                documents=texts,
                embeddings=embeddings.tolist(),
                metadatas=metadatas
            )
            
            # 4. 更新知识库状态
            knowledge_service.update_knowledge_base(
                knowledge_base_id,
                KnowledgeBaseUpdate(vectorized=True)
            )
            
            self.log_info(f"文档处理完成，成功添加 {len(document_ids)} 个文档")
            
            return {
                'success': True,
                'processed_count': len(document_ids),
                'document_ids': document_ids,
                'knowledge_base_id': knowledge_base_id
            }
            
        except Exception as e:
            self.log_error(f"添加文档到知识库失败: {str(e)}", error=e)
            return {
                'success': False,
                'error': str(e),
                'processed_count': 0
            }

# 创建全局RAG服务实例
rag_service = RAGService()
```

### 🎯 第五阶段：API端点与集成（1-2天）

#### 8. 创建知识库API端点
**文件：`app/api/v1/endpoints/knowledge.py`**

```python
"""
知识库管理API端点
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks

from app.api.dependencies import get_current_user, UserContext
from app.services.knowledge_service import knowledge_service
from app.services.processing.document_parser import document_parser
from app.services.processing.text_splitter import text_splitter
from app.services.ai.rag_service import rag_service
from app.models.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeQuery,
    SearchResult,
    SuccessResponse,
    PaginationParams
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])

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
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    获取知识库列表端点
    
    Args:
        status: 状态过滤
        is_public: 是否公开过滤
        page: 页码
        page_size: 每页大小
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含知识库列表
    """
    
    try:
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取知识库列表
        knowledge_bases = knowledge_service.list_knowledge_bases(
            user_id=current_user.user_id,
            status=status,
            is_public=is_public,
            limit=page_size,
            offset=offset
        )
        
        # 获取总数
        total_kbs = len([
            kb for kb_id, kb_data in knowledge_service._knowledge_bases.items()
            if (not status or kb_data.get("status") == status) and
               (is_public is None or kb_data.get("is_public") == is_public) and
               (not current_user.user_id or kb_data.get("created_by") == current_user.user_id or kb_data.get("is_public"))
        ])
        
        # 计算总页数
        total_pages = (total_kbs + page_size - 1) // page_size
        
        logger.info(f"获取知识库列表 - 用户: {current_user.user_id}, 数量: {len(knowledge_bases)}")
        
        return SuccessResponse(
            success=True,
            message="获取知识库列表成功",
            data={
                "items": [kb.dict() for kb in knowledge_bases],
                "total": total_kbs,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        )
        
    except Exception as e:
        logger.error(f"获取知识库列表异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识库列表时发生错误: {str(e)}"
        )

@router.post(
    "",
    response_model=SuccessResponse,
    summary="创建知识库",
    description="创建新的知识库"
)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    创建知识库端点
    
    Args:
        kb_data: 知识库数据
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含创建的知识库信息
    """
    
    try:
        # 创建知识库
        knowledge_base = knowledge_service.create_knowledge_base(
            kb_data, 
            current_user.user_id
        )
        
        if not knowledge_base:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建知识库失败"
            )
        
        logger.info(f"创建知识库成功 - ID: {knowledge_base.id}, 名称: {knowledge_base.name}")
        
        return SuccessResponse(
            success=True,
            message="知识库创建成功",
            data=knowledge_base.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建知识库异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建知识库时发生错误: {str(e)}"
        )

@router.get(
    "/{knowledge_base_id}",
    response_model=SuccessResponse,
    summary="获取知识库详情",
    description="获取指定知识库的详细信息"
)
async def get_knowledge_base_detail(
    knowledge_base_id: str,
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    获取知识库详情端点
    
    Args:
        knowledge_base_id: 知识库ID
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含知识库详情
    """
    
    try:
        # 获取知识库详情
        knowledge_base = knowledge_service.get_knowledge_base(knowledge_base_id)
        
        if not knowledge_base:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在: {knowledge_base_id}"
            )
        
        # 检查权限（非公开知识库只允许创建者访问）
        if not knowledge_base.is_public and knowledge_base.created_by != current_user.user_id:
            logger.warning(f"权限拒绝 - 用户: {current_user.user_id} 尝试访问非公开知识库: {knowledge_base_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此知识库"
            )
        
        logger.info(f"获取知识库详情 - ID: {knowledge_base_id}")
        
        return SuccessResponse(
            success=True,
            message="获取知识库详情成功",
            data=knowledge_base.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识库详情异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识库详情时发生错误: {str(e)}"
        )

@router.put(
    "/{knowledge_base_id}",
    response_model=SuccessResponse,
    summary="更新知识库",
    description="更新指定知识库的信息"
)
async def update_knowledge_base(
    knowledge_base_id: str,
    update_data: KnowledgeBaseUpdate,
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    更新知识库端点
    
    Args:
        knowledge_base_id: 知识库ID
        update_data: 更新数据
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含更新后的知识库信息
    """
    
    try:
        # 检查知识库是否存在
        existing_kb = knowledge_service.get_knowledge_base(knowledge_base_id)
        
        if not existing_kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在: {knowledge_base_id}"
            )
        
        # 检查权限（仅创建者可以更新）
        if existing_kb.created_by != current_user.user_id:
            logger.warning(f"权限拒绝 - 用户: {current_user.user_id} 尝试更新知识库: {knowledge_base_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权更新此知识库"
            )
        
        # 更新知识库
        updated_kb = knowledge_service.update_knowledge_base(knowledge_base_id, update_data)
        
        if not updated_kb:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新知识库失败"
            )
        
        logger.info(f"更新知识库成功 - ID: {knowledge_base_id}")
        
        return SuccessResponse(
            success=True,
            message="知识库更新成功",
            data=updated_kb.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新知识库异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新知识库时发生错误: {str(e)}"
        )

@router.delete(
    "/{knowledge_base_id}",
    response_model=SuccessResponse,
    summary="删除知识库",
    description="删除指定的知识库"
)
async def delete_knowledge_base(
    knowledge_base_id: str,
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    删除知识库端点
    
    Args:
        knowledge_base_id: 知识库ID
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应
    """
    
    try:
        # 检查知识库是否存在
        existing_kb = knowledge_service.get_knowledge_base(knowledge_base_id)
        
        if not existing_kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在: {knowledge_base_id}"
            )
        
        # 检查权限（仅创建者可以删除）
        if existing_kb.created_by != current_user.user_id:
            logger.warning(f"权限拒绝 - 用户: {current_user.user_id} 尝试删除知识库: {knowledge_base_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此知识库"
            )
        
        # 删除知识库
        success = knowledge_service.delete_knowledge_base(knowledge_base_id, current_user.user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除知识库失败: {knowledge_base_id}"
            )
        
        logger.info(f"删除知识库成功 - ID: {knowledge_base_id}")
        
        return SuccessResponse(
            success=True,
            message="知识库删除成功",
            data={
                "knowledge_base_id": knowledge_base_id,
                "deleted": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除知识库异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除知识库时发生错误: {str(e)}"
        )

@router.post(
    "/{knowledge_base_id}/upload",
    response_model=SuccessResponse,
    summary="上传文档",
    description="上传文档到知识库并进行处理"
)
async def upload_document(
    knowledge_base_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    上传文档端点
    
    Args:
        knowledge_base_id: 知识库ID
        background_tasks: 后台任务管理器
        file: 上传的文件
        chunk_size: 分块大小
        chunk_overlap: 分块重叠大小
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应
    """
    
    try:
        # 检查知识库是否存在
        existing_kb = knowledge_service.get_knowledge_base(knowledge_base_id)
        
        if not existing_kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在: {knowledge_base_id}"
            )
        
        # 检查权限
        if existing_kb.created_by != current_user.user_id and not existing_kb.is_public:
            logger.warning(f"权限拒绝 - 用户: {current_user.user_id} 尝试上传文档到知识库: {knowledge_base_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权上传文档到此知识库"
            )
        
        # 检查文件类型
        allowed_extensions = ['.pdf', '.docx', '.txt', '.md', '.json']
        file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型: {file_ext}，支持的格式: {', '.join(allowed_extensions)}"
            )
        
        # 保存文件
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 解析文档
            file_type = file_ext.lstrip('.')
            parsed_result = document_parser.parse_document(temp_file_path, file_type)
            
            # 分割文本
            text_splitter.chunk_size = chunk_size
            text_splitter.chunk_overlap = chunk_overlap
            
            chunks = text_splitter.split_text(
                parsed_result['content'],
                metadata={
                    'source_file': file.filename,
                    'file_type': file_type,
                    'file_size': len(content),
                    **parsed_result.get('metadata', {})
                }
            )
            
            # 添加文档到知识库
            document_count = 0
            for chunk in chunks:
                document_item = knowledge_service.add_document(
                    knowledge_base_id,
                    {
                        'content': chunk.content,
                        'metadata': chunk.metadata,
                        'source_file': file.filename,
                        'chunk_index': chunk.chunk_index,
                        'total_chunks': chunk.total_chunks
                    }
                )
                
                if document_item:
                    document_count += 1
            
            logger.info(f"上传文档成功 - 知识库: {knowledge_base_id}, 文件: {file.filename}, 文档块: {document_count}")
            
            # 后台任务：向量化处理
            background_tasks.add_task(
                self._vectorize_documents,
                knowledge_base_id,
                chunks
            )
            
            return SuccessResponse(
                success=True,
                message=f"文档上传成功，处理了 {document_count} 个文档块",
                data={
                    "knowledge_base_id": knowledge_base_id,
                    "file_name": file.filename,
                    "file_size": len(content),
                    "chunks_processed": document_count,
                    "vectorization_queued": True
                }
            )
            
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传文档异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文档时发生错误: {str(e)}"
        )
    
    async def _vectorize_documents(self, knowledge_base_id: str, chunks: List):
        """后台向量化文档"""
        try:
            # 准备文档数据
            documents = []
            for chunk in chunks:
                documents.append({
                    'content': chunk.content,
                    'metadata': chunk.metadata
                })
            
            # 添加到向量存储
            result = rag_service.add_documents_to_knowledge_base(
                knowledge_base_id,
                documents
            )
            
            if result['success']:
                logger.info(f"向量化完成 - 知识库: {knowledge_base_id}, 处理文档: {result['processed_count']}")
            else:
                logger.error(f"向量化失败 - 知识库: {knowledge_base_id}, 错误: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"后台向量化异常: {str(e)}", exc_info=True)

@router.get(
    "/{knowledge_base_id}/documents",
    response_model=SuccessResponse,
    summary="获取知识库文档列表",
    description="获取指定知识库的文档列表"
)
async def get_knowledge_base_documents(
    knowledge_base_id: str,
    page: int = 1,
    page_size: int = 20,
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    获取知识库文档列表端点
    
    Args:
        knowledge_base_id: 知识库ID
        page: 页码
        page_size: 每页大小
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含文档列表
    """
    
    try:
        # 检查知识库是否存在
        existing_kb = knowledge_service.get_knowledge_base(knowledge_base_id)
        
        if not existing_kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在: {knowledge_base_id}"
            )
        
        # 检查权限
        if not existing_kb.is_public and existing_kb.created_by != current_user.user_id:
            logger.warning(f"权限拒绝 - 用户: {current_user.user_id} 尝试获取知识库文档: {knowledge_base_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此知识库的文档"
            )
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取文档列表
        documents = knowledge_service.get_documents(
            knowledge_base_id,
            limit=page_size,
            offset=offset
        )
        
        # 获取文档总数
        total_docs = len(knowledge_service._documents.get(knowledge_base_id, []))
        
        # 计算总页数
        total_pages = (total_docs + page_size - 1) // page_size if total_docs > 0 else 1
        
        logger.info(f"获取知识库文档列表 - 知识库: {knowledge_base_id}, 数量: {len(documents)}")
        
        return SuccessResponse(
            success=True,
            message="获取文档列表成功",
            data={
                "items": [doc.dict() for doc in documents],
                "total": total_docs,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识库文档列表异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档列表时发生错误: {str(e)}"
        )

@router.post(
    "/{knowledge_base_id}/search",
    response_model=SuccessResponse,
    summary="搜索知识库",
    description="在指定知识库中搜索相关内容"
)
async def search_knowledge_base(
    knowledge_base_id: str,
    query: KnowledgeQuery,
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    搜索知识库端点
    
    Args:
        knowledge_base_id: 知识库ID
        query: 搜索查询
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含搜索结果
    """
    
    try:
        # 检查知识库是否存在
        existing_kb = knowledge_service.get_knowledge_base(knowledge_base_id)
        
        if not existing_kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在: {knowledge_base_id}"
            )
        
        # 检查权限
        if not existing_kb.is_public and existing_kb.created_by != current_user.user_id:
            logger.warning(f"权限拒绝 - 用户: {current_user.user_id} 尝试搜索知识库: {knowledge_base_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权搜索此知识库"
            )
        
        # 执行搜索
        search_results = rag_service.retrieve(
            query=query.query,
            knowledge_base_id=knowledge_base_id,
            top_k=query.top_k,
            score_threshold=query.score_threshold
        )
        
        logger.info(f"搜索知识库 - 知识库: {knowledge_base_id}, 查询: '{query.query[:50]}...', 结果数: {len(search_results)}")
        
        return SuccessResponse(
            success=True,
            message="搜索成功",
            data={
                "query": query.query,
                "knowledge_base_id": knowledge_base_id,
                "results": search_results,
                "total": len(search_results)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索知识库异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索知识库时发生错误: {str(e)}"
        )

@router.post(
    "/{knowledge_base_id}/query",
    response_model=SuccessResponse,
    summary="查询知识库",
    description="使用RAG查询知识库并获取回答"
)
async def query_knowledge_base(
    knowledge_base_id: str,
    query: KnowledgeQuery,
    current_user: UserContext = Depends(get_current_user)
) -> SuccessResponse:
    """
    查询知识库端点
    
    Args:
        knowledge_base_id: 知识库ID
        query: 查询内容
        current_user: 当前用户上下文
        
    Returns:
        SuccessResponse: 成功响应，包含查询结果
    """
    
    try:
        # 检查知识库是否存在
        existing_kb = knowledge_service.get_knowledge_base(knowledge_base_id)
        
        if not existing_kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库不存在: {knowledge_base_id}"
            )
        
        # 检查权限
        if not existing_kb.is_public and existing_kb.created_by != current_user.user_id:
            logger.warning(f"权限拒绝 - 用户: {current_user.user_id} 尝试查询知识库: {knowledge_base_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查询此知识库"
            )
        
        # 使用RAG查询
        result = rag_service.answer_with_rag(
            query=query.query,
            knowledge_base_id=knowledge_base_id,
            top_k=query.top_k
        )
        
        logger.info(f"查询知识库 - 知识库: {knowledge_base_id}, 查询: '{query.query[:50]}...'")
        
        return SuccessResponse(
            success=result['success'],
            message="查询完成",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询知识库异常: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询知识库时发生错误: {str(e)}"
        )

# 导出路由器
__all__ = ["router"]
```

#### 9. 更新路由聚合器
**文件：`app/api/router.py`**

```python
"""
API路由聚合
将所有API路由集中注册到FastAPI应用
"""

from fastapi import APIRouter

# 导入所有端点路由
from app.api.v1.endpoints import (
    health,
    chat,
    employees,
    marketplace,
    knowledge  # 新增
)

# 创建API v1路由器
api_v1_router = APIRouter(prefix="/api/v1")

# 注册健康检查路由
api_v1_router.include_router(health.router, prefix="/health", tags=["health"])

# 注册聊天路由
api_v1_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# 注册员工管理路由
api_v1_router.include_router(employees.router, tags=["employees"])

# 注册市场广场路由
api_v1_router.include_router(marketplace.router, tags=["marketplace"])

# 注册知识库管理路由（新增）
api_v1_router.include_router(knowledge.router, tags=["knowledge-bases"])

# 创建主路由器
router = APIRouter()

# 包含API v1路由器
router.include_router(api_v1_router)

# 导出路由器
__all__ = ["router"]
```

### 🎯 第六阶段：集成测试与前端对接（1-2天）

#### 10. 创建知识库测试脚本
**文件：`test_knowledge_system.py`**

```python
"""
知识库系统测试脚本
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_knowledge_base_crud():
    """测试知识库CRUD操作"""
    print("=== 测试知识库CRUD ===")
    
    headers = {
        "X-Employee-ID": "test_emp",
        "X-User-ID": "test_user"
    }
    
    # 1. 创建知识库
    print("1. 创建知识库:")
    kb_data = {
        "name": "测试知识库",
        "description": "用于测试的知识库",
        "tags": ["测试", "文档"],
        "is_public": True,
        "category": "测试分类"
    }
    
    response = requests.post(f"{BASE_URL}/knowledge-bases", json=kb_data, headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        kb_info = result.get('data', {})
        kb_id = kb_info.get('id')
        print(f"   成功创建知识库: {kb_info.get('name')} (ID: {kb_id})")
    else:
        print(f"   失败: {response.text}")
        return None
    
    # 2. 获取知识库列表
    print("\n2. 获取知识库列表:")
    response = requests.get(f"{BASE_URL}/knowledge-bases", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        items = result.get('data', {}).get('items', [])
        print(f"   知识库数量: {len(items)}")
    
    # 3. 获取知识库详情
    print(f"\n3. 获取知识库详情 (ID: {kb_id}):")
    response = requests.get(f"{BASE_URL}/knowledge-bases/{kb_id}", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        kb_detail = result.get('data', {})
        print(f"   知识库: {kb_detail.get('name')}")
        print(f"   描述: {kb_detail.get('description')}")
        print(f"   文档数量: {kb_detail.get('doc_count')}")
    
    # 4. 搜索知识库（无文档时）
    print(f"\n4. 搜索知识库 (ID: {kb_id}):")
    search_data = {
        "query": "测试查询",
        "knowledge_base_id": kb_id,
        "top_k": 5,
        "score_threshold": 0.5
    }
    
    response = requests.post(f"{BASE_URL}/knowledge-bases/{kb_id}/search", json=search_data, headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        search_results = result.get('data', {}).get('results', [])
        print(f"   搜索结果数量: {len(search_results)}")
    
    # 5. 更新知识库
    print(f"\n5. 更新知识库 (ID: {kb_id}):")
    update_data = {
        "description": "更新后的描述",
        "tags": ["测试", "文档", "更新"]
    }
    
    response = requests.put(f"{BASE_URL}/knowledge-bases/{kb_id}", json=update_data, headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   更新成功: {result.get('message')}")
    
    return kb_id

def test_document_processing(kb_id: str):
    """测试文档处理"""
    print(f"\n=== 测试文档处理 (知识库: {kb_id}) ===")
    
    headers = {
        "X-Employee-ID": "test_emp",
        "X-User-ID": "test_user"
    }
    
    # 创建测试文本文件
    import tempfile
    import os
    
    test_content = """这是一份测试文档。

包含多个段落和内容。

测试文档的内容可以用于验证文档处理功能。

包括文本解析、分割和向量化等功能。

这是最后一段内容。"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        temp_file_path = f.name
    
    try:
        # 上传文档
        print("1. 上传文档:")
        with open(temp_file_path, 'rb') as file:
            files = {'file': ('test.txt', file, 'text/plain')}
            data = {'chunk_size': 500, 'chunk_overlap': 100}
            
            response = requests.post(
                f"{BASE_URL}/knowledge-bases/{kb_id}/upload",
                files=files,
                data=data,
                headers=headers
            )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   上传成功: {result.get('message')}")
            
            # 等待向量化处理
            print("   等待向量化处理...")
            time.sleep(3)
        else:
            print(f"   失败: {response.text}")
            return
    
    finally:
        # 清理临时文件
        os.unlink(temp_file_path)
    
    # 获取文档列表
    print("\n2. 获取文档列表:")
    response = requests.get(f"{BASE_URL}/knowledge-bases/{kb_id}/documents", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        items = result.get('data', {}).get('items', [])
        print(f"   文档数量: {len(items)}")
        
        for i, doc in enumerate(items[:2]):
            print(f"   文档{i+1}: {doc.get('content', '')[:50]}...")
    
    # 搜索文档
    print("\n3. 搜索文档:")
    search_data = {
        "query": "测试文档",
        "knowledge_base_id": kb_id,
        "top_k": 3,
        "score_threshold": 0.5
    }
    
    response = requests.post(f"{BASE_URL}/knowledge-bases/{kb_id}/search", json=search_data, headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        search_results = result.get('data', {}).get('results', [])
        print(f"   搜索结果数量: {len(search_results)}")
        
        for i, result in enumerate(search_results):
            print(f"   结果{i+1}: 分数={result.get('score', 0):.3f}, 内容={result.get('content', '')[:50]}...")
    
    # RAG查询
    print("\n4. RAG查询:")
    query_data = {
        "query": "文档包含什么内容？",
        "knowledge_base_id": kb_id,
        "top_k": 3,
        "score_threshold": 0.5
    }
    
    response = requests.post(f"{BASE_URL}/knowledge-bases/{kb_id}/query", json=query_data, headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        data = result.get('data', {})
        print(f"   查询成功: {data.get('success')}")
        print(f"   检索结果数: {data.get('result_count')}")

def test_system_integration():
    """测试系统集成"""
    print("\n=== 测试系统集成 ===")
    
    headers = {
        "X-Employee-ID": "test_emp",
        "X-User-ID": "test_user"
    }
    
    # 测试健康检查
    print("1. 系统健康检查:")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   系统状态: {result.get('status')}")
    
    # 测试各模块
    modules = [
        ("健康检查", "/health"),
        ("聊天", "/chat"),
        ("员工", "/employees"),
        ("市场", "/marketplace/employees"),
        ("知识库", "/knowledge-bases")
    ]
    
    print("\n2. 各模块状态:")
    for name, endpoint in modules:
        try:
            if endpoint == "/chat":
                # 聊天需要POST请求
                chat_data = {
                    "chat_request": {
                        "message": "测试",
                        "employee_id": "mock_emp_001",
                        "conversation_id": None
                    }
                }
                response = requests.post(f"{BASE_URL}{endpoint}", json=chat_data, headers=headers)
            else:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {name}: {response.status_code}")
            
        except Exception as e:
            print(f"   ❌ {name}: 连接失败 - {e}")

def main():
    """主测试函数"""
    print("开始知识库系统测试...")
    print("=" * 60)
    
    # 测试系统集成
    test_system_integration()
    
    # 测试知识库CRUD
    kb_id = test_knowledge_base_crud()
    
    if kb_id:
        # 测试文档处理
        test_document_processing(kb_id)
    
    print("\n" + "=" * 60)
    print("测试完成！")

if __name__ == "__main__":
    main()
```

## 📊 开发计划时间表

| 阶段 | 天数 | 主要内容 | 交付物 |
|------|------|----------|--------|
| **第一阶段** | 1-2天 | 数据模型与基础服务 | 1. 完善的Pydantic模型<br>2. 知识库基础服务 |
| **第二阶段** | 2-3天 | 文档处理服务 | 1. 文档解析器<br>2. 文本分割器 |
| **第三阶段** | 2-3天 | 向量化与存储 | 1. 嵌入服务<br>2. 向量存储(ChromaDB) |
| **第四阶段** | 2-3天 | RAG服务与API | 1. RAG检索服务<br>2. API端点 |
| **第五阶段** | 1-2天 | 前端对接与测试 | 1. 前端API服务层<br>2. 完整测试套件 |

**总计：8-13个工作日**

## 🚀 立即行动步骤

### 1. **安装依赖**
```bash
cd backend-python-ai
pip install -r requirements.txt

# 安装知识库相关依赖
pip install pypdf2 python-docx sentence-transformers chromadb
```

### 2. **创建目录结构**
```bash
mkdir -p app/services/processing
mkdir -p data/uploads
mkdir -p data/vector_db
```

### 3. **按顺序实现**
按照我提供的代码顺序，依次创建文件：

1. 更新 `app/models/schemas.py`
2. 创建 `app/services/knowledge_service.py`
3. 创建 `app/services/processing/document_parser.py`
4. 创建 `app/services/processing/text_splitter.py`
5. 创建 `app/services/processing/embedding_service.py`
6. 创建 `app/services/processing/vector_store.py`
7. 创建 `app/services/ai/rag_service.py`
8. 创建 `app/api/v1/endpoints/knowledge.py`
9. 更新 `app/api/router.py`
10. 创建 `test_knowledge_system.py`

### 4. **测试与验证**
```bash
# 启动后端服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 在另一个终端运行测试
python test_knowledge_system.py
```

## 🔧 注意事项

### 1. **依赖管理**
- **PyPDF2**：用于PDF解析
- **python-docx**：用于Word文档解析
- **sentence-transformers**：用于文本向量化
- **chromadb**：向量数据库

### 2. **资源管理**
- 大文件处理需要异步任务
- 向量化过程可能消耗较多内存
- 建议添加进度追踪和错误处理

### 3. **性能优化**
- 批量处理文档
- 缓存嵌入结果
- 异步文件上传和处理

### 4. **错误处理**
- 文件格式验证
- 网络异常处理
- 内存溢出保护

## 📈 预期成果

完成知识库服务开发后，你将拥有：

✅ **完整的文档处理流程**：上传 → 解析 → 分割 → 向量化 → 存储  
✅ **智能检索能力**：基于向量相似度的语义搜索  
✅ **RAG问答系统**：基于知识库的智能问答  
✅ **RESTful API**：完整的CRUD操作和搜索接口  
✅ **前端对接支持**：为前端提供完整的知识库管理界面