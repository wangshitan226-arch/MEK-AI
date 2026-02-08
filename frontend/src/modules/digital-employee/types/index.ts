import { Employee, normalizeEmployee } from '@/shared/types/employee';
import { CreatedEmployee, DigitalEmployeeConfig } from '@/shared/types/digitalEmployee';

// === 数据状态管理类型 ===
export interface DigitalEmployeeState {
  // 列表状态
  activeTab: 'created' | 'hired';
  createdEmployees: CreatedEmployee[];
  hiredEmployees: Employee[];
  
  // 加载状态
  loading: boolean;
  error: string | null;
}

export interface DigitalEmployeeActions {
  // Tab操作
  setActiveTab: (tab: 'created' | 'hired') => void;
  
  // 加载数据
  loadCreatedEmployees: () => Promise<void>;
  loadHiredEmployees: () => Promise<void>;
  
  // 创建员工操作
  createDigitalEmployee: (config: { industry: string; role: string }) => Promise<CreatedEmployee>;
  saveDigitalEmployee: (employee: CreatedEmployee) => Promise<CreatedEmployee>;
  updateDigitalEmployee: (id: string, updates: Partial<CreatedEmployee>) => Promise<CreatedEmployee>;
  deleteDigitalEmployee: (id: string) => Promise<void>;
  publishDigitalEmployee: (id: string) => Promise<CreatedEmployee>;
  
  // 工具函数
  getDigitalEmployeeById: (id: string) => CreatedEmployee | undefined;
  getCreatedEmployeesCount: () => number;
  getHiredEmployeesCount: () => number;
}

export type DigitalEmployeeStore = DigitalEmployeeState & DigitalEmployeeActions;

// === 编辑器状态管理类型 ===
export interface DigitalEmployeeEditorState {
  // 编辑状态
  editingEmployee: CreatedEmployee | null;
  isCreateModalOpen: boolean;
  isEditorOpen: boolean;
  
  // 编辑器数据
  formData: Partial<CreatedEmployee>;
  activeEditorTab: 'persona' | 'skills' | 'anthropomorphism' | 'reply' | 'business' | 'human';
  
  // 预览状态
  previewMessages: Array<{ role: 'user' | 'model'; content: string }>;
  chatInput: string;
  
  // 加载状态
  saving: boolean;
  publishing: boolean;
}

export interface DigitalEmployeeEditorActions {
  // 模态框控制
  openCreateModal: () => void;
  closeCreateModal: () => void;
  openEditor: (employee?: CreatedEmployee) => void;
  closeEditor: () => void;
  
  // 表单操作
  setFormData: (data: Partial<CreatedEmployee>) => void;
  updateFormField: <K extends keyof CreatedEmployee>(field: K, value: CreatedEmployee[K]) => void;
  setActiveEditorTab: (tab: DigitalEmployeeEditorState['activeEditorTab']) => void;
  
  // 预览操作
  setPreviewMessages: (messages: Array<{ role: 'user' | 'model'; content: string }>) => void;
  setChatInput: (input: string) => void;
  sendPreviewMessage: (content: string) => void;
  
  // 业务操作
  saveDraft: () => Promise<CreatedEmployee>;
  publishEmployee: () => Promise<CreatedEmployee>;
  resetEditor: () => void;
  
  // 状态管理
  setSaving: (saving: boolean) => void;
  setPublishing: (publishing: boolean) => void;
}

export type DigitalEmployeeEditorStore = DigitalEmployeeEditorState & DigitalEmployeeEditorActions;

// === 服务层接口 ===
export interface IDigitalEmployeeService {
  // 创建员工
  createDigitalEmployee: (config: { industry: string; role: string }) => Promise<CreatedEmployee>;
  
  // CRUD操作
  getCreatedEmployees: () => Promise<CreatedEmployee[]>;
  getDigitalEmployee: (id: string) => Promise<CreatedEmployee>;
  saveDigitalEmployee: (employee: CreatedEmployee) => Promise<CreatedEmployee>;
  updateDigitalEmployee: (id: string, updates: Partial<CreatedEmployee>) => Promise<CreatedEmployee>;
  deleteDigitalEmployee: (id: string) => Promise<boolean>;
  publishDigitalEmployee: (id: string) => Promise<CreatedEmployee>;
  
  // 预览功能
  generatePreviewResponse: (employee: CreatedEmployee, userMessage: string) => Promise<string>;
}