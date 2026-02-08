import { create } from 'zustand';
import { KnowledgeBaseUIStore } from '../../types';

// 初始化UI状态
const initialState = {
  isBuildKBModalOpen: false,
  isAddFileModalOpen: false,
  activeModal: null,
};

// 创建UI状态store
export const useKnowledgeBaseUIStore = create<KnowledgeBaseUIStore>((set) => ({
  ...initialState,

  openBuildKBModal: () => {
    set({ 
      isBuildKBModalOpen: true,
      activeModal: 'create'
    });
  },

  closeBuildKBModal: () => {
    set({ 
      isBuildKBModalOpen: false,
      activeModal: null
    });
  },

  openAddFileModal: (kbId?: string) => {
    set({ 
      isAddFileModalOpen: true,
      activeModal: 'upload'
    });
  },

  closeAddFileModal: () => {
    set({ 
      isAddFileModalOpen: false,
      activeModal: null
    });
  },

  setActiveModal: (modal) => {
    set({ activeModal: modal });
  },

  resetUI: () => {
    set(initialState);
  },
}));