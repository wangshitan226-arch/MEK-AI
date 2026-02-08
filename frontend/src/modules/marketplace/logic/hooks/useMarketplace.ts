// src/modules/marketplace/logic/hooks/useMarketplace.ts
import { useEffect } from 'react';
import {
  useMarketplaceStore,
  useFilteredEmployees,
  useActiveCategory
} from '../stores/marketplaceStore';

export const useMarketplace = () => {
  const store = useMarketplaceStore();
  const filteredEmployees = useFilteredEmployees();
  const activeCategory = useActiveCategory();

  // 初始化加载数据
  useEffect(() => {
    store.loadEmployees();
    store.loadCategories();
    store.setActiveCategory('all');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // 依赖为空，仅执行一次

  // 处理分类切换
  const handleCategoryChange = (categoryId: string) => {
    store.setActiveCategory(categoryId);
  };

  // 处理搜索
  const handleSearchChange = (query: string) => {
    store.setSearchQuery(query);
  };

  // 获取员工状态 (工具函数)
  const getEmployeeStatus = (employeeId: string) => {
    const employee = store.employees.find(e => e.id === employeeId);
    if (!employee) return null;
    return {
      isHired: employee.isHired,
      isInTrial: employee.isInTrial,
    };
  };

  return {
    // 数据
    employees: filteredEmployees,
    categories: store.categories,
    activeCategoryId: store.activeCategoryId,
    loading: store.loading,
    error: store.error,
    searchQuery: store.searchQuery,

    // 基础操作
    onCategoryChange: handleCategoryChange,
    onSearchChange: handleSearchChange,

    // 工具函数
    getEmployeeStatus,
  };
};