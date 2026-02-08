import { 
    KnowledgeBase, 
    KnowledgeItem, 
    FileUploadConfig,
    normalizeKnowledgeBase,
    normalizeKnowledgeItem 
  } from '@/shared/types/knowledge';
  
  // Mock知识库数据
  export const mockKnowledgeBases: KnowledgeBase[] = [
    {
      id: 'kb1',
      name: '企业AI战略报告',
      description: '包含企业AI战略规划、实施路径和案例分析',
      docCount: 9,
      createdAt: '2024-01-15T10:30:00Z',
      updatedAt: '2024-02-01T14:20:00Z',
      createdBy: 'admin',
      status: 'active',
      tags: ['战略', 'AI', '企业规划'],
      isPublic: true,
      vectorized: true,
    },
    {
      id: 'kb2',
      name: '产品需求文档',
      description: '各版本产品需求文档和用户反馈',
      docCount: 4,
      createdAt: '2024-01-20T09:15:00Z',
      updatedAt: '2024-01-28T16:45:00Z',
      createdBy: 'product-manager',
      status: 'active',
      tags: ['PRD', '需求', '用户反馈'],
      isPublic: false,
      vectorized: true,
    },
    {
      id: 'kb3',
      name: '技术架构设计',
      description: '系统架构、技术选型和设计文档',
      docCount: 7,
      createdAt: '2024-01-25T13:00:00Z',
      updatedAt: '2024-01-31T11:30:00Z',
      createdBy: 'tech-lead',
      status: 'active',
      tags: ['架构', '技术', '设计'],
      isPublic: true,
      vectorized: false,
    },
    {
      id: 'kb4',
      name: '市场分析报告',
      description: '行业市场趋势和竞争对手分析',
      docCount: 12,
      createdAt: '2024-02-01T08:45:00Z',
      updatedAt: '2024-02-01T08:45:00Z',
      createdBy: 'market-analyst',
      status: 'processing',
      tags: ['市场', '分析', '竞争'],
      isPublic: true,
      vectorized: false,
    },
    {
      id: 'kb5',
      name: '客户服务手册',
      description: '客服流程、话术和常见问题',
      docCount: 5,
      createdAt: '2024-01-18T14:30:00Z',
      updatedAt: '2024-01-25T10:15:00Z',
      createdBy: 'service-manager',
      status: 'active',
      tags: ['客服', '手册', 'FAQ'],
      isPublic: false,
      vectorized: true,
    },
  ];
  
  // Mock知识点数据
  export const mockKnowledgeItems: Record<string, KnowledgeItem[]> = {
    'kb1': [
      {
        id: 'ki-001',
        knowledgeBaseId: 'kb1',
        serialNo: 1,
        content: '人工智能（Artificial Intelligence，AI）是一门旨在使计算机系统能够模拟、延伸和扩展人类智能的技术科学。它涵盖了机器学习、自然语言处理、计算机视觉等多个领域，核心目标是让机器具备感知、推理、学习和决策的能力。',
        wordCount: 128,
        createTime: '2024-02-01T22:32:00Z',
        sourceFile: 'AI战略报告.pdf',
        metadata: { section: '第一章', page: 1, confidence: 0.95 },
      },
      {
        id: 'ki-002',
        knowledgeBaseId: 'kb1',
        serialNo: 2,
        content: '机器学习是人工智能的一个重要分支，它专注于开发能够从数据中学习并改进的算法，而无需显式编程。常见的机器学习类型包括监督学习、无监督学习和强化学习，广泛应用于推荐系统、图像识别、语音助手等场景。',
        wordCount: 115,
        createTime: '2024-02-01T22:32:00Z',
        sourceFile: 'AI战略报告.pdf',
        metadata: { section: '第二章', page: 3, confidence: 0.92 },
      },
    ],
    'kb2': [
      {
        id: 'ki-101',
        knowledgeBaseId: 'kb2',
        serialNo: 1,
        content: '用户反馈显示，当前版本的搜索功能准确率需要提升，特别是在长尾关键词的匹配上。建议引入语义搜索和向量化检索技术。',
        wordCount: 45,
        createTime: '2024-02-01T10:15:00Z',
        sourceFile: '用户反馈汇总.xlsx',
        metadata: { section: '搜索功能', confidence: 0.88 },
      },
    ],
  };
  
  // 默认配置
  export const defaultUploadConfig: FileUploadConfig = {
    fileType: 'text',
    knowledgeLength: 2000,
    overlapLength: 30,
    lineBreakSegment: true,
    maxSegmentLength: 500,
    updateTime: '2024-02-01T22:30:00Z',
  };
  
  // Mock API服务函数（与真实后端接口保持一致）
  export const mockKnowledgeBaseAPI = {
    // ========== 知识库管理 ==========
    getKnowledgeBases: (): Promise<KnowledgeBase[]> => {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(mockKnowledgeBases.map(normalizeKnowledgeBase));
        }, 300);
      });
    },
  
    createKnowledgeBase: (data: { name: string; description?: string }): Promise<KnowledgeBase> => {
      return new Promise((resolve) => {
        setTimeout(() => {
          const newKB: KnowledgeBase = {
            id: `kb-${Date.now()}`,
            name: data.name,
            description: data.description || '',
            docCount: 0,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            createdBy: 'current-user',
            status: 'active',
            tags: [],
            isPublic: true,
            vectorized: false,
          };
          mockKnowledgeBases.push(newKB);
          resolve(newKB);
        }, 500);
      });
    },
  
    updateKnowledgeBase: (id: string, updates: Partial<KnowledgeBase>): Promise<KnowledgeBase> => {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const kb = mockKnowledgeBases.find(k => k.id === id);
          if (kb) {
            const updated = { ...kb, ...updates, updatedAt: new Date().toISOString() };
            resolve(updated);
          } else {
            reject(new Error('知识库不存在'));
          }
        }, 300);
      });
    },
  
    deleteKnowledgeBase: (id: string): Promise<boolean> => {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(true);
        }, 300);
      });
    },
  
    // ========== 文档管理 ==========
    getDocuments: (kbId: string): Promise<KnowledgeItem[]> => {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(mockKnowledgeItems[kbId]?.map(normalizeKnowledgeItem) || []);
        }, 300);
      });
    },
  
    uploadDocument: (kbId: string, file: File): Promise<{ fileId: string; fileUrl: string }> => {
      return new Promise((resolve) => {
        setTimeout(() => {
          const fileId = `file-${Date.now()}`;
          const fileUrl = URL.createObjectURL(file);
          
          // 模拟上传进度（实际项目中应该使用XMLHttpRequest或fetch的progress事件）
          console.log(`Uploading ${file.name} to knowledge base ${kbId}`);
          
          resolve({ fileId, fileUrl });
        }, 1500);
      });
    },
  
    parseDocument: (
      fileId: string, 
      config: FileUploadConfig
    ): Promise<{ knowledgeList: KnowledgeItem[] }> => {
      return new Promise((resolve) => {
        setTimeout(() => {
          // 模拟解析结果
          const knowledgeList: KnowledgeItem[] = [
            {
              id: `ki-${Date.now()}-1`,
              knowledgeBaseId: 'temp',
              serialNo: 1,
              content: '这是从上传文件中解析出的第一个知识点。内容基于您的配置参数进行处理，确保分段和重叠长度符合要求。',
              wordCount: 35,
              createTime: new Date().toISOString(),
              sourceFile: 'uploaded-file.pdf',
              metadata: { 
                section: '解析结果', 
                confidence: 0.85,
                processingConfig: JSON.stringify(config)
              },
            },
            {
              id: `ki-${Date.now()}-2`,
              knowledgeBaseId: 'temp',
              serialNo: 2,
              content: '第二个知识点示例。系统会根据您设置的"知识点长度"和"重叠长度"智能分段，保留上下文连贯性。',
              wordCount: 42,
              createTime: new Date().toISOString(),
              sourceFile: 'uploaded-file.pdf',
              metadata: { 
                section: '解析结果', 
                confidence: 0.88,
                processingConfig: JSON.stringify(config)
              },
            },
            {
              id: `ki-${Date.now()}-3`,
              knowledgeBaseId: 'temp',
              serialNo: 3,
              content: '如果开启了"换行自动分段"，系统会在检测到换行符时创建新段落，但每段不会超过500字（根据配置）。',
              wordCount: 48,
              createTime: new Date().toISOString(),
              sourceFile: 'uploaded-file.pdf',
              metadata: { 
                section: '解析结果', 
                confidence: 0.90,
                processingConfig: JSON.stringify(config)
              },
            },
          ];
          
          resolve({ knowledgeList });
        }, 2000);
      });
    },
  
    saveParsedKnowledge: (kbId: string, knowledgeList: KnowledgeItem[]): Promise<boolean> => {
      return new Promise((resolve) => {
        setTimeout(() => {
          console.log(`Saving ${knowledgeList.length} knowledge items to KB ${kbId}`);
          resolve(true);
        }, 1000);
      });
    },
  
    // ========== 配置管理 ==========
    getDefaultConfig: (): Promise<FileUploadConfig> => {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(defaultUploadConfig);
        }, 200);
      });
    },
  
    saveConfig: (config: FileUploadConfig): Promise<FileUploadConfig> => {
      return new Promise((resolve) => {
        setTimeout(() => {
          const updatedConfig = {
            ...config,
            updateTime: new Date().toISOString(),
          };
          resolve(updatedConfig);
        }, 300);
      });
    },
  };