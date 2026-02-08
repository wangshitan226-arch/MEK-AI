import React, { useState } from 'react';
import { X, ChevronDown } from 'lucide-react';

export interface CreateDigitalEmployeeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (data: { industry: string; role: string }) => void;
  onAIGenerate?: () => void;
  loading?: boolean;
  // 新增：由父组件控制的值
  industry?: string;
  role?: string;
  onIndustryChange?: (value: string) => void;
  onRoleChange?: (value: string) => void;
}

export const CreateDigitalEmployeeModal: React.FC<CreateDigitalEmployeeModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  onAIGenerate,
  loading = false,
  // 新增
  industry: externalIndustry,
  role: externalRole,
  onIndustryChange,
  onRoleChange,
}) => {
  // 如果父组件传递了值，使用父组件的；否则使用内部状态
  const [internalIndustry, setInternalIndustry] = useState('');
  const [internalRole, setInternalRole] = useState('');
  
  const industry = externalIndustry !== undefined ? externalIndustry : internalIndustry;
  const role = externalRole !== undefined ? externalRole : internalRole;
  
  const setIndustry = (value: string) => {
    if (onIndustryChange) {
      onIndustryChange(value);
    } else {
      setInternalIndustry(value);
    }
  };
  const handleConfirm = () => {
    onConfirm({ industry, role });
  };
  const setRole = (value: string) => {
    if (onRoleChange) {
      onRoleChange(value);
    } else {
      setInternalRole(value);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center font-sans">
      <div 
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      ></div>

      <div className="relative bg-white rounded-xl shadow-2xl w-[500px] animate-in fade-in zoom-in duration-200 overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-start p-8 pb-0">
          <div>
            <h2 className="text-xl font-bold text-slate-900 mb-2">创建数字员工</h2>
            <p className="text-sm text-slate-500">想创建已写好提示词的数字员工，点AI一键生成</p>
          </div>
          <button 
            onClick={onClose} 
            className="text-slate-400 hover:text-slate-600 transition-colors -mt-2 -mr-2 p-2"
            disabled={loading}
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-8 space-y-6">
          {/* Industry Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700 flex">
              <span className="text-red-500 mr-1">*</span>选择行业
            </label>
            <div className="flex space-x-2">
              <div className="relative w-1/3">
                <select 
                  className="w-full appearance-none border border-slate-300 rounded-md px-3 py-2 text-sm text-slate-700 bg-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-200"
                  disabled={loading}
                >
                  <option>自定义</option>
                  <option>教育</option>
                  <option>金融</option>
                  <option>医疗</option>
                  <option>零售</option>
                  <option>科技</option>
                </select>
                <ChevronDown size={14} className="absolute right-3 top-3 text-slate-400 pointer-events-none" />
              </div>
              <input 
                type="text" 
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                className="flex-1 border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-200"
                placeholder="请输入行业"
                disabled={loading}
              />
            </div>
          </div>

          {/* Role Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700 flex">
              <span className="text-red-500 mr-1">*</span>选择岗位
            </label>
            <div className="flex space-x-2">
              <div className="relative w-1/3">
                <select 
                  className="w-full appearance-none border border-slate-300 rounded-md px-3 py-2 text-sm text-slate-700 bg-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-200"
                  disabled={loading}
                >
                  <option>自定义</option>
                  <option>经理</option>
                  <option>专员</option>
                  <option>顾问</option>
                  <option>分析师</option>
                  <option>助理</option>
                </select>
                <ChevronDown size={14} className="absolute right-3 top-3 text-slate-400 pointer-events-none" />
              </div>
              <input 
                type="text" 
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="flex-1 border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-200"
                placeholder="请输入岗位"
                disabled={loading}
              />
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-8 pb-8 flex justify-end space-x-4">
          <button 
            onClick={onAIGenerate}
            disabled={loading}
            className="px-6 py-2 border border-blue-200 text-blue-600 rounded-md text-sm font-medium hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            AI一键生成
          </button>
          <button 
            onClick={handleConfirm}
            disabled={loading || !industry.trim() || !role.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 shadow-sm shadow-blue-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                创建中...
              </>
            ) : '立即创建'}
          </button>
        </div>
      </div>
    </div>
  );
};