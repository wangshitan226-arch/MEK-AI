/**
 * 类型适配器 - 用于不同层之间的类型转换
 * 解决AI组件层、业务逻辑层和页面层之间的类型不匹配问题
 */

import { Employee as SharedEmployee } from './employee';
import { CreatedEmployee, normalizeDigitalEmployee } from './digitalEmployee';
import { KnowledgeBase } from './knowledge';

// ============================================
// AI组件使用的原始类型（来自Gemini生成）
// ============================================
export interface AIEmployee {
  id: string;
  name: string;
  description: string;
  category: string[];
  tags: string[];
  price: number;
  originalPrice?: number;
  trialCount: number;
  hireCount: number;
  avatar: string;
  isHot?: boolean;
  isRecruited: boolean;
  isHired: boolean;
}

export interface AIKnowledgeBaseItem {
  id: string;
  name: string;
  docCount: number;
}

// ============================================
// UI Pages 层使用的类型（兼容版本）
// ============================================

/**
 * UI Pages - 数字员工页面使用的Employee类型
 * 与 SharedEmployee 兼容，但 avatar 为可选
 */
export interface UIPageEmployee {
  id: string;
  name: string;
  description: string;
  category: string[];
  tags: string[];
  price: number;
  originalPrice?: number;
  trialCount: number;
  hireCount: number;
  avatar: string;
  isHot?: boolean;
  isRecruited: boolean;
  isHired: boolean;
}

/**
 * UI Pages - CreatedEmployee 兼容类型
 * status 支持 published 状态
 */
export interface UICreatedEmployee extends UIPageEmployee {
  industry: string;
  role: string;
  prompt?: string;
  model?: string;
  knowledgeBaseIds?: string[];
  createdAt?: string;
  createdBy?: string;
  status: 'draft' | 'published' | 'archived' | 'active' | 'inactive';
  variant?: 'created' | 'hired';
}

// ============================================
// Status 类型定义和转换
// ============================================

/** SharedEmployee 支持的状态 */
export type SharedEmployeeStatus = 'active' | 'inactive' | 'draft';

/** CreatedEmployee 支持的状态（扩展） */
export type CreatedEmployeeStatus = 'draft' | 'published' | 'archived' | 'active' | 'inactive';

/** Status 转换映射 */
export const StatusMapping: Record<CreatedEmployeeStatus, SharedEmployeeStatus> = {
  'draft': 'draft',
  'published': 'active',
  'archived': 'inactive',
  'active': 'active',
  'inactive': 'inactive',
};

/** 反向 Status 转换（默认映射） */
export const ReverseStatusMapping: Record<SharedEmployeeStatus, CreatedEmployeeStatus> = {
  'draft': 'draft',
  'active': 'active',
  'inactive': 'inactive',
};

// ============================================
// Employee 转换函数
// ============================================

/**
 * 将共享Employee类型转换为AI组件需要的Employee类型
 * 处理 price: 'free' → 0 的转换
 */
export const toAIEmployee = (employee: SharedEmployee | CreatedEmployee): AIEmployee => {
  const price = employee.price === 'free' ? 0 : employee.price;

  return {
    id: employee.id,
    name: employee.name,
    description: employee.description,
    avatar: employee.avatar,
    category: employee.category,
    tags: employee.tags,
    price: price as number,
    originalPrice: employee.originalPrice,
    trialCount: employee.trialCount,
    hireCount: employee.hireCount,
    isHot: employee.isHot,
    isRecruited: employee.isRecruited,
    isHired: employee.isHired,
  };
};

/**
 * 将AI组件Employee类型转换为共享Employee类型
 * 处理 price: 0 → 'free' 的转换
 * 确保 avatar 有默认值
 */
export const toSharedEmployee = (aiEmployee: AIEmployee): SharedEmployee => {
  const price = aiEmployee.price === 0 ? 'free' : aiEmployee.price;
  const name = aiEmployee.name || '未命名员工';

  return {
    id: aiEmployee.id,
    name,
    description: aiEmployee.description || '',
    avatar: aiEmployee.avatar?.trim()
      ? aiEmployee.avatar
      : `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`,
    category: aiEmployee.category || ['默认'],
    tags: aiEmployee.tags || [],
    price: price as 'free' | number,
    originalPrice: aiEmployee.originalPrice,
    trialCount: aiEmployee.trialCount || 0,
    hireCount: aiEmployee.hireCount || 0,
    isHired: aiEmployee.isHired || false,
    isRecruited: aiEmployee.isRecruited || false,
    isHot: aiEmployee.isHot,
  };
};

