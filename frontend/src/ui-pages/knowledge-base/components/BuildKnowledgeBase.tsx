import React, { useState } from 'react';
import { X } from 'lucide-react';

export interface BuildKnowledgeBaseProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (name: string, description?: string) => void;
  loading?: boolean;
}

export const BuildKnowledgeBase: React.FC<BuildKnowledgeBaseProps> = ({
  isOpen,
  onClose,
  onConfirm,
  loading = false,
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleConfirm = () => {
    if (name.trim()) {
      onConfirm(name, description.trim() || undefined);
      setName('');
      setDescription('');
      setError('');
    } else {
        setError('请输入知识库名称');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setName(e.target.value);
      if (e.target.value.trim()) {
          setError('');
      }
  };

  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setDescription(e.target.value);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      ></div>

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl w-[480px] animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="flex justify-between items-center p-6 pb-2">
          <h2 className="text-lg font-bold text-slate-900">创建知识库</h2>
          <button 
            onClick={onClose} 
            className="text-slate-400 hover:text-slate-600 transition-colors p-1 rounded-full hover:bg-slate-50"
            disabled={loading}
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4">
          <div className="mb-4">
            <label className="block text-sm text-slate-700 mb-2 font-medium">
              知识库名称 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={handleInputChange}
              placeholder="例如：公司背景/产品介绍/岗位职责/客户案例"
              className={`w-full border rounded px-4 py-3 text-sm focus:outline-none focus:ring-1 transition-all
                ${error ? 'border-red-500 focus:ring-red-500' : 'border-blue-500 focus:ring-blue-500'}
                text-slate-900 placeholder-slate-400`}
              autoFocus
              disabled={loading}
            />
            {error && <p className="text-red-500 text-xs mt-2">{error}</p>}
          </div>
          
          <div className="mb-2">
            <label className="block text-sm text-slate-700 mb-2 font-medium">
              描述（可选）
            </label>
            <textarea
              value={description}
              onChange={handleDescriptionChange}
              placeholder="简要描述这个知识库的用途"
              className="w-full border border-slate-300 rounded px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500
                text-slate-900 placeholder-slate-400 resize-none h-24"
              disabled={loading}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 pt-2 flex justify-end space-x-3">
          <button 
            onClick={onClose}
            disabled={loading}
            className="px-6 py-2 rounded border border-slate-200 text-slate-600 hover:bg-slate-50 text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            取消
          </button>
          <button 
            onClick={handleConfirm}
            disabled={loading || !name.trim()}
            className="px-6 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 text-sm font-medium transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                创建中...
              </>
            ) : '确定'}
          </button>
        </div>
      </div>
    </div>
  );
};