import React, { useState, useRef, useEffect } from 'react';
import ChatHeader from './components/ChatHeader';
import ChatMessages from './components/ChatMessages';
import ChatInput from './components/ChatInput';
import { rasaAPI } from './utils/rasaAPI';
import { Message, ChatState } from './types/chat';
import { formatMessage, formatUserMessage } from './utils/messageUtils';
import './styles/globals.css';
import './App.css';

interface AppProps {}

const App: React.FC<AppProps> = () => {
  const [chatState, setChatState] = useState<ChatState>({
    messages: [],
    isTyping: false,
    isConnected: false,
    sessionId: null,
    medicalData: null
  });

  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Initialize chat on component mount
  useEffect(() => {
    initializeChat();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatState.messages]);

  const initializeChat = async () => {
    try {
      const response = await rasaAPI.sendMessage('hello');
      
      setChatState((prev: ChatState) => ({
        ...prev,
        isConnected: true,
        sessionId: response.sessionId || `session_${Date.now()}`,
        messages: response.messages?.map(msg => formatMessage(msg)) || []
      }));
    } catch (error) {
      console.error('Failed to initialize chat:', error);
      setChatState((prev: ChatState) => ({
        ...prev,
        isConnected: false,
        messages: [{
          id: Date.now().toString(),
          text: 'Sorry, I\'m having trouble connecting. Please check if the Rasa server is running.',
          sender: 'bot',
          timestamp: new Date(),
          type: 'error'
        }]
      }));
    }
  };

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = formatUserMessage(text.trim());

    // Add user message immediately
    setChatState((prev: ChatState) => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isTyping: true
    }));

    try {
      const response = await rasaAPI.sendMessage(text, chatState.sessionId || 'user');
      
      const botMessages = response.messages?.map(msg => formatMessage(msg)) || [];
      
      setChatState((prev: ChatState) => ({
        ...prev,
        messages: [...prev.messages, ...botMessages],
        isTyping: false,
        medicalData: response.medicalData || prev.medicalData
      }));
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
        type: 'error'
      };
      
      setChatState((prev: ChatState) => ({
        ...prev,
        messages: [...prev.messages, errorMessage],
        isTyping: false
      }));
    }
  };

  const clearChat = () => {
    setChatState({
      messages: [],
      isTyping: false,
      isConnected: false,
      sessionId: null,
      medicalData: null
    });
    
    // Reinitialize chat
    setTimeout(() => {
      initializeChat();
    }, 500);
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  const handleRetry = () => {
    if (!chatState.isConnected) {
      initializeChat();
    }
  };

  return (
    <div className="app">
      <div className="chat-container" ref={chatContainerRef}>
        <ChatHeader 
          isConnected={chatState.isConnected}
          onClear={clearChat}
          onRetry={handleRetry}
        />
        
        <ChatMessages 
          messages={chatState.messages}
          isTyping={chatState.isTyping}
          onSuggestionClick={handleSuggestionClick}
        />
        
        <ChatInput 
          onSendMessage={sendMessage}
          disabled={!chatState.isConnected}
          isTyping={chatState.isTyping}
        />
      </div>
    </div>
  );
};

export default App;
