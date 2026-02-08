import React, { useEffect } from 'react';
import { useNotifications } from '../../core/notifications/hooks/useNotifications';

/**
 * 统一占位组件，用于所有正在开发中的模块页面
 * 显示友好的开发中提示
 */
const UnderDevelopmentBridge: React.FC = () => {
  
  return (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center">
      <div className="max-w-md">
        <div className="text-6xl mb-4">🚧</div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">功能开发中</h1>
        <p className="text-gray-600 mb-6">
          我们的工程师正在全力开发此功能，力求为您带来更好的体验。
        </p>
        <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-500">
          <p>预计上线时间：敬请关注官方公告</p>
          <p className="mt-1">您可以先体验其他已上线的功能</p>
        </div>
      </div>
    </div>
  );
};

export default UnderDevelopmentBridge;