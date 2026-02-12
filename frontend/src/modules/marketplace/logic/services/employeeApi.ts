/**
 * 员工 API 服务层
 * 替换原有的 mockMarketplaceAPI
 */

import { apiClient } from '@/core/services/apiClient';
import { API_ENDPOINTS } from '@/core/config/api';
import { transformEmployeesFromApi, transformEmployeeFromApi } from '@/shared/utils/transform';
import { Employee } from '@/shared/types/employee';
import { Category } from '../../../../ui-pages/marketplace/types';

// API 响应类型
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
}

interface HireResponse {
  success: boolean;
  message: string;
  employee_id?: string;
}

interface TrialResponse {
  success: boolean;
  message: string;
  trial_expires_at?: string;
}

/**
 * 获取员工列表（市场广场）
 */
export async function getEmployees(): Promise<Employee[]> {
  const response = await apiClient.get<ApiResponse<any>>(API_ENDPOINTS.MARKETPLACE.LIST);

  if (!response.success || !response.data) {
    throw new Error(response.message || '获取员工列表失败');
  }

  // 后端返回格式: { items: [...], total: ... }
  // 注意：apiClient 已经使用 keysToCamel 将 snake_case 转为 camelCase
  const items = response.data.items || response.data;
  
  // 数据已经是 camelCase，只需要确保 avatar 有默认值
  return items.map((emp: any) => ({
    ...emp,
    avatar: emp.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(emp.name)}&background=random`,
    // 确保布尔值正确
    isHired: Boolean(emp.isHired),
    isRecruited: Boolean(emp.isRecruited),
  }));
}

/**
 * 获取单个员工详情
 */
export async function getEmployeeById(id: string): Promise<Employee> {
  const response = await apiClient.get<ApiResponse<any>>(
    API_ENDPOINTS.EMPLOYEES.DETAIL(id)
  );
  
  if (!response.success || !response.data) {
    throw new Error(response.message || '获取员工详情失败');
  }
  
  return transformEmployeeFromApi(response.data);
}

/**
 * 获取分类列表
 */
export async function getCategories(): Promise<Category[]> {
  const response = await apiClient.get<ApiResponse<any>>(
    API_ENDPOINTS.EMPLOYEES.CATEGORIES
  );

  if (!response.success || !response.data) {
    throw new Error(response.message || '获取分类列表失败');
  }

  // 后端返回格式可能是数组或 { categories: [...] }
  const categories = Array.isArray(response.data) ? response.data : response.data.categories || [];

  // 转换分类数据
  return categories.map((cat: any) => ({
    id: cat.id || cat.toLowerCase().replace(/\s+/g, '-'),
    name: cat.name || cat,
    count: cat.count || 0,
  }));
}

/**
 * 雇佣员工
 */
export async function hireEmployee(employeeId: string): Promise<HireResponse> {
  const response = await apiClient.post<HireResponse>(
    API_ENDPOINTS.MARKETPLACE.HIRE(employeeId),
    {}  // 请求体，可以添加 organization_id 等参数
  );

  return response;
}

/**
 * 试用员工
 */
export async function trialEmployee(employeeId: string): Promise<TrialResponse> {
  const response = await apiClient.post<TrialResponse>(
    API_ENDPOINTS.MARKETPLACE.TRIAL(employeeId),
    {}  // 请求体
  );

  return response;
}

/**
 * 获取聊天会话列表
 */
export async function getChatSessions(employeeId: string): Promise<any[]> {
  const response = await apiClient.get<ApiResponse<any[]>>(
    `${API_ENDPOINTS.CHAT.SESSIONS}?employee_id=${employeeId}`
  );
  
  if (!response.success || !response.data) {
    return [];
  }
  
  return response.data.map((session: any) => ({
    id: session.id,
    title: session.title,
    employeeId: session.employee_id,
    lastModified: session.last_modified 
      ? new Date(session.last_modified).getTime() 
      : Date.now(),
  }));
}

/**
 * 获取会话消息
 */
export async function getSessionMessages(sessionId: string): Promise<any[]> {
  const response = await apiClient.get<ApiResponse<any[]>>(
    API_ENDPOINTS.CHAT.SESSION_MESSAGES(sessionId)
  );
  
  if (!response.success || !response.data) {
    return [];
  }
  
  return response.data.map((msg: any) => ({
    id: msg.id || `msg-${Date.now()}-${Math.random()}`,
    role: msg.role === 'assistant' ? 'model' : msg.role,
    content: msg.content,
    timestamp: msg.timestamp 
      ? new Date(msg.timestamp).getTime() 
      : Date.now(),
  }));
}

/**
 * 发送聊天消息
 */
export async function sendChatMessage(
  employeeId: string,
  content: string,
  sessionId?: string
): Promise<{ message: string; conversation_id?: string }> {
  const response = await apiClient.post<ApiResponse<any>>(API_ENDPOINTS.CHAT.SEND, {
    message: content,
    employee_id: employeeId,
    conversation_id: sessionId,
  });

  // 后端返回格式: { success: true, message: "消息处理成功", data: { response: "AI回复", ... } }
  // 注意：response.message 是状态消息，AI回复在 response.data.response 中
  if (!response.success) {
    throw new Error(response.message || '聊天请求失败');
  }

  // 增强的响应解析逻辑
  let aiMessage = '';
  let conversationId = sessionId;

  if (response.data) {
    // 尝试多种可能的字段名
    aiMessage = response.data.response 
      || response.data.answer 
      || response.data.content 
      || response.data.message 
      || '';
    
    conversationId = response.data.conversation_id 
      || response.data.conversationId 
      || sessionId;
  }

  // 如果仍然没有消息，使用外层message（兼容旧版本）
  if (!aiMessage && response.message && response.message !== '消息处理成功') {
    aiMessage = response.message;
  }

  // 确保有返回消息
  if (!aiMessage) {
    console.error('API响应结构:', response);
    throw new Error('AI回复内容为空，请检查后端响应格式');
  }

  return {
    message: aiMessage,
    conversation_id: conversationId,
  };
}

/**
 * 创建新会话
 */
export async function createChatSession(
  employeeId: string,
  title: string
): Promise<{ id: string; title: string }> {
  const response = await apiClient.post<{
    id: string;
    title: string;
    employee_id: string;
  }>(API_ENDPOINTS.CHAT.SESSIONS, {
    employee_id: employeeId,
    title,
  });
  
  return {
    id: response.id,
    title: response.title,
  };
}

/**
 * 删除会话
 */
export async function deleteChatSession(sessionId: string): Promise<void> {
  await apiClient.delete(API_ENDPOINTS.CHAT.DELETE_SESSION(sessionId));
}

/**
 * 兼容旧 mock API 的对象导出
 * 用于平滑迁移，后续可逐步替换为直接导入函数
 */
export const employeeApi = {
  getEmployees,
  getEmployeeById,
  getCategories,
  hireEmployee,
  trialEmployee,
  getChatSessions,
  getSessionMessages,
  sendChatMessage,
  createChatSession,
  deleteChatSession,
};

export default employeeApi;
