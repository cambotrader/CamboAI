// API Configuration for CamboAI Mobile App
export const API_CONFIG = {
  // Development URLs
  DEV_BASE_URL: 'http://localhost:8000',
  
  // Production URLs (update these when you deploy)
  PROD_BASE_URL: 'https://your-backend-url.com',
  
  // Current environment
  BASE_URL: __DEV__ ? 'http://localhost:8000' : 'https://your-backend-url.com',
  
  // API Endpoints matching your FastAPI backend
  ENDPOINTS: {
    // Market Data
    MARKET_OVERVIEW: '/api/market-data/overview',
    MARKET_PRICES: '/api/market-data/prices',
    MARKET_HISTORY: '/api/market-data/history',
    
    // Trading
    TRADES: '/api/trading/trades',
    PLACE_ORDER: '/api/trading/order',
    ORDER_HISTORY: '/api/trading/orders',
    
    // Portfolio
    PORTFOLIO: '/api/portfolio',
    PORTFOLIO_PERFORMANCE: '/api/portfolio/performance',
    PORTFOLIO_POSITIONS: '/api/portfolio/positions',
    
    // Analysis
    ANALYSIS: '/api/analysis',
    TECHNICAL_ANALYSIS: '/api/analysis/technical',
    SENTIMENT_ANALYSIS: '/api/analysis/sentiment',
    
    // Risk Management
    RISK_METRICS: '/api/risk/metrics',
    RISK_ASSESSMENT: '/api/risk/assessment',
    
    // Authentication
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    ME: '/api/auth/me',
    
    // Health Check
    HEALTH: '/health',
  }
};

// Helper function to build full URL
export const buildUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// API Headers
export const getHeaders = (token?: string) => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};