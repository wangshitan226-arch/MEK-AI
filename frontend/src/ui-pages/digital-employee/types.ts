// 市场页面使用的类型
export interface Employee {
    id: string;
    name: string;
    description: string;
    category: string[];
    tags: string[];
    price: number;
    originalPrice?: number;
    trialCount: number;
    hireCount: number;
    avatar?: string;
    isHot?: boolean;
    isRecruited?: boolean;
    isHired?: boolean;
  }
  
  export interface Category {
    id: string;
    name: string;
  }
  
  export interface ChatSession {
    id: string;
    title: string;
    employeeId: string;
    lastModified: number;
  }
  
  export interface Message {
    id: string;
    role: 'user' | 'model';
    content: string;
    timestamp: number;
  }