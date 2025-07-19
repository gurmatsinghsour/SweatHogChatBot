import React from 'react';
import { Message as MessageType } from '../types/chat';
import { formatTime } from '../utils/messageUtils';
import './Message.css';

interface MessageProps {
  message: MessageType;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const { text, isUser, timestamp, isTyping } = message;

  if (isTyping) {
    return (
      <div className="message-wrapper bot">
        <div className="message typing">
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`message-wrapper ${isUser ? 'user' : 'bot'}`}>
      <div className="message">
        <div className="message-content">
          {text}
        </div>
        <div className="message-time">
          {formatTime(timestamp)}
        </div>
      </div>
    </div>
  );
};

export default Message;
