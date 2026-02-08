import React from 'react';
import { useNavigate } from 'react-router-dom';
import { CreateDigitalEmployeeModal } from '@/ui-pages/digital-employee/components/CreateDigitalEmployeeModal';
import { useDigitalEmployeeCreation } from '../logic/hooks/useDigitalEmployeeCreation';

const CreateDigitalEmployeeBridge: React.FC = () => {
  const navigate = useNavigate();
  const creationLogic = useDigitalEmployeeCreation();

  // 处理创建确认
  const handleCreateConfirm = async () => {
    try {
      const newEmployee = await creationLogic.onCreateConfirm();
      // 创建成功后，模态框会自动关闭，编辑器会自动打开
    } catch (error) {
      console.error('创建失败:', error);
    }
  };

  // 处理取消
  const handleCancel = () => {
    navigate('/digital-employee');
  };

  return (
    <CreateDigitalEmployeeModal
      isOpen={true}
      onClose={handleCancel}
      onConfirm={handleCreateConfirm}
      onAIGenerate={creationLogic.onAIGenerate}
      loading={false}
    />
  );
};

export default CreateDigitalEmployeeBridge;