import axios from 'axios';
import { UserMessage, RasaAPIResponse } from '../types/chat';

const RASA_URL = 'http://localhost:5005';

export class RasaAPI {
  private static instance: RasaAPI;
  private baseURL: string;

  private constructor() {
    this.baseURL = RASA_URL;
  }

  public static getInstance(): RasaAPI {
    if (!RasaAPI.instance) {
      RasaAPI.instance = new RasaAPI();
    }
    return RasaAPI.instance;
  }

  async sendMessage(message: string, sender: string = 'user'): Promise<RasaAPIResponse> {
    try {
      const userMessage: UserMessage = {
        sender,
        message
      };

      const response = await axios.post(
        `${this.baseURL}/webhooks/rest/webhook`,
        userMessage,
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 10000, // 10 seconds timeout
        }
      );

      return {
        messages: response.data,
        sessionId: sender,
        medicalData: undefined
      };
    } catch (error) {
      console.error('Error sending message to Rasa:', error);
      throw new Error('Failed to communicate with the chatbot. Please try again.');
    }
  }

  async checkHealth(): Promise<boolean> {
    try {
      await axios.get(`${this.baseURL}/`, { timeout: 5000 });
      return true;
    } catch (error) {
      console.error('Rasa health check failed:', error);
      return false;
    }
  }
}

export const rasaAPI = RasaAPI.getInstance();
