# ⚛️ Build Modern React Frontend
# Creates a complete React frontend connected to the CamboAI API

Write-Host "⚛️ Building Modern React Frontend..." -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "backend\app\main.py")) {
    Write-Host "❌ Please run this from the CamboAI root directory" -ForegroundColor Red
    exit 1
}

# Create frontend directory structure
Write-Host "`n📁 Creating React frontend structure..." -ForegroundColor Yellow

$directories = @(
    "frontend-new\src\components\common",
    "frontend-new\src\components\trading", 
    "frontend-new\src\components\dashboard",
    "frontend-new\src\pages",
    "frontend-new\src\services",
    "frontend-new\src\hooks",
    "frontend-new\src\store",
    "frontend-new\src\utils",
    "frontend-new\src\types",
    "frontend-new\public"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

# Create package.json
Write-Host "📦 Creating package.json..." -ForegroundColor Blue

$packageJson = @'
{
  "name": "camboai-frontend",
  "version": "1.0.0",
  "description": "CamboAI Trading Platform Frontend",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "react-scripts": "5.0.1",
    "@mui/material": "^5.13.0",
    "@mui/icons-material": "^5.13.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "@reduxjs/toolkit": "^1.9.0",
    "react-redux": "^8.1.0",
    "axios": "^1.4.0",
    "socket.io-client": "^4.7.0",
    "recharts": "^2.7.0",
    "react-query": "^3.39.0",
    "react-hook-form": "^7.45.0",
    "react-toastify": "^9.1.0",
    "date-fns": "^2.30.0",
    "numeral": "^2.0.6",
    "lodash": "^4.17.21",
    "typescript": "^4.9.5",
    "@types/node": "^16.18.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/lodash": "^4.14.195",
    "@types/numeral": "^2.0.2"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject",
    "type-check": "tsc --noEmit",
    "format": "prettier --write \"src/**/*.{js,jsx,ts,tsx}\"",
    "lint": "eslint \"src/**/*.{js,jsx,ts,tsx}\""
  },
  "eslintConfig": {
    "extends": ["react-app", "react-app/jest"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  },
  "proxy": "http://localhost:8000"
}
'@

$packageJson | Out-File -FilePath "frontend-new\package.json" -Encoding UTF8

# Create TypeScript config
$tsconfigJson = @'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
'@

$tsconfigJson | Out-File -FilePath "frontend-new\tsconfig.json" -Encoding UTF8

# Create main App component
Write-Host "⚛️ Creating React components..." -ForegroundColor Blue

$appTsx = @'
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ToastContainer } from 'react-toastify';

import { store } from './store/store';
import Dashboard from './pages/Dashboard';
import Trading from './pages/Trading';
import Portfolio from './pages/Portfolio';
import Login from './pages/Login';
import { AuthProvider } from './hooks/useAuth';
import { WebSocketProvider } from './hooks/useWebSocket';

import 'react-toastify/dist/ReactToastify.css';
import './App.css';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00ff88',
    },
    secondary: {
      main: '#007AFF',
    },
    background: {
      default: '#0a0a0a',
      paper: '#1a1a1a',
    },
  },
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={darkTheme}>
          <CssBaseline />
          <AuthProvider>
            <WebSocketProvider>
              <Router>
                <div className="App">
                  <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/trading" element={<Trading />} />
                    <Route path="/portfolio" element={<Portfolio />} />
                  </Routes>
                </div>
              </Router>
              <ToastContainer
                position="top-right"
                autoClose={5000}
                hideProgressBar={false}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                theme="dark"
              />
            </WebSocketProvider>
          </AuthProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </Provider>
  );
}

export default App;
'@

$appTsx | Out-File -FilePath "frontend-new\src\App.tsx" -Encoding UTF8

# Create API service
$apiService = @'
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    apiClient.post('/auth/login', credentials),
  
  register: (userData: any) =>
    apiClient.post('/auth/register', userData),
  
  logout: () =>
    apiClient.post('/auth/logout'),
  
  getProfile: () =>
    apiClient.get('/auth/profile'),
};

// Trading API
export const tradingAPI = {
  // Orders
  placeOrder: (orderData: any) =>
    apiClient.post('/trading/orders', orderData),
  
  getOrders: (params?: any) =>
    apiClient.get('/trading/orders', { params }),
  
  cancelOrder: (orderId: string) =>
    apiClient.delete(`/trading/orders/${orderId}`),
  
  // Positions
  getPositions: () =>
    apiClient.get('/trading/positions'),
  
  // Account
  getAccount: () =>
    apiClient.get('/trading/account/summary'),
  
  // Market Data
  getMarketData: (symbol: string) =>
    apiClient.get(`/trading/market-data/${symbol}`),
  
  // Portfolio
  getPortfolioSummary: () =>
    apiClient.get('/trading/portfolio/summary'),
  
  // AI & Analytics
  getAISignals: (params?: any) =>
    apiClient.get('/trading/ai/signals', { params }),
  
  getDeFiOpportunities: () =>
    apiClient.get('/trading/defi/opportunities'),
  
  getArbitrageOpportunities: () =>
    apiClient.get('/trading/arbitrage/opportunities'),
};

