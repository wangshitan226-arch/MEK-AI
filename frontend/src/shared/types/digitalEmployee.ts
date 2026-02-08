/**
 * 数字员工扩展类型定义
 */

import { Employee, normalizeEmployee } from './employee';

// 默认提示词模板
export const DEFAULT_PROMPT_TEMPLATE = `你是一个专业的AI助手。请根据用户的问题提供有帮助、准确且专业的回答。

在回答时，请遵循以下原则：
1. 保持礼貌和专业
2. 提供准确的信息
3. 如果不确定，请诚实地说明
4. 尽量简洁明了，但确保信息完整`;


// 数字员工扩展字段接口（不继承，而是组合）
export interface DigitalEmployeeFields {
  // 创建相关的扩展字段
  industry: string;
  role: string;
  prompt?: string;
  model?: string;
  knowledgeBaseIds?: string[];
  createdAt?: string;
  createdBy?: string;
  status?: 'draft' | 'published' | 'archived' | 'active' | 'inactive';
  variant?: 'created' | 'hired';
}

// 完整的创建数字员工类型（组合方式）
export type CreatedEmployee = Employee & DigitalEmployeeFields;

// 配置接口
export interface DigitalEmployeeConfig {
  // 创建配置
  industry: string;
  role: string;
  
  // 人设配置
  persona?: {
    avatar: string;
    name: string;
    description: string;
    prompt: string;
  };
  
  // 技能配置
  skills?: {
    model: string;
    imageRecognition: boolean;
    knowledgeBaseIds: string[];
  };
}

/**
 * 创建安全的默认数字员工
 */
export const createSafeDigitalEmployee = (overrides?: Partial<CreatedEmployee>): CreatedEmployee => {
  const baseEmployee = normalizeEmployee(overrides);
  
  return {
    ...baseEmployee,
    // 如果 overrides 中有值，使用 overrides 的，否则使用默认值
    industry: overrides?.industry ?? '',
    role: overrides?.role ?? '',
    name: overrides?.name || '未命名员工', // 如果传了空字符串，就用空字符串
    description: overrides?.description ?? '', // 如果传了空字符串，就用空字符串
    prompt: overrides?.prompt || DEFAULT_PROMPT_TEMPLATE,
    model: overrides?.model || 'gemini-2.5-pro-preview',
    // ...
  };
};

/**
 * 检查是否为创建的数字员工
 */
export const isCreatedEmployee = (employee: Employee): employee is CreatedEmployee => {
  return (employee as CreatedEmployee).tags?.includes('created') || false;
};

/**
 * 检查是否为招聘的数字员工
 */
export const isHiredEmployee = (employee: Employee): boolean => {
  return employee.isRecruited && !isCreatedEmployee(employee);
};

/**
 * 规范化数字员工数据（使用组合方式，避免继承问题）
 */
export const normalizeDigitalEmployee = (data: any): CreatedEmployee => {
  const employee = normalizeEmployee(data);
  
  return {
    ...employee,
    industry: data?.industry || '',
    role: data?.role || '',
    prompt: data?.prompt || '',
    model: data?.model || 'gemini-2.5-pro-preview',
    knowledgeBaseIds: Array.isArray(data?.knowledgeBaseIds) ? data.knowledgeBaseIds : [],
    createdAt: data?.createdAt || new Date().toISOString(),
    createdBy: data?.createdBy || 'current-user',
    status: data?.status || 'draft',
    variant: 'created' as const,
  };
};