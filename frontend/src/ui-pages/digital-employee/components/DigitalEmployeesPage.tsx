import React from 'react';
import { Plus, Users } from 'lucide-react';
import { EmployeeCard } from './EmployeeCard';
import { Employee } from '@/shared/types/employee';

// 纯props接口
export interface DigitalEmployeesPageProps {
  // 数据
  createdEmployees: Employee[];
  hiredEmployees: Employee[];
  
  // 状态
  activeTab: 'created' | 'hired';
  currentView: string;
  loading?: boolean;
  error?: string | null;
  
  // 回调函数
  onEmployeeClick: (employeeId: string) => void;
  onNavigate: (view: string) => void;
  onTabChange: (tab: 'created' | 'hired') => void;
  onCreateClick: () => void;
  onEditEmployee: (employeeId: string) => void;
  onDismissEmployee: (employeeId: string) => void;
}

export const DigitalEmployeesPage: React.FC<DigitalEmployeesPageProps> = ({
  createdEmployees,
  hiredEmployees,
  activeTab,
  currentView,
  loading = false,
  error = null,
  onEmployeeClick,
  onNavigate,
  onTabChange,
  onCreateClick,
  onEditEmployee,
  onDismissEmployee,
}) => {
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 font-sans text-slate-900 p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-slate-600">加载中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 font-sans text-slate-900 p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      <main className="p-8 min-h-screen relative">
        {/* Header */}
        <div className="mb-4">
          <div className="flex items-center space-x-2 text-sm text-slate-500 mb-6">
            <span 
              className="cursor-pointer hover:text-slate-800" 
              onClick={() => onNavigate('digital-employees')}
            >
              数字员工
            </span>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center space-x-8 border-b border-slate-200 mb-8">
          <button 
            onClick={() => onTabChange('created')}
            className={`pb-3 text-sm font-bold transition-colors relative px-1 ${
              activeTab === 'created' ? 'text-blue-600' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            我创建的
            {activeTab === 'created' && <span className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-600 rounded-t-full"></span>}
          </button>
          <button 
            onClick={() => onTabChange('hired')}
            className={`pb-3 text-sm font-bold transition-colors relative px-1 ${
              activeTab === 'hired' ? 'text-blue-600' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            我招聘的
            {activeTab === 'hired' && <span className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-600 rounded-t-full"></span>}
          </button>
        </div>

        {/* Content */}
        {activeTab === 'created' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 animate-in fade-in duration-300">
            {/* Create Card */}
            <div 
              className="bg-white rounded-lg border-2 border-dashed border-blue-200 flex flex-col items-center justify-center p-10 cursor-pointer hover:border-blue-400 hover:bg-blue-50/20 transition-all h-[360px] group shadow-sm hover:shadow-md"
              onClick={onCreateClick}
            >
              <div className="w-16 h-16 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mb-6 border border-blue-100 group-hover:scale-110 transition-transform duration-300">
                <Plus size={32} strokeWidth={2.5} />
              </div>
              <span className="font-bold text-slate-800 text-lg">创建数字员工</span>
            </div>
            
            {/* Created Employees List */}
            {createdEmployees.map(emp => (
              <EmployeeCard 
                key={emp.id} 
                employee={emp} 
                onClick={onEmployeeClick} 
                variant="created"
                onEdit={onEditEmployee}
                onDelete={onDismissEmployee}
              />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 animate-in fade-in duration-300">
            {hiredEmployees.length > 0 ? (
              hiredEmployees.map(emp => (
                <EmployeeCard 
                  key={emp.id} 
                  employee={emp} 
                  onClick={onEmployeeClick} 
                  variant="default"
                />
              ))
            ) : (
              <div className="col-span-full py-20 flex flex-col items-center justify-center text-slate-400">
                <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                  <Users size={24} className="text-slate-300"/>
                </div>
                <p>暂无招聘的数字员工</p>
                <button 
                  onClick={() => onNavigate('marketplace')} 
                  className="mt-4 text-blue-600 text-sm hover:underline"
                >
                  去广场招聘
                </button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default DigitalEmployeesPage;