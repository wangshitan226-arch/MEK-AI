/**
 * API 配置文件
 * 定义基础URL、端点和全局配置
 */

// API 基础配置
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api/v1',
  TIMEOUT: 30000, // 30秒超时
  RETRY_COUNT: 3,
  RETRY_DELAY: 1000,
} as const;

// HTTP 请求头常量
export const API_HEADERS = {
  CONTENT_TYPE: 'Content-Type',
  AUTHORIZATION: 'Authorization',
  X_EMPLOYEE_ID: 'X-Employee-ID',
  X_USER_ID: 'X-User-ID',
  ACCEPT: 'Accept',
} as const;

// API 端点定义
export const API_ENDPOINTS = {
  // 员工相关
  EMPLOYEES: {
    LIST: '/employees',
    DETAIL: (id: string) => `/employees/${id}`,
    CREATE: '/employees',
    UPDATE: (id: string) => `/employees/${id}`,
    DELETE: (id: string) => `/employees/${id}`,
    PUBLISH: (id: string) => `/employees/${id}/publish`,
    CATEGORIES: '/employees/categories',
    PREVIEW: '/employees/preview',
  },

  // 市场广场相关
  MARKETPLACE: {
    LIST: '/marketplace/employees',
    HIRE: (id: string) => `/marketplace/${id}/hire`,
    TRIAL: (id: string) => `/marketplace/${id}/trial`,
    CATEGORIES: '/marketplace/categories',
    INDUSTRIES: '/marketplace/industries',
  },

  // 聊天相关
  CHAT: {
    SEND: '/chat',
    STREAM: '/chat/stream',
    SESSIONS: '/chat/sessions',
    SESSION_DETAIL: (id: string) => `/chat/sessions/${id}`,
    SESSION_MESSAGES: (id: string) => `/chat/sessions/${id}/messages`,
    DELETE_SESSION: (id: string) => `/chat/sessions/${id}`,
  },

  // 知识库相关
  KNOWLEDGE_BASE: {
    LIST: '/knowledge-bases',
    DETAIL: (id: string) => `/knowledge-bases/${id}`,
    CREATE: '/knowledge-bases',
    UPDATE: (id: string) => `/knowledge-bases/${id}`,
    DELETE: (id: string) => `/knowledge-bases/${id}`,
    DOCUMENTS: (id: string) => `/knowledge-bases/${id}/documents`,
    UPLOAD: (id: string) => `/knowledge-bases/${id}/upload`,
    PARSE: (id: string) => `/knowledge-bases/${id}/parse`,
    CONFIG: '/knowledge-bases/config',
  },

  // 用户相关 (预留)
  USER: {
    PROFILE: '/users/profile',
    PREFERENCES: '/users/preferences',
  },
} as const;

// API 响应状态码
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_ERROR: 500,
} as const;

// API 错误码映射
export const API_ERROR_CODES = {
  EMPLOYEE_NOT_FOUND: 'EMPLOYEE_NOT_FOUND',
  INVALID_REQUEST: 'INVALID_REQUEST',
  AI_SERVICE_ERROR: 'AI_SERVICE_ERROR',
  KNOWLEDGE_BASE_ERROR: 'KNOWLEDGE_BASE_ERROR',
  UNAUTHORIZED: 'UNAUTHORIZED',
  RATE_LIMITED: 'RATE_LIMITED',
} as const;

// 环境判断
export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD;

// 是否使用 Mock 数据 (开发环境可切换)
export const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK === 'true' || false;
