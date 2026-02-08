import React, { useState, useRef, useEffect } from 'react';
import { 
  ChevronLeft, 
  Upload, 
  ChevronDown, 
  RotateCcw, 
  Wand2, 
  X,
  Bot,
  User,
  Send,
  AlertCircle
} from 'lucide-react';
import { Employee } from '@/shared/types/employee';
import { KnowledgeBase } from '@/shared/types/knowledge';

// 本地类型定义，用于避免类型冲突
export interface EditDigitalEmployeeProps {
  // 初始数据
  initialData?: Partial<Employee>;
  
  // 外部数据
  knowledgeBases: KnowledgeBase[];
  
  // 状态
  activeTab?: 'persona' | 'skills' | 'anthropomorphism' | 'reply' | 'business' | 'human';
  formData: Partial<Employee>;
  previewMessages: Array<{ role: 'user' | 'model'; content: string }>;
  chatInput: string;
  hasSaved?: boolean;
  errors?: Record<string, boolean>;
  saving?: boolean;
  publishing?: boolean;
  
  // 事件处理
  onCancel: () => void;
  onSave: () => void;
  onPublish: () => void;
  onInputChange: (field: string, value: any) => void;
  onImageUpload: (file: File) => void;
  onTabChange: (tab: 'persona' | 'skills' | 'anthropomorphism' | 'reply' | 'business' | 'human') => void;
  onChatInputChange: (input: string) => void;
  onSendPreviewMessage: (content: string) => void;
  
  // 其他
  fileInputRef?: React.RefObject<HTMLInputElement>;
}

// 组件实现保持不变...

