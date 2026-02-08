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
      // role 映射到 name（岗位名称）
      editorStore.setFormData({
        id,
        industry: location.state.industry || '',
        name: location.state.role || '',  // role 作为岗位名称
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
      // 如果是新创建，调用 createDigitalEmployee 创建新员工
      if (location.state?.isNew) {
        // 构建新员工数据（不包含ID，让后端生成）
        const employeeData: Partial<CreatedEmployee> = {
          name: editorStore.formData.name || '未命名员工',
          description: editorStore.formData.description || '暂无描述',
          avatar: editorStore.formData.avatar || '',
          category: editorStore.formData.category || [],
          tags: [...(editorStore.formData.tags || []), 'created'],
          price: editorStore.formData.price || 'free',
          trialCount: 0,
          hireCount: 0,
          isHired: false,
          isRecruited: false,
          industry: editorStore.formData.industry || '',
          role: editorStore.formData.name || '',  // role 使用 name 的值（岗位名称）
          prompt: editorStore.formData.prompt || '',
          model: editorStore.formData.model || 'gemini-2.5-pro-preview',
          knowledgeBaseIds: editorStore.formData.knowledgeBaseIds || [],
          status: 'draft',
        };

        // 调用 createDigitalEmployee 创建新员工
        const createdEmployee = await store.createDigitalEmployee(employeeData as CreatedEmployee);

        // 更新编辑器状态
        editorStore.setEditingEmployee(createdEmployee);
        editorStore.setFormData(createdEmployee);

        // 替换URL，移除 isNew 标记，使用后端返回的真实ID
        navigate(`/digital-employee/edit/${createdEmployee.id}`, { replace: true });

        return createdEmployee;
      } else {
        // 更新已有员工
        const savedEmployee = await editorStore.saveDraft();
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