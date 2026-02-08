import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDigitalEmployeeStore } from '../stores/digitalEmployeeStore';
import { useDigitalEmployeeEditorStore } from '../stores/digitalEmployeeEditorStore';

export const useDigitalEmployeeCreation = () => {
  const navigate = useNavigate();
  const store = useDigitalEmployeeStore();
  const editorStore = useDigitalEmployeeEditorStore();

  const [industry, setIndustry] = useState('');
  const [role, setRole] = useState('');

  // 处理创建确认
const handleCreateConfirm = async () => {
  try {
    // 不创建员工，只生成临时ID并跳转
    const tempId = `emp-${Date.now()}`;
    
    // 关闭创建弹窗
    editorStore.closeCreateModal();

    // 直接跳转，传递用户输入的数据
    navigate(`/digital-employee/edit/${tempId}`, {
      state: { 
        industry,  // 用户输入的行业
        role,      // 用户输入的岗位
        isNew: true, // 标记为新创建
      }
    });
    
    return tempId;
  } catch (error) {
    console.error('创建数字员工失败:', error);
    throw error;
  }
};

  // 处理创建取消
  const handleCreateCancel = () => {
    editorStore.closeCreateModal();
  };

  // 处理AI一键生成
  const handleAIGenerate = () => {
    // 这里可以调用AI生成服务
    console.log('调用AI生成数字员工');
    // 暂时使用默认值
    setIndustry('AI生成行业');
    setRole('AI生成岗位');
  };

  return {
    // 状态
    industry,
    role,
    
    // 设置函数
    setIndustry,
    setRole,
    
    // 事件处理
    onCreateConfirm: handleCreateConfirm,
    onCreateCancel: handleCreateCancel,
    onAIGenerate: handleAIGenerate,
  };
};