import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../stores/chatStore';
import { useMarketplaceStore } from '../stores/marketplaceStore';
import { useMarketplaceUIStore } from '../stores/marketplaceUIStore';
import { useUserStore } from '@/core/store/userStore';
import { useDigitalEmployeeStore } from '@/modules/digital-employee/logic/stores/digitalEmployeeStore';
import { createSafeEmployee, normalizeEmployee } from '@/shared/types/employee';

export const useChatLogic = () => {
  const navigate = useNavigate();
  
  // 获取所有store
  const chatStore = useChatStore();
  const marketplaceStore = useMarketplaceStore();
  const uiStore = useMarketplaceUIStore();
  const userStore = useUserStore();
  const digitalEmployeeStore = useDigitalEmployeeStore();

  // 找到当前员工
  const findActiveEmployee = () => {
    if (!uiStore.selectedEmployeeId) {
      return null;
    }
    
    const employeeId = uiStore.selectedEmployeeId;
    
    // 从marketplace找
    let employee = marketplaceStore.employees.find(e => e.id === employeeId);
    
    // 从userStore找
    if (!employee) {
      employee = userStore.recruitedEmployees.find(e => e.id === employeeId);
    }
    
    // 从数字员工store找（包括创建的和招聘的）
    if (!employee) {
      employee = digitalEmployeeStore.getDigitalEmployeeById(employeeId);
    }
    
    return employee ? normalizeEmployee(employee) : null;
  };

  const activeEmployee = findActiveEmployee();

  // 设置当前员工
  if (activeEmployee && chatStore.currentEmployeeId !== activeEmployee.id) {
    chatStore.setCurrentEmployee(activeEmployee.id);
  }

  // 获取数据
  const sessions = activeEmployee ? chatStore.getSessions(activeEmployee.id) : [];
  const messages = chatStore.currentSessionId ? chatStore.getMessages(chatStore.currentSessionId) : [];

  // 操作函数
  const handleBackToMarketplace = () => {
    uiStore.resetUI();
    chatStore.resetChat();
    navigate('/marketplace');
  };

  const handleNewChat = () => {
    if (activeEmployee) {
      chatStore.createSession(activeEmployee.id,'新会话');
    }
  };

  const handleSelectSession = (sessionId: string) => {
    chatStore.selectSession(sessionId);
  };

  const handleInputChange = (value: string) => {
    chatStore.setInputValue(value);
  };

  const handleSendMessage = () => {
    if (activeEmployee && chatStore.inputValue.trim()) {
      chatStore.sendMessage(activeEmployee.id, chatStore.inputValue);
    }
  };

  const handleCopyMessage = (messageId: string, content: string) => {
    chatStore.copyMessage(messageId, content);
  };

  const handleToggleHistory = () => {
    chatStore.toggleHistory();
  };

  // 返回数据
  const safeEmployee = activeEmployee || createSafeEmployee();
  
  return {
    // 数据
    activeEmployee: safeEmployee,
    sessions,
    currentSessionId: chatStore.currentSessionId,
    messages,
    inputValue: chatStore.inputValue,
    isHistoryVisible: chatStore.isHistoryVisible,
    copiedMessageId: chatStore.copiedMessageId,
    
    // 操作
    onBack: handleBackToMarketplace,
    onNewChat: handleNewChat,
    onSelectSession: handleSelectSession,
    onInputChange: handleInputChange,
    onSendMessage: handleSendMessage,
    onCopyMessage: handleCopyMessage,
    onToggleHistory: handleToggleHistory,
    
    // 状态
    isReady: !!activeEmployee
  };
};