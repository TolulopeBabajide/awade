/**
 * WebSocket Service for Real-time AI Generation Progress
 * 
 * This service provides real-time communication between the frontend and backend
 * for AI generation processes, allowing users to see live progress updates.
 */

export interface ProgressUpdate {
  step: string;
  status: 'started' | 'in-progress' | 'completed' | 'error';
  message: string;
  progress: number; // 0-100
  estimatedTimeRemaining?: number; // in seconds
  data?: any; // Additional data for the step
}

export interface GenerationSession {
  sessionId: string;
  type: 'lesson-plan' | 'lesson-resource';
  topic?: string;
  subject?: string;
  gradeLevel?: string;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private listeners: Map<string, ((data: any) => void)[]> = new Map();
  private isConnecting = false;

  constructor() {
    this.connect();
  }

  private connect() {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;
    const wsUrl = process.env.NODE_ENV === 'production' 
      ? 'wss://your-production-domain.com/ws' 
      : 'ws://localhost:8000/ws';

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnecting = false;
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
      };

    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      this.isConnecting = false;
      this.attemptReconnect();
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${this.reconnectDelay}ms`);

    setTimeout(() => {
      this.connect();
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000); // Max 30 seconds
    }, this.reconnectDelay);
  }

  private handleMessage(data: any) {
    const { type, payload } = data;

    switch (type) {
      case 'progress_update':
        this.emit('progress_update', payload);
        break;
      case 'generation_complete':
        this.emit('generation_complete', payload);
        break;
      case 'generation_error':
        this.emit('generation_error', payload);
        break;
      case 'session_started':
        this.emit('session_started', payload);
        break;
      default:
        console.log('Unknown message type:', type);
    }
  }

  // Subscribe to events
  on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.listeners.get(event);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }

  // Emit events to listeners
  private emit(event: string, data: any) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  // Start a generation session
  startGeneration(session: GenerationSession) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'start_generation',
        payload: session
      }));
    } else {
      console.warn('WebSocket not connected, cannot start generation');
    }
  }

  // Cancel a generation session
  cancelGeneration(sessionId: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'cancel_generation',
        payload: { sessionId }
      }));
    }
  }

  // Get connection status
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  // Disconnect
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners.clear();
  }
}

// Create singleton instance
export const websocketService = new WebSocketService();

// Export for use in components
export default websocketService;
