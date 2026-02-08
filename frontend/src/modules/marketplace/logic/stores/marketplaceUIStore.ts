// src/modules/marketplace/logic/stores/marketplaceUIStore.ts
import { create } from 'zustand';
import { MarketplaceUIStore } from '../../types';

// 初始化UI状态
const initialUIState = {
  currentView: 'marketplace' as const,
  selectedEmployeeId: null,
  isHireModalOpen: false,
  hiringEmployee: null,
};

// 创建UI store
export const useMarketplaceUIStore = create<MarketplaceUIStore>((set) => ({
  ...initialUIState,

  // 设置当前视图
  setView: (view) => {
    set({ currentView: view });
  },

  // 选择员工
  selectEmployee: (id) => {
    set({ selectedEmployeeId: id });
  },

  // 打开招聘弹窗
  openHireModal: (employee) => {
    set({
      isHireModalOpen: true,
      hiringEmployee: employee,
      selectedEmployeeId: employee.id,
    });
  },

  // 关闭招聘弹窗
  closeHireModal: () => {
    set({
      isHireModalOpen: false,
      hiringEmployee: null,
    });
  },

  // 重置UI状态（例如返回市场时）
  resetUI: () => {
    set({
      ...initialUIState,
      currentView: 'marketplace',
    });
  },
}));