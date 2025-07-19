import { Message, RasaResponse } from '../types/chat';

export const formatMessage = (rasaResponse: RasaResponse): Message => {
  return {
    id: generateId(),
    text: rasaResponse.text,
    sender: 'bot',
    timestamp: new Date(),
    type: 'text',
    isUser: false,
    isTyping: false,
  };
};

export const formatUserMessage = (text: string): Message => {
  return {
    id: generateId(),
    text,
    sender: 'user',
    timestamp: new Date(),
    type: 'text',
    isUser: true,
    isTyping: false,
  };
};

export const formatTypingMessage = (): Message => {
  return {
    id: generateId(),
    text: '',
    sender: 'bot',
    timestamp: new Date(),
    type: 'typing',
    isUser: false,
    isTyping: true,
  };
};

export const generateId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

export const formatTime = (date: Date): string => {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export const isValidMessage = (message: string): boolean => {
  return message.trim().length > 0 && message.trim().length <= 1000;
};

export const sanitizeMessage = (message: string): string => {
  return message.trim().replace(/\s+/g, ' ');
};