/**
 * 将 SharedEmployee 转换为 UIPageEmployee
 * 主要用于桥接层到页面组件的数据传递
 */
export const toUIPageEmployee = (employee: SharedEmployee): UIPageEmployee => {
  const price = employee.price === 'free' ? 0 : employee.price;

  return {
    id: employee.id,
    name: employee.name,
    description: employee.description,
    category: employee.category,
    tags: employee.tags,
    price: price as number,
    originalPrice: employee.originalPrice,
    trialCount: employee.trialCount,
    hireCount: employee.hireCount,
    avatar: employee.avatar,
    isHot: employee.isHot,
    isRecruited: employee.isRecruited,
    isHired: employee.isHired,
  };
};

/**
 * 将 UIPageEmployee 转换为 SharedEmployee
 * 确保 avatar 必填且有默认值
 */
export const fromUIPageEmployee = (employee: UIPageEmployee): SharedEmployee => {
  const name = employee.name || '未命名员工';

  return {
    id: employee.id,
    name,
    description: employee.description || '',
    avatar: employee.avatar?.trim()
      ? employee.avatar
      : `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`,
    category: employee.category || ['默认'],
    tags: employee.tags || [],
    price: employee.price,
    originalPrice: employee.originalPrice,
    trialCount: employee.trialCount || 0,
    hireCount: employee.hireCount || 0,
    isHired: employee.isHired || false,
    isRecruited: employee.isRecruited || false,
    isHot: employee.isHot,
  };
};

// ============================================
// CreatedEmployee 转换函数
// ============================================

/**
 * 将 CreatedEmployee 转换为 UICreatedEmployee
 * 用于桥接层到页面组件的数据传递
 */
