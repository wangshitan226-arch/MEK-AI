import { create } from 'zustand';
import { normalizeEmployee } from '@/shared/types/employee';
import { normalizeDigitalEmployee } from '@/shared/types/digitalEmployee';
import { useUserStore } from '@/core/store/userStore';
import { DigitalEmployeeStore } from '../../types';
import {
  getCreatedEmployees,
  createDigitalEmployee as apiCreateDigitalEmployee,
  saveDigitalEmployee as apiSaveDigitalEmployee,
  updateDigitalEmployee as apiUpdateDigitalEmployee,
  deleteDigitalEmployee as apiDeleteDigitalEmployee,
  publishDigitalEmployee as apiPublishDigitalEmployee,
} from '../services/digitalEmployeeApi';

// 初始化状态
const initialState = {
  activeTab: 'hired' as const,
  createdEmployees: [] as any[], // 使用any避免类型冲突
  hiredEmployees: [] as any[],
  loading: false,
  error: null as string | null,
};

// 创建store
export const useDigitalEmployeeStore = create<DigitalEmployeeStore>((set, get) => ({
  ...initialState,

  // 设置当前Tab
  setActiveTab: (tab) => {
    set({ activeTab: tab });
    
    // 根据Tab加载对应数据
    if (tab === 'created') {
      get().loadCreatedEmployees();
    } else {
      get().loadHiredEmployees();
    }
  },

  // 加载创建的数字员工 - 使用真实 API
  loadCreatedEmployees: async () => {
    set({ loading: true, error: null });
    try {
      const data = await getCreatedEmployees();
      set({ createdEmployees: data, loading: false });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '加载创建员工失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },

  // 加载招聘的数字员工（从userStore同步）
  loadHiredEmployees: async () => {
    set({ loading: true, error: null });
    try {
      const userStore = useUserStore.getState();
      const normalizedEmployees = userStore.recruitedEmployees.map(normalizeEmployee);
      set({ hiredEmployees: normalizedEmployees, loading: false });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '加载招聘员工失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },

  // 创建数字员工（初始化）- 使用真实 API
  createDigitalEmployee: async (employee) => {
    set({ loading: true, error: null });
    try {
      const newEmployee = await apiCreateDigitalEmployee(employee);

      // 关键：立即添加到 createdEmployees，而不是只返回
      set((state) => ({
        createdEmployees: [newEmployee, ...state.createdEmployees],
        loading: false,
      }));

      return newEmployee;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '创建数字员工失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },
  // 保存数字员工（草稿）- 使用真实 API
  saveDigitalEmployee: async (employee) => {
    set({ loading: true, error: null });
    try {
      const savedEmployee = await apiSaveDigitalEmployee(employee);

      // 更新本地状态
      set((state) => {
        const exists = state.createdEmployees.some((emp: any) => emp.id === savedEmployee.id);

        if (exists) {
          return {
            createdEmployees: state.createdEmployees.map((emp: any) =>
              emp.id === savedEmployee.id ? savedEmployee : emp
            ),
            loading: false,
          };
        } else {
          return {
            createdEmployees: [savedEmployee, ...state.createdEmployees],
            loading: false,
          };
        }
      });

      return savedEmployee;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '保存数字员工失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },

  // 更新数字员工 - 使用真实 API
  updateDigitalEmployee: async (id, updates) => {
    set({ loading: true, error: null });
    try {
      const updatedEmployee = await apiUpdateDigitalEmployee(id, updates);

      set((state) => ({
        createdEmployees: state.createdEmployees.map((emp: any) =>
          emp.id === id ? updatedEmployee : emp
        ),
        loading: false,
      }));

      return updatedEmployee;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '更新数字员工失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },

  // 删除数字员工 - 使用真实 API
  deleteDigitalEmployee: async (id) => {
    set({ loading: true, error: null });
    try {
      await apiDeleteDigitalEmployee(id);
      set((state) => ({
        createdEmployees: state.createdEmployees.filter((emp: any) => emp.id !== id),
        loading: false,
      }));
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '删除数字员工失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },

  // 发布数字员工 - 使用真实 API
  publishDigitalEmployee: async (id) => {
    set({ loading: true, error: null });
    try {
      const publishedEmployee = await apiPublishDigitalEmployee(id);

      set((state) => ({
        createdEmployees: state.createdEmployees.map((emp: any) =>
          emp.id === id ? publishedEmployee : emp
        ),
        loading: false,
      }));

      return publishedEmployee;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '发布数字员工失败';
      set({ error: errorMsg, loading: false });
      throw error;
    }
  },

  // 根据ID获取数字员工
  getDigitalEmployeeById: (id) => {
    return get().createdEmployees.find((emp: any) => emp.id === id);
  },

  // 获取创建员工数量
  getCreatedEmployeesCount: () => {
    return get().createdEmployees.length;
  },

  // 获取招聘员工数量
  getHiredEmployeesCount: () => {
    return get().hiredEmployees.length;
  },
}));