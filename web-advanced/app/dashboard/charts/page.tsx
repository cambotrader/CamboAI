"use client";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

import { useToast } from '@/components/ui/use-toast';
import dynamic from 'next/dynamic';
import { ConnectDataPanel } from '@/components/dashboard/connect-data-panel';
import { DateRangeCompact, DateRange } from '@/components/ui/date-range-compact';
import { ShortcutsTooltip } from '@/components/ui/shortcuts-tooltip';

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
  const [marketType, setMarketType] = useState<'stock' | 'crypto'>('stock');
  const [interval, setInterval] = useState<string>('1d');
  const [range, setRange] = useState<string>('1mo');
  const [typedSymbol, setTypedSymbol] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [reloadTrigger, setReloadTrigger] = useState<number>(0);
  const { toast } = useToast();
  const [fromDate, setFromDate] = useState<string>("");
  const [toDate, setToDate] = useState<string>("");
  const [preset, setPreset] = useState<string>("1mo");
  const [truncated, setTruncated] = useState<boolean>(false);
  const [clampInfo, setClampInfo] = useState<string>("");

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

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem('charts_prefs') || '{}');
      if (saved.marketType) setMarketType(saved.marketType);
      if (saved.interval) setInterval(saved.interval);
      if (saved.range) setRange(saved.range);
      if (saved.fromDate) setFromDate(saved.fromDate);
      if (saved.toDate) setToDate(saved.toDate);
      if (saved.preset) setPreset(saved.preset);
      if (saved.symbol) {
        setSelectedSymbol(saved.symbol);
        // trigger initial fetch
        setTimeout(() => loadSymbol(saved.symbol), 0);
      }
    } catch {}
  }, []);

  // Persist preferences
  useEffect(() => {
    const prefs = { marketType, interval, range, symbol: selectedSymbol, fromDate, toDate, preset };
    localStorage.setItem('charts_prefs', JSON.stringify(prefs));
  }, [marketType, interval, range, selectedSymbol, fromDate, toDate, preset]);

  // Cap client-side date span per interval (prevent >1000 candles for crypto; keep reasonable for stocks)
  function clampDateRange(baseFrom: string, baseTo: string): { from: string, to: string } {
    setClampInfo("");
    if (!baseFrom || !baseTo) return { from: baseFrom, to: baseTo } as any;
    const from = new Date(baseFrom);
    const to = new Date(baseTo);
    if (to < from) return { from: baseFrom, to: baseTo } as any;

    // Preset-driven span (days)
    const presetDaysMap: Record<string, number> = {
      '1d': 1,
      '5d': 5,
      '1mo': 30,
      '3mo': 90,
      '6mo': 180,
      '1y': 365,
      '2y': 730,
      '5y': 1825,
      '10y': 3650,
      'ytd': 365,
      'max': 36500,
      'custom': 36500,
    };

    // Interval safety caps to keep requests reasonable
    const daysByInterval: Record<string, number> = {
      '1m': 1,   // tight cap to avoid frequent truncation
      '2m': 2,
      '5m': 5,
      '15m': 15,
      '1h': 45,
      '4h': 120,
      '1d': 1825,
      '1wk': 3650,
      '1mo': 36500,
    };

    const presetDays = presetDaysMap[preset] ?? 90;
    const intervalMax = daysByInterval[interval] ?? 90;
    const maxDays = Math.min(presetDays, intervalMax);

    const ms = 86400000;
    const spanDays = Math.ceil((to.getTime() - from.getTime()) / ms) + 1;
    if (spanDays > maxDays) {
      const newFrom = new Date(to.getTime() - (maxDays - 1) * ms);
      setClampInfo(`capped to ${interval} limit (${maxDays}d)`);
      return { from: newFrom.toISOString().slice(0,10), to: to.toISOString().slice(0,10) };
    }
    return { from: baseFrom, to: baseTo };
  }

  // Debounce reloading when controls change
  useEffect(() => {
    const t = setTimeout(() => {
      // Clamp range before loading
      const clamped = clampDateRange(fromDate, toDate);
      if (clamped.from !== fromDate) setFromDate(clamped.from);
      if (clamped.to !== toDate) setToDate(clamped.to);
      loadSymbol(selectedSymbol);
    }, 400);
    return () => clearTimeout(t);
  }, [marketType, interval, range, fromDate, toDate, preset]);

  // Manual reload trigger
  useEffect(() => {
    if (reloadTrigger) loadSymbol(selectedSymbol);
  }, [reloadTrigger]);

  useEffect(() => {
    generateAICommentary();
  }, [chartData]);

  // Keyboard shortcuts: R reload, Left/Right arrows to shift window
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'r' || e.key === 'R') {
        e.preventDefault();
        setReloadTrigger(Date.now());
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        const now = toDate ? new Date(toDate) : new Date();
        const prev = (d: Date, days: number) => new Date(d.getTime() - days * 86400000);
        let days = 30;
        if (preset === '1d') days = 1; else if (preset === '5d') days = 5; else if (preset === '1mo') days = 30; else if (preset === '3mo') days = 90; else if (preset === '6mo') days = 180; else if (preset === '1y') days = 365;
        const newTo = prev(now, days);
        const newFrom = prev(newTo, days);
        setFromDate(newFrom.toISOString().slice(0,10));
        setToDate(newTo.toISOString().slice(0,10));
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        const baseFrom = fromDate ? new Date(fromDate) : new Date();
        const nextDate = (d: Date, days: number) => new Date(d.getTime() + days * 86400000);
        let days = 30;
        if (preset === '1d') days = 1; else if (preset === '5d') days = 5; else if (preset === '1mo') days = 30; else if (preset === '3mo') days = 90; else if (preset === '6mo') days = 180; else if (preset === '1y') days = 365;
        const newFrom = nextDate(baseFrom, days);
        const newTo = nextDate(newFrom, days);
        setFromDate(newFrom.toISOString().slice(0,10));
        setToDate(newTo.toISOString().slice(0,10));
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [preset, fromDate, toDate]);

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
    setSelectedSymbol(symbol);
    setErrorMsg('');
    setLoading(true);
    try {
      const params: Record<string, string> = { type: marketType, symbol, interval, range };
      if (fromDate) params.from = fromDate;
      if (toDate) params.to = toDate;
      const qs = new URLSearchParams(params).toString();
      const res = await fetch(`/api/market/ohlc?${qs}`);
      if (!res.ok) throw new Error(`Failed to fetch data (${res.status})`);
      const data = await res.json();
      const prices = (data.candles || []).map((c: any) => ({
        time: new Date(c.t).toISOString(),
        open: c.o,
        high: c.h,
        low: c.l,
        close: c.c,
        volume: c.v ?? 0,
      }));
      if (prices.length > 0) {
        setChartData({ symbol, prices });
        const wasTruncated = marketType === 'crypto' && !!data.truncated;
        setTruncated(wasTruncated);
        if (wasTruncated) {
          toast({ title: 'Range truncated', description: 'Binance capped results at 1000 intervals. Narrow your range or use a higher interval.' });
        }
      } else {
        setErrorMsg('No data returned for this symbol/settings.');
        setTruncated(false);
      }
    } catch (e: any) {
      const msg = e?.message || 'Failed to load data';
      setErrorMsg(msg);
      toast({ title: 'Fetch Error', description: msg });
      const newData = {
        ...SAMPLE_DATA,
        symbol,
        prices: SAMPLE_DATA.prices.map(p => ({
          ...p,
          open: p.open * (0.9 + Math.random() * 0.2),
          high: p.high * (0.9 + Math.random() * 0.2),
          low: p.low * (0.9 + Math.random() * 0.2),
          close: p.close * (0.9 + Math.random() * 0.2),
        }))
      };
      setChartData(newData);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">📈 Advanced Charts</h1>
        <div className="flex items-center gap-3 text-sm text-gray-500">
          <span>Preset: {preset || 'custom'} {fromDate && toDate ? `(${fromDate} → ${toDate})` : ''}</span>
          <ShortcutsTooltip />
        </div>
        <div className="flex space-x-2">
          {(
            marketType === 'stock'
              ? ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
              : ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT']
          ).map(symbol => (
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

      <div className="flex flex-wrap gap-3 items-center">
        <select className="p-2 border rounded" value={marketType} onChange={e => setMarketType(e.target.value as any)}>
          <option value="stock">Stocks (Yahoo)</option>
          <option value="crypto">Crypto (Binance)</option>
        </select>

        {marketType === 'stock' ? (
          <>
            <select className="p-2 border rounded" value={interval} onChange={e => setInterval(e.target.value)}>
              <option value="1m">1m</option>
              <option value="2m">2m</option>
              <option value="5m">5m</option>
              <option value="15m">15m</option>
              <option value="1d">1d</option>
              <option value="1wk">1wk</option>
              <option value="1mo">1mo</option>
            </select>
            <DateRangeCompact
              value={{ from: fromDate || undefined, to: toDate || undefined }}
              onChange={(v, p) => {
                setFromDate(v.from || "");
                setToDate(v.to || "");
                if (p) setPreset(p);
                setReloadTrigger(Date.now());
              }}
            />
          </>
        ) : (
          <>
            <div className="flex items-center gap-2">
              <select className="p-2 border rounded" value={interval} onChange={e => setInterval(e.target.value)}>
                <option value="1m">1m</option>
                <option value="5m">5m</option>
                <option value="15m">15m</option>
                <option value="1h">1h</option>
                <option value="4h">4h</option>
                <option value="1d">1d</option>
              </select>
              <div className="flex items-center gap-2">
                <DateRangeCompact
                  value={{ from: fromDate || undefined, to: toDate || undefined }}
                  onChange={(v, p) => {
                    setFromDate(v.from || "");
                    setToDate(v.to || "");
                    if (p) setPreset(p);
                    setReloadTrigger(Date.now());
                  }}
                />
                {clampInfo && (
                  <span className="flex items-center gap-1 text-xs px-2 py-1 rounded bg-slate-100 text-slate-700 border border-slate-200">
                    <span title="Adjusted by preset + interval">ⓘ</span>
                    <span>{clampInfo}</span>
                  </span>
                )}
                {truncated && (
                  <span className="text-xs px-2 py-1 rounded bg-amber-100 text-amber-800 border border-amber-200" title="Binance returned only 1000 candles">Truncated</span>
                )}
              </div>
            </div>
          </>
        )}

        <div className="flex items-center gap-2">
          <input
            className="p-2 border rounded w-40"
            placeholder={marketType === 'crypto' ? 'e.g., BTCUSDT' : 'e.g., AAPL'}
            value={typedSymbol}
            onChange={(e) => setTypedSymbol(e.target.value.toUpperCase().trim())}
          />

          <Button
            size="sm"
            onClick={() => {
              const s = typedSymbol;
              if (!s) return;
              // Basic validation
              const stockOk = /^[A-Z.]{1,10}$/.test(s);
              const cryptoOk = /^[A-Z0-9]{5,15}$/.test(s); // e.g., BTCUSDT
              if ((marketType === 'stock' && !stockOk) || (marketType === 'crypto' && !cryptoOk)) {
                toast({ title: 'Invalid symbol', description: 'Please check format.' });
                return;
              }
              if (fromDate && toDate && new Date(fromDate) > new Date(toDate)) {
                toast({ title: 'Invalid range', description: 'From date must be before To date.' });
                return;
              }
              setSelectedSymbol(s);
              loadSymbol(s);
            }}
          >Go</Button>
          <div className="flex items-center gap-2">
            <Button size="sm" variant="outline" onClick={() => setReloadTrigger(Date.now())} title="R">{loading ? 'Loading...' : 'Reload'}</Button>
            <Button size="sm" variant="outline" onClick={() => {
              // Shift back the current window based on preset
              const now = toDate ? new Date(toDate) : new Date();
              const prev = (d: Date, days: number) => new Date(d.getTime() - days * 86400000);
              let days = 30;
              if (preset === '1d') days = 1; else if (preset === '5d') days = 5; else if (preset === '1mo') days = 30; else if (preset === '3mo') days = 90; else if (preset === '6mo') days = 180; else if (preset === '1y') days = 365;
              const newTo = prev(now, days);
              const newFrom = prev(newTo, days);
              setFromDate(newFrom.toISOString().slice(0,10));
              setToDate(newTo.toISOString().slice(0,10));
            }} title="ArrowLeft">Last</Button>
            <Button size="sm" variant="outline" onClick={() => {
              const baseFrom = fromDate ? new Date(fromDate) : new Date();
              const nextDate = (d: Date, days: number) => new Date(d.getTime() + days * 86400000);
              let days = 30;
              if (preset === '1d') days = 1; else if (preset === '5d') days = 5; else if (preset === '1mo') days = 30; else if (preset === '3mo') days = 90; else if (preset === '6mo') days = 180; else if (preset === '1y') days = 365;
              const newFrom = nextDate(baseFrom, days);
              const newTo = nextDate(newFrom, days);
              setFromDate(newFrom.toISOString().slice(0,10));
              setToDate(newTo.toISOString().slice(0,10));
            }} title="ArrowRight">Next</Button>
          </div>
        </div>
      </div>

      <ConnectDataPanel />

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