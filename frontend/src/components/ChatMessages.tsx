import React, { useEffect, useRef } from 'react';
import { Message as MessageType } from '../types/chat';
import Message from './Message';
import './ChatMessages.css';

interface ChatMessagesProps {
  messages: MessageType[];
  isTyping: boolean;
  onSuggestionClick: (suggestion: string) => void;
}

const ChatMessages: React.FC<ChatMessagesProps> = ({ messages, isTyping, onSuggestionClick }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="chat-messages empty">
        <div className="welcome-message">
          <div className="welcome-icon">
            <svg 
              width="48" 
              height="48" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2"
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <h2 className="welcome-title">Welcome to your Health Assessment</h2>
          <p className="welcome-description">
            I'm here to help you evaluate your diabetes readmission risk. 
            Let's start by collecting some basic information about your health.
          </p>
          <div className="welcome-suggestions">
            <p className="suggestions-title">You can try saying:</p>
            <div className="suggestion-buttons">
              <button className="suggestion-button">
                "I want to assess my diabetes risk"
              </button>
              <button className="suggestion-button">
                "Let's start the health assessment"
              </button>
              <button className="suggestion-button">
                "Help me understand my readmission risk"
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-messages">
      <div className="messages-container">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatMessages;
