// 导入共享类型
import { Employee } from '@/shared/types/employee';
import { Category, ChatSession, Message } from '../../../ui-pages/marketplace/types';

// 使用统一的Employee类型
export type EmployeeWithStatus = Employee;

// === 数据状态管理类型 ===
export interface MarketplaceState {
  employees: Employee[];
  categories: Category[];
  activeCategoryId: string | null;
  searchQuery: string;
  loading: boolean;
  error: string | null;
}

export interface MarketplaceActions {
  setActiveCategory: (categoryId: string | null) => void;
  hireEmployee: (employeeId: string) => Promise<void>;
  toggleTrialEmployee: (employeeId: string) => void;
  setSearchQuery: (query: string) => void;
  loadEmployees: () => Promise<void>;
  loadCategories: () => Promise<void>;
}

export type MarketplaceStore = MarketplaceState & MarketplaceActions;

// === UI状态管理类型 ===
export type ViewState = 'marketplace' | 'chat';

export interface MarketplaceUIState {
  currentView: ViewState;
  selectedEmployeeId: string | null;
  isHireModalOpen: boolean;
  hiringEmployee: Employee | null;
}

export interface MarketplaceUIActions {
  setView: (view: ViewState) => void;
  selectEmployee: (id: string | null) => void;
  openHireModal: (employee: Employee) => void;
  closeHireModal: () => void;
  resetUI: () => void;
}

export type MarketplaceUIStore = MarketplaceUIState & MarketplaceUIActions;

// === 聊天状态管理类型 ===
export interface ChatState {
  sessions: ChatSession[];
  messagesMap: Record<string, Message[]>;
  currentSessionId: string | null;
  chatInputValue: string;
  isHistoryVisible: boolean;
  copiedMessageId: string | null;
}

export interface ChatActions {
  setSessions: (sessions: ChatSession[]) => void;
  setMessagesMap: (messagesMap: Record<string, Message[]>) => void;
  setCurrentSessionId: (sessionId: string | null) => void;
  setChatInputValue: (value: string) => void;
  setIsHistoryVisible: (visible: boolean) => void;
  setCopiedMessageId: (messageId: string | null) => void;
  sendMessage: (employeeId: string) => Promise<void>;
  createNewSession: (employeeId: string) => void;
  selectSession: (sessionId: string) => void;
  copyMessage: (messageId: string, content: string) => void;
}

export type ChatStore = ChatState & ChatActions;