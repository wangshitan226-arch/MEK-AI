import { create } from 'zustand';
import { MarketplaceStore } from '../../types';
import { getEmployees, getCategories, hireEmployee as hireEmployeeApi } from '../services/employeeApi';
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
      const result = await hireEmployeeApi(employeeId);

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
      // 从API获取员工列表，API已根据当前用户返回正确的is_hired状态
      const employees = await getEmployees();
      
      // 调试：打印API返回的原始数据
      console.log('[loadEmployees] API返回:', employees.map(e => ({ id: e.id, name: e.name, isHired: e.isHired, isRecruited: e.isRecruited })));

      // 直接使用API返回的状态，不再从userStore覆盖
      // 后端已经根据当前用户的hire_records查询了正确的is_hired状态
      const employeesWithStatus = employees.map(emp => ({
        ...emp,
        // 确保布尔值类型正确
        isHired: Boolean(emp.isHired),
        isRecruited: Boolean(emp.isRecruited),
        isInTrial: emp.isInTrial || false,
        hiredAt: emp.hiredAt || (emp.isHired ? new Date().toISOString() : undefined)
      }));
      
      // 调试：打印处理后的数据
      console.log('[loadEmployees] 处理后:', employeesWithStatus.map(e => ({ id: e.id, name: e.name, isHired: e.isHired, isRecruited: e.isRecruited })));

      // 同时同步到userStore（用于其他页面）
      const userStore = useUserStore.getState();
      const hiredEmployees = employeesWithStatus.filter(emp => emp.isHired);
      hiredEmployees.forEach(emp => {
        if (!userStore.recruitedEmployees.find(re => re.id === emp.id)) {
          userStore.addRecruitedEmployee(emp);
        }
      });

      set({
        employees: employeesWithStatus,
        loading: false
      });

      const hiredCount = employeesWithStatus.filter(emp => emp.isHired).length;
      console.log(`[loadEmployees] 加载了 ${employeesWithStatus.length} 个员工，其中 ${hiredCount} 个已招聘`);
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