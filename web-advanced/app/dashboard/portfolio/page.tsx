"use client";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import dynamic from 'next/dynamic';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

type Position = {
  id: number;
  symbol: string;
  quantity: number;
  entry_price: number;
  current_price: number;
  pnl: number;
  pnl_percentage: number;
  market_value: number;
  entry_date: string;
};

type PerformanceData = {
  date: string;
  value: number;
  daily_return: number;
  cumulative_return: number;
};

export default function PortfolioPage() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [summary, setSummary] = useState<any>({});
  const [performance, setPerformance] = useState<PerformanceData[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadPortfolioData();
  }, []);

  const loadPortfolioData = async () => {
    setLoading(true);
    try {
      // Simulate API calls - replace with real API calls
      await Promise.all([
        loadPositions(),
        loadSummary(),
        loadPerformance()
      ]);
    } catch (error) {
      console.error('Failed to load portfolio data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadPositions = async () => {
    // Mock data - replace with real API call to /api/portfolio/positions
    const mockPositions = [
      {
        id: 1,
        symbol: 'AAPL',
        quantity: 100,
        entry_price: 150.00,
        current_price: 175.50,
        pnl: 2550,
        pnl_percentage: 17.0,
        market_value: 17550,
        entry_date: '2024-01-15T10:30:00Z'
      },
      {
        id: 2,
        symbol: 'MSFT',
        quantity: 50,
        entry_price: 300.00,
        current_price: 285.75,
        pnl: -712.50,
        pnl_percentage: -4.75,
        market_value: 14287.50,
        entry_date: '2024-02-01T14:20:00Z'
      },
      {
        id: 3,
        symbol: 'GOOGL',
        quantity: 25,
        entry_price: 2800.00,
        current_price: 2950.25,
        pnl: 3756.25,
        pnl_percentage: 5.38,
        market_value: 73756.25,
        entry_date: '2024-01-20T09:15:00Z'
      },
      {
        id: 4,
        symbol: 'TSLA',
        quantity: 75,
        entry_price: 220.00,
        current_price: 195.80,
        pnl: -1815,
        pnl_percentage: -10.9,
        market_value: 14685,
        entry_date: '2024-02-10T11:45:00Z'
      }
    ];
    setPositions(mockPositions);
  };

  const loadSummary = async () => {
    // Calculate summary from positions
    const totalValue = positions.reduce((sum, pos) => sum + pos.market_value, 0);
    const totalPnL = positions.reduce((sum, pos) => sum + pos.pnl, 0);
    const totalInvested = positions.reduce((sum, pos) => sum + (pos.quantity * pos.entry_price), 0);
    
    setSummary({
      total_value: 120278.75,
      total_pnl: 3778.75,
      total_return_pct: 3.24,
      day_pnl: 1245.20,
      day_pnl_pct: 1.04,
      cash_balance: 15420.50,
      buying_power: 62140.25,
      positions_count: 4
    });
  };

  const loadPerformance = async () => {
    // Mock performance data
    const mockPerformance = Array.from({length: 90}, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (89 - i));
      const baseValue = 115000;
      const noise = Math.sin(i / 10) * 5000 + Math.random() * 2000 - 1000;
      const value = baseValue + noise;
      
      return {
        date: date.toISOString(),
        value: value,
        daily_return: i === 0 ? 0 : ((value - (baseValue + Math.sin((i-1) / 10) * 5000)) / (baseValue + Math.sin((i-1) / 10) * 5000)) * 100,
        cumulative_return: ((value - baseValue) / baseValue) * 100
      };
    });
    setPerformance(mockPerformance);
  };

  const generatePerformanceChart = () => {
    if (performance.length === 0) return null;

    return {
      data: [
        {
          x: performance.map(p => p.date),
          y: performance.map(p => p.value),
          type: 'scatter',
          mode: 'lines',
          name: 'Portfolio Value',
          line: { color: '#3B82F6', width: 2 },
          fill: 'tonexty',
          fillcolor: 'rgba(59, 130, 246, 0.1)'
        }
      ],
      layout: {
        title: 'Portfolio Performance (90 Days)',
        xaxis: { title: 'Date' },
        yaxis: { title: 'Portfolio Value ($)' },
        showlegend: false,
        height: 400,
        plot_bgcolor: '#F9FAFB',
        paper_bgcolor: '#FFFFFF',
        margin: { l: 80, r: 40, t: 40, b: 60 }
      }
    };
  };

  const performanceChart = generatePerformanceChart();

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">📊 Portfolio Management</h1>
        <Button onClick={loadPortfolioData} disabled={loading}>
          {loading ? 'Updating...' : '🔄 Refresh'}
        </Button>
      </div>

      {/* Portfolio Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-600">Total Value</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${summary.total_value?.toLocaleString()}</div>
            <p className="text-xs text-gray-500">Available: ${summary.cash_balance?.toLocaleString()}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-600">Total P&L</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${summary.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {summary.total_pnl >= 0 ? '+' : ''}${summary.total_pnl?.toLocaleString()}
            </div>
            <p className={`text-xs ${summary.total_return_pct >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {summary.total_return_pct >= 0 ? '+' : ''}{summary.total_return_pct}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-600">Day P&L</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${summary.day_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {summary.day_pnl >= 0 ? '+' : ''}${summary.day_pnl?.toLocaleString()}
            </div>
            <p className={`text-xs ${summary.day_pnl_pct >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {summary.day_pnl_pct >= 0 ? '+' : ''}{summary.day_pnl_pct}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-600">Buying Power</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${summary.buying_power?.toLocaleString()}</div>
            <p className="text-xs text-gray-500">{summary.positions_count} positions</p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="positions">Positions</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {performanceChart && (
            <Card>
              <CardContent className="pt-6">
                <Plot
                  data={performanceChart.data}
                  layout={performanceChart.layout}
                  style={{ width: '100%', height: '400px' }}
                  config={{ displayModeBar: true, responsive: true }}
                />
              </CardContent>
            </Card>
          )}

          {/* Top Positions */}
          <Card>
            <CardHeader>
              <CardTitle>Top Positions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {positions.slice(0, 3).map((position) => (
                  <div key={position.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="font-bold text-blue-600">{position.symbol[0]}</span>
                      </div>
                      <div>
                        <div className="font-semibold">{position.symbol}</div>
                        <div className="text-sm text-gray-500">{position.quantity} shares</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold">${position.market_value.toLocaleString()}</div>
                      <div className={`text-sm ${position.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {position.pnl >= 0 ? '+' : ''}${position.pnl.toLocaleString()} ({position.pnl_percentage >= 0 ? '+' : ''}{position.pnl_percentage.toFixed(1)}%)
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="positions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>All Positions ({positions.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b text-left text-sm text-gray-500">
                      <th className="pb-2">Symbol</th>
                      <th className="pb-2">Quantity</th>
                      <th className="pb-2">Avg Price</th>
                      <th className="pb-2">Current Price</th>
                      <th className="pb-2">Market Value</th>
                      <th className="pb-2">P&L</th>
                      <th className="pb-2">P&L %</th>
                      <th className="pb-2">Entry Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {positions.map((position) => (
                      <tr key={position.id} className="border-b">
                        <td className="py-3">
                          <div className="flex items-center space-x-2">
                            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-xs font-bold text-blue-600">{position.symbol[0]}</span>
                            </div>
                            <span className="font-semibold">{position.symbol}</span>
                          </div>
                        </td>
                        <td className="py-3">{position.quantity}</td>
                        <td className="py-3">${position.entry_price.toFixed(2)}</td>
                        <td className="py-3">${position.current_price.toFixed(2)}</td>
                        <td className="py-3">${position.market_value.toLocaleString()}</td>
                        <td className={`py-3 ${position.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {position.pnl >= 0 ? '+' : ''}${position.pnl.toLocaleString()}
                        </td>
                        <td className={`py-3 ${position.pnl_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {position.pnl_percentage >= 0 ? '+' : ''}{position.pnl_percentage.toFixed(2)}%
                        </td>
                        <td className="py-3 text-gray-500">
                          {new Date(position.entry_date).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          {performanceChart && (
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Performance Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <Plot
                  data={performanceChart.data}
                  layout={performanceChart.layout}
                  style={{ width: '100%', height: '500px' }}
                  config={{ displayModeBar: true, responsive: true }}
                />
              </CardContent>
            </Card>
          )}

          {/* Performance Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-600">Best Day</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-xl font-bold text-green-600">+$2,450</div>
                <p className="text-xs text-gray-500">+2.1%</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-600">Worst Day</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-xl font-bold text-red-600">-$1,890</div>
                <p className="text-xs text-gray-500">-1.6%</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-600">Win Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-xl font-bold">67%</div>
                <p className="text-xs text-gray-500">45 up days</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-600">Sharpe Ratio</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-xl font-bold">1.45</div>
                <p className="text-xs text-gray-500">Risk-adjusted</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}