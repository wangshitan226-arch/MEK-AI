/**
 * 数据转换工具
 * 处理 snake_case (后端) ↔ camelCase (前端) 的转换
 */

/**
 * 将 snake_case 字符串转换为 camelCase
 */
export function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

/**
 * 将 camelCase 字符串转换为 snake_case
 */
export function camelToSnake(str: string): string {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
}

/**
 * 递归将对象的 key 从 snake_case 转换为 camelCase
 */
export function keysToCamel(obj: any): any {
  if (obj === null || obj === undefined) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(item => keysToCamel(item));
  }

  if (typeof obj !== 'object') {
    return obj;
  }

  const result: any = {};
  for (const [key, value] of Object.entries(obj)) {
    const camelKey = snakeToCamel(key);
    result[camelKey] = keysToCamel(value);
  }
  return result;
}

/**
 * 递归将对象的 key 从 camelCase 转换为 snake_case
 */
export function keysToSnake(obj: any): any {
  if (obj === null || obj === undefined) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(item => keysToSnake(item));
  }

  if (typeof obj !== 'object') {
    return obj;
  }

  const result: any = {};
  for (const [key, value] of Object.entries(obj)) {
    const snakeKey = camelToSnake(key);
    result[snakeKey] = keysToSnake(value);
  }
  return result;
}

/**
 * 后端 Employee 数据 (snake_case) → 前端 Employee 数据 (camelCase)
 */
export function transformEmployeeFromApi(data: any): any {
  if (!data) return null;

  return {
    id: data.id,
    name: data.name,
    description: data.description,
    avatar: data.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(data.name)}&background=random`,
    category: data.category || [],
    tags: data.tags || [],
    price: data.price === 0 || data.price === 'free' ? 'free' : (data.price || 0),
    originalPrice: data.original_price,
    trialCount: data.trial_count || 0,
    hireCount: data.hire_count || 0,
    isHired: Boolean(data.is_hired),
    isRecruited: Boolean(data.is_recruited),
    isInTrial: data.is_in_trial,
    hiredAt: data.hired_at,
    createdAt: data.created_at,
    createdBy: data.created_by,
    status: data.status,
    skills: data.skills,
    knowledgeBaseIds: data.knowledge_base_ids,
    isHot: data.is_hot,
    industry: data.industry,
    role: data.role,
    prompt: data.prompt,
    model: data.model,
  };
}

/**
 * 前端 Employee 数据 (camelCase) → 后端 Employee 数据 (snake_case)
 */
export function transformEmployeeToApi(data: any): any {
  if (!data) return null;

  const result: any = {
    id: data.id,
    name: data.name,
    description: data.description,
    avatar: data.avatar,
    category: data.category,
    tags: data.tags,
    price: data.price === 'free' ? 0 : data.price,
    trial_count: data.trialCount,
    hire_count: data.hireCount,
    is_hired: data.isHired,
    is_recruited: data.isRecruited,
    status: data.status,
    skills: data.skills,
  };

  // 可选字段
  if (data.originalPrice !== undefined) result.original_price = data.originalPrice;
  if (data.isInTrial !== undefined) result.is_in_trial = data.isInTrial;
  if (data.hiredAt !== undefined) result.hired_at = data.hiredAt;
  if (data.createdAt !== undefined) result.created_at = data.createdAt;
  if (data.createdBy !== undefined) result.created_by = data.createdBy;
  if (data.knowledgeBaseIds !== undefined) result.knowledge_base_ids = data.knowledgeBaseIds;
  if (data.isHot !== undefined) result.is_hot = data.isHot;
  if (data.industry !== undefined) result.industry = data.industry;
  if (data.role !== undefined) result.role = data.role;
  if (data.prompt !== undefined) result.prompt = data.prompt;
  if (data.model !== undefined) result.model = data.model;

  return result;
}

/**
 * 后端 ChatMessage 数据 → 前端 Message 数据
 */
export function transformMessageFromApi(data: any): any {
  if (!data) return null;

  return {
    id: data.id || `msg-${Date.now()}`,
    role: data.role === 'assistant' ? 'model' : data.role,
    content: data.content,
    timestamp: data.timestamp ? new Date(data.timestamp).getTime() : Date.now(),
  };
}

/**
 * 前端 Message 数据 → 后端 ChatMessage 数据
 */
export function transformMessageToApi(data: any): any {
  if (!data) return null;

  return {
    id: data.id,
    role: data.role === 'model' ? 'assistant' : data.role,
    content: data.content,
    timestamp: data.timestamp ? new Date(data.timestamp).toISOString() : new Date().toISOString(),
  };
}

/**
 * 后端 ChatSession 数据 → 前端 ChatSession 数据
 */
export function transformSessionFromApi(data: any): any {
  if (!data) return null;

  return {
    id: data.id,
    title: data.title,
    employeeId: data.employee_id,
    lastModified: data.last_modified ? new Date(data.last_modified).getTime() : Date.now(),
  };
}

/**
 * 后端 KnowledgeBase 数据 → 前端 KnowledgeBase 数据
 */
export function transformKnowledgeBaseFromApi(data: any): any {
  if (!data) return null;

  return {
    id: data.id,
    name: data.name,
    description: data.description,
    docCount: data.doc_count || 0,
    createdAt: data.created_at || new Date().toISOString(),
    updatedAt: data.updated_at || new Date().toISOString(),
    createdBy: data.created_by || 'system',
    status: data.status || 'active',
    tags: data.tags || [],
    isPublic: data.is_public ?? true,
    vectorized: data.vectorized ?? false,
  };
}

/**
 * 前端 KnowledgeBase 数据 → 后端 KnowledgeBase 数据
 */
export function transformKnowledgeBaseToApi(data: any): any {
  if (!data) return null;

  return {
    id: data.id,
    name: data.name,
    description: data.description,
    doc_count: data.docCount,
    created_at: data.createdAt,
    updated_at: data.updatedAt,
    created_by: data.createdBy,
    status: data.status,
    tags: data.tags,
    is_public: data.isPublic,
    vectorized: data.vectorized,
  };
}

/**
 * 批量转换员工列表
 */
export function transformEmployeesFromApi(data: any[]): any[] {
  if (!Array.isArray(data)) return [];
  return data.map(transformEmployeeFromApi);
}

/**
 * 批量转换消息列表
 */
export function transformMessagesFromApi(data: any[]): any[] {
  if (!Array.isArray(data)) return [];
  return data.map(transformMessageFromApi);
}

/**
 * 批量转换会话列表
 */
export function transformSessionsFromApi(data: any[]): any[] {
  if (!Array.isArray(data)) return [];
  return data.map(transformSessionFromApi);
}

/**
 * 批量转换知识库列表
 */
export function transformKnowledgeBasesFromApi(data: any[]): any[] {
  if (!Array.isArray(data)) return [];
  return data.map(transformKnowledgeBaseFromApi);
}
