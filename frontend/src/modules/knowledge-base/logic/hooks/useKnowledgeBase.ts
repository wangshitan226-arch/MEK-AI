import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useKnowledgeBaseStore } from '../stores/knowledgeBaseStore';
import { useKnowledgeBaseUIStore } from '../stores/knowledgeBaseUIStore';

export const useKnowledgeBase = () => {
  const navigate = useNavigate();
  const store = useKnowledgeBaseStore();
  const uiStore = useKnowledgeBaseUIStore();

  // 初始化加载数据
  useEffect(() => {
    store.loadKnowledgeBases();
  }, []);

  // 处理创建知识库点击
  const handleCreateKBClick = () => {
    uiStore.openBuildKBModal();
  };

  // 处理确认创建知识库
  const handleConfirmCreateKB = async (name: string, description?: string) => {
    try {
      const newKB = await store.createKnowledgeBase(name, description);
      uiStore.closeBuildKBModal();
      
      // 自动打开添加文件弹窗
      store.setCurrentKBId(newKB.id);
      setTimeout(() => {
        uiStore.openAddFileModal(newKB.id);
      }, 200);
      
      return newKB;
    } catch (error) {
      console.error('创建知识库失败:', error);
      throw error;
    }
  };

  // 处理知识库项目点击
  const handleKBItemClick = (id: string) => {
    store.setCurrentKBId(id);
    uiStore.openAddFileModal(id);
  };

  // 处理导航
  const handleNavigate = (view: string) => {
    if (view === 'marketplace') {
      navigate('/marketplace');
    } else if (view === 'digital-employees') {
      navigate('/digital-employee');
    }
  };

  // 获取当前知识库
  const currentKB = store.knowledgeBases.find(kb => kb.id === store.currentKBId);

  return {
    // 状态
    knowledgeBases: store.knowledgeBases,
    loading: store.loading,
    error: store.error,
    currentKBId: store.currentKBId,
    currentKB,
    
    // UI状态
    isBuildKBModalOpen: uiStore.isBuildKBModalOpen,
    isAddFileModalOpen: uiStore.isAddFileModalOpen,
    
    // 事件处理
    onCreateClick: handleCreateKBClick,
    onItemClick: handleKBItemClick,
    onConfirmCreateKB: handleConfirmCreateKB,
    onNavigate: handleNavigate,
    
    // Store操作方法
    closeBuildKBModal: uiStore.closeBuildKBModal,
    closeAddFileModal: uiStore.closeAddFileModal,
  };
};