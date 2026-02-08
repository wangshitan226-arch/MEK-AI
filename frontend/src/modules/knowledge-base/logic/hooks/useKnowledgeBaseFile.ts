import { useRef, useEffect, useCallback, useState, useSyncExternalStore } from 'react';
import { KnowledgeItem } from '@/shared/types/knowledge';
import { knowledgeBaseService } from '../services/knowledgeBaseService';
import { useKnowledgeBaseStore } from '../stores/knowledgeBaseStore';
import { useKnowledgeFileStore, defaultFileState, defaultConfig } from '../stores/knowledgeFileStore';

// 自定义 hook 用于订阅 store 的特定部分
function useFileState(kbId: string | undefined) {
  const store = useKnowledgeFileStore();
  const [state, setState] = useState(() => 
    kbId ? store.getFileState(kbId) : defaultFileState()
  );

  useEffect(() => {
    if (!kbId) return;
    
    // 订阅 store 变化
    const unsubscribe = useKnowledgeFileStore.subscribe((newStoreState) => {
      const newFileState = newStoreState.fileStates[kbId] || defaultFileState();
      setState(newFileState);
    });

    return unsubscribe;
  }, [kbId]);

  return state;
}

export const useKnowledgeBaseFile = (knowledgeBaseId?: string) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const kbStore = useKnowledgeBaseStore();
  const fileStore = useKnowledgeFileStore();
  
  // 使用自定义订阅 hook
  const fileState = useFileState(knowledgeBaseId);
  
  // 配置使用普通 selector（config 不会频繁变化）
  const config = useKnowledgeFileStore((state) => state.config);

  // 初始化配置 - 只执行一次
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const backendConfig = await knowledgeBaseService.getDefaultConfig();
        fileStore.initConfig({
          fileType: backendConfig.fileType === 'text' ? 'text' : 'table',
          chunkLength: backendConfig.knowledgeLength,
          overlapLength: backendConfig.overlapLength,
          autoSegment: backendConfig.lineBreakSegment,
        });
      } catch (err) {
        console.error('加载配置失败:', err);
      }
    };

    loadConfig();
  }, []);

  // 处理文件选择
  const handleFileChange = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    if (!knowledgeBaseId) return;

    const file = e.target.files[0];
    fileStore.setSelectedFile(knowledgeBaseId, file);
    // 重置之前的解析结果
    fileStore.setParseResults(knowledgeBaseId, []);
  }, [knowledgeBaseId, fileStore]);

  // 处理AI处理
  const handleAIProcess = useCallback(async () => {
    if (!knowledgeBaseId) return;
    
    // 从 store 获取最新状态
    const currentState = fileStore.getFileState(knowledgeBaseId);
    if (!currentState.selectedFile) {
      fileStore.setError(knowledgeBaseId, '请先选择文件');
      return;
    }

    fileStore.setIsUploading(knowledgeBaseId, true);
    fileStore.setIsParsing(knowledgeBaseId, true);
    fileStore.setError(knowledgeBaseId, null);

    try {
      const result = await knowledgeBaseService.uploadDocument(
        knowledgeBaseId, 
        currentState.selectedFile, 
        {
          chunkSize: config.chunkLength,
          chunkOverlap: config.overlapLength,
        }
      );

      if (result.chunks && result.chunks.length > 0) {
        // 获取最新的 parseResults
        const latestState = fileStore.getFileState(knowledgeBaseId);
        const startIndex = latestState.parseResults.length;
        const newKnowledgeItems: KnowledgeItem[] = result.chunks.map((chunk, index) => ({
          id: `ki-${Date.now()}-${index}`,
          knowledgeBaseId: knowledgeBaseId,
          serialNo: startIndex + index + 1,
          content: chunk.content || '',
          wordCount: chunk.word_count || chunk.content?.length || 0,
          createTime: new Date().toISOString(),
          sourceFile: currentState.selectedFile?.name,
          metadata: chunk.metadata || {},
        }));

        fileStore.appendParseResults(knowledgeBaseId, newKnowledgeItems);
      } else {
        fileStore.setError(knowledgeBaseId, '未获取到解析结果');
      }
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : '文件处理失败';
      fileStore.setError(knowledgeBaseId, errMsg);
    } finally {
      fileStore.setIsUploading(knowledgeBaseId, false);
      fileStore.setIsParsing(knowledgeBaseId, false);
    }
  }, [knowledgeBaseId, config, fileStore]);

  // 处理确认保存
  const handleConfirmSave = useCallback(async () => {
    if (!knowledgeBaseId) return false;
    
    const currentState = fileStore.getFileState(knowledgeBaseId);
    if (currentState.parseResults.length === 0) {
      fileStore.setError(knowledgeBaseId, '没有可保存的数据');
      return false;
    }

    try {
      const success = await knowledgeBaseService.saveParsedKnowledge(
        knowledgeBaseId, 
        currentState.parseResults
      );
      if (success) {
        await kbStore.loadKnowledgeBases();
        fileStore.resetFileState(knowledgeBaseId);
        return true;
      }
      return false;
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : '保存失败';
      fileStore.setError(knowledgeBaseId, errMsg);
      throw err;
    }
  }, [knowledgeBaseId, fileStore, kbStore]);

  // 触发文件选择
  const triggerFileSelect = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  // 配置操作
  const setFileType = useCallback((type: 'text' | 'table') => {
    fileStore.setConfig({ fileType: type });
  }, [fileStore]);

  const setChunkLength = useCallback((value: number) => {
    fileStore.setConfig({ chunkLength: value });
  }, [fileStore]);

  const setOverlapLength = useCallback((value: number) => {
    fileStore.setConfig({ overlapLength: value });
  }, [fileStore]);

  const setAutoSegment = useCallback((value: boolean) => {
    fileStore.setConfig({ autoSegment: value });
  }, [fileStore]);

  // 重置文件处理
  const resetFileProcessing = useCallback(() => {
    if (knowledgeBaseId) {
      fileStore.resetFileState(knowledgeBaseId);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [knowledgeBaseId, fileStore]);

  return {
    // 配置状态
    fileType: config.fileType,
    chunkLength: config.chunkLength,
    overlapLength: config.overlapLength,
    autoSegment: config.autoSegment,

    // 文件状态
    selectedFile: fileState.selectedFile,
    isUploading: fileState.isUploading,
    uploadedFileId: fileState.uploadedFileId,
    isParsing: fileState.isParsing,
    parseResults: fileState.parseResults,
    error: fileState.error,
    fileInputRef,

    // 配置操作
    setFileType,
    setChunkLength,
    setOverlapLength,
    setAutoSegment,

    // 文件操作
    handleFileChange,
    triggerFileSelect,
    handleAIProcess,
    handleConfirmSave,
    resetFileProcessing,

    // 工具函数
    canProcess: !!fileState.selectedFile && !fileState.isUploading && !fileState.isParsing,
    canSave: fileState.parseResults.length > 0 && !fileState.isParsing,
  };
};
