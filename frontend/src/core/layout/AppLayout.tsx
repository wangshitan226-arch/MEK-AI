import React from 'react';
import { Outlet } from 'react-router-dom';
import { AppSidebar } from '../../shared/components/AppSidebar';
import { useSidebarLogic } from '../../shared/hooks/useSidebarLogic';

/**
 * 应用主布局组件
 * 提供：左侧导航栏 + 右侧主内容区 的经典B端布局
 * 所有需要此布局的页面路由，都应作为此组件的子路由（通过 `<Outlet />` 渲染）
 */
const AppLayout: React.FC = () => {
  // 获取侧边栏所需的逻辑：导航项、活动项、点击处理
  const { navItems, activeNavId, handleNavClick, handleSubNavClick } = useSidebarLogic();

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 左侧侧边栏 */}
      <div className="flex-shrink-0 w-64 border-r border-gray-200 bg-white overflow-y-auto">
        <AppSidebar
          navItems={navItems}
          activeNavId={activeNavId}
          onNavClick={handleNavClick}
          onSubNavClick={handleSubNavClick}
        />
      </div>

      {/* 右侧主内容区 */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* 顶部导航栏（预留，可根据需要添加） */}
        {/* <AppHeader /> */}

        {/* 页面内容区域 - 此处将渲染各个模块的页面（如 marketplace, my-employees） */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;