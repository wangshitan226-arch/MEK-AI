// src/modules/marketplace/logic/services/mockData.ts
import { Employee, Category, ChatSession, Message } from '../../../../ui-pages/marketplace/types';

// Mock员工数据（基于原网站示例）
export const mockEmployees: Employee[] = [
  {
    id: '1',
    name: 'CEO决策大脑',
    description: '为企业高层提供战略决策支持的AI助手，拥有顶级商业洞察力',
    category: ['战略管理', '数据分析'],
    tags: ['顶尖专家', '行业专家', '高配版'],
    price: 2999,
    trialCount: 156,
    hireCount: 89,
    isHired: false, // Default not recruited
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=CEO'
  },
  {
    id: '10086',
    name: 'CEO决策大脑',
    description: '拥有世界顶级智慧，富有全面的思考和判断，给出建议和思考判断。',
    category: ['pro', 'strategy'],
    tags: ['顶尖专家', '2试用', '1招聘'],
    price: 1980,
    originalPrice: 1980,
    trialCount: 2,
    hireCount: 1,
    avatar: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=200&q=80',
  },
  {
    id: '2',
    name: 'AI提问助手',
    description: '帮助你提出更好问题的AI助手，提升思考深度',
    category: ['战略管理', '沟通协作'],
    tags: ['效率工具', '初学者友好'],
    price: 2000,
    trialCount: 423,
    hireCount: 287,
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Assistant'
  },
  {
    id: '3',
    name: '私域运营专家',
    description: '专门负责私域流量运营的AI数字员工',
    category: ['获客引流', '私域运营'],
    tags: ['增长黑客', '转化专家'],
    price: 1999,
    trialCount: 89,
    hireCount: 45,
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Marketing'
  },
  {
    id: '4',
    name: '客服销售助手',
    description: '7x24小时在线客服，自动处理常见问题',
    category: ['客服销售', '技术支持'],
    tags: ['全天候', '多语言'],
    price: 1499,
    trialCount: 312,
    hireCount: 167,
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Support'
  },
  {
    id: '5',
    name: '品牌营销官',
    description: '负责品牌建设与营销策划的AI专家',
    category: ['品牌营销', '内容创作'],
    tags: ['创意专家', '爆款制造'],
    price: 2499,
    trialCount: 78,
    hireCount: 32,
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Brand'
  },
  {
    id: '6',
    name: '技术架构师',
    description: '为企业提供技术架构咨询的AI专家',
    category: ['技术支持', '产品开发'],
    tags: ['技术大牛', '架构专家'],
    price: 3999,
    trialCount: 45,
    hireCount: 23,
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Tech'
  }
];

// Mock分类数据
export const mockCategories: Category[] = [
  { id: 'all', name: '全部', count: 6 },
  { id: 'strategy', name: '战略管理', count: 2 },
  { id: 'marketing', name: '获客引流', count: 1 },
  { id: 'operation', name: '私域运营', count: 1 },
  { id: 'sales', name: '客服销售', count: 1 },
  { id: 'brand', name: '品牌营销', count: 1 },
  { id: 'tech', name: '技术支持', count: 2 },
];

// Mock 聊天会话数据
export const mockSessions: ChatSession[] = [
    { id: 's1', title: '学习数学的有效方法和策略推荐', employeeId: '2', lastModified: Date.now() },
    { id: 's2', title: '如何让孩子有效学好英语', employeeId: '2', lastModified: Date.now() - 100000 },
    { id: 's3', title: '孩子如何高效学英语的文案创作...', employeeId: '2', lastModified: Date.now() - 200000 },
    { id: 's4', title: '孩子如何学好英语的口播文案', employeeId: '2', lastModified: Date.now() - 300000 },
  ];
  
  // Mock 消息数据
  export const mockMessagesMap: Record<string, Message[]> = {
    's1': [
      { id: 'm1', role: 'user', content: '请给我推荐一些学习数学的好方法', timestamp: Date.now() - 50000 },
      { 
        id: 'm2', 
        role: 'model', 
        content: '学习数学的有效方法包括：\n1. 理解而非死记硬背公式。\n2. 多做练习题，尤其是错题整理。\n3. 建立知识体系，将知识点串联起来。', 
        timestamp: Date.now() - 40000 
      }
    ]
  };

// Mock API服务函数
export const mockMarketplaceAPI = {
  // 获取员工列表
  getEmployees: (): Promise<Employee[]> => {
    return new Promise((resolve) => {
      setTimeout(() => resolve(mockEmployees), ); // 模拟网络延迟
    });
  },
  
  // 获取分类列表
  getCategories: (): Promise<Category[]> => {
    return new Promise((resolve) => {
      setTimeout(() => resolve(mockCategories), );
    });
  },
  
  // 雇佣员工
  hireEmployee: (employeeId: string): Promise<{ success: boolean; message: string }> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const employee = mockEmployees.find(e => e.id === employeeId);
        if (employee) {
          resolve({
            success: true,
            message: `成功雇佣${employee.name}`
          });
        } else {
          resolve({
            success: false,
            message: '员工不存在'
          });
        }
      }, ); // 模拟较长的操作时间
    });
  },
  
  // 试用员工
  trialEmployee: (employeeId: string): Promise<{ success: boolean; message: string }> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          message: '开始7天试用'
        });
      }, );
    });
  },
  // 获取聊天会话列表
  getChatSessions: (employeeId: string): Promise<ChatSession[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockSessions.filter(session => session.employeeId === employeeId));
      }, );
    });
  },
  
  // 获取会话消息
  getSessionMessages: (sessionId: string): Promise<Message[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockMessagesMap[sessionId] || []);
      }, );
    });
  },
  
  // 发送消息 - 修复返回类型
  sendChatMessage: (sessionId: string | null, employeeId: string, content: string): Promise<{
    success: boolean;
    newSession?: ChatSession;
    newMessage: Message;
  }> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const newSessionId = sessionId || `s${Date.now()}`;
        const newMessageId = `m${Date.now()}`;
        
        const result: {
          success: boolean;
          newSession?: ChatSession;
          newMessage: Message;
        } = {
          success: true,
          newMessage: {
            id: newMessageId,
            role: 'model' as const,
            content: `这是 ${employeeId} 号员工的回复：${content}`,
            timestamp: Date.now()
          }
        };
        
        if (!sessionId) {
          result.newSession = {
            id: newSessionId,
            title: content.slice(0, 15) + (content.length > 15 ? '...' : ''),
            employeeId,
            lastModified: Date.now()
          };
        }
        
        resolve(result);
      }, );
    });
  }
};

