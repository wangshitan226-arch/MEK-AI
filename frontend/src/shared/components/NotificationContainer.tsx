import React from 'react';
import { useNotificationsStore } from '../../core/notifications/stores/notificationsStore';
import { X } from 'lucide-react';

/**
 * 全局通知容器组件
 * 应放置在应用根组件中，用于显示所有全局提示
 */
export const NotificationContainer: React.FC = () => {
  const { notifications, removeNotification } = useNotificationsStore();
  
  if (notifications.length === 0) return null;
  
  // 根据类型获取对应的样式
  const getTypeStyles = (type: string) => {
    switch (type) {
      case 'success': return 'bg-green-50 text-green-800 border-green-200';
      case 'warning': return 'bg-yellow-50 text-yellow-800 border-yellow-200';
      case 'error': return 'bg-red-50 text-red-800 border-red-200';
      default: return 'bg-blue-50 text-blue-800 border-blue-200';
    }
  };
  
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 w-80">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`p-4 rounded-lg border ${getTypeStyles(notification.type)} shadow-lg transition-all duration-300`}
        >
          <div className="flex justify-between items-start">
            <div className="pr-4">
              <p className="font-medium">{notification.message}</p>
            </div>
            <button
              onClick={() => removeNotification(notification.id)}
              className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X size={18} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};