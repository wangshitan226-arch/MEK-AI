import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from '../layout/AppLayout';

// 懒加载组件 - 实现代码分割
const EnhancedMarketplaceBridge = lazy(() => import('../../modules/marketplace/EnhancedMarketplaceBridge'));
const UnderDevelopmentBridge = lazy(() => import('../../modules/under-development/UnderDevelopmentBridge'));
const DigitalEmployeeBridge = lazy(() => import('@/modules/digital-employee/DigitalEmployeeBridge'));
const ChatBridge = lazy(() => import('@/modules/marketplace/ChatBridge'));
const KnowledgeBaseBridge = lazy(() => import('@/modules/knowledge-base/KnowledgeBaseBridge'));

// 加载组件
const LoadingFallback = () => (
  <div className="flex items-center justify-center min-h-screen bg-slate-50">
    <div className="text-center">
      <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
      <p className="text-slate-600">加载中...</p>
    </div>
  </div>
);

export const AppRouter: React.FC = () => {
  return (
    <Router>
      <Suspense fallback={<LoadingFallback />}>
        <Routes>
          {/* 主布局路由 - 所有需要侧边栏的页面都作为它的子路由 */}
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Navigate to="/marketplace" replace />} />
            <Route path="marketplace" element={<EnhancedMarketplaceBridge />} />
            <Route path="chat/:employeeId" element={<ChatBridge />} />
            <Route path="my-employees" element={<UnderDevelopmentBridge />} />
            <Route path="digital-employee" element={<DigitalEmployeeBridge />} />
            <Route path="digital-employee/edit/:id" element={<DigitalEmployeeBridge />} />
            <Route path="knowledge-base" element={<KnowledgeBaseBridge />} />
            <Route path="dashboard" element={<UnderDevelopmentBridge />} />
            <Route path="tag-library" element={<UnderDevelopmentBridge />} />
            <Route path="agent-integration" element={<UnderDevelopmentBridge />} />
            <Route path="all-employees-group" element={<UnderDevelopmentBridge />} />
            <Route path="trffic-group" element={<UnderDevelopmentBridge />} />
            <Route path="product-development-group" element={<UnderDevelopmentBridge />} />
            <Route path="groups" element={<UnderDevelopmentBridge />} />
            <Route path="wecom" element={<UnderDevelopmentBridge />} />
            <Route path="wechat" element={<UnderDevelopmentBridge />} />
            <Route path="my-business" element={<UnderDevelopmentBridge />} />
            <Route path="role-management" element={<UnderDevelopmentBridge />} />
            <Route path="account-management" element={<UnderDevelopmentBridge />} />
          </Route>
          
          {/* 独立路由（不需要侧边栏的页面，如登录页） */}
          {/* <Route path="/login" element={<Login />} /> */}
          
          <Route path="*" element={<div>404 - 页面不存在</div>} />
        </Routes>
      </Suspense>
    </Router>
  );
};