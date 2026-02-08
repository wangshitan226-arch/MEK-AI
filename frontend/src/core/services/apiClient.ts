/**
 * API 客户端
 * 封装 HTTP 请求，处理 headers、错误、超时和重试
 */

import { API_CONFIG, API_HEADERS, HTTP_STATUS } from '../config/api';
import { keysToCamel, keysToSnake } from '@/shared/utils/transform';

// API 错误类
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public errorCode?: string,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// 请求配置接口
interface RequestConfig extends RequestInit {
  timeout?: number;
  retryCount?: number;
  retryDelay?: number;
  skipTransform?: boolean; // 是否跳过自动转换
}

// 默认请求头
const getDefaultHeaders = (): Record<string, string> => {
  const headers: Record<string, string> = {
    [API_HEADERS.CONTENT_TYPE]: 'application/json',
    [API_HEADERS.ACCEPT]: 'application/json',
  };

  // 从 localStorage 获取用户上下文 (临时方案，后续使用 auth token)
  const userId = localStorage.getItem('userId') || 'anonymous';
  headers[API_HEADERS.X_USER_ID] = userId;
  
  // X-Employee-ID 是必需的
  const employeeId = localStorage.getItem('currentEmployeeId') || 'default-employee';
  headers[API_HEADERS.X_EMPLOYEE_ID] = employeeId;

  return headers;
};

// 设置当前员工上下文 (用于聊天)
export const setEmployeeContext = (employeeId: string | null) => {
  if (employeeId) {
    localStorage.setItem('currentEmployeeId', employeeId);
  } else {
    localStorage.removeItem('currentEmployeeId');
  }
};

// 获取当前员工上下文
export const getEmployeeContext = (): string | null => {
  return localStorage.getItem('currentEmployeeId');
};

// 超时包装器
const fetchWithTimeout = (
  url: string,
  options: RequestInit,
  timeout: number
): Promise<Response> => {
  return Promise.race([
    fetch(url, options),
    new Promise<Response>((_, reject) =>
      setTimeout(() => reject(new ApiError('请求超时', 408)), timeout)
    ),
  ]);
};

// 延迟函数
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// 核心请求函数
async function request<T>(
  endpoint: string,
  config: RequestConfig = {}
): Promise<T> {
  const {
    timeout = API_CONFIG.TIMEOUT,
    retryCount = API_CONFIG.RETRY_COUNT,
    retryDelay = API_CONFIG.RETRY_DELAY,
    skipTransform = false,
    ...fetchConfig
  } = config;

  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  const headers = {
    ...getDefaultHeaders(),
    ...((fetchConfig.headers as Record<string, string>) || {}),
  };

  // 转换请求体
  let body = fetchConfig.body;
  if (body && typeof body === 'object' && !skipTransform) {
    body = JSON.stringify(keysToSnake(body));
  }

  let lastError: Error | null = null;

  // 重试逻辑
  for (let attempt = 0; attempt <= retryCount; attempt++) {
    try {
      const response = await fetchWithTimeout(
        url,
        { ...fetchConfig, headers, body },
        timeout
      );

      // 处理无内容响应
      if (response.status === 204) {
        return {} as T;
      }

      // 解析响应
      const data = await response.json();

      // 检查业务错误
      if (!response.ok) {
        throw new ApiError(
          data.message || data.detail || '请求失败',
          response.status,
          data.code,
          data
        );
      }

      // 转换响应数据
      if (!skipTransform) {
        return keysToCamel(data) as T;
      }
      return data as T;
    } catch (error) {
      lastError = error as Error;

      // 如果是 ApiError 且不是网络错误，不重试
      if (error instanceof ApiError && error.statusCode < 500) {
        throw error;
      }

      // 最后一次尝试，直接抛出错误
      if (attempt === retryCount) {
        break;
      }

      // 等待后重试
      await delay(retryDelay * Math.pow(2, attempt));
    }
  }

  // 所有重试失败
  if (lastError instanceof ApiError) {
    throw lastError;
  }
  throw new ApiError(
    lastError?.message || '网络请求失败',
    HTTP_STATUS.INTERNAL_ERROR
  );
}

// HTTP 方法封装
export const apiClient = {
  // GET 请求
  get: <T>(endpoint: string, config?: RequestConfig) =>
    request<T>(endpoint, { ...config, method: 'GET' }),

  // POST 请求
  post: <T>(endpoint: string, data?: any, config?: RequestConfig) =>
    request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),

  // PUT 请求
  put: <T>(endpoint: string, data?: any, config?: RequestConfig) =>
    request<T>(endpoint, {
      ...config,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),

  // PATCH 请求
  patch: <T>(endpoint: string, data?: any, config?: RequestConfig) =>
    request<T>(endpoint, {
      ...config,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    }),

  // DELETE 请求
  delete: <T>(endpoint: string, config?: RequestConfig) =>
    request<T>(endpoint, { ...config, method: 'DELETE' }),

  // 流式请求 (用于 SSE)
  stream: async (
    endpoint: string,
    data?: any,
    onMessage?: (chunk: string) => void,
    config?: RequestConfig
  ) => {
    const url = `${API_CONFIG.BASE_URL}${endpoint}`;
    const headers = {
      ...getDefaultHeaders(),
      Accept: 'text/event-stream',
    };

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: data ? JSON.stringify(keysToSnake(data)) : undefined,
      ...config,
    });

    if (!response.ok) {
      throw new ApiError('流式请求失败', response.status);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new ApiError('无法读取响应流', 500);
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') return;
          onMessage?.(data);
        }
      }
    }
  },
};

export default apiClient;
