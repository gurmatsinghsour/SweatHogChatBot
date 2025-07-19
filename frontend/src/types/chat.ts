import { MedicalData } from './medical';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type: 'text' | 'error' | 'typing';
  isUser?: boolean;
  isTyping?: boolean;
}

export interface ChatState {
  messages: Message[];
  isConnected: boolean;
  isTyping: boolean;
  sessionId: string | null;
  medicalData: MedicalData | null;
}

export interface RasaResponse {
  recipient_id: string;
  text: string;
}

export interface RasaAPIResponse {
  messages: RasaResponse[];
  sessionId?: string;
  medicalData?: MedicalData;
}

export interface Button {
  title: string;
  payload: string;
}

export interface UserMessage {
  sender: string;
  message: string;
}
