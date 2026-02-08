import React, { useState, useRef, useCallback, useEffect } from 'react';
// 导入AI生成的纯样式组件
import { KnowledgeBase } from '../../ui-pages/knowledge-base/components/KnowledgeBase';
import { BuildKnowledgeBase } from '../../ui-pages/knowledge-base/components/BuildKnowledgeBase';
import { AddFile } from '../../ui-pages/knowledge-base/components/AddFile';
// 导入业务逻辑Hook
import { useKnowledgeBase } from './logic/hooks/useKnowledgeBase';
import { knowledgeBaseService } from './logic/services/knowledgeBaseService';
import { useKnowledgeBaseStore } from './logic/stores/knowledgeBaseStore';
import { KnowledgeItem } from '@/shared/types/knowledge';

// 全局配置状态（所有知识库共享）
interface FileConfig {
  fileType: 'text' | 'table';
  chunkLength: number;
  overlapLength: number;
  autoSegment: boolean;
}

// 单个知识库的文件状态
interface KBFileState {
  selectedFile: File | null;
  parseResults: KnowledgeItem[];
  isUploading: boolean;
  isParsing: boolean;
  error: string | null;
}

export const KnowledgeBaseBridge: React.FC = () => {
  // 获取知识库主页面逻辑
  const knowledgeBase = useKnowledgeBase();
  const kbStore = useKnowledgeBaseStore();
  const currentKBId = knowledgeBase.currentKBId;

  // 全局配置
  const [config, setConfig] = useState<FileConfig>({
    fileType: 'text',
    chunkLength: 2000,
    overlapLength: 30,
    autoSegment: true,
  });

  // 每个知识库的文件状态
  const [kbFileStates, setKbFileStates] = useState<Record<string, KBFileState>>({});

  // 文件输入引用
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 初始化配置
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const backendConfig = await knowledgeBaseService.getDefaultConfig();
        setConfig({
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

  // 当打开知识库弹窗时，从后端加载已保存的知识点
  const hasLoadedRef = React.useRef(false);
  useEffect(() => {
    const loadSavedKnowledge = async () => {
      if (!currentKBId || !knowledgeBase.isAddFileModalOpen) return;
      
      // 使用 ref 防止重复加载
      if (hasLoadedRef.current) return;
      
      try {
        const items = await knowledgeBaseService.getDocuments(currentKBId);
        // 只有当当前没有预览数据时才加载（避免覆盖用户正在编辑的内容）
        const currentState = kbFileStates[currentKBId];
        if (!currentState?.parseResults || currentState.parseResults.length === 0) {
          if (items && items.length > 0) {
            setKbFileStates(prev => ({
              ...prev,
              [currentKBId]: {
                ...(prev[currentKBId] || { selectedFile: null, parseResults: [], isUploading: false, isParsing: false, error: null }),
                parseResults: items,
              },
            }));
          }
        }
        hasLoadedRef.current = true;
      } catch (err) {
        console.error('加载已保存知识点失败:', err);
      }
    };
    
    loadSavedKnowledge();
    
    // 弹窗关闭时重置 ref
    return () => {
      if (!knowledgeBase.isAddFileModalOpen) {
        hasLoadedRef.current = false;
      }
    };
  }, [currentKBId, knowledgeBase.isAddFileModalOpen]);

  // 获取当前知识库的文件状态
  const getCurrentFileState = (): KBFileState => {
    if (!currentKBId) {
      return { selectedFile: null, parseResults: [], isUploading: false, isParsing: false, error: null };
    }
    return kbFileStates[currentKBId] || { selectedFile: null, parseResults: [], isUploading: false, isParsing: false, error: null };
  };

  // 更新当前知识库的文件状态
  const updateFileState = (updates: Partial<KBFileState>) => {
    if (!currentKBId) return;
    setKbFileStates(prev => ({
      ...prev,
      [currentKBId]: {
        ...(prev[currentKBId] || { selectedFile: null, parseResults: [], isUploading: false, isParsing: false, error: null }),
        ...updates,
      },
    }));
  };

  // 当前状态
  const currentState = getCurrentFileState();

  // 处理文件选择
  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    if (!currentKBId) return;

    const file = e.target.files[0];
    updateFileState({
      selectedFile: file,
      error: null,
      parseResults: [], // 选择新文件时重置解析结果
    });
  }, [currentKBId]);

  // 处理AI处理
  const handleAIProcess = useCallback(async () => {
    if (!currentKBId) return;

    // 从 kbFileStates 获取最新状态，避免闭包问题
    const latestState = kbFileStates[currentKBId] || { selectedFile: null, parseResults: [], isUploading: false, isParsing: false, error: null };
    if (!latestState.selectedFile) return;

    // 设置上传状态
    setKbFileStates(prev => ({
      ...prev,
      [currentKBId]: {
        ...(prev[currentKBId] || { selectedFile: null, parseResults: [], isUploading: false, isParsing: false, error: null }),
        isUploading: true,
        isParsing: true,
        error: null,
      },
    }));

    try {
      const result = await knowledgeBaseService.uploadDocument(
        currentKBId,
        latestState.selectedFile,
        {
          chunkSize: config.chunkLength,
          chunkOverlap: config.overlapLength,
        }
      );

      if (result.chunks && result.chunks.length > 0) {
        // 再次获取最新状态（因为上传可能耗时，状态可能已变化）
        const currentFileState = kbFileStates[currentKBId] || { selectedFile: null, parseResults: [], isUploading: false, isParsing: false, error: null };
        const startIndex = currentFileState.parseResults.length;
        const newKnowledgeItems: KnowledgeItem[] = result.chunks.map((chunk, index) => ({
          id: `ki-${Date.now()}-${index}`,
          knowledgeBaseId: currentKBId,
          serialNo: startIndex + index + 1,
          content: chunk.content || '',
          wordCount: chunk.word_count || chunk.content?.length || 0,
          createTime: new Date().toISOString(),
          sourceFile: latestState.selectedFile?.name,
          metadata: chunk.metadata || {},
        }));

        setKbFileStates(prev => ({
          ...prev,
          [currentKBId]: {
            ...(prev[currentKBId] || { selectedFile: null, parseResults: [], isUploading: false, isParsing: false, error: null }),
            parseResults: [...currentFileState.parseResults, ...newKnowledgeItems],
            isUploading: false,
            isParsing: false,
          },
        }));
      } else {
        setKbFileStates(prev => ({
          ...prev,
          [currentKBId]: {
            ...(prev[currentKBId] || { selectedFile: null, parseResults: [], isUploading: false, isParsing: false, error: null }),
            error: '未获取到解析结果',
            isUploading: false,
            isParsing: false,
          },
        }));
      }
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : '文件处理失败';
      setKbFileStates(prev => ({
        ...prev,
        [currentKBId]: {
          ...(prev[currentKBId] || { selectedFile: null, parseResults: [], isUploading: false, isParsing: false, error: null }),
          error: errMsg,
          isUploading: false,
          isParsing: false,
        },
      }));
    }
  }, [currentKBId, kbFileStates, config]);

  // 处理确认保存
  const handleConfirmSave = async () => {
    if (!currentKBId || currentState.parseResults.length === 0) return false;

    try {
      const success = await knowledgeBaseService.saveParsedKnowledge(currentKBId, currentState.parseResults);
      if (success) {
        await kbStore.loadKnowledgeBases();
        // 重置当前知识库的文件状态
        updateFileState({
          selectedFile: null,
          parseResults: [],
          isUploading: false,
          isParsing: false,
          error: null,
        });
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        return true;
      }
      return false;
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : '保存失败';
      updateFileState({ error: errMsg });
      throw err;
    }
  };

  // 触发文件选择
  const triggerFileSelect = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  // 删除单个知识块
  const handleDeleteKnowledgeItem = useCallback(async (itemId: string) => {
    if (!currentKBId) return;
    try {
      // 先调用后端 API 删除
      await knowledgeBaseService.deleteKnowledgeItem(currentKBId, itemId);
      // 更新前端状态
      setKbFileStates(prev => {
        const currentState = prev[currentKBId];
        if (!currentState) return prev;
        return {
          ...prev,
          [currentKBId]: {
            ...currentState,
            parseResults: currentState.parseResults.filter(item => item.id !== itemId),
          },
        };
      });
      // 刷新知识库列表以更新 docCount
      await kbStore.loadKnowledgeBases();
    } catch (err) {
      console.error('删除知识块失败:', err);
      alert('删除知识块失败');
    }
  }, [currentKBId, kbStore]);

  // 一键清除所有知识块
  const handleClearAllKnowledge = useCallback(async () => {
    if (!currentKBId) return;
    if (!confirm('确定要清空所有知识块吗？此操作不可恢复。')) return;
    try {
      // 先调用后端 API 清空
      await knowledgeBaseService.clearKnowledgeItems(currentKBId);
      // 更新前端状态
      setKbFileStates(prev => ({
        ...prev,
        [currentKBId]: {
          ...(prev[currentKBId] || { selectedFile: null, parseResults: [], isUploading: false, isParsing: false, error: null }),
          parseResults: [],
        },
      }));
      // 刷新知识库列表以更新 docCount
      await kbStore.loadKnowledgeBases();
    } catch (err) {
      console.error('清空知识块失败:', err);
      alert('清空知识块失败');
    }
  }, [currentKBId, kbStore]);

  // 删除知识库
  const handleDeleteKnowledgeBase = useCallback(async (kbId: string) => {
    if (!confirm('确定要删除这个知识库吗？此操作不可恢复。')) return;
    try {
      await kbStore.deleteKnowledgeBase(kbId);
      // 清除该知识库的文件状态
      setKbFileStates(prev => {
        const newState = { ...prev };
        delete newState[kbId];
        return newState;
      });
    } catch (err) {
      alert('删除知识库失败');
    }
  }, [kbStore]);

  // 配置操作
  const setFileType = useCallback((type: 'text' | 'table') => {
    setConfig(prev => ({ ...prev, fileType: type }));
  }, []);

  const setChunkLength = useCallback((value: number) => {
    setConfig(prev => ({ ...prev, chunkLength: value }));
  }, []);

  const setOverlapLength = useCallback((value: number) => {
    setConfig(prev => ({ ...prev, overlapLength: value }));
  }, []);

  const setAutoSegment = useCallback((value: boolean) => {
    setConfig(prev => ({ ...prev, autoSegment: value }));
  }, []);

  return (
    <>
      {/* 知识库主页面 */}
      <KnowledgeBase
        items={knowledgeBase.knowledgeBases}
        onCreateClick={knowledgeBase.onCreateClick}
        onItemClick={knowledgeBase.onItemClick}
        onDeleteKnowledgeBase={handleDeleteKnowledgeBase}
        loading={knowledgeBase.loading}
        error={knowledgeBase.error}
      />

      {/* 创建知识库弹窗 */}
      <BuildKnowledgeBase
        isOpen={knowledgeBase.isBuildKBModalOpen}
        onClose={knowledgeBase.closeBuildKBModal}
        onConfirm={knowledgeBase.onConfirmCreateKB}
        loading={knowledgeBase.loading}
      />

      {/* 添加文件弹窗 */}
      <AddFile
        isOpen={knowledgeBase.isAddFileModalOpen}
        onClose={knowledgeBase.closeAddFileModal}
        onConfirm={handleConfirmSave}

        // 配置状态
        fileType={config.fileType}
        chunkLength={config.chunkLength}
        overlapLength={config.overlapLength}
        autoSegment={config.autoSegment}

        // 文件状态
        selectedFile={currentState.selectedFile}
        isUploading={currentState.isUploading}
        uploadedFileId={null}
        isParsing={currentState.isParsing}
        parseResults={currentState.parseResults}

        // 事件处理
        onFileTypeChange={setFileType}
        onChunkLengthChange={setChunkLength}
        onOverlapLengthChange={setOverlapLength}
        onAutoSegmentChange={setAutoSegment}
        onFileChange={handleFileChange}
        onTriggerFileSelect={triggerFileSelect}
        onAIProcess={handleAIProcess}
        
        // 删除操作
        onDeleteKnowledgeItem={handleDeleteKnowledgeItem}
        onClearAllKnowledge={handleClearAllKnowledge}

        // 其他
        fileInputRef={fileInputRef}
        canProcess={!!currentState.selectedFile && !currentState.isUploading && !currentState.isParsing}
        canSave={!!currentState.selectedFile && currentState.parseResults.length > 0 && !currentState.isParsing}
        error={currentState.error}
        loading={knowledgeBase.loading}
      />
    </>
  );
};

export default KnowledgeBaseBridge;
