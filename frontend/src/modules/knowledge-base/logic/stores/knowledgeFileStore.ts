import { create } from 'zustand';
import { KnowledgeItem } from '@/shared/types/knowledge';

// 单个知识库的文件处理状态
export interface KBFileState {
  selectedFile: File | null;
  uploadedFileId: string | null;
  uploadedChunks: any[];
  parseResults: KnowledgeItem[];
  isUploading: boolean;
  isParsing: boolean;
  error: string | null;
}

// 全局配置（所有知识库共享）
export interface FileConfig {
  fileType: 'text' | 'table';
  chunkLength: number;
  overlapLength: number;
  autoSegment: boolean;
}

// 默认状态
export const defaultFileState = (): KBFileState => ({
  selectedFile: null,
  uploadedFileId: null,
  uploadedChunks: [],
  parseResults: [],
  isUploading: false,
  isParsing: false,
  error: null,
});

export const defaultConfig: FileConfig = {
  fileType: 'text',
  chunkLength: 2000,
  overlapLength: 30,
  autoSegment: true,
};

// 所有知识库的文件状态映射
interface FileStateMap {
  [kbId: string]: KBFileState;
}

interface KnowledgeFileStore {
  // 所有知识库的文件状态
  fileStates: FileStateMap;
  // 全局配置
  config: FileConfig;

  // Actions - 直接操作状态
  setSelectedFile: (kbId: string, file: File | null) => void;
  setParseResults: (kbId: string, results: KnowledgeItem[]) => void;
  appendParseResults: (kbId: string, results: KnowledgeItem[]) => void;
  setIsUploading: (kbId: string, value: boolean) => void;
  setIsParsing: (kbId: string, value: boolean) => void;
  setError: (kbId: string, error: string | null) => void;
  resetFileState: (kbId: string) => void;
  
  // 配置操作
  setConfig: (config: Partial<FileConfig>) => void;
  initConfig: (config: Partial<FileConfig>) => void;
  
  // 获取状态（用于非订阅场景）
  getFileState: (kbId: string) => KBFileState;
}

export const useKnowledgeFileStore = create<KnowledgeFileStore>((set, get) => ({
  fileStates: {},
  config: { ...defaultConfig },

  // 获取指定知识库的文件状态
  getFileState: (kbId: string): KBFileState => {
    return get().fileStates[kbId] || defaultFileState();
  },

  // 设置选中文件
  setSelectedFile: (kbId: string, file: File | null) => {
    set((s) => ({
      fileStates: {
        ...s.fileStates,
        [kbId]: {
          ...(s.fileStates[kbId] || defaultFileState()),
          selectedFile: file,
          error: null,
        },
      },
    }));
  },

  // 设置解析结果（覆盖）
  setParseResults: (kbId: string, results: KnowledgeItem[]) => {
    set((s) => ({
      fileStates: {
        ...s.fileStates,
        [kbId]: {
          ...(s.fileStates[kbId] || defaultFileState()),
          parseResults: results,
        },
      },
    }));
  },

  // 追加解析结果（用于追加文件）
  appendParseResults: (kbId: string, results: KnowledgeItem[]) => {
    set((s) => {
      const current = s.fileStates[kbId] || defaultFileState();
      return {
        fileStates: {
          ...s.fileStates,
          [kbId]: {
            ...current,
            parseResults: [...current.parseResults, ...results],
          },
        },
      };
    });
  },

  // 设置上传状态
  setIsUploading: (kbId: string, value: boolean) => {
    set((s) => ({
      fileStates: {
        ...s.fileStates,
        [kbId]: {
          ...(s.fileStates[kbId] || defaultFileState()),
          isUploading: value,
        },
      },
    }));
  },

  // 设置解析状态
  setIsParsing: (kbId: string, value: boolean) => {
    set((s) => ({
      fileStates: {
        ...s.fileStates,
        [kbId]: {
          ...(s.fileStates[kbId] || defaultFileState()),
          isParsing: value,
        },
      },
    }));
  },

  // 设置错误
  setError: (kbId: string, error: string | null) => {
    set((s) => ({
      fileStates: {
        ...s.fileStates,
        [kbId]: {
          ...(s.fileStates[kbId] || defaultFileState()),
          error,
        },
      },
    }));
  },

  // 重置文件状态
  resetFileState: (kbId: string) => {
    set((s) => ({
      fileStates: {
        ...s.fileStates,
        [kbId]: defaultFileState(),
      },
    }));
  },

  // 更新全局配置
  setConfig: (newConfig: Partial<FileConfig>) => {
    set((s) => ({
      config: { ...s.config, ...newConfig },
    }));
  },

  // 初始化配置
  initConfig: (cfg: Partial<FileConfig>) => {
    set({
      config: { ...defaultConfig, ...cfg },
    });
  },
}));
