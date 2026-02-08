/**
 * 知识库核心类型定义 - 所有模块共享
 */

export interface KnowledgeBase {
    id: string;
    name: string;
    description?: string;
    docCount: number;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    status: 'active' | 'inactive' | 'processing';
    tags?: string[];
    isPublic?: boolean;
    vectorized?: boolean;
  }
  
  // AI组件使用的简化知识库项（来自Gemini）
  export interface KnowledgeBaseItem {
    id: string;
    name: string;
    docCount: number;
  }
  
  export interface KnowledgeItem {
    id: string;
    knowledgeBaseId: string;
    serialNo: number;
    content: string;
    wordCount: number;
    createTime: string;
    sourceFile?: string;
    embeddings?: number[];
    metadata?: {
      section?: string;
      page?: number;
      confidence?: number;
      [key: string]: any; // 允许扩展字段
    };
  }
  
  export interface FileUploadConfig {
    fileType: 'text' | 'table' | 'pdf' | 'markdown';
    knowledgeLength: number;
    overlapLength: number;
    lineBreakSegment: boolean;
    maxSegmentLength: number;
    updateTime: string;
  }
  
  export interface ParsedFileResult {
    fileId: string;
    fileName: string;
    fileSize: number;
    fileType: string;
    knowledgeList: KnowledgeItem[];
    parseStatus: 'pending' | 'processing' | 'completed' | 'failed';
    error?: string;
  }
  
  export interface UploadedFile {
    id: string;
    name: string;
    size: number;
    type: string;
    uploadTime: string;
    knowledgeBaseId: string;
    status: 'uploading' | 'uploaded' | 'parsing' | 'completed' | 'failed';
    progress?: number;
  }
  
  /**
   * 数据规范化函数
   */
  export const normalizeKnowledgeBase = (data: any): KnowledgeBase => ({
    id: data?.id || `kb-${Date.now()}`,
    name: data?.name || '未命名知识库',
    description: data?.description || '',
    docCount: data?.doc_count || data?.docCount || 0,
    createdAt: data?.created_at || data?.createdAt || new Date().toISOString(),
    updatedAt: data?.updated_at || data?.updatedAt || new Date().toISOString(),
    createdBy: data?.created_by || data?.createdBy || 'system',
    status: data?.status || 'active',
    tags: Array.isArray(data?.tags) ? data.tags : [],
    isPublic: data?.is_public ?? data?.isPublic ?? true,
    vectorized: data?.vectorized ?? false,
  });
  
  export const normalizeKnowledgeItem = (data: any): KnowledgeItem => ({
    id: data?.id || `ki-${Date.now()}`,
    knowledgeBaseId: data?.knowledgeBaseId || '',
    serialNo: typeof data?.serialNo === 'number' ? data.serialNo : 1,
    content: data?.content || '',
    wordCount: typeof data?.wordCount === 'number' ? data.wordCount : 0,
    createTime: data?.createTime || new Date().toISOString(),
    sourceFile: data?.sourceFile,
    embeddings: data?.embeddings,
    metadata: data?.metadata || {},
  });
  
  /**
   * 将完整的KnowledgeBase转换为简化的KnowledgeBaseItem（供AI组件使用）
   */
  export const toKnowledgeBaseItem = (kb: KnowledgeBase): KnowledgeBaseItem => ({
    id: kb.id,
    name: kb.name,
    docCount: kb.docCount,
  });
  
  /**
   * 批量转换知识库
   */
  export const toKnowledgeBaseItemList = (kbs: KnowledgeBase[]): KnowledgeBaseItem[] => {
    return kbs.map(toKnowledgeBaseItem);
  };