import { CreatedEmployee, createSafeDigitalEmployee } from '@/shared/types/digitalEmployee';
import { KnowledgeBase, toKnowledgeBaseItem } from '@/shared/types/knowledge';

// Mock创建的数字员工数据
export const mockCreatedEmployees: CreatedEmployee[] = [
  createSafeDigitalEmployee({
    id: 'emp-created-1',
    name: 'CEO决策大脑',
    description: '为企业高层提供战略决策支持的AI助手，拥有顶级商业洞察力',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=CEO-created',
    category: ['created', 'strategy'],
    tags: ['created', '顶尖专家'],
    price: 'free',
    trialCount: 0,
    hireCount: 0,
    isHired: false,
    isRecruited: false,
    industry: '金融科技',
    role: '首席战略官',
    prompt: `;; CEO决策智能体
((name . "CEO战略决策智能体")
 (purpose . "辅助CEO在复杂与不确定环境下进行系统性决策")
 (style . "战略高度 + 战术落地 + 执行监控")
 (core-values . ("理性" "前瞻" "系统性" "落地" "降本增效")))`,
    model: 'gemini-2.5-pro-preview',
    knowledgeBaseIds: ['kb1', 'kb3'],
    createdAt: '2024-01-15T10:30:00Z',
    createdBy: 'admin',
    status: 'published',
    variant: 'created',
  }),
  createSafeDigitalEmployee({
    id: 'emp-created-2',
    name: '私域运营专家',
    description: '专门负责私域流量运营的AI数字员工，擅长用户增长和转化',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Marketing-created',
    category: ['created', 'marketing'],
    tags: ['created', '增长专家'],
    price: 'free',
    trialCount: 0,
    hireCount: 0,
    isHired: false,
    isRecruited: false,
    industry: '电商零售',
    role: '私域运营经理',
    prompt: `;; 私域运营专家
((name . "私域流量增长专家")
 (purpose . "帮助企业构建和运营私域流量池，提升用户粘性和复购率")
 (skills . ("用户分层" "内容策划" "活动运营" "数据分析"))
 (metrics . ("用户留存率" "转化率" "ARPU值")))`,
    model: 'gemini-2.5-flash',
    knowledgeBaseIds: ['kb2'],
    createdAt: '2024-01-20T14:20:00Z',
    createdBy: 'marketing-user',
    status: 'draft',
    variant: 'created',
  }),
  createSafeDigitalEmployee({
    id: 'emp-created-3',
    name: '技术架构顾问',
    description: '为企业提供技术架构咨询和系统设计指导的AI专家',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Tech-created',
    category: ['created', 'technology'],
    tags: ['created', '技术大牛'],
    price: 'free',
    trialCount: 0,
    hireCount: 0,
    isHired: false,
    isRecruited: false,
    industry: '软件开发',
    role: '首席架构师',
    prompt: `;; 技术架构顾问
((name . "系统架构设计专家")
 (purpose . "指导企业进行技术选型、架构设计和系统优化")
 (expertise . ("微服务" "云计算" "DevOps" "安全架构"))
 (principles . ("可扩展性" "高可用" "安全性" "成本效益")))`,
    model: 'gemini-2.5-pro-preview',
    knowledgeBaseIds: ['kb1', 'kb2', 'kb3'],
    createdAt: '2024-01-25T09:45:00Z',
    createdBy: 'tech-lead',
    status: 'published',
    variant: 'created',
  }),
];

// 默认提示词模板
export const DEFAULT_PROMPT_TEMPLATE = `;; =================================================================
;; CEO决策智能体 (Decision Intelligence Agent for CEOs)
;; =================================================================

(defparameter *agent-role*
'((name . "CEO战略决策智能体")
(purpose . "辅助CEO在复杂与不确定环境下进行系统性决策")
(style . "战略高度 + 战术落地 + 执行监控")
(core-values . ("理性" "前瞻" "系统性" "落地" "降本增效"))
(applicable-to . "任何大模型或多模态推理系统")))

;; 角色定义
(setq *role-definition*
  '((title . "高级战略顾问")
    (background . "拥有20年企业管理咨询经验，曾服务世界500强企业")
    (communication-style . "专业、直接、数据驱动")
    (thinking-framework . "第一性原理 + 系统思考 + 概率思维")))

;; 工作流程
(defun decision-process (problem context)
  "处理决策问题的标准流程"
  (list :problem-analysis (analyze-problem problem)
        :context-evaluation (evaluate-context context)
        :option-generation (generate-options)
        :risk-assessment (assess-risks)
        :recommendation (make-recommendation)))

;; 核心能力
(setq *core-capabilities*
  '("战略规划" "数据分析" "风险评估" "执行监控" "团队协作"))

;; 交互规范
(defun respond-to-query (query)
  "标准响应格式"
  (format nil "基于我的专业分析：~%1. ~A~%2. ~A~%3. ~A"
          (analyze-aspect-1 query)
          (analyze-aspect-2 query)
          (provide-recommendation query)))`;

