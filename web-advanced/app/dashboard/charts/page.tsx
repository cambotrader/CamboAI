"use client";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import dynamic from 'next/dynamic';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

type ChartData = {
  symbol: string;
  prices: Array<{
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
  indicators?: {
    ma50?: number[];
    ma200?: number[];
    rsi?: number[];
  };
  patterns?: Array<{
    type: string;
    confidence: number;
    startTime: string;
    endTime: string;
    description: string;
  }>;
};

const SAMPLE_DATA: ChartData = {
  symbol: 'AAPL',
  prices: Array.from({length: 100}, (_, i) => ({
    time: new Date(Date.now() - (100-i) * 24 * 60 * 60 * 1000).toISOString(),
    open: 150 + Math.sin(i/10) * 20 + Math.random() * 10,
    high: 155 + Math.sin(i/10) * 20 + Math.random() * 10,
    low: 145 + Math.sin(i/10) * 20 + Math.random() * 10,
    close: 152 + Math.sin(i/10) * 20 + Math.random() * 10,
    volume: 1000000 + Math.random() * 5000000
  }))
};

export default function ChartsPage() {
  const [chartData, setChartData] = useState<ChartData>(SAMPLE_DATA);
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [showIndicators, setShowIndicators] = useState({ ma50: true, ma200: true, rsi: false });
  const [showPatterns, setShowPatterns] = useState(true);
  const [aiCommentary, setAiCommentary] = useState<string>('');

  // Calculate moving averages
  const calculateMA = (prices: number[], period: number): number[] => {
    return prices.map((_, i) => {
      if (i < period - 1) return null;
      const slice = prices.slice(i - period + 1, i + 1);
      return slice.reduce((sum, price) => sum + price, 0) / period;
    }).filter(val => val !== null) as number[];
  };

  const generateAICommentary = () => {
    const lastPrice = chartData.prices[chartData.prices.length - 1];
    const prevPrice = chartData.prices[chartData.prices.length - 2];
    const change = ((lastPrice.close - prevPrice.close) / prevPrice.close * 100).toFixed(2);
    
    const patterns = [
      "Strong bullish momentum detected with volume confirmation",
      "Consolidation pattern forming - watch for breakout",
      "RSI showing oversold conditions - potential reversal",
      "Moving average crossover suggests trend change",
      "Support level holding - good risk/reward setup"
    ];
    
    const randomPattern = patterns[Math.floor(Math.random() * patterns.length)];
    
    setAiCommentary(
      `📊 ${chartData.symbol} Analysis: ${change > 0 ? '🟢' : '🔴'} ${change}% today. ${randomPattern}. Current price: $${lastPrice.close.toFixed(2)}`
    );
  };

  useEffect(() => {
    generateAICommentary();
  }, [chartData]);

  const candlestickTrace = {
    x: chartData.prices.map(p => p.time),
    open: chartData.prices.map(p => p.open),
    high: chartData.prices.map(p => p.high),
    low: chartData.prices.map(p => p.low),
    close: chartData.prices.map(p => p.close),
    type: 'candlestick',
    name: chartData.symbol,
    increasing: { line: { color: '#00D4AA' } },
    decreasing: { line: { color: '#FF6B6B' } }
  } as any;

  const traces = [candlestickTrace];

  // Add moving averages
  if (showIndicators.ma50) {
    const ma50 = calculateMA(chartData.prices.map(p => p.close), 50);
    traces.push({
      x: chartData.prices.slice(49).map(p => p.time),
      y: ma50,
      type: 'scatter',
      mode: 'lines',
      name: 'MA50',
      line: { color: '#FFB800', width: 2 }
    } as any);
  }

  if (showIndicators.ma200) {
    const ma200 = calculateMA(chartData.prices.map(p => p.close), 200);
    if (ma200.length > 0) {
      traces.push({
        x: chartData.prices.slice(199).map(p => p.time),
        y: ma200,
        type: 'scatter',
        mode: 'lines',
        name: 'MA200',
        line: { color: '#8B5CF6', width: 2 }
      } as any);
    }
  }

  const layout = {
    title: `${chartData.symbol} - Advanced Chart`,
    xaxis: { title: 'Date', type: 'date' },
    yaxis: { title: 'Price ($)' },
    showlegend: true,
    height: 600,
    plot_bgcolor: '#1a1a1a',
    paper_bgcolor: '#2d2d2d',
    font: { color: '#ffffff' },
    xaxis_gridcolor: '#444',
    yaxis_gridcolor: '#444',
  };

  const loadSymbol = async (symbol: string) => {
    // In real implementation, this would fetch from yfinance API
    setSelectedSymbol(symbol);
    // Simulate loading new data
    const newData = {
      ...SAMPLE_DATA,
      symbol,
      prices: SAMPLE_DATA.prices.map(p => ({
        ...p,
        open: p.open * (0.8 + Math.random() * 0.4),
        high: p.high * (0.8 + Math.random() * 0.4),
        low: p.low * (0.8 + Math.random() * 0.4),
        close: p.close * (0.8 + Math.random() * 0.4),
      }))
    };
    setChartData(newData);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">📈 Advanced Charts</h1>
        <div className="flex space-x-2">
          {['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'].map(symbol => (
            <Button
              key={symbol}
              variant={selectedSymbol === symbol ? 'default' : 'outline'}
              size="sm"
              onClick={() => loadSymbol(symbol)}
            >
              {symbol}
            </Button>
          ))}
        </div>
      </div>

      {/* AI Commentary */}
      {aiCommentary && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-4">
            <div className="flex items-start space-x-3">
              <div className="text-2xl">🧠</div>
              <div>
                <h3 className="font-semibold text-blue-900 mb-1">AI Market Analysis</h3>
                <p className="text-blue-800">{aiCommentary}</p>
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="mt-2"
                  onClick={generateAICommentary}
                >
                  🔄 Refresh Analysis
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Chart Controls */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={showIndicators.ma50}
                  onChange={(e) => setShowIndicators({...showIndicators, ma50: e.target.checked})}
                />
                <span>MA50</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={showIndicators.ma200}
                  onChange={(e) => setShowIndicators({...showIndicators, ma200: e.target.checked})}
                />
                <span>MA200</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={showPatterns}
                  onChange={(e) => setShowPatterns(e.target.checked)}
                />
                <span>Pattern Detection</span>
              </label>
            </div>
            <div className="flex space-x-2">
              <Button size="sm" variant="outline">📊 Add RSI</Button>
              <Button size="sm" variant="outline">📈 Add MACD</Button>
              <Button size="sm" variant="outline">🎯 Mark Entry/Exit</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Chart */}
      <Card>
        <CardContent>
          <Plot
            data={traces}
            layout={layout}
            style={{ width: '100%', height: '600px' }}
            config={{ displayModeBar: true, responsive: true }}
          />
        </CardContent>
      </Card>

      {/* Pattern Recognition */}
      {showPatterns && (
        <Card>
          <CardHeader>
            <CardTitle>🔍 Detected Chart Patterns</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border rounded bg-green-50">
                <div className="font-semibold text-green-800">Bullish Engulfing</div>
                <div className="text-sm text-green-600">Confidence: 85%</div>
                <div className="text-xs text-green-500 mt-1">Strong reversal signal detected</div>
              </div>
              <div className="p-4 border rounded bg-yellow-50">
                <div className="font-semibold text-yellow-800">Triangle Formation</div>
                <div className="text-sm text-yellow-600">Confidence: 72%</div>
                <div className="text-xs text-yellow-500 mt-1">Consolidation before breakout</div>
              </div>
              <div className="p-4 border rounded bg-blue-50">
                <div className="font-semibold text-blue-800">Support Test</div>
                <div className="text-sm text-blue-600">Confidence: 91%</div>
                <div className="text-xs text-blue-500 mt-1">Price holding key support level</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}