import { useState, useCallback } from 'react';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
  duration?: number;
}

export const useNotification = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const showNotification = useCallback((notification: Omit<Notification, 'id'>) => {
    const id = Date.now().toString();
    const newNotification = { ...notification, id };
    
    setNotifications(prev => [...prev, newNotification]);

    // 自动移除通知
    const duration = notification.duration || 5000;
    setTimeout(() => {
      removeNotification(id);
    }, duration);
  }, []);

  const showSuccess = useCallback((message: string, title = '成功') => {
    showNotification({
      type: 'success',
      title,
      message,
      duration: 3000
    });
  }, [showNotification]);

  const showError = useCallback((message: string, title = '错误') => {
    showNotification({
      type: 'error',
      title,
      message,
      duration: 5000
    });
  }, [showNotification]);

  const showInfo = useCallback((message: string, title = '提示') => {
    showNotification({
      type: 'info',
      title,
      message,
      duration: 4000
    });
  }, [showNotification]);

  const showWarning = useCallback((message: string, title = '警告') => {
    showNotification({
      type: 'warning',
      title,
      message,
      duration: 4000
    });
  }, [showNotification]);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  return {
    notifications,
    showSuccess,
    showError,
    showInfo,
    showWarning,
    removeNotification
  };
};