/**
 * 数字员工 API 服务层
 * 替换原有的 mockDigitalEmployeeAPI
 */

import { apiClient } from '@/core/services/apiClient';
import { API_ENDPOINTS } from '@/core/config/api';
import {
  transformEmployeesFromApi,
  transformEmployeeFromApi,
  transformEmployeeToApi,
} from '@/shared/utils/transform';
import { CreatedEmployee } from '@/shared/types/digitalEmployee';
import { KnowledgeBase } from '@/shared/types/knowledge';

// API 响应类型
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
}

/**
 * 获取已创建的数字员工列表
 */
export async function getCreatedEmployees(): Promise<CreatedEmployee[]> {
  const response = await apiClient.get<ApiResponse<any[]>>(
    API_ENDPOINTS.EMPLOYEES.LIST
  );

  if (!response.success || !response.data) {
    throw new Error(response.message || '获取数字员工列表失败');
  }

  // 过滤出创建的数字员工（有 created 标签的）
  const employees = transformEmployeesFromApi(response.data);
  return employees.filter(
    (emp: any) => emp.tags?.includes('created') || emp.variant === 'created'
  ) as CreatedEmployee[];
}

/**
 * 获取单个数字员工详情
 */
export async function getDigitalEmployee(id: string): Promise<CreatedEmployee> {
  const response = await apiClient.get<ApiResponse<any>>(
    API_ENDPOINTS.EMPLOYEES.DETAIL(id)
  );

  if (!response.success || !response.data) {
    throw new Error(response.message || '获取数字员工详情失败');
  }

  return transformEmployeeFromApi(response.data) as CreatedEmployee;
}

/**
 * 创建数字员工
 */
export async function createDigitalEmployee(
  employee: Partial<CreatedEmployee>
): Promise<CreatedEmployee> {
  const data = transformEmployeeToApi({
    ...employee,
    tags: [...(employee.tags || []), 'created'],
    status: employee.status || 'draft',
  });

  const response = await apiClient.post<ApiResponse<any>>(
    API_ENDPOINTS.EMPLOYEES.CREATE,
    data
  );

  if (!response.success || !response.data) {
    throw new Error(response.message || '创建数字员工失败');
  }

  return transformEmployeeFromApi(response.data) as CreatedEmployee;
}

/**
 * 保存数字员工（创建或更新）
 */
export async function saveDigitalEmployee(
  employee: Partial<CreatedEmployee> & { id?: string }
): Promise<CreatedEmployee> {
  if (employee.id) {
    // 更新现有员工
    return updateDigitalEmployee(employee.id, employee);
  } else {
    // 创建新员工
    return createDigitalEmployee(employee);
  }
}

/**
 * 更新数字员工
 */
export async function updateDigitalEmployee(
  id: string,
  employee: Partial<CreatedEmployee>
): Promise<CreatedEmployee> {
  const data = transformEmployeeToApi(employee);

  const response = await apiClient.put<ApiResponse<any>>(
    API_ENDPOINTS.EMPLOYEES.UPDATE(id),
    data
  );

  if (!response.success || !response.data) {
    throw new Error(response.message || '更新数字员工失败');
  }

  return transformEmployeeFromApi(response.data) as CreatedEmployee;
}

/**
 * 删除数字员工
 */
export async function deleteDigitalEmployee(id: string): Promise<void> {
  const response = await apiClient.delete<ApiResponse<any>>(
    API_ENDPOINTS.EMPLOYEES.DELETE(id)
  );

  if (!response.success) {
    throw new Error(response.message || '删除数字员工失败');
  }
}

/**
 * 发布数字员工
 */
export async function publishDigitalEmployee(
  id: string
): Promise<CreatedEmployee> {
  const response = await apiClient.post<ApiResponse<any>>(
    API_ENDPOINTS.EMPLOYEES.PUBLISH(id)
  );

  if (!response.success || !response.data) {
    throw new Error(response.message || '发布数字员工失败');
  }

  return transformEmployeeFromApi(response.data) as CreatedEmployee;
}

/**
 * 生成预览回复
 */
export async function generatePreviewResponse(
  employeeId: string,
  input: string
): Promise<string> {
  const response = await apiClient.post<{
    message: string;
    conversation_id?: string;
  }>(API_ENDPOINTS.CHAT.SEND, {
    message: input,
    employee_id: employeeId,
    stream: false,
  });

  return response.message || '暂无回复';
}

/**
 * 获取知识库列表
 */
export async function getKnowledgeBases(): Promise<KnowledgeBase[]> {
  const response = await apiClient.get<ApiResponse<any[]>>(
    API_ENDPOINTS.KNOWLEDGE_BASE.LIST
  );

  if (!response.success || !response.data) {
    return [];
  }

  return response.data.map((kb: any) => ({
    id: kb.id,
    name: kb.name,
    description: kb.description,
    docCount: kb.doc_count || 0,
    createdAt: kb.created_at || new Date().toISOString(),
    updatedAt: kb.updated_at || new Date().toISOString(),
    createdBy: kb.created_by || 'system',
    status: kb.status || 'active',
    tags: kb.tags || [],
    isPublic: kb.is_public ?? true,
    vectorized: kb.vectorized ?? false,
  }));
}

/**
 * 兼容旧 mock API 的对象导出
 */
export const digitalEmployeeApi = {
  getCreatedEmployees,
  getDigitalEmployee,
  createDigitalEmployee,
  saveDigitalEmployee,
  updateDigitalEmployee,
  deleteDigitalEmployee,
  publishDigitalEmployee,
  generatePreviewResponse,
  getKnowledgeBases,
};

export default digitalEmployeeApi;
