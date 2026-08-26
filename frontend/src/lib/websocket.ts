export class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private listeners: Map<string, Function[]> = new Map();
  private token: string | null = null;
  private reconnectTimeout: any;

  connect(token: string) {
    this.token = token;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    // Assuming backend is at 8000 for dev, we proxy or connect directly
    const wsUrl = import.meta.env.DEV 
      ? `ws://localhost:8000/ws/live?token=${token}`
      : `${protocol}//${host}/ws/live?token=${token}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const handlers = this.listeners.get(data.type) || [];
        handlers.forEach(handler => handler(data.payload));
      } catch (err) {
        console.error('Error parsing WS message', err);
      }
    };

    this.ws.onclose = () => {
      this.handleReconnect();
    };

    this.ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const timeout = Math.pow(2, this.reconnectAttempts) * 1000;
      console.log(`Reconnecting in ${timeout}ms...`);
      this.reconnectTimeout = setTimeout(() => {
        if (this.token) this.connect(this.token);
      }, timeout);
    }
  }

  disconnect() {
    if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.token = null;
  }

  onMessage(type: string, callback: Function) {
    const handlers = this.listeners.get(type) || [];
    handlers.push(callback);
    this.listeners.set(type, handlers);
    return () => {
      const h = this.listeners.get(type) || [];
      this.listeners.set(type, h.filter(cb => cb !== callback));
    };
  }
}

export const wsManager = new WebSocketManager();
