import React from 'react';
import { X, Minus, Plus, Loader2, FileText, Upload } from 'lucide-react';

export interface AddFileProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<boolean> | void;
  
  // 配置状态
  fileType: 'text' | 'table';
  chunkLength: number;
  overlapLength: number;
  autoSegment: boolean;
  
  // 文件状态
  selectedFile: File | null;
  isUploading: boolean;
  uploadedFileId: string | null;
  isParsing: boolean;
  parseResults: Array<{
    id: string;
    serialNo: number;
    content: string;
    wordCount: number;
    createTime: string;
  }>;
  
  // 事件处理
  onFileTypeChange: (type: 'text' | 'table') => void;
  onChunkLengthChange: (value: number) => void;
  onOverlapLengthChange: (value: number) => void;
  onAutoSegmentChange: (value: boolean) => void;
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onTriggerFileSelect: () => void;
  onAIProcess: () => void;
  
  // 删除操作
  onDeleteKnowledgeItem?: (id: string) => void;
  onClearAllKnowledge?: () => void;
  
  // 其他
  fileInputRef: React.RefObject<HTMLInputElement>;
  canProcess?: boolean;
  canSave?: boolean;
  error?: string | null;
  loading?: boolean;
}

export const AddFile: React.FC<AddFileProps> = ({
  isOpen,
  onClose,
  onConfirm,
  
  fileType,
  chunkLength,
  overlapLength,
  autoSegment,
  
  selectedFile,
  isUploading,
  uploadedFileId,
  isParsing,
  parseResults,
  
  onFileTypeChange,
  onChunkLengthChange,
  onOverlapLengthChange,
  onAutoSegmentChange,
  onFileChange,
  onTriggerFileSelect,
  onAIProcess,
  
  onDeleteKnowledgeItem,
  onClearAllKnowledge,
  
  fileInputRef,
  canProcess = false,
  canSave = false,
  error = null,
  loading = false,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center font-sans">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      ></div>

      {/* Modal - Fixed Dimensions with Flex Column Layout */}
      <div className="relative bg-white rounded-xl shadow-2xl w-[900px] h-[600px] flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200">
        
        {/* 1. Header (Fixed Height, Shrink 0) */}
        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-100 shrink-0 bg-white">
          <div className="flex items-center space-x-2">
             <h2 className="text-lg font-bold text-slate-800">添加文件</h2>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors p-1 rounded-full hover:bg-slate-50">
            <X size={20} />
          </button>
        </div>

        {/* 2. Body (Flex 1, Takes remaining height) */}
        <div className="flex flex-1 overflow-hidden min-h-0">
            
            {/* Left Sidebar: Config & Upload (Scrollable) */}
            <div className="w-[340px] border-r border-slate-100 p-6 flex flex-col overflow-y-auto bg-white shrink-0">
                
                {/* File Type */}
                <div className="mb-6">
                    <label className="block text-xs text-slate-700 mb-2.5 font-bold">
                        <span className="text-red-500 mr-1">*</span>文件类型
                    </label>
                    <div className="flex rounded-md overflow-hidden border border-blue-600">
                        <button 
                            onClick={() => onFileTypeChange('table')}
                            className={`flex-1 py-1.5 text-sm font-medium transition-colors ${fileType === 'table' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'}`}
                            disabled={isUploading || isParsing}
                        >
                            表格类型
                        </button>
                        <button 
                            onClick={() => onFileTypeChange('text')}
                            className={`flex-1 py-1.5 text-sm font-medium transition-colors ${fileType === 'text' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'}`}
                            disabled={isUploading || isParsing}
                        >
                            文本类型
                        </button>
                    </div>
                </div>

                {/* Chunk Length */}
                <div className="mb-6">
                    <label className="block text-xs text-slate-700 mb-2.5 font-bold">
                         <span className="text-red-500 mr-1">*</span>知识点长度
                    </label>
                    <div className="flex items-center border border-slate-300 rounded px-1 py-1 group focus-within:border-blue-500 hover:border-slate-400 transition-colors">
                        <button 
                            onClick={() => onChunkLengthChange(Math.max(100, chunkLength - 100))}
                            className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            disabled={isUploading || isParsing}
                        >
                            <Minus size={14} />
                        </button>
                        <input 
                            type="number" 
                            value={chunkLength} 
                            onChange={(e) => onChunkLengthChange(Number(e.target.value))}
                            className="flex-1 text-center text-sm text-slate-900 font-medium focus:outline-none bg-transparent"
                            disabled={isUploading || isParsing}
                        />
                         <button 
                            onClick={() => onChunkLengthChange(chunkLength + 100)}
                            className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            disabled={isUploading || isParsing}
                        >
                            <Plus size={14} />
                        </button>
                    </div>
                </div>

                {/* Overlap Length */}
                <div className="mb-6">
                    <label className="block text-xs text-slate-700 mb-2.5 font-bold">
                        <span className="text-red-500 mr-1">*</span>知识点重叠长度
                    </label>
                    <div className="flex items-center border border-slate-300 rounded px-1 py-1 group focus-within:border-blue-500 hover:border-slate-400 transition-colors">
                        <button 
                             onClick={() => onOverlapLengthChange(Math.max(0, overlapLength - 10))}
                            className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            disabled={isUploading || isParsing}
                        >
                            <Minus size={14} />
                        </button>
                        <input 
                            type="number" 
                            value={overlapLength} 
                            onChange={(e) => onOverlapLengthChange(Number(e.target.value))}
                            className="flex-1 text-center text-sm text-slate-900 font-medium focus:outline-none bg-transparent"
                            disabled={isUploading || isParsing}
                        />
                         <button 
                            onClick={() => onOverlapLengthChange(overlapLength + 10)}
                            className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            disabled={isUploading || isParsing}
                        >
                            <Plus size={14} />
                        </button>
                    </div>
                </div>

                 {/* Auto Segment */}
                <div className="mb-6">
                    <div className="flex justify-between items-center mb-2">
                        <label className="text-sm text-slate-700 font-medium">换行自动分段</label>
                        <button 
                            onClick={() => onAutoSegmentChange(!autoSegment)}
                            className={`w-9 h-5 rounded-full relative transition-colors ${autoSegment ? 'bg-blue-600' : 'bg-slate-200'} disabled:opacity-50`}
                            disabled={isUploading || isParsing}
                        >
                            <div className={`w-3.5 h-3.5 bg-white rounded-full absolute top-0.5 transition-all shadow-sm ${autoSegment ? 'left-[20px]' : 'left-0.5'}`}></div>
                        </button>
                    </div>
                    <p className="text-[10px] text-slate-400 mt-1">仅txt/docx生效，每段最多500字</p>
                </div>

                {/* Upload Area */}
                <div className="mb-6">
                     <label className="block text-xs text-slate-700 mb-2.5 font-bold">
                        <span className="text-red-500 mr-1">*</span>知识库文件
                     </label>
                     <div className="flex items-center space-x-3">
                        <input 
                            type="file" 
                            ref={fileInputRef} 
                            onChange={onFileChange} 
                            className="hidden" 
                            accept=".txt,.doc,.docx,.pdf,.md"
                            disabled={isUploading || isParsing}
                        />
                        <button 
                            onClick={onTriggerFileSelect}
                            disabled={isUploading || isParsing}
                            className="px-6 py-1.5 text-sm border border-slate-300 rounded-md text-slate-700 hover:bg-slate-50 transition-colors bg-white font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                        >
                            <Upload size={14} className="mr-2" />
                            上传
                        </button>
                        
                        {isUploading && (
                            <div className="flex items-center text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                                <Loader2 size={12} className="animate-spin mr-1.5"/>
                                <span>上传中...</span>
                            </div>
                        )}
                        
                        {!isUploading && selectedFile && (
                            <div className="flex items-center text-xs text-slate-600 bg-slate-100 px-2 py-1 rounded max-w-[140px]">
                                <FileText size={12} className="mr-1.5 flex-shrink-0" />
                                <span className="truncate" title={selectedFile.name}>{selectedFile.name}</span>
                            </div>
                        )}
                     </div>
                     
                     {error && (
                       <div className="mt-2 text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
                         {error}
                       </div>
                     )}
                </div>
                
                {/* AI Process Button */}
                <div className="mt-2">
                     <button 
                        onClick={onAIProcess}
                        disabled={!canProcess || isParsing}
                        className={`w-[120px] h-[36px] text-white text-sm font-medium rounded-md shadow-sm flex items-center justify-center space-x-2 transition-all
                            ${(!canProcess || isParsing) ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 shadow-blue-200'}
                        `}
                     >
                        {isParsing ? (
                            <>
                                <Loader2 size={16} className="animate-spin" />
                                <span>处理中...</span>
                            </>
                        ) : (
                            <span>AI处理</span>
                        )}
                     </button>
                </div>
            </div>

            {/* Right Content: Preview */}
            <div className="flex-1 p-6 flex flex-col bg-slate-50 overflow-hidden">
                <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center justify-between">
                    <div className="flex items-center">
                        知识点预览
                        {parseResults.length > 0 && <span className="ml-2 text-xs font-normal text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200">共 {parseResults.length} 条</span>}
                    </div>
                    {parseResults.length > 0 && (
                        <button
                            onClick={onClearAllKnowledge}
                            className="text-xs text-red-500 hover:text-red-600 hover:underline"
                        >
                            一键清除
                        </button>
                    )}
                </h3>
                
                <div className="flex-1 bg-white border border-slate-200 rounded-lg flex flex-col overflow-hidden shadow-sm">
                    {/* Table Header */}
                    <div className="flex bg-slate-50 border-b border-slate-200 text-xs text-slate-500 py-3 px-4 font-bold shrink-0">
                        <div className="w-16 text-center border-r border-slate-200 mr-4">序号</div>
                        <div className="flex-1">知识点内容</div>
                    </div>
                    
                    {/* Table Body */}
                    <div className="flex-1 overflow-y-auto bg-white">
                        {parseResults.length > 0 ? (
                            <div className="divide-y divide-slate-100">
                                {parseResults.map((item, index) => (
                                    <div key={item.id} className="flex text-xs hover:bg-blue-50/30 transition-colors group">
                                        <div className="w-16 py-3 text-center text-slate-400 font-mono border-r border-slate-100 shrink-0 flex items-center justify-center mr-4 bg-slate-50/50 group-hover:bg-transparent">
                                            {index + 1}
                                        </div>
                                        <div className="flex-1 py-3 px-4 text-slate-700 leading-relaxed break-all">
                                            {item.content}
                                        </div>
                                        <button
                                            onClick={() => onDeleteKnowledgeItem?.(item.id)}
                                            className="px-3 py-3 text-slate-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                            title="删除"
                                        >
                                            ×
                                        </button>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            /* Empty State */
                            <div className="h-full flex flex-col items-center justify-center text-slate-400 text-sm bg-white">
                                <div className="w-16 h-16 mb-3 bg-slate-50 rounded-full flex items-center justify-center">
                                    <span className="text-2xl opacity-20">📄</span>
                                </div>
                                <span className="text-slate-400">暂无数据</span>
                                <span className="text-slate-400 text-xs mt-1">请先上传文件并进行AI处理</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>

        {/* 3. Footer (Fixed Height, Shrink 0) - BUTTONS ARE HERE */}
        <div className="px-6 py-4 border-t border-slate-100 bg-white shrink-0 flex justify-end space-x-3 z-20">
          <button 
            onClick={onClose}
            className="px-6 py-2 rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50 text-sm font-medium transition-colors"
            disabled={loading}
          >
            取消
          </button>
          <button 
            onClick={async () => {
              if (typeof onConfirm === 'function') {
                const result = await onConfirm();
                if (result) onClose();
              }
            }}
            disabled={!canSave || loading}
            className={`px-6 py-2 rounded-md text-sm font-medium transition-all shadow-sm flex items-center
                ${canSave && !loading
                    ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-blue-200' 
                    : 'bg-blue-100 text-blue-400 cursor-not-allowed'
                }
            `}
          >
            {loading ? (
              <>
                <Loader2 size={16} className="animate-spin mr-2" />
                保存中...
              </>
            ) : '确定'}
          </button>
        </div>
      </div>
    </div>
  );
};