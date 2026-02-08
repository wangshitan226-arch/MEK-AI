import { KnowledgeBase, KnowledgeItem, FileUploadConfig, ParsedFileResult } from '@/shared/types/knowledge';

// === 数据状态管理类型 ===
export interface KnowledgeBaseState {
  knowledgeBases: KnowledgeBase[];
  currentKBId: string | null;
  loading: boolean;
  error: string | null;
}

export interface KnowledgeBaseActions {
  // 知识库CRUD
  createKnowledgeBase: (name: string, description?: string) => Promise<KnowledgeBase>;
  updateKnowledgeBase: (id: string, updates: Partial<KnowledgeBase>) => Promise<void>;
  deleteKnowledgeBase: (id: string) => Promise<void>;
  loadKnowledgeBases: () => Promise<void>;
  setCurrentKBId: (id: string | null) => void;
  
  // 文档管理
  addDocumentToKB: (kbId: string, fileData: any) => Promise<ParsedFileResult>;
  getDocumentsByKB: (kbId: string) => Promise<KnowledgeItem[]>;
  deleteDocument: (kbId: string, docId: string) => Promise<void>;
}

export type KnowledgeBaseStore = KnowledgeBaseState & KnowledgeBaseActions;

// === UI状态管理类型 ===
export interface KnowledgeBaseUIState {
  isBuildKBModalOpen: boolean;
  isAddFileModalOpen: boolean;
  activeModal: 'create' | 'upload' | 'settings' | null;
}

export interface KnowledgeBaseUIActions {
  openBuildKBModal: () => void;
  closeBuildKBModal: () => void;
  openAddFileModal: (kbId?: string) => void;
  closeAddFileModal: () => void;
  setActiveModal: (modal: KnowledgeBaseUIState['activeModal']) => void;
  resetUI: () => void;
}

export type KnowledgeBaseUIStore = KnowledgeBaseUIState & KnowledgeBaseUIActions;

// === 文件处理状态类型 ===
export interface FileProcessingState {
  selectedFile: File | null;
  uploadedFileId: string | null;
  isUploading: boolean;
  isParsing: boolean;
  parseResults: KnowledgeItem[];
  uploadConfig: FileUploadConfig;
}

export interface FileProcessingActions {
  setSelectedFile: (file: File | null) => void;
  setUploadedFileId: (id: string | null) => void;
  setIsUploading: (uploading: boolean) => void;
  setIsParsing: (parsing: boolean) => void;
  setParseResults: (results: KnowledgeItem[]) => void;
  setUploadConfig: (config: FileUploadConfig) => void;
  updateConfigField: <K extends keyof FileUploadConfig>(field: K, value: FileUploadConfig[K]) => void;
  resetFileProcessing: () => void;
}

export type FileProcessingStore = FileProcessingState & FileProcessingActions;

// === 服务层接口 ===
export interface IKnowledgeBaseService {
  // 知识库管理
  getKnowledgeBases: () => Promise<KnowledgeBase[]>;
  createKnowledgeBase: (data: { name: string; description?: string }) => Promise<KnowledgeBase>;
  updateKnowledgeBase: (id: string, data: Partial<KnowledgeBase>) => Promise<KnowledgeBase>;
  deleteKnowledgeBase: (id: string) => Promise<boolean>;
  
  // 文档管理
  getDocuments: (kbId: string) => Promise<KnowledgeItem[]>;
  uploadDocument: (kbId: string, file: File, config?: { chunkSize?: number; chunkOverlap?: number }) => Promise<{ fileId: string; fileUrl?: string; chunksProcessed?: number; chunks?: any[] }>;
  parseDocument: (fileId: string, config: FileUploadConfig) => Promise<{ knowledgeList: KnowledgeItem[] }>;
  saveParsedKnowledge: (kbId: string, knowledgeList: KnowledgeItem[]) => Promise<boolean>;
  deleteKnowledgeItem: (kbId: string, itemId: string) => Promise<boolean>;
  clearKnowledgeItems: (kbId: string) => Promise<boolean>;
  
  // 配置管理
  getDefaultConfig: () => Promise<FileUploadConfig>;
  saveConfig: (config: FileUploadConfig) => Promise<FileUploadConfig>;
}