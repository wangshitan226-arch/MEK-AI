/**
 * 统一的Employee类型 - 所有模块都使用这个
 */
export interface Employee {
    id: string;
    name: string;
    description: string;
    avatar: string;
    category: string[];
    tags: string[];
    price: number | 'free';
    originalPrice?: number;
    trialCount: number;
    hireCount: number;
    isHired: boolean;
    isRecruited: boolean;
    isInTrial?: boolean;
    hiredAt?: string;
    createdAt?: string;
    createdBy?: string;
    status?: 'published' | 'archived'|'active' | 'inactive' | 'draft';
    skills?: string[];
    knowledgeBaseIds?: string[];
    isHot?: boolean;
    
    // 数字员工特有字段（可选）
    industry?: string;
    role?: string;
    prompt?: string;
    model?: string;
  }
  
  /**
   * 安全的数据规范化函数
   */
  export const normalizeEmployee = (data: any): Employee => {
    const name = data?.name || '未命名员工';
    const tags = Array.isArray(data?.tags) ? data.tags : [];
    
    // 检查是否为创建的数字员工
    const isCreated = tags.includes('created');
    
    return {
      id: data?.id || `emp-${Date.now()}`,
      name,
      description: data?.description || '',
      avatar: data?.avatar?.trim() ? data.avatar : `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`,
      category: Array.isArray(data?.category) ? data.category : 
                typeof data?.category === 'string' ? [data.category] : 
                isCreated ? ['created'] : ['默认'],
      tags,
      price: typeof data?.price === 'number' ? data.price : 
             data?.price === 'free' ? 'free' : 
             typeof data?.price === 'string' ? parseFloat(data.price) || 0 : 0,
      originalPrice: data?.originalPrice,
      trialCount: data?.trialCount || 0,
      hireCount: data?.hireCount || 0,
      isHired: Boolean(data?.isHired),
      isRecruited: Boolean(data?.isRecruited),
      isInTrial: data?.isInTrial,
      hiredAt: data?.hiredAt,
      createdAt: data?.createdAt || new Date().toISOString(),
      createdBy: data?.createdBy,
      status: data?.status,
      skills: data?.skills,
      knowledgeBaseIds: data?.knowledgeBaseIds,
      isHot: data?.isHot,
      
      // 数字员工特有字段
      industry: data?.industry,
      role: data?.role,
      prompt: data?.prompt,
      model: data?.model,
    };
  };
  
  /**
   * 创建安全的默认员工
   */
  export const createSafeEmployee = (overrides?: Partial<Employee>): Employee => ({
    id: 'unknown',
    name: '未知员工',
    description: '',
    avatar: 'https://ui-avatars.com/api/?name=Unknown&background=random',
    category: ['默认'],
    tags: [],
    price: 0,
    trialCount: 0,
    hireCount: 0,
    isHired: false,
    isRecruited: false,
    ...overrides
  });