import { IKnowledgeBaseService } from '../../types';
import { knowledgeBaseApi } from './knowledgeBaseApi';

/**
 * 知识库服务层 - 统一API接口
 * 已切换到真实后端API
 */
export const knowledgeBaseService: IKnowledgeBaseService = {
  // ========== 知识库管理 ==========
  getKnowledgeBases: async () => {
    return knowledgeBaseApi.getKnowledgeBases();
  },

  createKnowledgeBase: async (data) => {
    return knowledgeBaseApi.createKnowledgeBase(data);
  },

  updateKnowledgeBase: async (id, data) => {
    return knowledgeBaseApi.updateKnowledgeBase(id, data);
  },

  deleteKnowledgeBase: async (id) => {
    return knowledgeBaseApi.deleteKnowledgeBase(id);
  },

  // ========== 文档管理 ==========
  getDocuments: async (kbId) => {
    return knowledgeBaseApi.getDocuments(kbId);
  },

  uploadDocument: async (kbId, file, config) => {
    return knowledgeBaseApi.uploadDocument(kbId, file, config);
  },

  parseDocument: async (fileId, config) => {
    // 后端上传和解析是一体的，这里模拟解析结果
    // 实际项目中，如果需要单独解析，可以调用后端解析接口
    console.warn('parseDocument 已集成到 uploadDocument，此处返回空结果');
    return {
      knowledgeList: [],
    };
  },

  saveParsedKnowledge: async (kbId, knowledgeList) => {
    return knowledgeBaseApi.saveParsedKnowledge(kbId, knowledgeList);
  },

  deleteKnowledgeItem: async (kbId, itemId) => {
    return knowledgeBaseApi.deleteKnowledgeItem(kbId, itemId);
  },

  clearKnowledgeItems: async (kbId) => {
    return knowledgeBaseApi.clearKnowledgeItems(kbId);
  },

  // ========== 配置管理 ==========
  getDefaultConfig: async () => {
    return knowledgeBaseApi.getDefaultConfig();
  },

  saveConfig: async (config) => {
    return knowledgeBaseApi.saveConfig(config);
  },
};
