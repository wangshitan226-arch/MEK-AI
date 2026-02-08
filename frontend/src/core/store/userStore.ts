import { create } from 'zustand';
import { Employee, normalizeEmployee } from '@/shared/types/employee';

interface UserStore {
  recruitedEmployees: Employee[];
  addRecruitedEmployee: (employee: any) => void;
  removeRecruitedEmployee: (employeeId: string) => void;
  setRecruitedEmployees: (employees: any[]) => void;
  clearRecruitedEmployees: () => void;
  isEmployeeRecruited: (employeeId: string) => boolean;
  getRecruitedEmployee: (employeeId: string) => Employee | undefined;
}

export const useUserStore = create<UserStore>((set, get) => ({
  recruitedEmployees: [],
  
  addRecruitedEmployee: (employeeData) => {
    const employee = normalizeEmployee(employeeData);
    
    set((state) => {
      // 检查是否已经存在
      const exists = state.recruitedEmployees.some(emp => emp.id === employee.id);
      
      if (exists) {
        return {
          recruitedEmployees: state.recruitedEmployees.map(emp =>
            emp.id === employee.id ? { ...emp, ...employee, isRecruited: true } : emp
          )
        };
      }
      
      return {
        recruitedEmployees: [...state.recruitedEmployees, { ...employee, isRecruited: true }]
      };
    });
  },
    
  removeRecruitedEmployee: (employeeId) => {
    set((state) => ({
      recruitedEmployees: state.recruitedEmployees.filter(emp => emp.id !== employeeId)
    }));
  },
    
  setRecruitedEmployees: (employeesData) => {
    const normalizedEmployees = employeesData.map(normalizeEmployee);
    set({ 
      recruitedEmployees: normalizedEmployees.map(emp => ({ ...emp, isRecruited: true }))
    });
  },
  
  clearRecruitedEmployees: () => {
    set({ recruitedEmployees: [] });
  },
  
  isEmployeeRecruited: (employeeId) => {
    return get().recruitedEmployees.some(emp => emp.id === employeeId);
  },
  
  getRecruitedEmployee: (employeeId) => {
    return get().recruitedEmployees.find(emp => emp.id === employeeId);
  }
}));