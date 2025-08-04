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

  // Open PDF report in new window/tab
  openReportInNewWindow(reportUrl: string): void {
    window.open(reportUrl, '_blank');
  }

  extractDownloadLink(message: string): string | null {
    // Check for predict_with_report API endpoint (which generates and serves PDF)
    const reportApiPattern = /http:\/\/localhost:\d+\/predict_with_report/;
    const apiMatch = message.match(reportApiPattern);
    if (apiMatch) {
      return apiMatch[0];
    }
    
    // Also check for direct download URLs - more specific pattern to avoid capturing extra characters
    const downloadPattern = /http:\/\/localhost:\d+\/download_report\/[a-zA-Z0-9_.-]+\.pdf/;
    const downloadMatch = message.match(downloadPattern);
    if (downloadMatch) {
      return downloadMatch[0];
    }
    
    return null;
  }

  // Helper method to check if a message contains a download link
  hasDownloadLink(message: string): boolean {
    return this.extractDownloadLink(message) !== null;
  }

  // Helper method to extract filename from download URL
  extractFilenameFromUrl(url: string): string {
    const parts = url.split('/');
    return parts[parts.length - 1] || 'medical_report.pdf';
  }
}

export const rasaAPI = RasaAPI.getInstance();
