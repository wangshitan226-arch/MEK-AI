import { create } from 'zustand';
import { CreatedEmployee } from '@/shared/types/digitalEmployee';
import { DigitalEmployeeEditorStore } from '../../types';
import {
  saveDigitalEmployee as apiSaveDigitalEmployee,
  publishDigitalEmployee as apiPublishDigitalEmployee,
  generatePreviewResponse as apiGeneratePreviewResponse,
} from '../services/digitalEmployeeApi';

// 默认提示词模板
const DEFAULT_PROMPT_TEMPLATE = `你是一个专业的AI助手。请根据用户的问题提供有帮助、准确且专业的回答。

在回答时，请遵循以下原则：
1. 保持礼貌和专业
2. 提供准确的信息
3. 如果不确定，请诚实地说明
4. 尽量简洁明了，但确保信息完整`;

// 初始表单数据
const initialFormData: Partial<CreatedEmployee> = {
  name: '',
  description: '',
  avatar: '',
  industry: '',
  role: '',
  prompt: DEFAULT_PROMPT_TEMPLATE,
  model: 'gemini-2.5-pro-preview',
  knowledgeBaseIds: [],
  status: 'draft',
};

// 初始化状态
const initialState = {
  editingEmployee: null,
  isCreateModalOpen: false,
  isEditorOpen: false,
  formData: initialFormData,
  activeEditorTab: 'persona' as const,
  previewMessages: [],
  chatInput: '',
  saving: false,
  publishing: false,
};

// 创建编辑器store
export const useDigitalEmployeeEditorStore = create<DigitalEmployeeEditorStore>((set, get) => ({
  ...initialState,

  // 打开创建弹窗
  openCreateModal: () => {
    set({ isCreateModalOpen: true });
  },

  // 关闭创建弹窗
  closeCreateModal: () => {
    set({ isCreateModalOpen: false });
  },

  // 打开编辑器
  openEditor: (employee?: CreatedEmployee) => {
    if (employee) {
      set({
        isEditorOpen: true,
        editingEmployee: employee,
        formData: { ...initialFormData, ...employee },
        previewMessages: [
          {
            role: 'model',
            content: `你好，我是${employee.name}。${employee.description} 我已准备好为您服务。`,
          },
        ],
      });
    } else {
      set({
        isEditorOpen: true,
        editingEmployee: null,
        formData: initialFormData,
        previewMessages: [],
      });
    }
  },
  // 打开编辑器用于新创建
  openEditorForCreate: (initialData: { id: string; industry: string; role: string }) => {
    set({
      isEditorOpen: true,
      editingEmployee: null, // 未保存前没有editingEmployee
      formData: {
        ...initialFormData,
        id: initialData.id,
        industry: initialData.industry,
        role: initialData.role,
        name: '', // 名称为空，让用户填写
        description: '', // 介绍为空
      },
      previewMessages: [], // 初始无消息
      isCreateModalOpen: false, // 确保弹窗关闭
    });
  },

  // 设置 editingEmployee（保存后调用）
  setEditingEmployee: (employee: CreatedEmployee) => {
    set({ editingEmployee: employee });
  },
  // 关闭编辑器
  closeEditor: () => {
    set({
      isEditorOpen: false,
      editingEmployee: null,
      formData: initialFormData,
      previewMessages: [],
      chatInput: '',
    });
  },

  // 设置表单数据
  setFormData: (data) => {
    set({ formData: { ...get().formData, ...data } });
  },

  // 更新表单字段
  updateFormField: (field, value) => {
    set((state) => ({
      formData: { ...state.formData, [field]: value },
    }));
  },

  // 设置编辑器Tab
  setActiveEditorTab: (tab) => {
    set({ activeEditorTab: tab });
  },

  // 设置预览消息
  setPreviewMessages: (messages) => {
    set({ previewMessages: messages });
  },

  // 设置聊天输入
  setChatInput: (input) => {
    set({ chatInput: input });
  },

  // 发送预览消息
  sendPreviewMessage: async (content) => {
    const { formData, previewMessages } = get();

    // 添加用户消息
    const userMessage = { role: 'user' as const, content };
    const updatedMessages = [...previewMessages, userMessage];
    set({ previewMessages: updatedMessages, chatInput: '' });

    // 生成AI响应
    try {
      const response = await apiGeneratePreviewResponse(
        formData.id || '',
        content
      );

      const aiMessage = { role: 'model' as const, content: response };
      set({ previewMessages: [...updatedMessages, aiMessage] });
    } catch (error) {
      console.error('生成预览响应失败:', error);
      const errorMessage = { role: 'model' as const, content: '抱歉，预览功能暂时不可用。' };
      set({ previewMessages: [...updatedMessages, errorMessage] });
    }
  },

  // 保存草稿
  saveDraft: async () => {
    const { formData } = get();
    set({ saving: true });

    try {
      const savedEmployee = await apiSaveDigitalEmployee(
        formData as CreatedEmployee
      );

      // 更新预览消息
      set({
        saving: false,
        editingEmployee: savedEmployee,
        previewMessages: [
          {
            role: 'model',
            content: `配置已保存！我是${savedEmployee.name}，${savedEmployee.description} 现在可以开始测试对话了。`,
          },
        ],
      });

      return savedEmployee;
    } catch (error) {
      set({ saving: false });
      throw error;
    }
  },

  // 发布员工
  publishEmployee: async () => {
    const { editingEmployee } = get();
    set({ publishing: true });

    try {
      if (!editingEmployee) {
        throw new Error('没有可发布的员工');
      }

      const publishedEmployee = await apiPublishDigitalEmployee(
        editingEmployee.id
      );

      set({ publishing: false });
      return publishedEmployee;
    } catch (error) {
      set({ publishing: false });
      throw error;
    }
  },

  // 重置编辑器
  resetEditor: () => {
    set(initialState);
  },

  // 设置保存状态
  setSaving: (saving) => {
    set({ saving });
  },

  // 设置发布状态
  setPublishing: (publishing) => {
    set({ publishing });
  },
}));