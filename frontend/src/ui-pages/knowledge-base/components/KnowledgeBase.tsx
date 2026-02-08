import React from 'react';
import { Plus, FileText } from 'lucide-react';

export interface KnowledgeBaseProps {
  items: Array<{
    id: string;
    name: string;
    docCount: number;
    description?: string;
  }>;
  onCreateClick: () => void;
  onItemClick: (id: string) => void;
  onDeleteKnowledgeBase?: (id: string) => void;
  loading?: boolean;
  error?: string | null;
}

export const KnowledgeBase: React.FC<KnowledgeBaseProps> = ({
  items,
  onCreateClick,
  onItemClick,
  onDeleteKnowledgeBase,
  loading = false,
  error = null,
}) => {
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 font-sans text-slate-900 p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-slate-600">加载知识库中...</p>
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
      {/* Header Breadcrumb - 在实际桥接组件中会包含Sidebar */}
      <main className="p-8 min-h-screen relative">
        {/* Header Breadcrumb */}
        <div className="mb-8">
            <div className="flex items-center space-x-2 text-sm text-slate-500">
                <span className="text-slate-400 text-xs mr-2">{"<"}</span>
                <span className="cursor-pointer text-slate-600 hover:text-slate-800 font-medium">知识库</span>
            </div>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">
            
            {/* Create Card */}
            <div 
                onClick={onCreateClick}
                className="bg-white rounded-lg border-2 border-dashed border-blue-200 flex flex-col items-center justify-center p-8 cursor-pointer hover:border-blue-400 hover:bg-blue-50/20 transition-all h-[180px] group shadow-sm hover:shadow-md"
            >
                <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mb-4 border border-blue-100 group-hover:scale-110 transition-transform duration-300">
                    <Plus size={24} strokeWidth={2.5} />
                </div>
                <span className="font-bold text-slate-800">创建知识库</span>
            </div>

            {/* Existing KB Cards */}
            {items.map((item) => (
                <div 
                    key={item.id}
                    className="bg-white rounded-lg border border-slate-100 p-6 flex flex-col justify-between h-[180px] shadow-sm hover:shadow-md cursor-pointer transition-all group relative"
                >
                    {/* Delete Button */}
                    {onDeleteKnowledgeBase && (
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                onDeleteKnowledgeBase(item.id);
                            }}
                            className="absolute top-3 right-3 w-6 h-6 flex items-center justify-center text-slate-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors z-10"
                            title="删除知识库"
                        >
                            ×
                        </button>
                    )}
                    
                    <div onClick={() => onItemClick(item.id)}>
                        <h3 className="font-bold text-slate-800 text-lg mb-2 truncate pr-6" title={item.name}>
                            {item.name}
                        </h3>
                        {item.description && (
                          <p className="text-slate-500 text-sm line-clamp-2 mb-2">
                            {item.description}
                          </p>
                        )}
                    </div>
                    
                    <div className="flex items-center justify-between" onClick={() => onItemClick(item.id)}>
                      <div className="flex items-center space-x-2 text-slate-400 text-sm">
                          <FileText size={16} />
                          <span>{item.docCount ?? 0} 个知识块</span>
                      </div>
                      <div className="text-xs text-slate-400 group-hover:text-blue-500 transition-colors">
                        查看详情 →
                      </div>
                    </div>
                </div>
            ))}

        </div>
      </main>
    </div>
  );
};