import axios, { AxiosResponse } from 'axios';
import { API_CONFIG, buildUrl, getHeaders } from '../config/api';

// Types matching your backend models
export interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: number;
  high?: number;
  low?: number;
  timestamp?: string;
}

export interface Trade {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  amount: number;
  price: number;
  timestamp: string;
  status?: string;
}

export interface Portfolio {
  totalValue: number;
  totalPnL: number;
  totalPnLPercent: number;
  positions: Position[];
}

export interface Position {
  symbol: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  value: number;
  pnl: number;
  pnlPercent: number;
}

export interface AnalysisData {
  symbol: string;
  technicalIndicators: {
    rsi: number;
    macd: number;
    sma: number;
    ema: number;
  };
  sentiment: {
    score: number;
    label: string;
  };
  recommendation: string;
}

class ApiService {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  private async request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    endpoint: string,
    data?: any
  ): Promise<T> {
    try {
      const response: AxiosResponse<T> = await axios({
        method,
        url: buildUrl(endpoint),
        data,
        headers: getHeaders(this.token || undefined),
        timeout: 10000,
      });
      return response.data;
    } catch (error) {
      console.error(`API Error (${method} ${endpoint}):`, error);
      throw error;
    }
  }

  // Market Data APIs
  async getMarketOverview(): Promise<MarketData[]> {
    return this.request<MarketData[]>('GET', API_CONFIG.ENDPOINTS.MARKET_OVERVIEW);
  }

  async getMarketPrices(symbols: string[]): Promise<MarketData[]> {
    return this.request<MarketData[]>('GET', `${API_CONFIG.ENDPOINTS.MARKET_PRICES}?symbols=${symbols.join(',')}`);
  }

  async getMarketHistory(symbol: string, period: string = '1d'): Promise<any> {
    return this.request('GET', `${API_CONFIG.ENDPOINTS.MARKET_HISTORY}/${symbol}?period=${period}`);
  }

  // Trading APIs
  async getTrades(): Promise<Trade[]> {
    return this.request<Trade[]>('GET', API_CONFIG.ENDPOINTS.TRADES);
  }

  async placeOrder(order: {
    symbol: string;
    type: 'buy' | 'sell';
    amount: number;
    price: number;
  }): Promise<Trade> {
    return this.request<Trade>('POST', API_CONFIG.ENDPOINTS.PLACE_ORDER, order);
  }

  async getOrderHistory(): Promise<Trade[]> {
    return this.request<Trade[]>('GET', API_CONFIG.ENDPOINTS.ORDER_HISTORY);
  }

  // Portfolio APIs
  async getPortfolio(): Promise<Portfolio> {
    return this.request<Portfolio>('GET', API_CONFIG.ENDPOINTS.PORTFOLIO);
  }

  async getPortfolioPerformance(): Promise<any> {
    return this.request('GET', API_CONFIG.ENDPOINTS.PORTFOLIO_PERFORMANCE);
  }

  async getPortfolioPositions(): Promise<Position[]> {
    return this.request<Position[]>('GET', API_CONFIG.ENDPOINTS.PORTFOLIO_POSITIONS);
  }

  // Analysis APIs
  async getAnalysis(symbol: string): Promise<AnalysisData> {
    return this.request<AnalysisData>('GET', `${API_CONFIG.ENDPOINTS.ANALYSIS}/${symbol}`);
  }

  async getTechnicalAnalysis(symbol: string): Promise<any> {
    return this.request('GET', `${API_CONFIG.ENDPOINTS.TECHNICAL_ANALYSIS}/${symbol}`);
  }

  async getSentimentAnalysis(symbol: string): Promise<any> {
    return this.request('GET', `${API_CONFIG.ENDPOINTS.SENTIMENT_ANALYSIS}/${symbol}`);
  }

  // Risk Management APIs
  async getRiskMetrics(): Promise<any> {
    return this.request('GET', API_CONFIG.ENDPOINTS.RISK_METRICS);
  }

  async getRiskAssessment(): Promise<any> {
    return this.request('GET', API_CONFIG.ENDPOINTS.RISK_ASSESSMENT);
  }

  // Authentication APIs
  async login(username: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    return this.request('POST', API_CONFIG.ENDPOINTS.LOGIN, formData);
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
  }): Promise<any> {
    return this.request('POST', API_CONFIG.ENDPOINTS.REGISTER, userData);
  }

  async getMe(): Promise<any> {
    return this.request('GET', API_CONFIG.ENDPOINTS.ME);
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request('GET', API_CONFIG.ENDPOINTS.HEALTH);
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;