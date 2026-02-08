import { create } from 'zustand';
import { KnowledgeBaseStore } from '../../types';
import { knowledgeBaseService } from '../services/knowledgeBaseService';
import { normalizeKnowledgeBase } from '@/shared/types/knowledge';

// 初始化状态
const initialState = {
  knowledgeBases: [],
  currentKBId: null,
  loading: false,
  error: null,
};

// 创建数据状态store
export const useKnowledgeBaseStore = create<KnowledgeBaseStore>((set, get) => ({
  ...initialState,

  // 加载知识库列表
  loadKnowledgeBases: async () => {
    set({ loading: true, error: null });
    try {
      const data = await knowledgeBaseService.getKnowledgeBases();
      set({ knowledgeBases: data, loading: false });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '加载知识库失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },

  // 创建知识库
  createKnowledgeBase: async (name: string, description?: string) => {
    set({ loading: true, error: null });
    try {
      const newKB = await knowledgeBaseService.createKnowledgeBase({ name, description });
      set((state) => ({
        knowledgeBases: [newKB, ...state.knowledgeBases],
        loading: false,
      }));
      return newKB;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '创建知识库失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },

  // 更新知识库
  updateKnowledgeBase: async (id: string, updates: any) => {
    set({ loading: true, error: null });
    try {
      const updatedKB = await knowledgeBaseService.updateKnowledgeBase(id, updates);
      set((state) => ({
        knowledgeBases: state.knowledgeBases.map(kb =>
          kb.id === id ? normalizeKnowledgeBase(updatedKB) : kb
        ),
        loading: false,
      }));
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '更新知识库失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },

  // 删除知识库
  deleteKnowledgeBase: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const success = await knowledgeBaseService.deleteKnowledgeBase(id);
      if (success) {
        set((state) => ({
          knowledgeBases: state.knowledgeBases.filter(kb => kb.id !== id),
          loading: false,
          // 如果删除的是当前选中的知识库，清除当前选择
          currentKBId: get().currentKBId === id ? null : get().currentKBId,
        }));
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '删除知识库失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },

  // 设置当前选中的知识库ID
  setCurrentKBId: (id: string | null) => {
    set({ currentKBId: id });
  },

  // 添加文档到知识库
  addDocumentToKB: async (kbId: string, fileData: any) => {
    set({ loading: true, error: null });
    try {
      // 这里简化处理，实际应该调用uploadDocument和parseDocument
      // 为了简化，直接返回一个成功的Promise
      return Promise.resolve({
        fileId: `file-${Date.now()}`,
        fileName: fileData.name || '未知文件',
        fileSize: fileData.size || 0,
        fileType: fileData.type || 'text/plain',
        knowledgeList: [],
        parseStatus: 'completed' as const,
      });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '添加文档失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },

  // 获取知识库的文档列表
  getDocumentsByKB: async (kbId: string) => {
    set({ loading: true, error: null });
    try {
      return await knowledgeBaseService.getDocuments(kbId);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '获取文档列表失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },

  // 删除文档
  deleteDocument: async (kbId: string, docId: string) => {
    set({ loading: true, error: null });
    try {
      // 实际应该调用后端API
      // await knowledgeBaseService.deleteDocument(kbId, docId);
      
      // 更新本地状态
      set((state) => ({
        knowledgeBases: state.knowledgeBases.map(kb => 
          kb.id === kbId ? { ...kb, docCount: Math.max(0, kb.docCount - 1) } : kb
        ),
        loading: false,
      }));
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '删除文档失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },
}));

// 创建选择器hooks（提高性能）
export const useCurrentKnowledgeBase = () => {
  return useKnowledgeBaseStore((state) =>
    state.knowledgeBases.find(kb => kb.id === state.currentKBId)
  );
};

export const useKnowledgeBaseById = (id: string) => {
  return useKnowledgeBaseStore((state) =>
    state.knowledgeBases.find(kb => kb.id === id)
  );
};

export const useKnowledgeBasesCount = () => {
  return useKnowledgeBaseStore((state) => state.knowledgeBases.length);
};