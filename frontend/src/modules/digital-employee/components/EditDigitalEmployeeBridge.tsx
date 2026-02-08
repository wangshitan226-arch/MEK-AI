import React, { useRef } from 'react';
import { EditDigitalEmployee } from '@/ui-pages/digital-employee/components/EditDigitalEmployee';
import { useDigitalEmployeeEditor } from '../logic/hooks/useDigitalEmployeeEditor';
import { useEffect } from 'react';
const EditDigitalEmployeeBridge: React.FC = () => {
  const editorLogic = useDigitalEmployeeEditor();
  const fileInputRef = useRef<HTMLInputElement>(null);
    // 确保进入编辑页面时弹窗已关闭
    useEffect(() => {
      editorLogic.closeCreateModal?.();
    }, []);
  // 处理图片上传
  const handleImageUpload = (file: File) => {
    editorLogic.onImageUpload(file);
  };

  // 处理保存
  const handleSave = async () => {
    const { isValid } = editorLogic.validateForm();
    if (!isValid) {
      alert('请完善带 * 的必填项');
      return;
    }
    
    try {
      await editorLogic.onSaveDraft();
    } catch (error) {
      console.error('保存失败:', error);
      alert('保存失败，请重试');
    }
  };

  // 处理发布
  const handlePublish = async () => {
    const { isValid } = editorLogic.validateForm();
    if (!isValid) {
      alert('请完善带 * 的必填项后再发布');
      return;
    }
    
    try {
      await editorLogic.onPublish();
    } catch (error) {
      console.error('发布失败:', error);
      alert('发布失败，请重试');
    }
  };

  return (
    <EditDigitalEmployee
      initialData={editorLogic.editingEmployee || undefined}
      knowledgeBases={editorLogic.knowledgeBases}
      activeTab={editorLogic.activeEditorTab}
      formData={editorLogic.formData}
      previewMessages={editorLogic.previewMessages}
      chatInput={editorLogic.chatInput}
      hasSaved={!!editorLogic.editingEmployee}
      errors={{}}
      saving={editorLogic.saving}
      publishing={editorLogic.publishing}
      onCancel={editorLogic.onCancel}
      onSave={handleSave}
      onPublish={handlePublish}
      onInputChange={editorLogic.onInputChange}
      onImageUpload={handleImageUpload}
      onTabChange={editorLogic.onTabChange}
      onChatInputChange={editorLogic.onChatInputChange}
      onSendPreviewMessage={editorLogic.onSendPreviewMessage}
      fileInputRef={fileInputRef}
    />
  );
};

export default EditDigitalEmployeeBridge;