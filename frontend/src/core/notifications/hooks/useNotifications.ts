import { useNotificationsStore } from '../stores/notificationsStore';

/**
 * 全局通知系统 Hook
 * 用于在任意组件中触发全局提示消息
 */
export const useNotifications = () => {
  const { showNotification } = useNotificationsStore();

  return {
    showNotification,
  };
};