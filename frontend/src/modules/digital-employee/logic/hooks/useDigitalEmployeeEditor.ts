import { useEffect } from 'react';
import { useNavigate, useParams,useLocation } from 'react-router-dom';
import { useDigitalEmployeeStore } from '../stores/digitalEmployeeStore';
import { useDigitalEmployeeEditorStore } from '../stores/digitalEmployeeEditorStore';
import { useKnowledgeBase } from '@/modules/knowledge-base/logic/hooks/useKnowledgeBase';
import { CreatedEmployee } from '@/shared/types/digitalEmployee';

export const useDigitalEmployeeEditor = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  
  const store = useDigitalEmployeeStore();
  const editorStore = useDigitalEmployeeEditorStore();
  const knowledgeBase = useKnowledgeBase();

  // 加载编辑员工数据
const location = useLocation();

useEffect(() => {
  if (id) {
    // 如果是新创建（从弹窗跳转来的）
    if (location.state?.isNew) {
      // 打开空编辑器，使用弹窗传入的数据
      editorStore.setFormData({
        id,
        industry: location.state.industry || '',
        role: location.state.role || '',
      });
      editorStore.openEditor();
    } else {
      // 编辑已有员工
      store.loadCreatedEmployees().then(() => {
        const employee = store.getDigitalEmployeeById(id);
        if (employee) {
          editorStore.openEditor(employee);
        }
      });
    }
  }
}, [id]);

  // 处理表单字段更新（修复类型错误）
  const handleInputChange = (field: keyof CreatedEmployee | string, value: any) => {
    // 使用类型断言，因为field可能是字符串键
    editorStore.updateFormField(field as keyof CreatedEmployee, value);
  };

  // 处理图片上传
  const handleImageUpload = (file: File) => {
    const imageUrl = URL.createObjectURL(file);
    handleInputChange('avatar', imageUrl);
  };

  // 处理保存草稿
const handleSaveDraft = async () => {
  try {
    // 如果是新创建，直接保存表单数据，不要调用 createDigitalEmployee
    if (location.state?.isNew) {
      // 直接使用表单中的数据创建，不调用 Mock API 的 createDigitalEmployee
      const employeeData: CreatedEmployee = {
        id, // 使用URL中的临时ID
        name: editorStore.formData.name || '未命名员工',
        description: editorStore.formData.description || '',
        avatar: editorStore.formData.avatar || '',
        category: editorStore.formData.category || [],
        tags: editorStore.formData.tags || ['created'],
        price: editorStore.formData.price || 'free',
        trialCount: editorStore.formData.trialCount || 0,
        hireCount: editorStore.formData.hireCount || 0,
        isHired: false,
        isRecruited: false,
        industry: editorStore.formData.industry || '',
        role: editorStore.formData.role || '',
        status: 'draft',
        ...editorStore.formData,
      };
      
      // 只调用 saveDigitalEmployee 一次
      const savedEmployee = await store.saveDigitalEmployee(employeeData as CreatedEmployee);
      
      // 更新表单数据为已保存的状态
      editorStore.setFormData(savedEmployee);
      
      // 替换URL，移除 isNew 标记
      navigate(`/digital-employee/edit/${savedEmployee.id}`, { replace: true });
      
      return savedEmployee;
    } else {
      // 正常保存
      const savedEmployee = await editorStore.saveDraft();
      await store.saveDigitalEmployee(savedEmployee);
      return savedEmployee;
    }
  } catch (error) {
    console.error('保存草稿失败:', error);
    throw error;
  }
};

  // 处理发布
  const handlePublish = async () => {
    try {
      const publishedEmployee = await editorStore.publishEmployee();
      
      // 更新主store中的员工状态
      await store.publishDigitalEmployee(publishedEmployee.id);
      
      // 导航回列表页
      navigate('/digital-employee');
      
      return publishedEmployee;
    } catch (error) {
      console.error('发布失败:', error);
      throw error;
    }
  };

  // 处理取消
  const handleCancel = () => {
    editorStore.closeEditor();
    navigate('/digital-employee');
  };

  // 处理预览消息发送
  const handleSendPreviewMessage = (content: string) => {
    editorStore.sendPreviewMessage(content);
  };

  // 验证表单
  const validateForm = () => {
    const { formData } = editorStore;
    const errors: Record<string, boolean> = {};
    
    if (!formData.avatar) errors.avatar = true;
    if (!formData.industry) errors.industry = true;
    if (!formData.name) errors.name = true;
    if (!formData.description) errors.description = true;
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors,
    };
  };

  return {
    // 状态
    formData: editorStore.formData,
    activeEditorTab: editorStore.activeEditorTab,
    previewMessages: editorStore.previewMessages,
    chatInput: editorStore.chatInput,
    saving: editorStore.saving,
    publishing: editorStore.publishing,
    knowledgeBases: knowledgeBase.knowledgeBases,
    
    // 编辑器状态
    isEditorOpen: editorStore.isEditorOpen,
    editingEmployee: editorStore.editingEmployee,
    closeCreateModal: editorStore.closeCreateModal, // 添加这行
    // 事件处理
    onInputChange: handleInputChange,
    onImageUpload: handleImageUpload,
    onTabChange: editorStore.setActiveEditorTab,
    onSaveDraft: handleSaveDraft,
    onPublish: handlePublish,
    onCancel: handleCancel,
    onChatInputChange: editorStore.setChatInput,
    onSendPreviewMessage: handleSendPreviewMessage,
    
    // 工具函数
    validateForm,
  };
};