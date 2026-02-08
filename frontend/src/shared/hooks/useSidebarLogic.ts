import { useState, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

/**
 * 侧边栏业务逻辑Hook
 * 集中管理侧边栏的：
 * 1. 导航数据
 * 2. 活动状态
 * 3. 点击跳转逻辑
 * 4. 未完成功能的提示
 */
export interface NavItem {
  id: string;
  label: string;
  path?: string; // 如果无path，则点击时显示“开发中”提示
  icon?: React.ReactNode; // 可传入图标组件
  badge?: string;                    // 新增：徽章文本
  badgeColor?: 'blue' | 'red';      // 新增：徽章颜色
  children?: NavItem[]; // 子菜单
}

export const useSidebarLogic = () => {
  const navigate = useNavigate();
  const location = useLocation();
//  const { showNotification } = useNotifications();

  // 侧边栏导航配置（后续可考虑从后端或配置文件中获取）
// 在 useSidebarLogic.ts 中，更新 navItems 初始状态：
const [navItems] = useState<NavItem[]>([
    { id: 'dashboard', label: '首页', path: '/dashboard' },
    { id: 'marketplace', label: 'AI员工广场', path: '/marketplace' },
//    { id: 'my-employees', label: '我的AI员工', path: '/my-employees' },
    { id: 'digital-employee', label: '数字员工', path: '/digital-employee' },
    { id: 'knowledge-base', label: '知识库', path: '/knowledge-base' },
    { id: 'tags', label: '标签库', path: '/tag-library' }, // 未配置path，点击将显示"开发中"
    { id: 'integration', label: '智能体集成', path: '/agent-integration' },
    { 
      id: 'ai-group', 
      label: 'AI数字员工群',
      children: [
        { id: 'all-groups', label: '全部AI员工群', path: '/all-employees-group' },
        { id: 'traffic-groups', label: '流量IP群', path: '/trffic-group' },
        { id: 'product-groups', label: '产品开发群', path: '/product-development-group' },
        { id: 'my-groups', label: '我创建的群聊', path: '/groups' },
      ]
    },
    { id: 'sop', label: '私聊SOP系统' },
    // 注意：这里需要将端口接入作为可展开项，或拆分为单独项
    { 
      id: 'port-access',
      label: '端口接入',
      children: [
        { id: 'wecom', label: '企业微信', path: '/wecom' },
        { id: 'wechat', label: '个人微信', path: '/wechat' },
      ]
    },
    { 
      id: 'enterprise', 
      label: '企业管理',
      badge: '全系降价',
      badgeColor: 'red',
      children: [
        { id: 'my-company', label: '我的企业', path: '/my-business' },
        { id: 'role-manage', label: '角色管理', path: '/role-management' },
        { id: 'account-manage', label: '账号管理', path: '/account-management' },
      ]
    },
  ]);

  // 根据当前URL路径，计算哪个导航项应被激活
  const getActiveNavId = useCallback((): string => {
    const currentPath = location.pathname;
    
    // 遍历所有导航项，查找匹配的路径
    const findActiveId = (items: NavItem[]): string | undefined => {
        for (const item of items) {
          if (item.children) {
            const childActiveId = findActiveId(item.children);
            if (childActiveId) return childActiveId; // 优先返回子项ID
          }
          if (item.path === currentPath) {
            return item.id;
          }
        }
        return undefined;
      };

    return findActiveId(navItems) || 'marketplace'; // 默认激活AI员工广场
  }, [location.pathname, navItems]);

  const activeNavId = getActiveNavId();

  // 处理主导航项点击
  const handleNavClick = useCallback((navId: string) => {
    const navItem = navItems.find(item => item.id === navId);
    // 如果有配置路径，则跳转
    if (navItem.path) {
      navigate(navItem.path);
    } 
  }, [navItems, navigate]);

  // 处理子导航项点击
  const handleSubNavClick = useCallback((parentId: string, childId: string) => {
    // 这里可以添加子项的特殊逻辑
    // 目前与主项处理方式相同，可以预留
    const parentItem = navItems.find(item => item.id === parentId);
    if (!parentItem?.children) return;
    
    const childItem = parentItem.children.find(item => item.id === childId);
    if (!childItem) return;
    
    // 对于子项，如果没有配置path，也显示提示
    if (childItem.path) {
        navigate(childItem.path);
    }
  }, [navItems]);

  return {
    navItems,
    activeNavId,
    handleNavClick,
    handleSubNavClick,
  };
};