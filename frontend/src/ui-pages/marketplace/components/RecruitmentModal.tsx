import React from 'react';
import { Employee } from '../types';
import { X, Minus, Plus } from 'lucide-react';

export interface RecruitmentModalProps {
  isOpen: boolean;
  employee: Employee;
  onClose: () => void;
  onConfirm: () => void;
}

export const RecruitmentModal: React.FC<RecruitmentModalProps> = ({
  isOpen,
  employee,
  onClose,
  onConfirm,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      ></div>

      {/* Modal Content */}
      <div className="relative bg-white rounded-lg shadow-xl w-[420px] p-6 animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-bold text-slate-900">招聘</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Plan Selection */}
        <div className="mb-6">
          <label className="block text-sm text-slate-600 mb-2">请选择套餐</label>
          <div className="border-2 border-blue-500 bg-blue-50/10 rounded-lg p-4 flex justify-between items-center cursor-pointer">
            <span className="font-bold text-lg text-slate-900">免费</span>
            <span className="text-slate-500 text-sm">¥{typeof employee.price === 'number' ? employee.price : '1980'}/年</span>
          </div>
        </div>

        {/* Quantity and Date Info */}
        <div className="space-y-4 mb-6">
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-600">数量</span>
            <div className="flex items-center border border-slate-200 rounded-md">
              <button className="p-1 text-slate-400 hover:bg-slate-50 border-r border-slate-200">
                <Minus size={14} />
              </button>
              <span className="w-10 text-center text-sm font-medium text-slate-700">1</span>
              <button className="p-1 text-slate-400 hover:bg-slate-50 border-l border-slate-200">
                <Plus size={14} />
              </button>
            </div>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-600">预计到期时间</span>
            <span className="text-sm text-slate-900 font-medium">2026-10-15</span>
          </div>

           <div className="flex justify-between items-center pt-2">
            <span className="text-sm text-slate-600">支付金额</span>
            <span className="text-base text-red-500 font-bold">¥0</span>
          </div>
        </div>

        {/* Action Button */}
        <button 
          onClick={onConfirm}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition-colors mb-4 shadow-sm shadow-blue-200"
        >
          免费招聘
        </button>

        {/* Agreement */}
        <div className="flex items-center justify-center space-x-2">
          <input 
            type="checkbox" 
            defaultChecked 
            className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500" 
            id="agreement"
          />
          <label htmlFor="agreement" className="text-xs text-blue-600 cursor-pointer hover:underline">
            我已充分阅读并同意《充值协议》
          </label>
        </div>
      </div>
    </div>
  );
};
