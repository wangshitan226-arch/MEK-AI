// src/modules/marketplace/logic/hooks/useMarketplaceInteraction.ts
import { useNavigate } from 'react-router-dom'; // 添加这行
import { useMarketplaceStore } from '../stores/marketplaceStore';
import { useMarketplaceUIStore } from '../stores/marketplaceUIStore';
import { useUserStore } from '@/core/store/userStore';

export const useMarketplaceInteraction = () => {
  const navigate = useNavigate(); // 添加这行
  const { hireEmployee } = useMarketplaceStore();
  const { setView, selectEmployee, openHireModal, closeHireModal, resetUI } = useMarketplaceUIStore();

  // 处理员工卡片点击
  const handleEmployeeCardClick = (employeeId: string) => {
    // 注意：这里需要从数据Store中获取最新的员工信息
    const { employees } = useMarketplaceStore.getState();
    const employee = employees.find(e => e.id === employeeId);
    if (!employee) return;

    if (employee.isHired || employee.isRecruited) {
      // 已雇佣：跳转到聊天界面
      navigate(`/chat/${employeeId}`); // 修改为路由导航
    } else {
      // 未雇佣：打开招聘弹窗
      openHireModal(employee);
    }
  };

  // 处理招聘确认
  const handleHireConfirm = async () => {
    const { hiringEmployee } = useMarketplaceUIStore.getState();
    if (!hiringEmployee) return;

    try {
      // 1. 调用核心数据操作
      await hireEmployee(hiringEmployee.id);
      // 2. 关闭弹窗
      closeHireModal();
      // 3. 可以在这里添加成功提示（未来集成通知系统）
      console.log(`成功雇佣员工：${hiringEmployee.name}`);
      // 注意：此处不自动跳转，等待用户再次点击已雇佣的卡片
    } catch (error) {
      // 错误状态已在 hireEmployee 中处理，这里可以记录日志
      console.error('雇佣操作失败:', error);
    }
  };

  // 处理从聊天界面返回市场
  const handleBackToMarketplace = () => {
    resetUI(); // 重置UI状态，回到市场视图
    navigate('/marketplace'); // 添加路由导航
  };

  // 处理关闭弹窗（无操作）
  const handleCloseModal = () => {
    closeHireModal();
  };

  return {
    handleEmployeeCardClick,
    handleHireConfirm,
    handleBackToMarketplace,
    handleCloseModal,
  };
};