import React from 'react';
import './ChatHeader.css';

interface ChatHeaderProps {
  isConnected: boolean;
  onClear: () => void;
  onRetry: () => void;
}

const ChatHeader: React.FC<ChatHeaderProps> = ({ isConnected, onClear, onRetry }) => {
  return (
    <header className="chat-header">
      <div className="header-content">
        <div className="header-left">
          <div className="header-icon">
            <svg 
              width="32" 
              height="32" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2"
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <path d="M9 12l2 2 4-4"/>
              <path d="M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9z"/>
            </svg>
          </div>
          <div className="header-info">
            <h1 className="header-title">Health Assessment Bot</h1>
            <p className="header-subtitle">
              Diabetes Readmission Risk Evaluation
            </p>
          </div>
        </div>
        <div className="header-right">
          <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            <div className="status-indicator"></div>
            <span className="status-text">
              {isConnected ? 'Connected' : 'Connecting...'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default ChatHeader;
