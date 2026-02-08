// AI组件使用的原始类型（保持与Gemini生成的一致）
export interface KnowledgeBaseItem {
    id: string;
    name: string;
    docCount: number;
  }
  
  export interface ParsedKnowledgeItem {
    knowledgeId: string;
    serialNo: number;
    content: string;
    wordCount: number;
    createTime: string;
  }