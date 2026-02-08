import { create } from 'zustand';
import { MarketplaceStore } from '../../types';
import { getEmployees, getCategories, hireEmployee } from '../services/employeeApi';
import { mockCategories } from '../services/mockData';
import { useUserStore } from '@/core/store/userStore';

// 初始化状态
const initialState = {
  employees: [],
  categories: [],
  activeCategoryId: null,
  searchQuery: '',
  loading: false,
  error: null,
};

// 创建store
export const useMarketplaceStore = create<MarketplaceStore>((set, get) => ({
  ...initialState,

  // 设置当前选中的分类
  setActiveCategory: (categoryId: string | null) => {
    set({ activeCategoryId: categoryId });
  },

  // 雇佣员工 - 关键修复：确保数据完全同步
  hireEmployee: async (employeeId: string) => {
    set({ loading: true, error: null });

    try {
      const result = await hireEmployee(employeeId);

      if (result.success) {
        const employee = get().employees.find(emp => emp.id === employeeId);
        if (!employee) throw new Error('员工不存在');

        // 更新本地状态
        set((state) => ({
          employees: state.employees.map(emp =>
            emp.id === employeeId
              ? {
                  ...emp,
                  isHired: true,
                  isRecruited: true,
                  hiredAt: new Date().toISOString()
                }
              : emp
          ),
          loading: false,
        }));

        // 添加到userStore，确保数据格式正确
        const employeeForUserStore = {
          ...employee,
          isHired: true,
          isRecruited: true,
          hiredAt: new Date().toISOString(),
          avatar: employee.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(employee.name)}&background=random`
        };

        useUserStore.getState().addRecruitedEmployee(employeeForUserStore);

        return Promise.resolve();
      } else {
        set({ error: result.message, loading: false });
        return Promise.reject(new Error(result.message));
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '雇佣失败';
      set({ error: errorMsg, loading: false });
      return Promise.reject(new Error(errorMsg));
    }
  },

  // 切换试用状态
  toggleTrialEmployee: (employeeId: string) => {
    set((state) => ({
      employees: state.employees.map(emp =>
        emp.id === employeeId
          ? {
            ...emp,
            isInTrial: !emp.isInTrial,
            trialExpiresAt: !emp.isInTrial
              ? new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
              : undefined
          }
          : emp
      ),
    }));
  },

  // 设置搜索查询
  setSearchQuery: (query: string) => {
    set({ searchQuery: query });
  },

  // 加载员工数据 - 使用真实 API
  loadEmployees: async () => {
    set({ loading: true, error: null });

    try {
      const employees = await getEmployees();

      // 从全局userStore获取已招聘的员工ID
      const userStore = useUserStore.getState();
      const recruitedIds = userStore.recruitedEmployees.map(emp => emp.id);

      // 同步状态：如果员工在userStore中已招聘，则更新本地状态
      const employeesWithStatus = employees.map(emp => {
        const isRecruited = recruitedIds.includes(emp.id);
        return {
          ...emp,
          isHired: isRecruited,
          isRecruited: isRecruited,
          isInTrial: false,
          hiredAt: isRecruited ? new Date().toISOString() : undefined
        };
      });

      set({
        employees: employeesWithStatus,
        loading: false
      });

      console.log(`加载了 ${employeesWithStatus.length} 个员工，其中 ${recruitedIds.length} 个已招聘`);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '加载员工数据失败';
      set({ error: errorMsg, loading: false });
      throw new Error(errorMsg);
    }
  },

  // 加载分类数据 - 使用真实 API
  loadCategories: async () => {
    try {
      const categories = await getCategories();
      set({ categories });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '加载分类数据失败';
      set({ error: errorMsg });
      throw new Error(errorMsg);
    }
  },
}));

// 创建选择器hooks（提高性能）
export const useFilteredEmployees = () => {
  const { employees, activeCategoryId, searchQuery } = useMarketplaceStore();
  return employees.filter(employee => {
    if (activeCategoryId && activeCategoryId !== 'all') {
      const category = mockCategories.find(c => c.id === activeCategoryId);
      if (category && !employee.category.includes(category.name)) {
        return false;
      }
    }
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        employee.name.toLowerCase().includes(query) ||
        employee.description.toLowerCase().includes(query) ||
        employee.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }
    return true;
  });
};

export const useActiveCategory = () => {
  return useMarketplaceStore((state) =>
    state.categories.find(c => c.id === state.activeCategoryId)
  );
};