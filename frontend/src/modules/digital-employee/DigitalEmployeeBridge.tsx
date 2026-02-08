import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import DigitalEmployeesPage from '@/ui-pages/digital-employee/components/DigitalEmployeesPage';
import { CreateDigitalEmployeeModal } from '@/ui-pages/digital-employee/components/CreateDigitalEmployeeModal';
import { useDigitalEmployee } from './logic/hooks/useDigitalEmployee';
import { useDigitalEmployeeCreation } from './logic/hooks/useDigitalEmployeeCreation';
import EditDigitalEmployeeBridge from './components/EditDigitalEmployeeBridge';
import { toAIEmployeeList } from '@/shared/types/typeAdapters';
import { 
    toUICreatedEmployeeList, 
    toUIPageEmployeeList,
    UICreatedEmployee,
    UIPageEmployee 
  } from '@/shared/types/typeAdapters';
const DigitalEmployeeBridge: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // 获取列表页面逻辑
  const listLogic = useDigitalEmployee();
  
  // 获取创建逻辑
  const creationLogic = useDigitalEmployeeCreation();

  // 检查当前是否在编辑页面
  const isEditPage = location.pathname.includes('/digital-employee/edit/');
  const isCreatePage = location.pathname === '/digital-employee/create';

  // 加载数据
  useEffect(() => {
    console.log('数字员工页面加载，当前标签页:', listLogic.activeTab);
  }, [listLogic.activeTab]);

  // 处理创建确认
  const handleCreateConfirm = async () => {
    try {
      await creationLogic.onCreateConfirm();
    } catch (error) {
      console.error('创建失败:', error);
    }
  };

  // 如果是编辑页面，渲染编辑器
  if (isEditPage || isCreatePage) {
    return <EditDigitalEmployeeBridge />;
  }

  // 渲染列表页面（使用类型适配器转换数据）
  return (
    <>
      <DigitalEmployeesPage
        createdEmployees={toUICreatedEmployeeList(listLogic.createdEmployees)}
        hiredEmployees={toAIEmployeeList(listLogic.hiredEmployees)}
        activeTab={listLogic.activeTab}
        currentView="digital-employee"
        loading={listLogic.loading}
        error={listLogic.error}
        onEmployeeClick={listLogic.onEmployeeClick}
        onNavigate={listLogic.onNavigate}
        onTabChange={listLogic.onTabChange}
        onCreateClick={listLogic.onCreateClick}
        onEditEmployee={listLogic.onEditEmployee}
        onDismissEmployee={listLogic.onDismissEmployee}
      />

      {/* 创建弹窗 */}
      <CreateDigitalEmployeeModal
        isOpen={listLogic.isCreateModalOpen}
        onClose={creationLogic.onCreateCancel}
        onConfirm={handleCreateConfirm}
        onAIGenerate={creationLogic.onAIGenerate}
        loading={listLogic.loading}
        // 新增：传递 useDigitalEmployeeCreation 中的值
        industry={creationLogic.industry}
        role={creationLogic.role}
        onIndustryChange={creationLogic.setIndustry}
        onRoleChange={creationLogic.setRole}
      />
    </>
  );
};

export default DigitalEmployeeBridge;