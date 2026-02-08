/**
 * 知识库真实 API 服务
 * 对接后端 Python 服务
 */

import { apiClient } from '@/core/services/apiClient';
import { API_ENDPOINTS } from '@/core/config/api';
import {
  KnowledgeBase,
  KnowledgeItem,
  FileUploadConfig,
  normalizeKnowledgeBase,
  normalizeKnowledgeItem,
} from '@/shared/types/knowledge';
import { transformKnowledgeBasesFromApi, transformKnowledgeBaseFromApi } from '@/shared/utils/transform';

// API 响应格式
interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

// 后端返回的知识库格式（snake_case）
interface BackendKnowledgeBase {
  id: string;
  name: string;
  description?: string;
  doc_count: number;
  created_at: string;
  updated_at: string;
  created_by: string;
  status: 'active' | 'inactive' | 'processing';
  tags?: string[];
  is_public?: boolean;
  vectorized?: boolean;
}

// 后端返回的知识点格式（snake_case）
interface BackendKnowledgeItem {
  id: string;
  knowledge_base_id: string;
  serial_no: number;
  content: string;
  word_count: number;
  create_time: string;
  source_file?: string;
  embeddings?: number[];
  metadata?: Record<string, any>;
}

// 转换后端知识库为前端格式
const transformKnowledgeBase = (kb: BackendKnowledgeBase): KnowledgeBase => ({
  id: kb.id,
  name: kb.name,
  description: kb.description || '',
  docCount: kb.doc_count || 0,
  createdAt: kb.created_at,
  updatedAt: kb.updated_at,
  createdBy: kb.created_by || 'system',
  status: kb.status || 'active',
  tags: kb.tags || [],
  isPublic: kb.is_public ?? true,
  vectorized: kb.vectorized ?? false,
});

// 转换后端知识点为前端格式
const transformKnowledgeItem = (item: BackendKnowledgeItem): KnowledgeItem => ({
  id: item.id,
  knowledgeBaseId: item.knowledge_base_id,
  serialNo: item.serial_no,
  content: item.content,
  wordCount: item.word_count || 0,
  createTime: item.create_time,
  sourceFile: item.source_file,
  embeddings: item.embeddings,
  metadata: item.metadata || {},
});

/**
 * 知识库真实 API 服务
 */
