import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDigitalEmployeeStore } from '../stores/digitalEmployeeStore';
import { useDigitalEmployeeEditorStore } from '../stores/digitalEmployeeEditorStore';

export const useDigitalEmployee = () => {
  const navigate = useNavigate();
  const store = useDigitalEmployeeStore();
  const editorStore = useDigitalEmployeeEditorStore();

  // 加载数据
  useEffect(() => {
    if (store.activeTab === 'created') {
      store.loadCreatedEmployees();
    } else {
      store.loadHiredEmployees();
    }
  }, [store.activeTab]);

  // 处理员工点击
  const handleEmployeeClick = (employeeId: string) => {
    const employee = store.getDigitalEmployeeById(employeeId);
    if (employee) {
      navigate(`/chat/${employeeId}`);
    } else {
      // 对于招聘的员工，使用原有逻辑
      navigate(`/chat/${employeeId}`);
    }
  };

  // 处理创建点击
  const handleCreateClick = () => {
    editorStore.openCreateModal();
  };

  // 处理编辑员工
  const handleEditEmployee = (employeeId: string) => {
    const employee = store.getDigitalEmployeeById(employeeId);
    if (employee) {
      editorStore.openEditor(employee);
      navigate(`/digital-employee/edit/${employeeId}`);
    }
  };

  // 处理删除员工
  const handleDismissEmployee = (employeeId: string) => {
    if (window.confirm('确定要解雇（删除）该数字员工吗？')) {
      store.deleteDigitalEmployee(employeeId);
    }
  };

  // 处理导航
  const handleNavigate = (view: string) => {
    if (view === 'marketplace') {
      navigate('/marketplace');
    } else if (view === 'knowledge-base') {
      navigate('/knowledge-base');
    }
  };

  // 处理Tab切换
  const handleTabChange = (tab: 'created' | 'hired') => {
    store.setActiveTab(tab);
  };

  // 根据当前Tab过滤员工
  const getCurrentEmployees = () => {
    if (store.activeTab === 'created') {
      return store.createdEmployees;
    } else {
      return store.hiredEmployees;
    }
  };

  return {
    // 状态
    activeTab: store.activeTab,
    createdEmployees: store.createdEmployees,
    hiredEmployees: store.hiredEmployees,
    currentEmployees: getCurrentEmployees(),
    loading: store.loading,
    error: store.error,
    
    // 编辑器状态
    isCreateModalOpen: editorStore.isCreateModalOpen,
    isEditorOpen: editorStore.isEditorOpen,
    
    // 事件处理
    onEmployeeClick: handleEmployeeClick,
    onNavigate: handleNavigate,
    onTabChange: handleTabChange,
    onCreateClick: handleCreateClick,
    onEditEmployee: handleEditEmployee,
    onDismissEmployee: handleDismissEmployee,
    
    // 工具函数
    getCreatedCount: store.getCreatedEmployeesCount,
    getHiredCount: store.getHiredEmployeesCount,
  };
};