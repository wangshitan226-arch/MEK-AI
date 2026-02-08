import { create } from 'zustand';
import { ChatSession, Message } from '../../../../ui-pages/marketplace/types';
import { sendChatMessage, createChatSession } from '../services/employeeApi';
import { setEmployeeContext } from '@/core/services/apiClient';

interface ChatState {
  // 每个员工独立的消息存储
  messagesBySession: Record<string, Message[]>; // sessionId -> Message[]
  sessionsByEmployee: Record<string, ChatSession[]>; // employeeId -> ChatSession[]
  
  // 当前状态
  currentEmployeeId: string | null;
  currentSessionId: string | null;
  inputValue: string;
  isHistoryVisible: boolean;
  copiedMessageId: string | null;
}

interface ChatActions {
  // 员工操作
  setCurrentEmployee: (employeeId: string) => void;
  
  // 会话操作
  createSession: (employeeId: string,title:string) => string;
  selectSession: (sessionId: string) => void;
  
  // 消息操作
  sendMessage: (employeeId: string, content: string) => void;
  copyMessage: (messageId: string, content: string) => void;
  
  // UI操作
  setInputValue: (value: string) => void;
  toggleHistory: () => void;
  
  // 重置
  resetChat: () => void;
  
  // 获取数据
  getSessions: (employeeId: string) => ChatSession[];
  getMessages: (sessionId: string) => Message[];
}

export const useChatStore = create<ChatState & ChatActions>((set, get) => ({
  // 初始状态
  messagesBySession: {},
  sessionsByEmployee: {},
  currentEmployeeId: null,
  currentSessionId: null,
  inputValue: '',
  isHistoryVisible: true,
  copiedMessageId: null,

  // 员工操作
  setCurrentEmployee: (employeeId) => {
    set({
      currentEmployeeId: employeeId,
      currentSessionId: null,
      inputValue: ''
    });
    // 设置员工上下文到 API headers
    setEmployeeContext(employeeId);
  },

  selectSession: (sessionId) => {
    set({
      currentSessionId: sessionId,
      inputValue: ''
    });
  },

  createSession: (employeeId: string, title: string = '新会话') => {
    const sessionId = `session-${employeeId}-${Date.now()}`;
    const newSession: ChatSession = {
      id: sessionId,
      title,
      employeeId,
      lastModified: Date.now()
    };
  
    set(state => ({
      sessionsByEmployee: {
        ...state.sessionsByEmployee,
        [employeeId]: [newSession, ...(state.sessionsByEmployee[employeeId] || [])]
      },
      currentSessionId: sessionId,
      inputValue: ''
    }));
  
    return sessionId;
  },
  
  // 修改 sendMessage 方法，使用真实 API
  sendMessage: async (employeeId, content) => {
    if (!content.trim()) return;

    const state = get();
    let sessionId = state.currentSessionId;

    // 如果没有当前会话或员工不匹配，创建新会话
    if (!sessionId || state.currentEmployeeId !== employeeId) {
      // 使用用户输入内容生成标题（截取前30个字符）
      const title = content.length > 30 ? content.slice(0, 30) + '...' : content;
      sessionId = get().createSession(employeeId, title);
    } else {
      // 如果会话已存在，检查是否需要更新标题
      const sessions = state.sessionsByEmployee[employeeId] || [];
      const sessionIndex = sessions.findIndex(s => s.id === sessionId);

      // 如果当前标题是"新会话"，则用第一条消息更新标题
      if (sessionIndex !== -1 && sessions[sessionIndex].title === '新会话') {
        const title = content.length > 30 ? content.slice(0, 30) + '...' : content;

        set(state => {
          const updatedSessions = [...(state.sessionsByEmployee[employeeId] || [])];
          if (updatedSessions[sessionIndex]) {
            updatedSessions[sessionIndex] = {
              ...updatedSessions[sessionIndex],
              title
            };
          }

          return {
            sessionsByEmployee: {
              ...state.sessionsByEmployee,
              [employeeId]: updatedSessions
            }
          };
        });
      }
    }

    // 添加用户消息
    const userMessage: Message = {
      id: `msg-${Date.now()}-user`,
      role: 'user',
      content,
      timestamp: Date.now()
    };

    set(state => ({
      messagesBySession: {
        ...state.messagesBySession,
        [sessionId!]: [...(state.messagesBySession[sessionId!] || []), userMessage]
      },
      inputValue: ''
    }));

    // 调用真实 API 获取 AI 回复
    try {
      // 设置员工上下文
      setEmployeeContext(employeeId);

      const response = await sendChatMessage(
        employeeId,
        content,
        sessionId || undefined
      );

      const aiMessage: Message = {
        id: `msg-${Date.now()}-ai`,
        role: 'model',
        content: response.message,
        timestamp: Date.now()
      };

      set(state => ({
        messagesBySession: {
          ...state.messagesBySession,
          [sessionId!]: [...(state.messagesBySession[sessionId!] || []), aiMessage]
        }
      }));
    } catch (error) {
      console.error('发送消息失败:', error);

      // 显示错误消息
      const errorMessage: Message = {
        id: `msg-${Date.now()}-error`,
        role: 'model',
        content: '抱歉，服务暂时不可用，请稍后重试。',
        timestamp: Date.now()
      };

      set(state => ({
        messagesBySession: {
          ...state.messagesBySession,
          [sessionId!]: [...(state.messagesBySession[sessionId!] || []), errorMessage]
        }
      }));
    }
  },

  copyMessage: (messageId, content) => {
    navigator.clipboard.writeText(content).then(() => {
      set({ copiedMessageId: messageId });
      setTimeout(() => set({ copiedMessageId: null }), 2000);
    }).catch(() => {
      // 降级方案
      const textArea = document.createElement('textarea');
      textArea.value = content;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      set({ copiedMessageId: messageId });
      setTimeout(() => set({ copiedMessageId: null }), 2000);
    });
  },

  // UI操作
  setInputValue: (value) => set({ inputValue: value }),
  toggleHistory: () => set(state => ({ isHistoryVisible: !state.isHistoryVisible })),
  
  // 重置
  resetChat: () => {
    set({
      currentEmployeeId: null,
      currentSessionId: null,
      inputValue: ''
    });
  },

  // 获取数据
  getSessions: (employeeId) => {
    return get().sessionsByEmployee[employeeId] || [];
  },

  getMessages: (sessionId) => {
    return get().messagesBySession[sessionId] || [];
  }
}));