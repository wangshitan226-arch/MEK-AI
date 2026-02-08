// 在 src/ui-pages/marketplace/components/ChatInterface.tsx 中做以下修改：

import React, { useRef, useEffect } from 'react'; // 1. 添加 useRef 和 useEffect
import { Employee, ChatSession, Message } from '../types';
import { 
  ChevronLeft, 
  MessageSquarePlus, 
  Image as ImageIcon, 
  Send, 
  Globe, 
  MessageSquareText, 
  PanelLeftClose, 
  PanelLeftOpen,
  Copy,
  Check,
  User
} from 'lucide-react';

export interface ChatInterfaceProps {
  employee: Employee;
  sessions: ChatSession[];
  currentSessionId: string | null;
  messages: Message[];
  inputValue: string;
  isHistoryVisible: boolean;
  copiedMessageId: string | null;
  onBack: () => void;
  onInputChange: (value: string) => void;
  onSendMessage: () => void;
  onNewChat: () => void;
  onSelectSession: (sessionId: string) => void;
  onToggleHistory: () => void;
  onCopyMessage: (messageId: string, content: string) => void;
}

const CopyButton: React.FC<{ 
  content: string; 
  isCopied: boolean;
  onCopy: () => void; 
}> = ({ content, isCopied, onCopy }) => {
  return (
    <button 
      onClick={onCopy} 
      className="flex items-center space-x-1 px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded-full text-xs text-slate-500 transition-all cursor-pointer"
    >
      {isCopied ? <Check size={12} className="text-green-600" /> : <Copy size={12} />}
      <span>{isCopied ? '已复制' : '复制'}</span>
    </button>
  );
};

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
    employee,
    sessions,
    currentSessionId,
    messages,
    inputValue,
    isHistoryVisible,
    copiedMessageId,
    onBack,
    onInputChange,
    onSendMessage,
    onNewChat,
    onSelectSession,
    onToggleHistory,
    onCopyMessage,
  }) => {
    // ✅ 添加安全防护 - 确保数据有效
    const safeSessions = Array.isArray(sessions) ? sessions : [];
    const safeMessages = Array.isArray(messages) ? messages : [];
    const safeEmployee = employee || {
      id: 'unknown',
      name: '未知员工',
      description: '',
      avatar: 'https://ui-avatars.com/api/?name=Employee',
      category: [],
      tags: [],
      price: 0,
      trialCount: 0,
      hireCount: 0,
      isHired: true,
      isRecruited: true,
    };
  // 1. 添加滚动锚点引用
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // 2. 添加自动滚动效果
  useEffect(() => {
    // 当消息变化或当前会话变化时，滚动到底部
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentSessionId]); // 依赖项：消息和当前会话ID

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
  };

  const renderIntro = () => (
    <div className="flex flex-col items-center justify-center px-4 py-10 pb-4">
      <div className="w-20 h-20 rounded-full overflow-hidden border-2 border-white shadow-lg mb-4">
          <img
            src={employee.avatar || `https://ui-avatars.com/api/?name=${employee.name}&background=random`}
            alt={employee.name}
            className="w-full h-full object-cover"
          />
      </div>
      
      <div className="flex items-center space-x-2 mb-6">
        <h1 className="text-xl font-bold text-slate-900">{employee.name}</h1>
        <span className="bg-blue-50 text-blue-600 text-[10px] px-1.5 py-0.5 rounded border border-blue-100 font-mono">
            gemini-2.5-pro-preview
        </span>
      </div>

      <div className="bg-slate-50 text-slate-600 px-5 py-3 rounded-lg max-w-2xl text-center text-sm leading-relaxed border border-slate-100 mb-8">
        {employee.description}
      </div>
    </div>
  );

  return (
    <div className="flex h-full bg-white overflow-hidden font-sans">
      {/* Main Container */}
      <div className="flex flex-1 h-full">
        
        {/* History Sidebar Column */}
        <div 
          className={`flex flex-col h-full flex-shrink-0 border-r border-slate-100 bg-white transition-all duration-300 ease-in-out ${
            isHistoryVisible ? 'w-72 opacity-100 translate-x-0' : 'w-0 opacity-0 -translate-x-4 overflow-hidden'
          }`}
        >
          {/* Top Bar: Back Button */}
          <div className="h-14 flex items-center px-4 border-b border-slate-50">
             <button 
                onClick={onBack}
                className="flex items-center space-x-1 text-slate-500 hover:text-slate-800 transition-colors"
              >
                <ChevronLeft size={18} />
                <span className="text-sm font-medium">返回广场</span>
             </button>
          </div>

          {/* History Header with Collapse */}
          <div className="px-4 py-4 flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <MessageSquareText size={16} className="text-slate-400" />
              <h2 className="font-bold text-slate-700 text-sm">历史</h2>
            </div>
            <button 
              onClick={onToggleHistory}
              className="text-slate-400 hover:text-slate-600 p-1 rounded hover:bg-slate-100 transition-colors"
              title="收起历史"
            >
              <PanelLeftClose size={16} />
            </button>
          </div>

          {/* History List */}
          <div className="flex-1 overflow-y-auto px-3 pb-4">
            <div className="px-1 py-1 text-xs text-slate-400 font-medium mb-1">今天</div>
            <div className="space-y-1">
              {safeSessions.map((session) => (
                <button
                  key={session.id}
                  onClick={() => onSelectSession(session.id)}
                  className={`w-full text-left px-3 py-2 text-sm rounded-md transition-colors truncate ${
                    currentSessionId === session.id
                      ? 'bg-slate-100 text-slate-900 font-medium'
                      : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  {session.title}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Chat Area Column */}
        <div className="flex-1 flex flex-col h-full relative bg-white">
          
          {/* Chat Area Top Bar */}
          <div className="h-14 border-b border-slate-50 flex items-center justify-between px-6 bg-white z-10">
            {/* Left: Expand Toggle (if sidebar closed) */}
            <div className="flex items-center">
               {!isHistoryVisible && (
                 <button 
                   onClick={onToggleHistory}
                   className="mr-3 text-slate-400 hover:text-slate-600 p-1.5 rounded-md hover:bg-slate-50 transition-colors"
                   title="展开历史"
                 >
                   <PanelLeftOpen size={18} />
                 </button>
               )}
            </div>

            {/* Right: New Chat Button */}
            <button 
              onClick={onNewChat}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-medium text-slate-600 hover:border-slate-300 hover:text-slate-900 transition-colors shadow-sm"
            >
              <MessageSquarePlus size={14} />
              <span>新建会话</span>
            </button>
          </div>

          {/* Scrollable Content Area */}
          <div className="flex-1 overflow-y-auto relative bg-white">
            <div className="max-w-3xl mx-auto w-full">
              {/* Intro Section - Always part of the scroll view */}
              {renderIntro()}

              {/* Message List */}
              <div className="px-4 pb-4 space-y-6">
                {safeMessages.map((msg) => (
                  <div 
                    key={msg.id} 
                    className={`flex group ${msg.role === 'user' ? 'justify-end' : 'justify-start'} items-start space-x-3`}
                  >
                    {/* Model Avatar (Left) */}
                    {msg.role === 'model' && (
                      <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0 mt-1 border border-slate-100">
                        <img
                          src={employee.avatar || `https://ui-avatars.com/api/?name=${employee.name}`}
                          alt={employee.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    )}

                    <div className={`flex flex-col max-w-[80%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                      {/* Name Label */}
                      <span className="text-xs text-slate-400 mb-1 px-1">
                        {msg.role === 'user' ? '我' : employee.name}
                      </span>
                      
                    {/* Message Bubble */}
                    <div 
                    className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm relative group-hover:shadow-md transition-shadow max-w-full ${
                        msg.role === 'user' 
                        ? 'bg-blue-600 text-white rounded-tr-none' 
                        : 'bg-slate-50 border border-slate-100 text-slate-800 rounded-tl-none'
                    }`}
                    style={{ wordBreak: 'break-word' }}
                    >
                    <div 
                        className="whitespace-pre-wrap overflow-hidden"
                        style={{ 
                        wordBreak: 'break-word',
                        overflowWrap: 'break-word',
                        maxWidth: '100%'
                        }}
                    >
                        {msg.content}
                    </div>
                    </div>

                      {/* Actions (Copy) - Visible on Hover */}
                      <div className={`mt-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200 px-1`}>
                         <CopyButton 
                           content={msg.content} 
                           isCopied={copiedMessageId === msg.id}
                           onCopy={() => onCopyMessage(msg.id, msg.content)}
                         />
                      </div>
                    </div>

                    {/* User Avatar (Right) */}
                    {msg.role === 'user' && (
                      <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0 mt-1 text-slate-500">
                        <User size={16} />
                      </div>
                    )}
                  </div>
                ))}
                {/* 3. 确保滚动锚点存在并正确引用 */}
                <div ref={messagesEndRef} className="h-4" />
              </div>
            </div>
          </div>

          {/* Input Area */}
          <div className="p-6 pt-2 shrink-0 bg-white">
             <div className="max-w-4xl mx-auto w-full relative">
                <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 shadow-sm focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-400 transition-all">
                    <textarea 
                        value={inputValue}
                        onChange={(e) => onInputChange(e.target.value)}
                        onKeyDown={handleKeyDown}
                        className="w-full bg-transparent border-none resize-none focus:outline-none text-slate-700 h-12 text-sm"
                        placeholder="输入文字..."
                    ></textarea>
                    
                    <div className="flex justify-between items-center mt-3">
                        <div className="flex items-center space-x-2">
                             <button className="flex items-center space-x-1.5 text-slate-500 hover:text-blue-600 bg-white border border-slate-200 px-3 py-1.5 rounded-full text-xs transition-colors shadow-sm">
                                <Globe size={14} />
                                <span>联网搜索</span>
                            </button>
                        </div>
                        <div className="flex items-center space-x-3">
                             <button className="text-slate-400 hover:text-slate-600 transition-colors p-1.5 hover:bg-slate-200 rounded-lg">
                                <ImageIcon size={20} />
                            </button>
                             <button 
                               onClick={onSendMessage}
                               disabled={!inputValue.trim()}
                               className={`p-2 rounded-lg transition-all shadow-sm ${
                                 inputValue.trim() 
                                  ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-blue-200' 
                                  : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                               }`}
                             >
                                <Send size={16} />
                            </button>
                        </div>
                    </div>
                </div>
                <div className="text-center mt-3 text-xs text-slate-300">
                    AI生成的内容可能不准确，请注意甄别
                </div>
             </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default ChatInterface;