// System API
export const systemAPI = {
  getSystemStatus: () =>
    apiClient.get('/system/status'),
  
  getHealth: () =>
    axios.get(`${API_BASE_URL}/health`),
};

export default apiClient;
'@

$apiService | Out-File -FilePath "frontend-new\src\services\api.ts" -Encoding UTF8

# Create WebSocket hook
$webSocketHook = @'
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { toast } from 'react-toastify';

interface WebSocketContextType {
  socket: Socket | null;
  connected: boolean;
  subscribe: (channel: string, callback: (data: any) => void) => void;
  unsubscribe: (channel: string) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

interface MarketTick {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp: string;
}

interface OrderUpdate {
  order_id: string;
  symbol: string;
  status: string;
  filled_quantity: number;
  remaining_quantity: number;
  average_fill_price: number;
}

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [subscriptions, setSubscriptions] = useState<Map<string, (data: any) => void>>(new Map());

  useEffect(() => {
    const socketUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    const newSocket = io(socketUrl, {
      transports: ['websocket'],
      autoConnect: true,
    });

    newSocket.on('connect', () => {
      console.log('✅ WebSocket connected');
      setConnected(true);
      toast.success('Connected to live data feed');
    });

    newSocket.on('disconnect', () => {
      console.log('❌ WebSocket disconnected');
      setConnected(false);
      toast.warn('Disconnected from live data feed');
    });

    newSocket.on('market_tick', (data: MarketTick) => {
      const callback = subscriptions.get('market_tick');
      if (callback) callback(data);
    });

    newSocket.on('order_update', (data: OrderUpdate) => {
      const callback = subscriptions.get('order_update');
      if (callback) callback(data);
      
      // Show toast notification for order updates
      toast.info(`Order ${data.status}: ${data.symbol}`);
    });

    newSocket.on('portfolio_update', (data: any) => {
      const callback = subscriptions.get('portfolio_update');
      if (callback) callback(data);
    });

    newSocket.on('risk_alert', (data: any) => {
      const callback = subscriptions.get('risk_alert');
      if (callback) callback(data);
      
      // Show warning toast for risk alerts
      toast.warn(`Risk Alert: ${data.message}`);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const subscribe = useCallback((channel: string, callback: (data: any) => void) => {
    setSubscriptions(prev => new Map(prev.set(channel, callback)));
  }, []);

  const unsubscribe = useCallback((channel: string) => {
    setSubscriptions(prev => {
      const newMap = new Map(prev);
      newMap.delete(channel);
      return newMap;
    });
  }, []);

  return (
    <WebSocketContext.Provider value={{ socket, connected, subscribe, unsubscribe }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

// Custom hooks for specific data types
export const useMarketData = (symbols: string[]) => {
  const { subscribe, unsubscribe } = useWebSocket();
  const [marketData, setMarketData] = useState<Record<string, MarketTick>>({});

  useEffect(() => {
    const handleMarketTick = (tick: MarketTick) => {
      if (symbols.includes(tick.symbol)) {
        setMarketData(prev => ({
          ...prev,
          [tick.symbol]: tick
        }));
      }
    };

    subscribe('market_tick', handleMarketTick);
    
    return () => {
      unsubscribe('market_tick');
    };
  }, [symbols, subscribe, unsubscribe]);

  return marketData;
};

export const useOrderUpdates = () => {
  const { subscribe, unsubscribe } = useWebSocket();
  const [orders, setOrders] = useState<OrderUpdate[]>([]);

  useEffect(() => {
    const handleOrderUpdate = (order: OrderUpdate) => {
      setOrders(prev => {
        const existing = prev.find(o => o.order_id === order.order_id);
        if (existing) {
          return prev.map(o => o.order_id === order.order_id ? order : o);
        } else {
          return [...prev, order];
        }
      });
    };

    subscribe('order_update', handleOrderUpdate);
    
    return () => {
      unsubscribe('order_update');
    };
  }, [subscribe, unsubscribe]);

  return orders;
};
'@

$webSocketHook | Out-File -FilePath "frontend-new\src\hooks\useWebSocket.tsx" -Encoding UTF8

# Create Dashboard component
$dashboardComponent = @'
import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  IconButton,
  Button,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalanceWallet,
  ShowChart,
  Notifications,
  Refresh,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { Line } from 'recharts';
import { toast } from 'react-toastify';
import numeral from 'numeral';

import { tradingAPI, systemAPI } from '../services/api';
import { useMarketData, useWebSocket } from '../hooks/useWebSocket';
import MarketDataCard from '../components/trading/MarketDataCard';
import PortfolioSummary from '../components/trading/PortfolioSummary';
import OrderBook from '../components/trading/OrderBook';

const Dashboard: React.FC = () => {
  const { connected } = useWebSocket();
  const [watchlistSymbols] = useState(['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY']);
  const marketData = useMarketData(watchlistSymbols);

  // Fetch portfolio data
  const { data: portfolioData, refetch: refetchPortfolio } = useQuery(
    'portfolio-summary',
    () => tradingAPI.getPortfolioSummary(),
    { refetchInterval: 30000 }
  );

  // Fetch account data
  const { data: accountData } = useQuery(
    'account-summary',
    () => tradingAPI.getAccount(),
    { refetchInterval: 30000 }
  );

  // Fetch system status
  const { data: systemStatus } = useQuery(
    'system-status',
    () => systemAPI.getSystemStatus(),
    { refetchInterval: 60000 }
  );

  // Fetch recent orders
  const { data: recentOrders } = useQuery(
    'recent-orders',
    () => tradingAPI.getOrders({ limit: 10 }),
    { refetchInterval: 10000 }
  );

  const portfolio = portfolioData?.data;
  const account = accountData?.data;
  const orders = recentOrders?.data || [];

  const formatCurrency = (value: number) => numeral(value).format('$0,0.00');
  const formatPercent = (value: number) => numeral(value / 100).format('0.00%');

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          🚀 CamboAI Trading Dashboard
        </Typography>
        
        <Box display="flex" alignItems="center" gap={2}>
          <Chip 
            label={connected ? "🟢 Live Data" : "🔴 Offline"} 
            color={connected ? "success" : "error"}
            variant="outlined"
          />
          <IconButton onClick={() => window.location.reload()}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Portfolio Overview */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Portfolio Performance
              </Typography>
              
              {portfolio && (
                <Grid container spacing={2}>
                  <Grid item xs={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="primary">
                        {formatCurrency(portfolio.total_value || 0)}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Total Portfolio Value
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={3}>
                    <Box textAlign="center">
                      <Typography 
                        variant="h4" 
                        color={portfolio.day_pnl >= 0 ? "success.main" : "error.main"}
                      >
                        {formatCurrency(portfolio.day_pnl || 0)}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Day P&L ({formatPercent(portfolio.day_pnl_percent || 0)})
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={3}>
                    <Box textAlign="center">
                      <Typography variant="h4">
                        {formatCurrency(account?.cash_balance || 0)}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Cash Balance
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={3}>
                    <Box textAlign="center">
                      <Typography variant="h4">
                        {formatCurrency(account?.buying_power || 0)}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Buying Power
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* System Status */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🖥️ System Status
              </Typography>
              
              {systemStatus?.data && (
                <Box>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">Market Data</Typography>
                    <Chip 
                      label={systemStatus.data.services?.market_data?.status || 'Unknown'} 
                      color="success" 
                      size="small" 
                    />
                  </Box>
                  
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">Trading Engine</Typography>
                    <Chip 
                      label={systemStatus.data.services?.paper_trading?.status || 'Unknown'} 
                      color="success" 
                      size="small" 
                    />
                  </Box>
                  
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">Risk Management</Typography>
                    <Chip 
                      label={systemStatus.data.services?.risk_management?.status || 'Unknown'} 
                      color="success" 
                      size="small" 
                    />
                  </Box>
                  
                  <Box display="flex" justifyContent="space-between" mb={2}>
                    <Typography variant="body2">WebSocket</Typography>
                    <Chip 
                      label={connected ? 'Connected' : 'Disconnected'} 
                      color={connected ? "success" : "error"} 
                      size="small" 
                    />
                  </Box>
                  
                  <Button 
                    variant="outlined" 
                    size="small" 
                    href="/api/v1/system/status" 
                    target="_blank"
                    fullWidth
                  >
                    View Detailed Status
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Live Market Data */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📈 Live Market Data
              </Typography>
              
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Symbol</TableCell>
                      <TableCell align="right">Price</TableCell>
                      <TableCell align="right">Change</TableCell>
                      <TableCell align="right">Volume</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {watchlistSymbols.map((symbol) => {
                      const data = marketData[symbol];
                      const isPositive = data?.change >= 0;
                      
                      return (
                        <TableRow key={symbol}>
                          <TableCell component="th" scope="row">
                            <strong>{symbol}</strong>
                          </TableCell>
                          <TableCell align="right">
                            ${data?.price?.toFixed(2) || '--'}
                          </TableCell>
                          <TableCell align="right">
                            <Box display="flex" alignItems="center" justifyContent="flex-end">
                              {isPositive ? (
                                <TrendingUp color="success" />
                              ) : (
                                <TrendingDown color="error" />
                              )}
                              <Typography 
                                color={isPositive ? "success.main" : "error.main"}
                                ml={0.5}
                              >
                                {data?.change_percent?.toFixed(2) || '0.00'}%
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            {numeral(data?.volume || 0).format('0.0a')}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Orders */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📋 Recent Orders
              </Typography>
              
              {orders.length > 0 ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell>Side</TableCell>
                        <TableCell align="right">Quantity</TableCell>
                        <TableCell>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {orders.slice(0, 5).map((order: any) => (
                        <TableRow key={order.id}>
                          <TableCell>{order.asset_symbol}</TableCell>
                          <TableCell>
                            <Chip 
                              label={order.side} 
                              color={order.side === 'buy' ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="right">{order.quantity}</TableCell>
                          <TableCell>
                            <Chip 
                              label={order.status} 
                              variant="outlined"
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No recent orders
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                ⚡ Quick Actions
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item>
                  <Button 
                    variant="contained" 
                    color="primary"
                    startIcon={<ShowChart />}
                    href="/trading"
                  >
                    Start Trading
                  </Button>
                </Grid>
                
                <Grid item>
                  <Button 
                    variant="outlined" 
                    startIcon={<AccountBalanceWallet />}
                    href="/portfolio"
                  >
                    View Portfolio
                  </Button>
                </Grid>
                
                <Grid item>
                  <Button 
                    variant="outlined" 
                    href="/api/docs"
                    target="_blank"
                  >
                    API Documentation
                  </Button>
                </Grid>
                
                <Grid item>
                  <Button 
                    variant="outlined" 
                    href="/demo"
                    target="_blank"
                  >
                    Demo Trading
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
'@

$dashboardComponent | Out-File -FilePath "frontend-new\src\pages\Dashboard.tsx" -Encoding UTF8

# Create main index file
$indexTsx = @'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'@

$indexTsx | Out-File -FilePath "frontend-new\src\index.tsx" -Encoding UTF8

# Create HTML template
$indexHtml = @'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="CamboAI Trading Platform - Institutional Grade AI-Powered Trading" />
    <title>CamboAI Trading Platform</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
'@

$indexHtml | Out-File -FilePath "frontend-new\public\index.html" -Encoding UTF8

# Create CSS
$appCss = @'
.App {
  text-align: left;
  background-color: #0a0a0a;
  min-height: 100vh;
}

.App-header {
  padding: 20px;
  color: white;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* Animation for market data updates */
@keyframes price-flash {
  0% { background-color: rgba(0, 255, 136, 0.3); }
  100% { background-color: transparent; }
}

.price-update {
  animation: price-flash 0.5s ease-in-out;
}

/* Loading animations */
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.loading {
  animation: pulse 2s infinite;
}
'@

$appCss | Out-File -FilePath "frontend-new\src\App.css" -Encoding UTF8

Write-Host "`n📦 Installing React dependencies..." -ForegroundColor Yellow
Write-Host "This will take a few minutes..." -ForegroundColor Gray

Set-Location "frontend-new"

try {
    # Check if npm is available
    npm --version | Out-Null
    
    Write-Host "Installing packages..." -ForegroundColor Blue
    npm install
    
    Write-Host "`n✅ React frontend created successfully!" -ForegroundColor Green
    Write-Host "`nTo start the frontend:" -ForegroundColor Cyan
    Write-Host "1. cd frontend-new" -ForegroundColor White
    Write-Host "2. npm start" -ForegroundColor White
    Write-Host "`nOr run both frontend + backend:" -ForegroundColor Cyan
    Write-Host "python run_camboai.py" -ForegroundColor White
    
} catch {
    Write-Host "`n⚠️ NPM not found. To complete setup:" -ForegroundColor Yellow
    Write-Host "1. Install Node.js: https://nodejs.org" -ForegroundColor White
    Write-Host "2. cd frontend-new" -ForegroundColor White
    Write-Host "3. npm install" -ForegroundColor White
    Write-Host "4. npm start" -ForegroundColor White
}

Set-Location ".."

Write-Host "`n🌟 Frontend Features:" -ForegroundColor Cyan
Write-Host "• Real-time market data display" -ForegroundColor Gray
Write-Host "• WebSocket live updates" -ForegroundColor Gray
Write-Host "• Material-UI dark theme" -ForegroundColor Gray
Write-Host "• Portfolio dashboard" -ForegroundColor Gray
Write-Host "• Order management" -ForegroundColor Gray
Write-Host "• System status monitoring" -ForegroundColor Gray

Write-Host "`n✅ Modern React frontend ready!" -ForegroundColor Green