export const toUICreatedEmployee = (employee: CreatedEmployee): UICreatedEmployee => {
  const price = employee.price === 'free' ? 0 : employee.price;

  return {
    id: employee.id,
    name: employee.name,
    description: employee.description,
    category: employee.category,
    tags: employee.tags,
    price: price as number,
    originalPrice: employee.originalPrice,
    trialCount: employee.trialCount,
    hireCount: employee.hireCount,
    avatar: employee.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(employee.name)}&background=random`,
    isHot: employee.isHot,
    isRecruited: employee.isRecruited,
    isHired: employee.isHired,
    industry: employee.industry || '',
    role: employee.role || '',
    prompt: employee.prompt,
    model: employee.model,
    knowledgeBaseIds: employee.knowledgeBaseIds,
    createdAt: employee.createdAt,
    createdBy: employee.createdBy,
    status: (employee.status as CreatedEmployeeStatus) || 'draft',
    variant: employee.variant || 'created',
  };
};

/**
 * 将 UICreatedEmployee 转换为 CreatedEmployee
 * 确保所有必填字段都有值
 */
export const fromUICreatedEmployee = (employee: UICreatedEmployee): CreatedEmployee => {
  const name = employee.name || '未命名员工';

  return {
    id: employee.id,
    name,
    description: employee.description || '',
    avatar: employee.avatar?.trim()
      ? employee.avatar
      : `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`,
    category: employee.category || ['默认'],
    tags: employee.tags || [],
    price: employee.price,
    originalPrice: employee.originalPrice,
    trialCount: employee.trialCount || 0,
    hireCount: employee.hireCount || 0,
    isHired: employee.isHired || false,
    isRecruited: employee.isRecruited || false,
    isHot: employee.isHot,
    industry: employee.industry || '',
    role: employee.role || '',
    prompt: employee.prompt,
    model: employee.model,
    knowledgeBaseIds: employee.knowledgeBaseIds,
    createdAt: employee.createdAt || new Date().toISOString(),
    createdBy: employee.createdBy || 'current-user',
    status: employee.status || 'draft',
    variant: employee.variant || 'created',
  };
};

/**
 * 将 CreatedEmployee 转换为 SharedEmployee
 * 处理 status 字段的映射
 */
export const createdEmployeeToShared = (employee: CreatedEmployee): SharedEmployee => {
  const mappedStatus = employee.status
    ? StatusMapping[employee.status as CreatedEmployeeStatus]
    : 'draft';

  return {
    id: employee.id,
    name: employee.name,
    description: employee.description,
    avatar: employee.avatar,
    category: employee.category,
    tags: employee.tags,
    price: employee.price,
    originalPrice: employee.originalPrice,
    trialCount: employee.trialCount,
    hireCount: employee.hireCount,
    isHired: employee.isHired,
    isRecruited: employee.isRecruited,
    isHot: employee.isHot,
    status: mappedStatus,
    industry: employee.industry,
    role: employee.role,
    prompt: employee.prompt,
    model: employee.model,
    knowledgeBaseIds: employee.knowledgeBaseIds,
    createdAt: employee.createdAt,
    createdBy: employee.createdBy,
  };
};

/**
 * 将 SharedEmployee 转换为 CreatedEmployee
 * 添加 CreatedEmployee 特有的字段
 */
export const sharedEmployeeToCreated = (
  employee: SharedEmployee,
  overrides?: Partial<CreatedEmployee>
): CreatedEmployee => {
  const baseStatus = employee.status || 'draft';
  const mappedStatus = ReverseStatusMapping[baseStatus] || 'draft';

  return {
    ...employee,
    industry: overrides?.industry || '',
    role: overrides?.role || '',
    prompt: overrides?.prompt,
    model: overrides?.model,
    knowledgeBaseIds: overrides?.knowledgeBaseIds,
    createdAt: overrides?.createdAt || new Date().toISOString(),
    createdBy: overrides?.createdBy || 'current-user',
    status: (overrides?.status as CreatedEmployeeStatus) || mappedStatus,
    variant: overrides?.variant || 'created',
  };
};

// ============================================
// Status 转换函数
// ============================================

/**
 * 将 CreatedEmployeeStatus 转换为 SharedEmployeeStatus
 * published → active, archived → inactive
 */
export const toSharedStatus = (status: CreatedEmployeeStatus): SharedEmployeeStatus => {
  return StatusMapping[status] || 'draft';
};

/**
 * 将 SharedEmployeeStatus 转换为 CreatedEmployeeStatus
 */
export const toCreatedStatus = (status: SharedEmployeeStatus): CreatedEmployeeStatus => {
  return ReverseStatusMapping[status] || 'draft';
};

// ============================================
// KnowledgeBase 转换函数
// ============================================

/**
 * 将共享KnowledgeBase类型转换为AI组件需要的KnowledgeBaseItem类型
 */
export const toAIKnowledgeBaseItem = (kb: KnowledgeBase): AIKnowledgeBaseItem => ({
  id: kb.id,
  name: kb.name,
  docCount: kb.docCount,
});

// ============================================
// 批量转换函数
// ============================================

/**
 * 批量转换员工列表为 AIEmployee
 */
export const toAIEmployeeList = (employees: (SharedEmployee | CreatedEmployee)[]): AIEmployee[] => {
  return employees.map(toAIEmployee);
};

/**
 * 批量转换员工列表为 UIPageEmployee
 */
export const toUIPageEmployeeList = (employees: SharedEmployee[]): UIPageEmployee[] => {
  return employees.map(toUIPageEmployee);
};

/**
 * 批量转换员工列表为 UICreatedEmployee
 */
export const toUICreatedEmployeeList = (employees: CreatedEmployee[]): UICreatedEmployee[] => {
  return employees.map(toUICreatedEmployee);
};

/**
 * 批量转换知识库列表
 */
export const toAIKnowledgeBaseItemList = (kbs: KnowledgeBase[]): AIKnowledgeBaseItem[] => {
  return kbs.map(toAIKnowledgeBaseItem);
};

// ============================================
// 类型守卫函数
// ============================================

/**
 * 检查是否为AI组件类型（用于类型守卫）
 */
export const isAIEmployee = (employee: any): employee is AIEmployee => {
  return employee && typeof employee.price === 'number';
};

/**
 * 检查是否为共享员工类型（用于类型守卫）
 */
export const isSharedEmployee = (employee: any): employee is SharedEmployee => {
  return employee && (typeof employee.price === 'number' || employee.price === 'free');
};

/**
 * 检查是否为 CreatedEmployee 类型
 */
export const isCreatedEmployee = (employee: any): employee is CreatedEmployee => {
  return (
    employee &&
    isSharedEmployee(employee) &&
    ('industry' in employee || 'role' in employee || 'status' in employee)
  );
};

/**
 * 检查是否为 UICreatedEmployee 类型
 */
export const isUICreatedEmployee = (employee: any): employee is UICreatedEmployee => {
  return (
    employee &&
    typeof employee.price === 'number' &&
    ('industry' in employee || 'role' in employee)
  );
};

// ============================================
// 安全创建函数
// ============================================

/**
 * 创建安全的员工对象（兼容 AIEmployee 和 SharedEmployee）
 */
export const createSafeEmployee = (data: any): AIEmployee & SharedEmployee => {
  const name = data?.name || '未命名员工';
  const base = {
    id: data?.id || `emp-${Date.now()}`,
    name,
    description: data?.description || '',
    avatar: data?.avatar?.trim()
      ? data.avatar
      : `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`,
    category: Array.isArray(data?.category) ? data.category : ['默认'],
    tags: Array.isArray(data?.tags) ? data.tags : [],
    trialCount: data?.trialCount || 0,
    hireCount: data?.hireCount || 0,
    isHired: data?.isHired || false,
    isRecruited: data?.isRecruited || false,
    isHot: data?.isHot,
  };

  const price = data?.price;
  const priceNumber = price === 'free' ? 0 : typeof price === 'number' ? price : 0;

  return {
    ...base,
    price: priceNumber,
    priceShared: price === 'free' ? 'free' : priceNumber,
  } as any;
};

/**
 * 创建安全的 UICreatedEmployee 对象
 */
export const createSafeUICreatedEmployee = (data: any): UICreatedEmployee => {
  const base = createSafeEmployee(data);

  return {
    ...toUIPageEmployee(base),
    industry: data?.industry || '',
    role: data?.role || '',
    prompt: data?.prompt,
    model: data?.model,
    knowledgeBaseIds: Array.isArray(data?.knowledgeBaseIds) ? data.knowledgeBaseIds : [],
    createdAt: data?.createdAt || new Date().toISOString(),
    createdBy: data?.createdBy || 'current-user',
    status: data?.status || 'draft',
    variant: data?.variant || 'created',
  };
};

/**
 * 创建安全的 CreatedEmployee 对象
 */
export const createSafeCreatedEmployee = (data: any): CreatedEmployee => {
  return fromUICreatedEmployee(createSafeUICreatedEmployee(data));
};

// ============================================
// 表单数据转换函数（用于编辑表单）
// ============================================

/**
 * 将 CreatedEmployee 转换为表单可用的 Partial<CreatedEmployee>
 * 处理所有字段，确保表单可以正确绑定
 */
export const toCreatedEmployeeFormData = (employee: CreatedEmployee): Partial<CreatedEmployee> => {
  return {
    id: employee.id,
    name: employee.name,
    description: employee.description,
    avatar: employee.avatar,
    category: [...employee.category],
    tags: [...employee.tags],
    price: employee.price,
    originalPrice: employee.originalPrice,
    trialCount: employee.trialCount,
    hireCount: employee.hireCount,
    isHired: employee.isHired,
    isRecruited: employee.isRecruited,
    isHot: employee.isHot,
    industry: employee.industry,
    role: employee.role,
    prompt: employee.prompt,
    model: employee.model,
    knowledgeBaseIds: employee.knowledgeBaseIds ? [...employee.knowledgeBaseIds] : [],
    status: employee.status,
    variant: employee.variant,
  };
};

/**
 * 将表单数据合并回 CreatedEmployee
 */
export const fromCreatedEmployeeFormData = (
  formData: Partial<CreatedEmployee>,
  original?: CreatedEmployee
): CreatedEmployee => {
  const name = formData.name || original?.name || '未命名员工';

  return {
    id: formData.id || original?.id || `emp-${Date.now()}`,
    name,
    description: formData.description || original?.description || '',
    avatar: formData.avatar?.trim()
      ? formData.avatar
      : original?.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`,
    category: formData.category || original?.category || ['默认'],
    tags: formData.tags || original?.tags || [],
    price: formData.price ?? original?.price ?? 0,
    originalPrice: formData.originalPrice ?? original?.originalPrice,
    trialCount: formData.trialCount ?? original?.trialCount ?? 0,
    hireCount: formData.hireCount ?? original?.hireCount ?? 0,
    isHired: formData.isHired ?? original?.isHired ?? false,
    isRecruited: formData.isRecruited ?? original?.isRecruited ?? false,
    isHot: formData.isHot ?? original?.isHot,
    industry: formData.industry || original?.industry || '',
    role: formData.role || original?.role || '',
    prompt: formData.prompt ?? original?.prompt,
    model: formData.model ?? original?.model,
    knowledgeBaseIds: formData.knowledgeBaseIds || original?.knowledgeBaseIds || [],
    createdAt: formData.createdAt || original?.createdAt || new Date().toISOString(),
    createdBy: formData.createdBy || original?.createdBy || 'current-user',
    status: (formData.status as CreatedEmployeeStatus) || original?.status || 'draft',
    variant: formData.variant || original?.variant || 'created',
  };
};