export const knowledgeBaseApi = {
  // ========== 知识库管理 ==========

  /**
   * 获取知识库列表
   */
  getKnowledgeBases: async (): Promise<KnowledgeBase[]> => {
    const response = await apiClient.get<ApiResponse<{ items: any[] }>>(
      API_ENDPOINTS.KNOWLEDGE_BASE.LIST,
      { skipTransform: true }
    );

    if (!response.success || !response.data) {
      throw new Error(response.message || '获取知识库列表失败');
    }

    // 使用专门的转换函数确保 docCount 正确
    return transformKnowledgeBasesFromApi(response.data.items);
  },

  /**
   * 创建知识库
   */
  createKnowledgeBase: async (data: {
    name: string;
    description?: string;
    isPublic?: boolean;
    tags?: string[];
  }): Promise<KnowledgeBase> => {
    const response = await apiClient.post<ApiResponse<BackendKnowledgeBase>>(
      API_ENDPOINTS.KNOWLEDGE_BASE.CREATE,
      {
        kb_data: {
          name: data.name,
          description: data.description,
          is_public: data.isPublic ?? true,
          tags: data.tags || [],
        },
      }
    );

    if (!response.success || !response.data) {
      throw new Error(response.message || '创建知识库失败');
    }

    return transformKnowledgeBase(response.data);
  },

  /**
   * 更新知识库
   */
  updateKnowledgeBase: async (
    id: string,
    updates: Partial<KnowledgeBase>
  ): Promise<KnowledgeBase> => {
    const response = await apiClient.put<ApiResponse<BackendKnowledgeBase>>(
      API_ENDPOINTS.KNOWLEDGE_BASE.UPDATE(id),
      {
        update_data: {
          name: updates.name,
          description: updates.description,
          is_public: updates.isPublic,
          tags: updates.tags,
        },
      }
    );

    if (!response.success || !response.data) {
      throw new Error(response.message || '更新知识库失败');
    }

    return transformKnowledgeBase(response.data);
  },

  /**
   * 删除知识库
   */
  deleteKnowledgeBase: async (id: string): Promise<boolean> => {
    const response = await apiClient.delete<ApiResponse<{ knowledge_base_id: string }>>(
      API_ENDPOINTS.KNOWLEDGE_BASE.DELETE(id)
    );

    if (!response.success) {
      throw new Error(response.message || '删除知识库失败');
    }

    return true;
  },

  // ========== 文档管理 ==========

  /**
   * 获取知识库的文档列表
   */
  getDocuments: async (kbId: string, limit: number = 1000): Promise<KnowledgeItem[]> => {
    const response = await apiClient.get<ApiResponse<{ items: BackendKnowledgeItem[] }>>(
      `${API_ENDPOINTS.KNOWLEDGE_BASE.DOCUMENTS(kbId)}?page_size=${limit}`
    );

    if (!response.success || !response.data) {
      throw new Error(response.message || '获取文档列表失败');
    }

    return response.data.items.map(transformKnowledgeItem);
  },

  /**
   * 上传文档
   */
  uploadDocument: async (
    kbId: string,
    file: File,
    config?: { chunkSize?: number; chunkOverlap?: number },
    onProgress?: (progress: number) => void
  ): Promise<{ fileId: string; fileUrl?: string; chunksProcessed: number; chunks: any[] }> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('chunk_size', String(config?.chunkSize || 1000));
    formData.append('chunk_overlap', String(config?.chunkOverlap || 200));

    // 使用原生 fetch 以便获取上传进度
    const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}${API_ENDPOINTS.KNOWLEDGE_BASE.UPLOAD(kbId)}`;

    const userId = localStorage.getItem('userId') || 'anonymous';
    const employeeId = localStorage.getItem('currentEmployeeId') || 'default-employee';

    const headers: Record<string, string> = {
      'X-User-ID': userId,
      'X-Employee-ID': employeeId,
    };

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const progress = Math.round((event.loaded * 100) / event.total);
          onProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          const response = JSON.parse(xhr.responseText);
          if (response.success) {
            resolve({
              fileId: response.data.file_id || `file-${Date.now()}`,
              fileUrl: response.data.file_url,
              chunksProcessed: response.data.chunks_processed || 0,
              chunks: response.data.chunks || [],
            });
          } else {
            reject(new Error(response.message || '上传失败'));
          }
        } else {
          reject(new Error(`上传失败: ${xhr.statusText}`));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('上传失败'));
      });

      xhr.open('POST', url);
      Object.entries(headers).forEach(([key, value]) => {
        xhr.setRequestHeader(key, value);
      });
      xhr.send(formData);
    });
  },

  /**
   * 保存解析后的知识点
   */
  saveParsedKnowledge: async (
    kbId: string,
    knowledgeList: KnowledgeItem[]
  ): Promise<boolean> => {
    const response = await apiClient.post<ApiResponse<{ saved_count: number }>>(
      `${API_ENDPOINTS.KNOWLEDGE_BASE.DETAIL(kbId)}/knowledge`,
      {
        items: knowledgeList.map((item) => ({
          content: item.content,
          serial_no: item.serialNo,
          source_file: item.sourceFile,
          metadata: item.metadata,
        })),
      }
    );

    if (!response.success) {
      throw new Error(response.message || '保存知识点失败');
    }

    return true;
  },

  /**
   * 删除单个知识点
   */
  deleteKnowledgeItem: async (kbId: string, itemId: string): Promise<boolean> => {
    const response = await apiClient.delete<ApiResponse<{ deleted: boolean }>>(
      `${API_ENDPOINTS.KNOWLEDGE_BASE.DETAIL(kbId)}/knowledge/${itemId}`
    );

    if (!response.success) {
      throw new Error(response.message || '删除知识点失败');
    }

    return true;
  },

  /**
   * 清空知识库所有知识点
   */
  clearKnowledgeItems: async (kbId: string): Promise<boolean> => {
    const response = await apiClient.delete<ApiResponse<{ cleared: boolean }>>(
      `${API_ENDPOINTS.KNOWLEDGE_BASE.DETAIL(kbId)}/knowledge`
    );

    if (!response.success) {
      throw new Error(response.message || '清空知识库失败');
    }

    return true;
  },

  // ========== 配置管理 ==========

  /**
   * 获取默认配置
   */
  getDefaultConfig: async (): Promise<FileUploadConfig> => {
    const response = await apiClient.get<ApiResponse<{
      knowledge_length: number;
      overlap_length: number;
      line_break_segment: boolean;
      max_segment_length: number;
      update_time: string;
    }>>(`${API_ENDPOINTS.KNOWLEDGE_BASE.CONFIG}/document-processing`);

    if (!response.success || !response.data) {
      throw new Error(response.message || '获取配置失败');
    }

    return {
      fileType: 'text',
      knowledgeLength: response.data.knowledge_length || 2000,
      overlapLength: response.data.overlap_length || 30,
      lineBreakSegment: response.data.line_break_segment ?? true,
      maxSegmentLength: response.data.max_segment_length || 500,
      updateTime: response.data.update_time || new Date().toISOString(),
    };
  },

  /**
   * 保存配置
   */
  saveConfig: async (config: FileUploadConfig): Promise<FileUploadConfig> => {
    // 后端可能不支持保存配置，这里先返回本地配置
    console.warn('保存配置功能暂未实现');
    return config;
  },
};

export default knowledgeBaseApi;
