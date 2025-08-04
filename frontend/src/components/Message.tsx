import React from 'react';
import { Message as MessageType } from '../types/chat';
import { formatTime } from '../utils/messageUtils';
import { rasaAPI } from '../utils/rasaAPI';
import './Message.css';

interface MessageProps {
  message: MessageType;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const { text, isUser, timestamp, isTyping } = message;

  // Handle download link clicks
  const handleDownloadClick = async (url: string) => {
    try {
      // Open PDF in new window/tab - this will trigger backend to generate fresh PDF
      rasaAPI.openReportInNewWindow(url);
    } catch (error) {
      console.error('Failed to open report:', error);
      alert('Failed to open the report. Please try again.');
    }
  };

  // Format message text to make download links clickable
  const formatMessageText = (text: string) => {
    const downloadUrl = rasaAPI.extractDownloadLink(text);
    
    if (downloadUrl) {
      // Split the text around the download URL
      const parts = text.split(downloadUrl);
      
      return (
        <>
          {parts[0]}
          <button 
            className="download-link-button"
            onClick={() => handleDownloadClick(downloadUrl)}
            title="Click to download your medical report"
          >
            📄 Download Report
          </button>
          {parts[1]}
        </>
      );
    }
    
    return text;
  };

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
          {isUser ? text : formatMessageText(text)}
        </div>
        <div className="message-time">
          {formatTime(timestamp)}
        </div>
      </div>
    </div>
  );
};

export default Message;
