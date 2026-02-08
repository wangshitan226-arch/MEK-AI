import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Home, Store, Users, BookOpen, Tag, Cpu, MessageSquare, Settings, LayoutGrid, Briefcase, CreditCard } from 'lucide-react';

// 定义从 useSidebarLogic 传递过来的 props 接口
export interface AppSidebarProps {
  navItems: NavItemData[];
  activeNavId: string;
  onNavClick: (navId: string) => void;
  onSubNavClick?: (parentId: string, childId: string) => void;
}

export interface NavItemData {
  id: string;
  label: string;
  path?: string;
  icon?: React.ReactNode;
  children?: NavItemData[];
  badge?: string;
  badgeColor?: 'blue' | 'red';
}

// 图标映射：将 navItem.id 映射到对应的图标组件
const iconMap: Record<string, React.ReactNode> = {
  'dashboard': <Home size={18} />,
  'marketplace': <Store size={18} />,
//  'my-employees': <Users size={18} />,
  'digital-employee': <Users size={18} />,
  'knowledge-base': <BookOpen size={18} />,
  'tags': <Tag size={18} />,
  'integration': <Cpu size={18} />,
  'ai-group': <LayoutGrid size={18} />,
  'all-groups': <LayoutGrid size={18} />,
  'traffic-groups': <Briefcase size={18} />,
  'product-groups': <Cpu size={18} />,
  'my-groups': <Users size={18} />,
  'sop': <MessageSquare size={18} />,
  'enterprise': <Settings size={18} />,
  'my-company': <Settings size={18} />,
  'role-manage': <Users size={18} />,
  'account-manage': <CreditCard size={18} />,
  // 端口接入相关
  'port-access': <MessageSquare size={18} />,
  'wecom': <MessageSquare size={18} />,
  'wechat': <MessageSquare size={18} />,
};

export const AppSidebar: React.FC<AppSidebarProps> = ({ 
  navItems, 
  activeNavId, 
  onNavClick,
  onSubNavClick 
}) => {
  // 用于跟踪哪些有子菜单的项是展开的
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set(['ai-group', 'enterprise']));

  const toggleExpand = (id: string) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  // 渲染单个导航项（递归渲染子项）
  const renderNavItem = (item: NavItemData, level = 0, parentId?: string) => {
    const isActive = activeNavId === item.id;
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.has(item.id);
    
    // 判断是否有激活的子项（用于父项的高亮显示）
    const hasActiveChild = item.children?.some(child => child.id === activeNavId) || false;

    return (
      <div key={item.id}>
        {/* 父项 */}
        <div
          className={`
            flex items-center justify-between px-3 py-2 rounded-md cursor-pointer group
            ${isActive || hasActiveChild ? 'bg-blue-50 text-blue-600' : 'text-slate-600 hover:bg-slate-50'}
            ${level > 0 ? 'pl-9' : ''}
          `}
            // AppSidebar.tsx 第88-95行（替换原onClick逻辑）
            onClick={() => {
                if (hasChildren) {
                toggleExpand(item.id); // 父项：展开/折叠
                } else {
                // 关键修改：区分层级，子项（level>0）调用onSubNavClick，父项调用onNavClick
                if (level > 0 && onSubNavClick) {
                    // 子项：找到父级ID（通过递归上下文），调用子项点击逻辑
                    // 先给renderNavItem新增parentId参数，再传递
                    onSubNavClick(parentId!, item.id); 
                } else {
                    onNavClick(item.id); // 父项：主导航逻辑
                }
                }
            }}
        >
          <div className="flex items-center space-x-3">
            <span className={isActive || hasActiveChild ? 'text-blue-600' : 'text-slate-400 group-hover:text-slate-600'}>
              {item.icon || iconMap[item.id] || <div className="w-4 h-4" />}
            </span>
            <span className="text-sm font-medium">{item.label}</span>
          </div>
          <div className="flex items-center space-x-2">
            {item.badge && (
              <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                item.badgeColor === 'red' ? 'bg-orange-500 text-white' : 'bg-blue-600 text-white'
              }`}>
                {item.badge}
              </span>
            )}
            {hasChildren && (
              isExpanded ? <ChevronDown size={14} className="text-slate-400" /> : <ChevronRight size={14} className="text-slate-400" />
            )}
          </div>
        </div>

        {/* 子菜单 */}
        {hasChildren && isExpanded && (
          <div className="ml-6 mt-1 space-y-1 border-l border-slate-100 pl-2">
            {item.children!.map(child => renderNavItem(child, level + 1, item.id))}
          </div>
        )}
      </div>
    );
  };

  return (
    <aside className="w-full h-full bg-white flex flex-col overflow-y-auto">
      {/* Logo Area */}
      <div className="p-5 flex items-center space-x-2">
        <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
          <div className="w-4 h-4 bg-white rounded-full opacity-80"></div>
        </div>
        <span className="font-bold text-lg tracking-tight">MEK AI</span>
        <span className="text-[10px] bg-amber-100 text-amber-700 px-1 py-0.5 rounded border border-amber-200">专业版</span>
      </div>

      {/* Nav Menu */}
      <nav className="flex-1 px-3 space-y-1">
        {/* 主要导航项分组 */}
        <div className="space-y-1 mb-6">
          {navItems.filter(item => 
            ['dashboard', 'marketplace', 'my-employees', 'digital-employee', 'knowledge-base', 'tags', 'integration'].includes(item.id)
          ).map(item => renderNavItem(item))}
        </div>

        {/* AI数字员工群 */}
        <div className="px-3 py-2 text-xs text-slate-400 font-medium">AI数字员工群</div>
        {navItems.filter(item => item.id === 'ai-group').map(item => renderNavItem(item))}

        {/* 端口接入 */}
        <div className="px-3 py-2 text-xs text-slate-400 font-medium mt-4">端口接入</div>
        {/* 这里可以添加端口接入的导航项，如果navItems中有的话 */}
        {navItems.filter(item => ['port-access', 'wecom', 'wechat'].includes(item.id)).map(item => renderNavItem(item))}

        {/* 企业管理 */}
        <div className="px-3 py-2 text-xs text-slate-400 font-medium mt-4">企业管理</div>
        {navItems.filter(item => item.id === 'enterprise').map(item => renderNavItem(item))}
      </nav>
      
      {/* Bottom Profile */}
      <div className="p-4 border-t border-slate-100">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded bg-slate-200"></div>
          <span className="text-sm font-medium text-slate-700">企业账号</span>
        </div>
      </div>
    </aside>
  );
};

export default AppSidebar;