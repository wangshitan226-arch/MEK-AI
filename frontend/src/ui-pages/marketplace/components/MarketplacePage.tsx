import React from 'react';
import { Employee, Category } from '../types';
import { CategoryFilter } from './CategoryFilter';
import { EmployeeCard } from './EmployeeCard';
import { Search, Plus, Briefcase, Zap, HelpCircle } from 'lucide-react';

export interface MarketplacePageProps {
  employees: Employee[];
  categories: Category[];
  activeCategoryId: string | null;
  onCategoryChange: (categoryId: string) => void;
  onHireClick?: (employeeId: string) => void;
  onEmployeeClick: (employeeId: string) => void;
  loading?: boolean;
  searchQuery?: string; // 确保有这个属性
  onSearchChange?: (query: string) => void; // 确保有这个属性
}

export const MarketplacePage: React.FC<MarketplacePageProps> = ({
  employees,
  categories,
  activeCategoryId,
  onCategoryChange,
  onHireClick,
  onEmployeeClick,
  loading = false,
}) => {
  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">

      {/* Main Content */}
      <main className="p-6 min-h-screen relative">
        {/* Top Header Section */}
        <div className="flex flex-col space-y-4 mb-8">
          {/* Breadcrumb-ish title */}
          <div className="flex items-center text-sm text-slate-500 mb-2">
            <span className="cursor-pointer hover:text-slate-700">员工广场</span>
          </div>

          {/* Filter Bar */}
          <div className="flex items-center justify-between bg-white/50 backdrop-blur-sm sticky top-0 z-10 py-2 border-b border-slate-100">
            {/* Left: Categories */}
            <div className="flex-1 overflow-hidden mr-4">
              <CategoryFilter
                categories={categories}
                activeCategoryId={activeCategoryId}
                onChange={onCategoryChange}
              />
            </div>

            {/* Right: Actions */}
            <div className="flex items-center space-x-3 shrink-0">
              {/* Industry Dropdown Mockup */}
              <div className="relative group">
                <button className="flex items-center justify-between w-28 px-3 py-1.5 text-sm bg-white border border-slate-200 rounded text-slate-500 hover:border-slate-300">
                  <span>选择行业</span>
                  <svg className="w-3 h-3 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                </button>
              </div>

              {/* Search Bar */}
              <div className="relative">
                <input 
                  type="text" 
                  placeholder="提问" 
                  className="pl-3 pr-8 py-1.5 text-sm border border-slate-200 rounded w-40 focus:outline-none focus:border-blue-500"
                />
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2 text-slate-300">
                  <span className="text-xs border border-slate-200 rounded px-1">⌘</span>
                </div>
              </div>
              
              {/* Search Button */}
              <button className="px-4 py-1.5 text-sm text-blue-600 bg-blue-50 border border-blue-200 rounded hover:bg-blue-100 transition-colors">
                搜索
              </button>

              {/* Create Button */}
              <button className="flex items-center space-x-1 px-4 py-1.5 text-sm text-white bg-blue-600 rounded hover:bg-blue-700 transition-colors shadow-sm">
                <span>创建数字员工</span>
              </button>
            </div>
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {loading ? (
            <div className="col-span-full py-20 text-center text-slate-400">
              Loading employees...
            </div>
          ) : employees.length > 0 ? (
            employees.map((employee) => (
              <EmployeeCard
                key={employee.id}
                employee={employee}
                onHireClick={onHireClick}
                onClick={onEmployeeClick}
              />
            ))
          ) : (
             <div className="col-span-full py-20 text-center text-slate-400">
              No employees found in this category.
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

const FloatingToolButton: React.FC<{ icon: React.ReactNode; color?: string }> = ({ icon, color = 'text-slate-400' }) => (
    <button className={`p-2 bg-white rounded-full shadow-md hover:shadow-lg hover:scale-105 transition-all ${color}`}>
        {icon}
    </button>
);
