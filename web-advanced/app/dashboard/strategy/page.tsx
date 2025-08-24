"use client";
import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ConnectDataPanel } from '@/components/dashboard/connect-data-panel';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

type Rule = {
  id: string;
  type: 'ma_cross' | 'rsi_threshold' | 'price_breakout';
  params: Record<string, number | string>;
};

export default function StrategyPage() {
  const [rules, setRules] = useState<Rule[]>([
    { id: '1', type: 'ma_cross', params: { fast: 50, slow: 200 } },
  ]);
  const [results, setResults] = useState<any | null>(null);

  const addRule = () => {
    setRules((r) => [
      ...r,
      { id: Date.now().toString(), type: 'rsi_threshold', params: { period: 14, overbought: 70, oversold: 30 } },
    ]);
  };

  const runBacktest = async () => {
    // Demo backtest output (replace with backend call)
    const equity = Array.from({ length: 120 }, (_, i) => 100000 + i * 250 + Math.sin(i / 6) * 800);
    const trades = 24;
    const winRate = 0.62;
    const sharpe = 1.45;
    const maxDD = -0.11;

    setResults({ equity, trades, winRate, sharpe, maxDD });
  };

  const chart = results
    ? {
        data: [
          {
            x: Array.from({ length: results.equity.length }, (_, i) => i + 1),
            y: results.equity,
            type: 'scatter',
            mode: 'lines',
            name: 'Equity Curve',
            line: { color: '#10B981', width: 2 },
          },
        ],
        layout: {
          title: 'Backtest Equity Curve',
          xaxis: { title: 'Bars' },
          yaxis: { title: 'Equity ($)' },
          height: 420,
          showlegend: false,
          plot_bgcolor: '#F9FAFB',
          paper_bgcolor: '#FFFFFF',
        },
      }
    : null;

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">🧪 Strategy Builder & Backtesting</h1>
        <div className="space-x-2">
          <Button onClick={addRule} variant="outline">+ Add Rule</Button>
          <Button onClick={runBacktest}>▶ Run Backtest</Button>
        </div>
      </div>

      <ConnectDataPanel />

      <Tabs defaultValue="builder" className="space-y-6">
        <TabsList>
          <TabsTrigger value="builder">Builder</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
        </TabsList>

        <TabsContent value="builder" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Rules</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {rules.map((rule) => (
                  <div key={rule.id} className="p-3 border rounded bg-gray-50 flex items-center justify-between">
                    <div>
                      <div className="font-semibold">{rule.type}</div>
                      <div className="text-xs text-gray-600">{JSON.stringify(rule.params)}</div>
                    </div>
                    <Button size="sm" variant="outline" onClick={() => setRules((r) => r.filter((x) => x.id !== rule.id))}>Remove</Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Parameters</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <input className="p-2 border rounded" placeholder="Symbol (e.g., AAPL)" defaultValue="AAPL" />
                <select className="p-2 border rounded" defaultValue="D">
                  <option value="1">1m</option>
                  <option value="5">5m</option>
                  <option value="60">1h</option>
                  <option value="D">1d</option>
                </select>
                <input className="p-2 border rounded" type="number" placeholder="Start ($)" defaultValue={100000} />
                <select className="p-2 border rounded" defaultValue="long_only">
                  <option value="long_only">Long Only</option>
                  <option value="long_short">Long/Short</option>
                </select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          {!results ? (
            <Card>
              <CardContent className="py-10 text-center text-gray-600">Run a backtest to see results</CardContent>
            </Card>
          ) : (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-sm">Trades</CardTitle></CardHeader>
                  <CardContent><div className="text-2xl font-bold">{results.trades}</div></CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-sm">Win Rate</CardTitle></CardHeader>
                  <CardContent><div className="text-2xl font-bold">{(results.winRate * 100).toFixed(1)}%</div></CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-sm">Sharpe</CardTitle></CardHeader>
                  <CardContent><div className="text-2xl font-bold">{results.sharpe.toFixed(2)}</div></CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-sm">Max Drawdown</CardTitle></CardHeader>
                  <CardContent><div className="text-2xl font-bold text-red-600">{(results.maxDD * 100).toFixed(1)}%</div></CardContent>
                </Card>
              </div>

              {chart && (
                <Card>
                  <CardContent className="pt-6">
                    <Plot data={chart.data} layout={chart.layout} style={{ width: '100%', height: '420px' }} config={{ displayModeBar: true, responsive: true }} />
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}