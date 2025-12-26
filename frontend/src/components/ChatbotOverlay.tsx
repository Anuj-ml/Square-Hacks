import React, { useState, useEffect, useRef } from 'react';
import { Icons } from './ui/Icons';
import { queryRagChatbot, getRagStatus, type RagQueryRequest, type RagResponse, type RagStatus } from '../lib/api';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  sources?: Array<{
    id: string;
    content: string;
    metadata: Record<string, any>;
  }>;
  confidence?: number;
  mode?: 'rag' | 'offline' | 'no_documents' | 'error';
}

interface ChatbotOverlayProps {
  theme?: 'dark' | 'light';
  dashboardContext?: {
    aqi?: number;
    bed_capacity?: number;
    active_alerts?: number;
  };
}

const ChatbotOverlay: React.FC<ChatbotOverlayProps> = ({ theme = 'dark', dashboardContext }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      type: 'bot',
      content: '👋 Hello! I\'m your Arogya-Swarm medical assistant. I can help you with:\n\n• Hospital surge protocols\n• Resource management guidelines\n• Emergency response procedures\n• Medical best practices\n\nWhat would you like to know?',
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [ragStatus, setRagStatus] = useState<RagStatus | null>(null);
  const [showSources, setShowSources] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Fetch RAG status on mount
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await getRagStatus();
        setRagStatus(status);
      } catch (error) {
        console.error('Failed to fetch RAG status:', error);
      }
    };
    fetchStatus();
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Prepare request with dashboard context
      const request: RagQueryRequest = {
        question: inputValue,
        context: dashboardContext,
      };

      // Query RAG system
      const response: RagResponse = await queryRagChatbot(request);

      // Create bot message
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
        confidence: response.confidence,
        mode: response.mode,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      // Error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: `❌ I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
        timestamp: new Date(),
        mode: 'error',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const clearChat = () => {
    setMessages([
      {
        id: '0',
        type: 'bot',
        content: '👋 Chat cleared. How can I help you?',
        timestamp: new Date(),
      }
    ]);
  };

  // Suggested questions
  const suggestedQuestions = [
    "What should we do during high AQI events?",
    "How to manage ICU capacity during surge?",
    "What are the staff fatigue protocols?",
    "How to handle dengue outbreak?",
  ];

  const askSuggestedQuestion = (question: string) => {
    setInputValue(question);
    inputRef.current?.focus();
  };

  const isDark = theme === 'dark';

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={toggleChat}
          className={`fixed bottom-6 right-6 w-16 h-16 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 z-50 ${
            isDark 
              ? 'bg-gradient-to-br from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500' 
              : 'bg-gradient-to-br from-purple-500 to-blue-500 hover:from-purple-400 hover:to-blue-400'
          }`}
          title="Open Medical Assistant"
        >
          <Icons.MessageSquare className="w-7 h-7 text-white" />
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white animate-pulse" />
        </button>
      )}

      {/* Chat Overlay */}
      {isOpen && (
        <div
          className={`fixed bottom-6 right-6 w-[420px] h-[650px] rounded-2xl shadow-2xl flex flex-col z-50 overflow-hidden ${
            isDark 
              ? 'bg-gray-900 border border-gray-700' 
              : 'bg-white border border-gray-200'
          }`}
        >
          {/* Header */}
          <div className={`flex items-center justify-between px-5 py-4 border-b ${
            isDark ? 'bg-gray-800 border-gray-700' : 'bg-gradient-to-r from-purple-50 to-blue-50 border-gray-200'
          }`}>
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                isDark ? 'bg-gradient-to-br from-purple-600 to-blue-600' : 'bg-gradient-to-br from-purple-500 to-blue-500'
              }`}>
                <Icons.Stethoscope className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  Medical Assistant
                </h3>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    {ragStatus?.status === 'healthy' ? 'Online' : 'Limited Mode'}
                  </span>
                  {ragStatus && ragStatus.document_count > 0 && (
                    <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                      • {ragStatus.document_count} docs
                    </span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={clearChat}
                className={`p-2 rounded-lg transition-colors ${
                  isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                }`}
                title="Clear chat"
              >
                <Icons.FileText className={`w-4 h-4 ${isDark ? 'text-gray-400' : 'text-gray-600'}`} />
              </button>
              <button
                onClick={toggleChat}
                className={`p-2 rounded-lg transition-colors ${
                  isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                }`}
                title="Close chat"
              >
                <Icons.X className={`w-5 h-5 ${isDark ? 'text-gray-400' : 'text-gray-600'}`} />
              </button>
            </div>
          </div>

          {/* Messages Area */}
          <div className={`flex-1 overflow-y-auto px-4 py-4 space-y-4 ${
            isDark ? 'bg-gray-900' : 'bg-gray-50'
          }`}>
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                  {/* Message Bubble */}
                  <div
                    className={`rounded-2xl px-4 py-3 ${
                      message.type === 'user'
                        ? isDark
                          ? 'bg-gradient-to-br from-purple-600 to-blue-600 text-white'
                          : 'bg-gradient-to-br from-purple-500 to-blue-500 text-white'
                        : isDark
                        ? 'bg-gray-800 text-gray-100 border border-gray-700'
                        : 'bg-white text-gray-900 border border-gray-200 shadow-sm'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    
                    {/* Confidence & Mode Badge */}
                    {message.type === 'bot' && message.mode && (
                      <div className="flex items-center gap-2 mt-2 pt-2 border-t border-opacity-20 border-current">
                        {message.confidence !== undefined && (
                          <span className="text-xs opacity-75">
                            {message.confidence}% confident
                          </span>
                        )}
                        {message.mode === 'offline' && (
                          <span className="text-xs bg-yellow-500 bg-opacity-20 px-2 py-0.5 rounded">
                            Offline Mode
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2">
                      <button
                        onClick={() => setShowSources(showSources === message.id ? null : message.id)}
                        className={`text-xs flex items-center gap-1 ${
                          isDark ? 'text-gray-400 hover:text-gray-300' : 'text-gray-600 hover:text-gray-700'
                        }`}
                      >
                        <Icons.FileText className="w-3 h-3" />
                        {message.sources.length} source{message.sources.length > 1 ? 's' : ''}
                        <Icons.ChevronRight className={`w-3 h-3 transition-transform ${
                          showSources === message.id ? 'rotate-90' : ''
                        }`} />
                      </button>
                      
                      {showSources === message.id && (
                        <div className={`mt-2 space-y-2 text-xs ${
                          isDark ? 'text-gray-400' : 'text-gray-600'
                        }`}>
                          {message.sources.map((source, idx) => (
                            <div
                              key={idx}
                              className={`p-2 rounded-lg ${
                                isDark ? 'bg-gray-800 border border-gray-700' : 'bg-gray-100 border border-gray-200'
                              }`}
                            >
                              <div className="font-medium mb-1">{source.metadata.category || 'Document'}</div>
                              <div className="opacity-75">{source.content}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Timestamp */}
                  <div className={`text-xs mt-1 ${
                    isDark ? 'text-gray-500' : 'text-gray-500'
                  } ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className={`rounded-2xl px-4 py-3 ${
                  isDark ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
                }`}>
                  <div className="flex items-center gap-2">
                    <div className="flex space-x-1">
                      <div className={`w-2 h-2 rounded-full animate-bounce ${
                        isDark ? 'bg-gray-400' : 'bg-gray-600'
                      }`} style={{ animationDelay: '0ms' }} />
                      <div className={`w-2 h-2 rounded-full animate-bounce ${
                        isDark ? 'bg-gray-400' : 'bg-gray-600'
                      }`} style={{ animationDelay: '150ms' }} />
                      <div className={`w-2 h-2 rounded-full animate-bounce ${
                        isDark ? 'bg-gray-400' : 'bg-gray-600'
                      }`} style={{ animationDelay: '300ms' }} />
                    </div>
                    <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                      Thinking...
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Questions (shown when no messages except welcome) */}
          {messages.length === 1 && !isLoading && (
            <div className={`px-4 py-3 border-t ${
              isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
            }`}>
              <p className={`text-xs mb-2 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                Suggested questions:
              </p>
              <div className="flex flex-wrap gap-2">
                {suggestedQuestions.map((question, idx) => (
                  <button
                    key={idx}
                    onClick={() => askSuggestedQuestion(question)}
                    className={`text-xs px-3 py-1.5 rounded-full transition-colors ${
                      isDark 
                        ? 'bg-gray-700 hover:bg-gray-600 text-gray-300' 
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    }`}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className={`px-4 py-4 border-t ${
            isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
          }`}>
            <div className="flex items-end gap-2">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about medical protocols..."
                disabled={isLoading}
                className={`flex-1 px-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-all ${
                  isDark 
                    ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:ring-purple-500' 
                    : 'bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-purple-400'
                } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
                className={`p-3 rounded-xl transition-all ${
                  !inputValue.trim() || isLoading
                    ? isDark
                      ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                      : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : isDark
                    ? 'bg-gradient-to-br from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white shadow-lg'
                    : 'bg-gradient-to-br from-purple-500 to-blue-500 hover:from-purple-400 hover:to-blue-400 text-white shadow-lg'
                }`}
              >
                <Icons.Send className="w-5 h-5" />
              </button>
            </div>
            
            {/* Context Indicator */}
            {dashboardContext && (
              <div className={`mt-2 text-xs flex items-center gap-2 ${
                isDark ? 'text-gray-500' : 'text-gray-500'
              }`}>
                <Icons.CheckCircle2 className="w-3 h-3" />
                <span>Using dashboard context for better answers</span>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default ChatbotOverlay;