export const EditDigitalEmployee: React.FC<EditDigitalEmployeeProps> = ({
  initialData,
  knowledgeBases,
  activeTab = 'persona',
  formData,
  previewMessages,
  chatInput,
  hasSaved = false,
  errors = {},
  saving = false,
  publishing = false,
  onCancel,
  onSave,
  onPublish,
  onInputChange,
  onImageUpload,
  onTabChange,
  onChatInputChange,
  onSendPreviewMessage,
  fileInputRef,
}) => {
  const [isKBDropdownOpen, setIsKBDropdownOpen] = useState(false);
  const kbDropdownRef = useRef<HTMLDivElement>(null);

  // 点击外部关闭知识库下拉框
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (kbDropdownRef.current && !kbDropdownRef.current.contains(event.target as Node)) {
        setIsKBDropdownOpen(false);
      }
    };

    if (isKBDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isKBDropdownOpen]);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onImageUpload(file);
    }
  };

  const handleKBSelect = (kbId: string) => {
    const currentIds = formData.knowledgeBaseIds || [];
    if (!currentIds.includes(kbId)) {
      onInputChange('knowledgeBaseIds', [...currentIds, kbId]);
    }
    setIsKBDropdownOpen(false);
  };

  const handleSendMessage = () => {
    if (chatInput.trim()) {
      onSendPreviewMessage(chatInput);
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">
      
      {/* LEFT SIDE: Editor */}
      <div className="flex-1 flex flex-col min-w-0 border-r border-slate-200 bg-white">
        
        {/* Header */}
        <div className="h-16 border-b border-slate-100 flex items-center px-6 justify-between bg-white shrink-0">
           <div className="flex items-center space-x-3">
              <button onClick={onCancel} className="p-1.5 hover:bg-slate-100 rounded-full text-slate-500 transition-colors">
                  <ChevronLeft size={22} />
              </button>
              <h1 className="text-lg font-bold text-slate-800">编辑数字员工</h1>
           </div>
           
           <div className="flex space-x-3">
             <button 
                onClick={onSave}
                disabled={saving}
                className="px-6 py-2 border border-blue-200 text-blue-600 rounded bg-white hover:bg-blue-50 text-sm font-medium transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
             >
                {saving ? (
                  <>
                    <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-2"></div>
                    保存中...
                  </>
                ) : '保存'}
             </button>
             <button 
                onClick={onPublish}
                disabled={publishing}
                className="px-6 py-2 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700 shadow-sm shadow-blue-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
             >
                {publishing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    发布中...
                  </>
                ) : '发布'}
             </button>
           </div>
        </div>

        {/* Tabs */}
        <div className="px-8 pt-6 border-b border-slate-100">
            <div className="flex space-x-8">
                {[
                    {id: 'persona', label: '人设'},
                    {id: 'skills', label: '技能'},
                    {id: 'anthropomorphism', label: '拟人化'},
                    {id: 'reply', label: '追加回复'},
                    {id: 'business', label: '业务对接'},
                    {id: 'human', label: '转人工'},
                ].map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => onTabChange(tab.id as any)}
                        className={`pb-3 text-sm font-medium transition-colors relative ${
                            activeTab === tab.id 
                                ? 'text-blue-600' 
                                : 'text-slate-500 hover:text-slate-700'
                        }`}
                    >
                        {tab.label}
                        {activeTab === tab.id && (
                            <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-5 h-0.5 bg-blue-600 rounded-full"></span>
                        )}
                    </button>
                ))}
            </div>
        </div>

        {/* Scrollable Form Content */}
        <div className="flex-1 overflow-y-auto p-8 bg-slate-50/30">
            <div className="max-w-4xl mx-auto space-y-6">
                
                {/* PERSONA TAB CONTENT */}
                {activeTab === 'persona' && (
                    <div className="bg-white p-8 rounded-xl border border-slate-100 shadow-sm space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-300">
                        {/* Avatar */}
                        <div className="flex items-start space-x-8">
                            <div className="w-[100px] text-right text-sm font-bold text-slate-700 pt-3">
                                <span className="text-red-500 mr-1">*</span>头像
                            </div>
                            <div className="flex-1">
                                <div 
                                    className={`w-24 h-24 rounded-full border-2 flex items-center justify-center cursor-pointer overflow-hidden relative group transition-all
                                        ${errors.avatar ? 'border-red-400 bg-red-50' : 'border-slate-200 bg-slate-50 hover:border-blue-400'}
                                    `}
                                    onClick={() => fileInputRef?.current?.click()}
                                >
                                    {formData.avatar ? (
                                        <img src={formData.avatar} alt="Avatar" className="w-full h-full object-cover" />
                                    ) : (
                                        <div className="flex flex-col items-center justify-center text-slate-400">
                                            <Upload size={24} className="mb-1" />
                                            <span className="text-xs">上传头像</span>
                                        </div>
                                    )}
                                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                        <Upload className="text-white" size={20} />
                                    </div>
                                </div>
                                <input 
                                    type="file" 
                                    ref={fileInputRef} 
                                    onChange={handleImageSelect} 
                                    className="hidden" 
                                    accept="image/*"
                                />
                                {errors.avatar && <p className="text-red-500 text-xs mt-2">请上传头像</p>}
                            </div>
                        </div>

                        {/* Industry & Role */}
                        <div className="flex items-start space-x-8">
                             <div className="w-[100px] text-right text-sm font-bold text-slate-700 pt-2.5">
                                <span className="text-red-500 mr-1">*</span>行业
                            </div>
                            <div className="flex-1 flex space-x-6">
                                <div className="flex-1 flex space-x-3">
                                    <div className="relative w-[120px]">
                                        <select className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm appearance-none bg-white focus:ring-2 focus:ring-blue-100 focus:border-blue-400 outline-none transition-all">
                                            <option>自定义</option>
                                        </select>
                                        <ChevronDown size={14} className="absolute right-2 top-3 text-slate-400 pointer-events-none"/>
                                    </div>
                                    <div className="flex-1">
                                        <input 
                                            type="text" 
                                            value={formData.industry || ''} 
                                            onChange={(e) => onInputChange('industry', e.target.value)}
                                            className={`w-full border rounded-md px-3 py-2 text-sm outline-none transition-all focus:ring-2 focus:ring-blue-100
                                                ${errors.industry ? 'border-red-300 focus:border-red-400' : 'border-slate-200 focus:border-blue-400'}
                                            `}
                                            placeholder="输入行业"
                                        />
                                        {errors.industry && <p className="text-red-500 text-xs mt-1 absolute">请输入行业</p>}
                                    </div>
                                </div>
                            </div>

                            <div className="w-[80px] text-right text-sm font-bold text-slate-700 pt-2.5">
                                <span className="text-red-500 mr-1">*</span>岗位/名称
                            </div>
                            <div className="flex-1 flex space-x-3">
                                <div className="relative w-[120px]">
                                    <select className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm appearance-none bg-white focus:ring-2 focus:ring-blue-100 focus:border-blue-400 outline-none transition-all">
                                        <option>自定义</option>
                                    </select>
                                    <ChevronDown size={14} className="absolute right-2 top-3 text-slate-400 pointer-events-none"/>
                                </div>
                                <div className="flex-1">
                                    <input 
                                        type="text" 
                                        value={formData.name || ''}
                                        onChange={(e) => onInputChange('name', e.target.value)}
                                        className={`w-full border rounded-md px-3 py-2 text-sm outline-none transition-all focus:ring-2 focus:ring-blue-100
                                            ${errors.name ? 'border-red-300 focus:border-red-400' : 'border-slate-200 focus:border-blue-400'}
                                        `}
                                        placeholder="输入名称"
                                    />
                                    {errors.name && <p className="text-red-500 text-xs mt-1 absolute">请输入名称</p>}
                                </div>
                            </div>
                        </div>

                        {/* Description */}
                        <div className="flex items-start space-x-8">
                            <div className="w-[100px] text-right text-sm font-bold text-slate-700 pt-2">
                                <span className="text-red-500 mr-1">*</span>介绍
                            </div>
                            <div className="flex-1 relative">
                                <textarea 
                                    value={formData.description || ''}
                                    onChange={(e) => onInputChange('description', e.target.value)}
                                    className={`w-full border rounded-md px-3 py-2 text-sm h-24 resize-none outline-none transition-all focus:ring-2 focus:ring-blue-100
                                        ${errors.description ? 'border-red-300 focus:border-red-400' : 'border-slate-200 focus:border-blue-400'}
                                    `}
                                    placeholder="数字员工的特长或工作内容，让大家更了解他哦"
                                    maxLength={200}
                                />
                                <span className="absolute bottom-2 right-2 text-xs text-slate-400">
                                    {(formData.description?.length || 0)} / 200
                                </span>
                                {errors.description && <p className="text-red-500 text-xs mt-1">请输入介绍</p>}
                            </div>
                        </div>

                        {/* Prompt */}
                        <div className="pt-4 border-t border-slate-100">
                            <div className="flex justify-between items-center mb-4">
                                <div className="flex space-x-4 text-sm text-slate-500">
                                    <span className="text-slate-900 font-bold border-b-2 border-blue-600 pb-1 cursor-pointer">提示词</span>
                                    <span className="hover:text-slate-800 cursor-pointer pb-1">角色、背景、职责、工作流、沟通方式、目的</span>
                                </div>
                                <div className="flex space-x-2">
                                    <button className="flex items-center px-3 py-1.5 border border-slate-200 rounded text-xs text-slate-600 hover:bg-slate-50 transition-colors">
                                        <RotateCcw size={12} className="mr-1.5"/>
                                        撤销
                                    </button>
                                    <button className="flex items-center px-3 py-1.5 bg-blue-50 text-blue-600 border border-blue-100 rounded text-xs hover:bg-blue-100 transition-colors">
                                        <Wand2 size={12} className="mr-1.5"/>
                                        AI一键生成/优化
                                    </button>
                                </div>
                            </div>
                            <div className="relative">
                                <textarea 
                                    value={formData.prompt || ''}
                                    onChange={(e) => onInputChange('prompt', e.target.value)}
                                    className="w-full border border-slate-200 rounded-lg p-4 text-sm font-mono h-[300px] focus:border-blue-400 focus:ring-2 focus:ring-blue-50 outline-none leading-relaxed text-slate-700 shadow-inner"
                                />
                            </div>
                        </div>
                    </div>
                )}

                {/* SKILLS TAB CONTENT */}
                {activeTab === 'skills' && (
                    <div className="bg-white p-8 rounded-xl border border-slate-100 shadow-sm space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
                        {/* Model Source */}
                        <div className="flex items-center space-x-8">
                            <div className="w-[100px] text-right text-sm font-bold text-slate-700">
                                模型来源
                            </div>
                            <div className="flex bg-slate-100 rounded-md p-1">
                                <button className="px-6 py-1.5 bg-white text-blue-600 shadow-sm font-medium text-sm rounded-md transition-all">系统内置</button>
                                <button className="px-6 py-1.5 text-slate-500 text-sm hover:text-slate-900 transition-colors">自有令牌</button>
                            </div>
                        </div>

                        {/* Model Selection */}
                        <div className="flex items-center space-x-8">
                            <div className="w-[100px] text-right text-sm font-bold text-slate-700">
                                模型选择
                            </div>
                            <div className="relative w-[320px]">
                                <select 
                                    value={formData.model || 'gemini-2.5-pro-preview'}
                                    onChange={(e) => onInputChange('model', e.target.value)}
                                    className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm appearance-none bg-white focus:border-blue-400 focus:ring-2 focus:ring-blue-50 outline-none transition-all"
                                >
                                    <option value="gemini-2.5-pro-preview">gemini-2.5-pro-preview</option>
                                    <option value="gemini-2.5-flash">gemini-2.5-flash</option>
                                </select>
                                <ChevronDown size={14} className="absolute right-3 top-3 text-slate-400 pointer-events-none"/>
                            </div>
                        </div>

                         {/* Image Recognition */}
                        <div className="flex items-center space-x-8">
                            <div className="w-[100px] text-right text-sm font-bold text-slate-700">
                                图片识别
                            </div>
                            <div className="flex bg-slate-100 rounded-md p-1">
                                <button className="px-6 py-1.5 bg-white text-slate-900 font-medium shadow-sm text-sm rounded-md">开启</button>
                                <button className="px-6 py-1.5 text-slate-500 text-sm hover:text-slate-900">关闭</button>
                            </div>
                        </div>

                        {/* Knowledge Base Association - Clean Style */}
                        <div className="border border-slate-200 rounded-lg p-6 relative mt-8 bg-slate-50/50">
                             <div className="absolute -top-3 left-4 bg-white px-2 text-sm font-bold text-slate-700">
                                关联知识库（可多选）
                             </div>
                             <div className="absolute top-[-26px] right-2 text-xs text-slate-400 hidden lg:block">
                                AI在和用户对话中，可以调用知识库内容进行专业回答
                             </div>

                             <div className="space-y-3 mt-2">
                                {/* Selected Tags Area */}
                                <div className="flex flex-wrap gap-2 min-h-[32px]">
                                    {(formData.knowledgeBaseIds || []).map(kbId => {
                                        const kb = knowledgeBases.find(k => k.id === kbId);
                                        return kb ? (
                                            <span key={kb.id} className="inline-flex items-center bg-blue-50 text-blue-700 px-2.5 py-1 rounded-md text-xs border border-blue-100 font-medium animate-in zoom-in duration-200">
                                                {kb.name}
                                                <button 
                                                    onClick={() => {
                                                        const currentIds = formData.knowledgeBaseIds || [];
                                                        onInputChange('knowledgeBaseIds', currentIds.filter(id => id !== kbId));
                                                    }}
                                                    className="ml-1.5 text-blue-400 hover:text-blue-600"
                                                >
                                                    <X size={14}/>
                                                </button>
                                            </span>
                                        ) : null;
                                    })}
                                    {(!formData.knowledgeBaseIds || formData.knowledgeBaseIds.length === 0) && (
                                        <span className="text-slate-400 text-xs py-1">暂未关联知识库</span>
                                    )}
                                </div>

                                {/* Dropdown Trigger */}
                                <div className="relative" ref={kbDropdownRef}>
                                     <button
                                        onClick={() => setIsKBDropdownOpen(!isKBDropdownOpen)}
                                        className="w-full border border-slate-200 rounded-md px-3 py-2.5 text-sm bg-white flex items-center justify-between hover:border-blue-400 focus:ring-2 focus:ring-blue-50 transition-all text-slate-700"
                                     >
                                        <span className="text-slate-500">点击选择知识库...</span>
                                        <ChevronDown size={16} className={`text-slate-400 transition-transform ${isKBDropdownOpen ? 'rotate-180' : ''}`}/>
                                     </button>
                                     
                                     {/* Dropdown Menu */}
                                     {isKBDropdownOpen && (
                                        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-md shadow-lg z-50 max-h-48 overflow-y-auto">
                                            {knowledgeBases.length === 0 ? (
                                                <div className="px-3 py-2 text-sm text-slate-400">暂无知识库</div>
                                            ) : (
                                                knowledgeBases.map(kb => {
                                                    const isSelected = (formData.knowledgeBaseIds || []).includes(kb.id);
                                                    return (
                                                        <button
                                                            key={kb.id}
                                                            onClick={() => handleKBSelect(kb.id)}
                                                            disabled={isSelected}
                                                            className={`w-full px-3 py-2 text-left text-sm hover:bg-blue-50 transition-colors ${
                                                                isSelected ? 'text-slate-400 cursor-not-allowed' : 'text-slate-700'
                                                            }`}
                                                        >
                                                            {kb.name} {isSelected && '(已选择)'}
                                                        </button>
                                                    );
                                                })
                                            )}
                                        </div>
                                     )}
                                </div>
                             </div>
                        </div>

                    </div>
                )}

            </div>
        </div>
      </div>

      {/* RIGHT SIDE: Chat Preview */}
      <div className="w-[420px] bg-white border-l border-slate-200 flex flex-col shrink-0 shadow-[-4px_0_15px_-3px_rgba(0,0,0,0.05)] z-10">
         {/* Preview Header */}
         <div className="h-16 border-b border-slate-100 flex items-center justify-between px-6 bg-white">
            <span className="text-sm font-bold text-slate-800 flex items-center">
                <Bot size={18} className="mr-2 text-blue-600"/>
                预览与调试
            </span>
            <span className="text-xs text-blue-600 bg-blue-50 border border-blue-100 px-2 py-1 rounded-full font-medium">
                {formData.model || 'gemini-2.5-pro-preview'}
            </span>
         </div>

         {/* Preview Body */}
         <div className="flex-1 overflow-hidden relative bg-white">
            {!hasSaved && previewMessages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-400 p-8 text-center bg-slate-50/50">
                    <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mb-4 shadow-sm">
                        <Wand2 size={24} className="text-blue-400" />
                    </div>
                    <p className="text-sm font-medium text-slate-600 mb-1">准备就绪</p>
                    <p className="text-xs text-slate-400">完善左侧信息并点击"保存"<br/>即可激活对话测试</p>
                </div>
            ) : (
                <div className="flex-1 overflow-y-auto p-5 space-y-6">
                    {previewMessages.map((msg, idx) => (
                        <div key={idx} className={`flex group ${msg.role === 'user' ? 'justify-end' : 'justify-start'} items-start space-x-3`}>
                            {/* Bot Avatar */}
                            {msg.role === 'model' && (
                                <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0 mt-1 border border-slate-100 shadow-sm">
                                    <img
                                        src={formData.avatar || `https://ui-avatars.com/api/?name=${formData.name || 'Bot'}&background=random`}
                                        alt="Bot"
                                        className="w-full h-full object-cover"
                                    />
                                </div>
                            )}

                            <div className={`flex flex-col max-w-[80%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                                <div 
                                    className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm transition-shadow hover:shadow-md ${
                                    msg.role === 'user' 
                                        ? 'bg-blue-600 text-white rounded-tr-none' 
                                        : 'bg-slate-50 border border-slate-100 text-slate-800 rounded-tl-none'
                                    }`}
                                >
                                    <div className="whitespace-pre-wrap">{msg.content}</div>
                                </div>
                            </div>

                            {/* User Avatar */}
                            {msg.role === 'user' && (
                                <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0 mt-1 text-slate-400 border border-slate-200">
                                    <User size={16} />
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
         </div>

         {/* Preview Input */}
         <div className="p-4 bg-white border-t border-slate-100">
            <div className="relative">
                <input 
                    type="text" 
                    value={chatInput}
                    onChange={(e) => onChatInputChange(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="输入文字进行测试..."
                    disabled={!hasSaved}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-4 pr-12 py-3.5 text-sm focus:outline-none focus:border-blue-400 focus:bg-white transition-all disabled:opacity-60 disabled:cursor-not-allowed placeholder-slate-400 text-slate-700 shadow-inner"
                />
                <button 
                    onClick={handleSendMessage}
                    disabled={!chatInput.trim() || !hasSaved}
                    className="absolute right-2 top-2 p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg disabled:text-slate-300 disabled:hover:bg-transparent transition-colors"
                >
                    <Send size={20} />
                </button>
            </div>
            {!hasSaved && (
                <div className="flex items-center justify-center mt-2 text-xs text-amber-500">
                    <AlertCircle size={12} className="mr-1"/>
                    <span>请先保存配置才能开始对话</span>
                </div>
            )}
         </div>
      </div>
    </div>
  );
};