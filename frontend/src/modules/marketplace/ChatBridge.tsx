import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ChatInterface from '@/ui-pages/marketplace/components/ChatInterface';
import { useChatLogic } from './logic/hooks/useChatLogic';
import { useMarketplaceUIStore } from './logic/stores/marketplaceUIStore';
import { toUIPageEmployee } from '@/shared/types/typeAdapters';
const ChatBridge: React.FC = () => {
  const { employeeId } = useParams<{ employeeId: string }>();
  const { selectEmployee } = useMarketplaceUIStore();
  const chatLogic = useChatLogic();

  // 设置选中的员工
  useEffect(() => {
    if (employeeId) {
      selectEmployee(employeeId);
    }
  }, [employeeId, selectEmployee]);

  // 如果没有员工数据，显示加载状态
  if (!chatLogic.activeEmployee) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-3 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-2"></div>
          <p className="text-slate-500 text-sm">加载聊天...</p>
        </div>
      </div>
    );
  }

  // 渲染聊天界面
  return (
    <ChatInterface
      employee={toUIPageEmployee(chatLogic.activeEmployee)}
      sessions={chatLogic.sessions}
      currentSessionId={chatLogic.currentSessionId}
      messages={chatLogic.messages}
      inputValue={chatLogic.inputValue}
      isHistoryVisible={chatLogic.isHistoryVisible}
      copiedMessageId={chatLogic.copiedMessageId}
      onBack={chatLogic.onBack}
      onInputChange={chatLogic.onInputChange}
      onSendMessage={chatLogic.onSendMessage}
      onNewChat={chatLogic.onNewChat}
      onSelectSession={chatLogic.onSelectSession}
      onToggleHistory={chatLogic.onToggleHistory}
      onCopyMessage={chatLogic.onCopyMessage}
    />
  );
};

export default ChatBridge;