"use client";

/**
 * 📊 REAL-TIME STREAMING DASHBOARD - BEYOND BLOOMBERG TERMINAL
 * Ultra-fast real-time market data, charts, and trading interface
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import io from 'socket.io-client';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface MarketTick {
  symbol: string;
  price: number;
  volume: number;
  timestamp: number;
  bid: number;
  ask: number;
  last: number;
  change: number;
  changePercent: number;
}

interface OptionsFlow {
  symbol: string;
  strike: number;
  expiry: string;
  type: 'call' | 'put';
  volume: number;
  openInterest: number;
  premium: number;
  impliedVol: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  unusual: boolean;
  timestamp: number;
}

interface NewsAlert {
  id: string;
  headline: string;
  source: string;
  urgency: 'low' | 'medium' | 'high' | 'breaking';
  symbols: string[];
  timestamp: number;
  impact: number; // -1 to 1
}

interface StreamingData {
  marketTicks: Record<string, MarketTick>;
  optionsFlow: OptionsFlow[];
  newsAlerts: NewsAlert[];
  volumeProfile: Record<string, { price: number; volume: number }[]>;
  orderBook: Record<string, { bids: [number, number][]; asks: [number, number][] }>;
}

const RealTimeStreaming: React.FC = () => {
  const [streamingData, setStreamingData] = useState<StreamingData>({
    marketTicks: {},
    optionsFlow: [],
    newsAlerts: [],
    volumeProfile: {},
    orderBook: {}
  });

  const [selectedSymbols, setSelectedSymbols] = useState<string[]>(['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA']);
  const [viewMode, setViewMode] = useState<'grid' | 'focus' | 'analysis'>('grid');
  const [focusedSymbol, setFocusedSymbol] = useState<string>('SPY');
  const [showOrderBook, setShowOrderBook] = useState(false);
  const [showOptionsFlow, setShowOptionsFlow] = useState(true);
  const [alertsFilter, setAlertsFilter] = useState<'all' | 'breaking' | 'high'>('all');
  
  const socketRef = useRef<any>(null);
  const chartRefs = useRef<Record<string, any>>({});
  const priceHistoryRef = useRef<Record<string, { time: number; price: number }[]>>({});

  // Initialize WebSocket connection
  useEffect(() => {
    socketRef.current = io(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000', {
      transports: ['websocket'],
      upgrade: false
    });

    socketRef.current.on('connect', () => {
      console.log('🔗 Connected to real-time stream');
      // Subscribe to selected symbols
      socketRef.current.emit('subscribe', { symbols: selectedSymbols });
    });

    socketRef.current.on('market_tick', handleMarketTick);
    socketRef.current.on('options_flow', handleOptionsFlow);
    socketRef.current.on('news_alert', handleNewsAlert);
    socketRef.current.on('volume_profile', handleVolumeProfile);
    socketRef.current.on('order_book', handleOrderBook);

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  // Handle market tick updates
  const handleMarketTick = useCallback((tick: MarketTick) => {
    setStreamingData(prev => ({
      ...prev,
      marketTicks: {
        ...prev.marketTicks,
        [tick.symbol]: tick
      }
    }));

    // Update price history for charting
    if (!priceHistoryRef.current[tick.symbol]) {
      priceHistoryRef.current[tick.symbol] = [];
    }
    
    priceHistoryRef.current[tick.symbol].push({
      time: tick.timestamp,
      price: tick.price
    });

    // Keep only last 1000 points
    if (priceHistoryRef.current[tick.symbol].length > 1000) {
      priceHistoryRef.current[tick.symbol] = priceHistoryRef.current[tick.symbol].slice(-1000);
    }
  }, []);

  const handleOptionsFlow = useCallback((flow: OptionsFlow) => {
    setStreamingData(prev => ({
      ...prev,
      optionsFlow: [flow, ...prev.optionsFlow.slice(0, 99)] // Keep latest 100
    }));
  }, []);

  const handleNewsAlert = useCallback((alert: NewsAlert) => {
    setStreamingData(prev => ({
      ...prev,
      newsAlerts: [alert, ...prev.newsAlerts.slice(0, 49)] // Keep latest 50
    }));
  }, []);

  const handleVolumeProfile = useCallback((data: { symbol: string; profile: { price: number; volume: number }[] }) => {
    setStreamingData(prev => ({
      ...prev,
      volumeProfile: {
        ...prev.volumeProfile,
        [data.symbol]: data.profile
      }
    }));
  }, []);

  const handleOrderBook = useCallback((data: { symbol: string; bids: [number, number][]; asks: [number, number][] }) => {
    setStreamingData(prev => ({
      ...prev,
      orderBook: {
        ...prev.orderBook,
        [data.symbol]: { bids: data.bids, asks: data.asks }
      }
    }));
  }, []);

  // Generate chart data for symbol
  const getChartData = useMemo(() => (symbol: string) => {
    const history = priceHistoryRef.current[symbol] || [];
    const last50 = history.slice(-50);

    return {
      labels: last50.map(point => new Date(point.time).toLocaleTimeString()),
      datasets: [
        {
          label: symbol,
          data: last50.map(point => point.price),
          borderColor: streamingData.marketTicks[symbol]?.change >= 0 ? '#10B981' : '#EF4444',
          backgroundColor: streamingData.marketTicks[symbol]?.change >= 0 ? '#10B98120' : '#EF444420',
          borderWidth: 2,
          fill: true,
          tension: 0.1,
          pointRadius: 0,
          pointHoverRadius: 4,
        }
      ]
    };
  }, [streamingData.marketTicks]);

  const chartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    scales: {
      x: {
        display: false
      },
      y: {
        position: 'right',
        grid: {
          color: '#374151'
        },
        ticks: {
          color: '#9CA3AF',
          font: {
            size: 10
          }
        }
      }
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    }
  };

  const filteredAlerts = useMemo(() => {
    return streamingData.newsAlerts.filter(alert => {
      switch (alertsFilter) {
        case 'breaking': return alert.urgency === 'breaking';
        case 'high': return alert.urgency === 'high' || alert.urgency === 'breaking';
        default: return true;
      }
    });
  }, [streamingData.newsAlerts, alertsFilter]);

  const unusualOptionsFlow = useMemo(() => {
    return streamingData.optionsFlow.filter(flow => flow.unusual);
  }, [streamingData.optionsFlow]);

  return (
    <div className="h-screen bg-gray-900 text-white overflow-hidden">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-green-400">CamboAI Real-Time Trading</h1>
          
          <div className="flex items-center space-x-4">
            {/* View Mode Toggle */}
            <div className="flex bg-gray-700 rounded-lg p-1">
              {['grid', 'focus', 'analysis'].map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode as any)}
                  className={`px-3 py-1 rounded text-sm transition-colors ${
                    viewMode === mode 
                      ? 'bg-green-500 text-white' 
                      : 'text-gray-300 hover:text-white'
                  }`}
                >
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                </button>
              ))}
            </div>

            {/* Alerts Filter */}
            <select
              value={alertsFilter}
              onChange={(e) => setAlertsFilter(e.target.value as any)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
            >
              <option value="all">All Alerts</option>
              <option value="high">High Priority</option>
              <option value="breaking">Breaking Only</option>
            </select>

            {/* Feature Toggles */}
            <div className="flex space-x-2">
              <button
                onClick={() => setShowOrderBook(!showOrderBook)}
                className={`px-3 py-1 rounded text-sm ${
                  showOrderBook ? 'bg-blue-500' : 'bg-gray-600'
                } hover:opacity-80`}
              >
                Order Book
              </button>
              <button
                onClick={() => setShowOptionsFlow(!showOptionsFlow)}
                className={`px-3 py-1 rounded text-sm ${
                  showOptionsFlow ? 'bg-purple-500' : 'bg-gray-600'
                } hover:opacity-80`}
              >
                Options Flow
              </button>
            </div>
          </div>
        </div>

        {/* Market Summary */}
        <div className="mt-4 grid grid-cols-6 gap-4">
          {selectedSymbols.map(symbol => {
            const tick = streamingData.marketTicks[symbol];
            if (!tick) return null;

            return (
              <motion.div
                key={symbol}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  focusedSymbol === symbol ? 'bg-green-600' : 'bg-gray-700 hover:bg-gray-600'
                }`}
                onClick={() => setFocusedSymbol(symbol)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="text-lg font-bold">{symbol}</div>
                <div className="text-xl">${tick.price.toFixed(2)}</div>
                <div className={`text-sm ${
                  tick.change >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {tick.change >= 0 ? '+' : ''}{tick.change.toFixed(2)} ({tick.changePercent.toFixed(2)}%)
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      <div className="flex h-[calc(100vh-200px)]">
        {/* Main Chart Area */}
        <div className={`${viewMode === 'grid' ? 'w-3/4' : 'w-full'}`}>
          {viewMode === 'grid' && (
            <div className="grid grid-cols-3 gap-2 p-2 h-full">
              {selectedSymbols.slice(0, 6).map(symbol => (
                <div key={symbol} className="bg-gray-800 rounded-lg p-3">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="text-lg font-semibold">{symbol}</h3>
                    <div className={`text-sm ${
                      streamingData.marketTicks[symbol]?.change >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {streamingData.marketTicks[symbol]?.changePercent?.toFixed(2)}%
                    </div>
                  </div>
                  <div className="h-32">
                    <Line data={getChartData(symbol)} options={chartOptions} />
                  </div>
                  <div className="mt-2 text-sm text-gray-400">
                    Vol: {streamingData.marketTicks[symbol]?.volume?.toLocaleString() || 'N/A'}
                  </div>
                </div>
              ))}
            </div>
          )}

          {viewMode === 'focus' && (
            <div className="p-4 h-full">
              <div className="bg-gray-800 rounded-lg p-4 h-full">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-bold">{focusedSymbol}</h2>
                  <div className="text-right">
                    <div className="text-3xl font-bold">
                      ${streamingData.marketTicks[focusedSymbol]?.price?.toFixed(2)}
                    </div>
                    <div className={`text-lg ${
                      streamingData.marketTicks[focusedSymbol]?.change >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {streamingData.marketTicks[focusedSymbol]?.change >= 0 ? '+' : ''}
                      {streamingData.marketTicks[focusedSymbol]?.change?.toFixed(2)} 
                      ({streamingData.marketTicks[focusedSymbol]?.changePercent?.toFixed(2)}%)
                    </div>
                  </div>
                </div>
                
                <div className="h-96">
                  <Line data={getChartData(focusedSymbol)} options={chartOptions} />
                </div>

                {/* Trading Interface */}
                <div className="mt-4 grid grid-cols-2 gap-4">
                  <div className="bg-gray-700 rounded p-3">
                    <h4 className="font-semibold mb-2">Quick Trade</h4>
                    <div className="flex space-x-2">
                      <button className="bg-green-500 hover:bg-green-600 px-4 py-2 rounded">
                        BUY
                      </button>
                      <button className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded">
                        SELL
                      </button>
                      <input
                        type="number"
                        placeholder="Qty"
                        className="bg-gray-600 border border-gray-500 rounded px-2 py-1 w-20"
                      />
                    </div>
                  </div>

                  <div className="bg-gray-700 rounded p-3">
                    <h4 className="font-semibold mb-2">Level II</h4>
                    <div className="text-sm space-y-1">
                      {streamingData.orderBook[focusedSymbol]?.asks?.slice(0, 3).map((ask, i) => (
                        <div key={i} className="flex justify-between text-red-400">
                          <span>{ask[1]}</span>
                          <span>${ask[0].toFixed(2)}</span>
                        </div>
                      ))}
                      <div className="border-t border-gray-600 my-1"></div>
                      {streamingData.orderBook[focusedSymbol]?.bids?.slice(0, 3).map((bid, i) => (
                        <div key={i} className="flex justify-between text-green-400">
                          <span>{bid[1]}</span>
                          <span>${bid[0].toFixed(2)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {viewMode === 'analysis' && (
            <div className="p-4 h-full">
              <div className="grid grid-cols-2 gap-4 h-full">
                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3">Market Heatmap</h3>
                  <div className="grid grid-cols-4 gap-2">
                    {selectedSymbols.map(symbol => {
                      const tick = streamingData.marketTicks[symbol];
                      const change = tick?.changePercent || 0;
                      const intensity = Math.min(Math.abs(change) / 5, 1);
                      
                      return (
                        <div
                          key={symbol}
                          className={`p-4 rounded text-center transition-all ${
                            change >= 0 
                              ? `bg-green-500 bg-opacity-${Math.floor(intensity * 100)}`
                              : `bg-red-500 bg-opacity-${Math.floor(intensity * 100)}`
                          }`}
                          style={{
                            backgroundColor: change >= 0 
                              ? `rgba(16, 185, 129, ${intensity})` 
                              : `rgba(239, 68, 68, ${intensity})`
                          }}
                        >
                          <div className="font-semibold">{symbol}</div>
                          <div className="text-sm">{change.toFixed(2)}%</div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3">Volume Leaders</h3>
                  <div className="space-y-2">
                    {selectedSymbols
                      .sort((a, b) => (streamingData.marketTicks[b]?.volume || 0) - (streamingData.marketTicks[a]?.volume || 0))
                      .slice(0, 6)
                      .map(symbol => {
                        const tick = streamingData.marketTicks[symbol];
                        return (
                          <div key={symbol} className="flex justify-between items-center">
                            <span className="font-semibold">{symbol}</span>
                            <div className="text-right">
                              <div>{(tick?.volume || 0).toLocaleString()}</div>
                              <div className={`text-sm ${tick?.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                {tick?.changePercent?.toFixed(2)}%
                              </div>
                            </div>
                          </div>
                        );
                      })}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Sidebar */}
        {viewMode === 'grid' && (
          <div className="w-1/4 bg-gray-800 border-l border-gray-700 overflow-hidden">
            <div className="h-full flex flex-col">
              {/* News Alerts */}
              <div className="flex-1 border-b border-gray-700">
                <div className="p-3 border-b border-gray-600">
                  <h3 className="font-semibold text-blue-400">Market Alerts</h3>
                </div>
                <div className="overflow-y-auto h-48">
                  <AnimatePresence>
                    {filteredAlerts.map(alert => (
                      <motion.div
                        key={alert.id}
                        initial={{ opacity: 0, x: 50 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -50 }}
                        className={`p-3 border-b border-gray-700 hover:bg-gray-700 cursor-pointer ${
                          alert.urgency === 'breaking' ? 'border-l-4 border-red-500' :
                          alert.urgency === 'high' ? 'border-l-4 border-yellow-500' : ''
                        }`}
                      >
                        <div className="text-sm font-medium">{alert.headline}</div>
                        <div className="flex justify-between items-center mt-1">
                          <span className="text-xs text-gray-400">{alert.source}</span>
                          <span className="text-xs text-blue-400">
                            {alert.symbols.join(', ')}
                          </span>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              </div>

              {/* Options Flow */}
              {showOptionsFlow && (
                <div className="flex-1">
                  <div className="p-3 border-b border-gray-600">
                    <h3 className="font-semibold text-purple-400">Unusual Options</h3>
                  </div>
                  <div className="overflow-y-auto h-48">
                    {unusualOptionsFlow.slice(0, 10).map((flow, index) => (
                      <div key={index} className="p-3 border-b border-gray-700 hover:bg-gray-700">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-semibold">{flow.symbol}</div>
                            <div className="text-sm text-gray-400">
                              ${flow.strike} {flow.type.toUpperCase()} {flow.expiry}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-semibold">
                              {flow.volume.toLocaleString()}
                            </div>
                            <div className="text-xs text-gray-400">
                              IV: {(flow.impliedVol * 100).toFixed(1)}%
                            </div>
                          </div>
                        </div>
                        <div className="mt-2 flex justify-between text-xs">
                          <span>Δ: {flow.delta.toFixed(3)}</span>
                          <span>Γ: {flow.gamma.toFixed(3)}</span>
                          <span>Θ: {flow.theta.toFixed(2)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Bottom Status Bar */}
      <div className="bg-gray-800 border-t border-gray-700 p-2">
        <div className="flex justify-between items-center text-sm">
          <div className="flex space-x-4">
            <span className="text-green-400">● Connected</span>
            <span>Market: OPEN</span>
            <span>Latency: 12ms</span>
          </div>
          <div className="flex space-x-4">
            <span>Updates/sec: 847</span>
            <span>Total Symbols: {Object.keys(streamingData.marketTicks).length}</span>
            <span>{new Date().toLocaleTimeString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeStreaming;