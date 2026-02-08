import React from 'react';
// 导入AI生成的纯样式组件
import { MarketplacePage } from '../../ui-pages/marketplace/components/MarketplacePage';
import { RecruitmentModal } from '../../ui-pages/marketplace/components/RecruitmentModal';
import { ChatInterface } from '../../ui-pages/marketplace/components/ChatInterface';
// 导入业务逻辑Hook
import { useMarketplace } from './logic/hooks/useMarketplace';
import { useMarketplaceInteraction } from './logic/hooks/useMarketplaceInteraction';
import { useChatLogic } from './logic/hooks/useChatLogic';
// 导入UI Store以获取状态
import { useMarketplaceUIStore } from './logic/stores/marketplaceUIStore';
// 导入类型适配器
import { toAIEmployee, toAIEmployeeList } from '@/shared/types/typeAdapters';

export const EnhancedMarketplaceBridge: React.FC = () => {
  // 获取市场数据与基础操作
  const marketplace = useMarketplace();
  
  // 获取市场交互逻辑
  const interaction = useMarketplaceInteraction();
  
  // 获取聊天逻辑
  const chat = useChatLogic();
  
  // 获取UI状态
  const { currentView, isHireModalOpen, hiringEmployee } = useMarketplaceUIStore();

  // 根据当前视图渲染不同的AI组件
  return (
    <>
      {/* 市场页面视图 */}
      {currentView === 'marketplace' && (
        <MarketplacePage
          employees={toAIEmployeeList(marketplace.employees)}
          categories={marketplace.categories}
          activeCategoryId={marketplace.activeCategoryId}
          onCategoryChange={marketplace.onCategoryChange}
          onEmployeeClick={interaction.handleEmployeeCardClick}
          loading={marketplace.loading}
          searchQuery={marketplace.searchQuery}
          onSearchChange={marketplace.onSearchChange}
        />
      )}

      {/* 聊天界面视图 */}
      {currentView === 'chat' && chat.activeEmployee && (
        <ChatInterface
          employee={toAIEmployee(chat.activeEmployee)}
          sessions={chat.sessions}
          currentSessionId={chat.currentSessionId}
          messages={chat.messages}
          inputValue={chat.inputValue}
          isHistoryVisible={chat.isHistoryVisible}
          copiedMessageId={chat.copiedMessageId}
          onBack={chat.onBack}
          onInputChange={chat.onInputChange}
          onSendMessage={chat.onSendMessage}
          onNewChat={chat.onNewChat}
          onSelectSession={chat.onSelectSession}
          onToggleHistory={chat.onToggleHistory}
          onCopyMessage={chat.onCopyMessage}
        />
      )}

      {/* 招聘弹窗 */}
      {hiringEmployee && (
        <RecruitmentModal
          isOpen={isHireModalOpen}
          employee={toAIEmployee(hiringEmployee)}
          onClose={interaction.handleCloseModal}
          onConfirm={interaction.handleHireConfirm}
        />
      )}
    </>
  );
};

export default EnhancedMarketplaceBridge;