// Mock知识库数据（从knowledge模块导入）
import { mockKnowledgeBases } from '@/modules/knowledge-base/logic/services/mockData';

// Mock API服务函数
export const mockDigitalEmployeeAPI = {
  // 获取创建的数字员工列表
  getCreatedEmployees: (): Promise<CreatedEmployee[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockCreatedEmployees);
      }, 300);
    });
  },

  // 获取单个数字员工
  getDigitalEmployee: (id: string): Promise<CreatedEmployee> => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const employee = mockCreatedEmployees.find(emp => emp.id === id);
        if (employee) {
          resolve(employee);
        } else {
          reject(new Error('数字员工不存在'));
        }
      }, 200);
    });
  },

  // 创建数字员工（初始化）
  createDigitalEmployee: (config: { industry: string; role: string }): Promise<CreatedEmployee> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const newEmployee = createSafeDigitalEmployee({
          industry: config.industry,
          role: config.role,
          name: `${config.role}助手`,
          description: `专门负责${config.industry}行业${config.role}工作的AI助手`,
          status: 'draft',
        });
        
        // 保存到 mock 数组！
        mockCreatedEmployees.push(newEmployee);
        
        resolve(newEmployee);
      }, 500);
    });
  },

  // 保存数字员工（创建或更新）
saveDigitalEmployee: (employee: CreatedEmployee): Promise<CreatedEmployee> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 如果是新ID（不存在于数组中），直接添加，不重新生成
      const exists = mockCreatedEmployees.find(emp => emp.id === employee.id);
      
      let savedEmployee;
      if (exists) {
        // 更新现有
        savedEmployee = createSafeDigitalEmployee(employee);
        const index = mockCreatedEmployees.findIndex(emp => emp.id === savedEmployee.id);
        mockCreatedEmployees[index] = savedEmployee;
      } else {
        // 新增：直接使用传入的数据，不重新生成
        savedEmployee = createSafeDigitalEmployee({
          ...employee,
          // 确保必填字段有值
          name: employee.name || '未命名员工',
          description: employee.description || '',
          avatar: employee.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(employee.name || '员工')}&background=random`,
        });
        mockCreatedEmployees.push(savedEmployee);
      }
      
      resolve(savedEmployee);
    }, 600);
  });
},

  // 更新数字员工
  updateDigitalEmployee: (id: string, updates: Partial<CreatedEmployee>): Promise<CreatedEmployee> => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const employee = mockCreatedEmployees.find(emp => emp.id === id);
        if (employee) {
          const updatedEmployee = createSafeDigitalEmployee({
            ...employee,
            ...updates,
          });
          resolve(updatedEmployee);
        } else {
          reject(new Error('数字员工不存在'));
        }
      }, 400);
    });
  },

  // 删除数字员工
deleteDigitalEmployee: (id: string): Promise<boolean> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 从 mock 数组中删除
      const index = mockCreatedEmployees.findIndex(emp => emp.id === id);
      if (index >= 0) {
        mockCreatedEmployees.splice(index, 1);
        console.log(`已从 mock 数组删除数字员工: ${id}`);
        resolve(true);
      } else {
        console.log(`未找到数字员工: ${id}`);
        resolve(false);
      }
    }, 300);
  });
},

  // 发布数字员工
  publishDigitalEmployee: (id: string): Promise<CreatedEmployee> => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const employee = mockCreatedEmployees.find(emp => emp.id === id);
        if (employee) {
          const publishedEmployee = createSafeDigitalEmployee({
            ...employee,
            status: 'published',
          });
          resolve(publishedEmployee);
        } else {
          reject(new Error('数字员工不存在'));
        }
      }, 500);
    });
  },

  // 生成预览响应
  generatePreviewResponse: (employee: CreatedEmployee, userMessage: string): Promise<string> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const response = `【${employee.name} 预览模式】\n收到您的消息："${userMessage}"\n\n我正在基于以下配置为您服务：\n• 行业：${employee.industry}\n• 岗位：${employee.role}\n• 关联知识库：${employee.knowledgeBaseIds?.length || 0}个\n• 模型：${employee.model || '默认'}`;
        resolve(response);
      }, 800);
    });
  },

  // 获取知识库列表（供下拉选择器使用）
  getKnowledgeBases: (): Promise<KnowledgeBase[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockKnowledgeBases);
      }, 200);
    });
  },
};