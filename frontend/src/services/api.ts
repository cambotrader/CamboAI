import axios from 'axios';

// Use same-origin by default so nginx can proxy /api -> backend.
// In development, set REACT_APP_API_URL to http://localhost:8000.
const API_BASE_URL = process.env.REACT_APP_API_URL ?? '';

export interface PortfolioPosition {
  id: number;
  symbol: string;
  quantity: number;
  entry_price: number;
  current_price: number;
  pnl: number;
  pnl_percentage: number;
  market_value: number;
  entry_date: string;
}

export interface PerformanceData {
  date: string;
  value: number;
  daily_return: number;
  cumulative_return: number;
}

export interface PortfolioSummary {
  total_value: number;
  total_pnl: number;
  total_return_percentage: number;
  positions_count: number;
  current_day_value: number;
  current_day_return: number;
}

export interface WatchlistItem {
  symbol: string;
  current_price: number;
  change: number;
  change_percentage: number;
  volume: number;
}

class ApiService {
  private axiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL || undefined,
      timeout: 10000,
    });

    // Add request interceptor for logging and auth
    this.axiosInstance.interceptors.request.use(
      (config) => {
        console.log(`Making API request to: ${config.url}`);
        
        // Add auth token if available
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        return config;
      },
      (error) => {
        console.error('Request error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Generic helpers used by some components (e.g., RiskManagement)
  async get<T = any>(url: string, config?: any): Promise<{ data: T }> {
    const response = await this.axiosInstance.get<T>(url, config);
    return { data: response.data } as { data: T };
  }

  async post<T = any>(url: string, body?: any, config?: any): Promise<{ data: T }> {
    const response = await this.axiosInstance.post<T>(url, body, config);
    return { data: response.data } as { data: T };
  }

  // Portfolio APIs
  async getPortfolioPositions(): Promise<PortfolioPosition[]> {
    const response = await this.axiosInstance.get('/api/portfolio/positions');
    return response.data;
  }

  async getPortfolioPerformance(days: number = 30): Promise<PerformanceData[]> {
    const response = await this.axiosInstance.get(`/api/portfolio/performance?days=${days}`);
    return response.data;
  }

  async getPortfolioSummary(): Promise<PortfolioSummary> {
    const response = await this.axiosInstance.get('/api/portfolio/summary');
    return response.data;
  }

  async getWatchlist(): Promise<WatchlistItem[]> {
    const response = await this.axiosInstance.get('/api/portfolio/watchlist');
    return response.data;
  }

  // Market Data APIs
  async getStockData(symbol: string, interval: string = '1d', period: string = '1mo') {
    const response = await this.axiosInstance.get(
      `/api/market-data/stock/${symbol}?interval=${interval}&period=${period}`
    );
    return response.data;
  }

  async getTechnicalAnalysis(data: { close: number[] }) {
    const response = await this.axiosInstance.post('/api/analysis/technical', data);
    return response.data;
  }

  // Pattern Scanner (real)
  async scanPatterns(payload: { symbol: string; timeframe?: string; indicators?: any }) {
    const response = await this.axiosInstance.post('/api/patterns/scan', payload);
    return response.data as { symbol: string; timeframe: string; detections: any[]; context: any };
  }

  async getPatternCatalog() {
    const response = await this.axiosInstance.get('/api/patterns/catalog');
    return response.data as { items: Array<{ name: string; type: string; why: string; how_to_detect: string; trade_notes: string; refs: string[] }> };
  }

  // News & Sentiment (real-lite)
  async getHeadlines(symbol?: string, sources?: string[], limit: number = 25) {
    const response = await this.axiosInstance.get('/api/news/headlines', { params: { symbol, sources: sources?.join(','), limit } });
    return response.data as { items: Array<{ source: string; title: string; url: string; t: string; tone: string; score: number }> };
  }

  async getSentiment(symbol?: string, sources?: string[], limit: number = 50) {
    const response = await this.axiosInstance.get('/api/sentiment/summary', { params: { symbol, sources: sources?.join(','), limit } });
    return response.data as { symbol?: string; score: number; label: string; history: number[] };
  }

  // Journal APIs
  async getJournal(params?: { query?: string; tag?: string; date_from?: string; date_to?: string; }) {
    const response = await this.axiosInstance.get('/api/journal', { params });
    return response.data as Array<{ id: number; title: string; body: string; tags: string[]; date: string }>;
  }

  async createJournal(note: { title?: string; body?: string; tags?: string[] }) {
    const response = await this.axiosInstance.post('/api/journal', note);
    return response.data as { id: number; title: string; body: string; tags: string[]; date: string };
  }

  async updateJournal(id: number, patch: { title?: string; body?: string; tags?: string[] }) {
    const response = await this.axiosInstance.put(`/api/journal/${id}`, patch);
    return response.data as { id: number; title: string; body: string; tags: string[]; date: string };
  }

  async deleteJournal(id: number) {
    const response = await this.axiosInstance.delete(`/api/journal/${id}`);
    return response.data as { ok: boolean };
  }

  // Trading APIs
  async getPositions() {
    const response = await this.axiosInstance.get('/api/trading/positions');
    return response.data;
  }

  async placeOrder(order: any) {
    const response = await this.axiosInstance.post('/api/trading/order', order);
    return response.data;
  }

  // Health check
  async healthCheck() {
    const response = await this.axiosInstance.get('/health');
    return response.data;
  }
}

// WebSocket service for real-time updates
class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private stateListeners = new Set<(state: number) => void>();
  private lastState: number = WebSocket.CLOSED;

  private notifyState(state: number) {
    this.lastState = state;
    this.stateListeners.forEach((cb) => {
      try { cb(state); } catch {}
    });
  }

  onStateChange(cb: (state: number) => void) {
    this.stateListeners.add(cb);
    // emit current state immediately
    cb(this.lastState);
    return () => this.stateListeners.delete(cb);
  }

  connect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    // Derive WS base: if explicit API base is set, use it; otherwise same-origin.
    let wsUrlBase: string;
    if (API_BASE_URL && API_BASE_URL.startsWith('http')) {
      wsUrlBase = API_BASE_URL.replace('http', 'ws');
    } else {
      const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      wsUrlBase = `${proto}//${window.location.host}`;
    }
    
    try {
      this.ws = new WebSocket(`${wsUrlBase}/ws/prices`);
      this.notifyState(WebSocket.CONNECTING);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.notifyState(WebSocket.OPEN);
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.notifyState(WebSocket.CLOSED);
        this.attemptReconnect(onMessage, onError);
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.notifyState(WebSocket.CLOSING);
        if (onError) {
          onError(error);
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.notifyState(WebSocket.CLOSED);
      if (onError) {
        onError(error as Event);
      }
    }
  }

  private attemptReconnect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect(onMessage, onError);
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  subscribe(symbols: string[]) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        symbols: symbols
      }));
    }
  }

  unsubscribe(symbols: string[]) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'unsubscribe',
        symbols: symbols
      }));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const apiService = new ApiService();
export const wsService = new WebSocketService();
