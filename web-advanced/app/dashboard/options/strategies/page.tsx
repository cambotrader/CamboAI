"use client";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { priceMultiLeg, deltaHedgeBacktest } from '@/lib/api/client';
import dynamic from 'next/dynamic';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

type OptionLeg = {
  right: 'call' | 'put';
  side: 'long' | 'short';
  qty: number;
  strike: number;
  expiry: number;
  vol: number;
  rate: number;
  div_yield: number;
  spot: number;
};

type Strategy = {
  name: string;
  description: string;
  outlook: 'bullish' | 'bearish' | 'neutral' | 'volatile';
  legs: Partial<OptionLeg>[];
};

const STRATEGIES: Strategy[] = [
  {
    name: 'Bull Call Spread',
    description: 'Buy low strike call, sell high strike call',
    outlook: 'bullish',
    legs: [
      { right: 'call', side: 'long', qty: 1, strike: 100 },
      { right: 'call', side: 'short', qty: 1, strike: 110 }
    ]
  },
  {
    name: 'Iron Condor',
    description: 'Sell OTM put spread and call spread',
    outlook: 'neutral',
    legs: [
      { right: 'put', side: 'long', qty: 1, strike: 90 },
      { right: 'put', side: 'short', qty: 1, strike: 95 },
      { right: 'call', side: 'short', qty: 1, strike: 105 },
      { right: 'call', side: 'long', qty: 1, strike: 110 }
    ]
  },
  {
    name: 'Long Straddle',
    description: 'Buy call and put at same strike',
    outlook: 'volatile',
    legs: [
      { right: 'call', side: 'long', qty: 1, strike: 100 },
      { right: 'put', side: 'long', qty: 1, strike: 100 }
    ]
  },
  {
    name: 'Covered Call',
    description: 'Own stock, sell call option',
    outlook: 'neutral',
    legs: [
      { right: 'call', side: 'short', qty: 1, strike: 105 }
    ]
  }
];

export default function StrategiesPage() {
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy>(STRATEGIES[0]);
  const [marketData, setMarketData] = useState({
    spot: 100,
    vol: 0.25,
    rate: 0.05,
    expiry: 0.25 // 3 months
  });
  const [result, setResult] = useState<any>(null);
  const [hedgeResult, setHedgeResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    priceStrategy();
  }, [selectedStrategy, marketData]);

  const priceStrategy = async () => {
    setLoading(true);
    try {
      const legs = selectedStrategy.legs.map(leg => ({
        right: leg.right || 'call',
        side: leg.side || 'long',
        qty: leg.qty || 1,
        strike: leg.strike || marketData.spot,
        expiry: marketData.expiry,
        vol: marketData.vol,
        rate: marketData.rate,
        div_yield: 0,
        spot: marketData.spot
      }));

      const response = await priceMultiLeg({
        preset: 'balanced',
        legs
      });

      setResult(response);
    } catch (error) {
      console.error('Pricing failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const runHedgeBacktest = async () => {
    setLoading(true);
    try {
      const response = await deltaHedgeBacktest({
        spot: marketData.spot,
        vol: marketData.vol,
        rate: marketData.rate,
        t: marketData.expiry,
        strike: selectedStrategy.legs[0]?.strike || marketData.spot,
        right: selectedStrategy.legs[0]?.right || 'call',
        hedging_dt: 1/252,
        mu: 0.08,
        transaction_bps: 5
      });
      setHedgeResult(response);
    } catch (error) {
      console.error('Hedge backtest failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const generatePayoffChart = () => {
    if (!result) return null;

    const spots = Array.from({length: 50}, (_, i) => 80 + i * 2);
    const payoffs = spots.map(spot => {
      let totalPayoff = 0;
      selectedStrategy.legs.forEach((leg, i) => {
        const strike = leg.strike || marketData.spot;
        const qty = leg.qty || 1;
        const side = leg.side || 'long';
        const right = leg.right || 'call';
        
        let intrinsic = 0;
        if (right === 'call') {
          intrinsic = Math.max(0, spot - strike);
        } else {
          intrinsic = Math.max(0, strike - spot);
        }
        
        const legPayoff = intrinsic * qty * (side === 'long' ? 1 : -1);
        totalPayoff += legPayoff;
      });
      
      // Subtract premium paid/received
      if (result.price) {
        totalPayoff -= result.price;
      }
      
      return totalPayoff;
    });

    return {
      data: [
        {
          x: spots,
          y: payoffs,
          type: 'scatter',
          mode: 'lines',
          name: selectedStrategy.name,
          line: { color: '#3B82F6', width: 3 }
        },
        {
          x: spots,
          y: spots.map(() => 0),
          type: 'scatter',
          mode: 'lines',
          name: 'Break Even',
          line: { color: '#9CA3AF', width: 1, dash: 'dash' }
        }
      ],
      layout: {
        title: `${selectedStrategy.name} - Profit/Loss at Expiration`,
        xaxis: { title: 'Underlying Price ($)' },
        yaxis: { title: 'Profit/Loss ($)' },
        showlegend: true,
        height: 400,
        plot_bgcolor: '#F9FAFB',
        paper_bgcolor: '#FFFFFF'
      }
    };
  };

  const chartData = generatePayoffChart();

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">💼 Options Strategies</h1>
        <Button onClick={runHedgeBacktest} disabled={loading}>
          🛡️ Run Delta Hedge Test
        </Button>
      </div>

      {/* Strategy Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Select Strategy</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {STRATEGIES.map((strategy) => (
              <Card 
                key={strategy.name}
                className={`cursor-pointer border-2 transition-all ${
                  selectedStrategy.name === strategy.name 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedStrategy(strategy)}
              >
                <CardContent className="p-4">
                  <div className="font-semibold text-sm">{strategy.name}</div>
                  <div className="text-xs text-gray-600 mt-1">{strategy.description}</div>
                  <Badge 
                    variant={strategy.outlook === 'bullish' ? 'default' : 
                            strategy.outlook === 'bearish' ? 'destructive' :
                            strategy.outlook === 'volatile' ? 'secondary' : 'outline'}
                    className="mt-2 text-xs"
                  >
                    {strategy.outlook}
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Market Parameters */}
        <Card>
          <CardHeader>
            <CardTitle>Market Parameters</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Spot Price</label>
              <input
                type="number"
                value={marketData.spot}
                onChange={(e) => setMarketData({...marketData, spot: Number(e.target.value)})}
                className="w-full p-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Volatility</label>
              <input
                type="number"
                step="0.01"
                value={marketData.vol}
                onChange={(e) => setMarketData({...marketData, vol: Number(e.target.value)})}
                className="w-full p-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Risk-free Rate</label>
              <input
                type="number"
                step="0.001"
                value={marketData.rate}
                onChange={(e) => setMarketData({...marketData, rate: Number(e.target.value)})}
                className="w-full p-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Time to Expiry (years)</label>
              <select
                value={marketData.expiry}
                onChange={(e) => setMarketData({...marketData, expiry: Number(e.target.value)})}
                className="w-full p-2 border rounded"
              >
                <option value={0.083}>1 Month</option>
                <option value={0.25}>3 Months</option>
                <option value={0.5}>6 Months</option>
                <option value={1.0}>1 Year</option>
              </select>
            </div>
            <Button onClick={priceStrategy} className="w-full" disabled={loading}>
              {loading ? 'Calculating...' : '🔄 Update Pricing'}
            </Button>
          </CardContent>
        </Card>

        {/* Strategy Details */}
        <Card>
          <CardHeader>
            <CardTitle>Strategy Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            {result ? (
              <div className="space-y-4">
                <div>
                  <div className="text-2xl font-bold">
                    ${result.price?.toFixed(2)}
                    <span className="text-sm font-normal text-gray-500 ml-2">Net Premium</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-gray-600">Delta</div>
                    <div className="font-semibold">{result.greeks?.delta?.toFixed(3)}</div>
                  </div>
                  <div>
                    <div className="text-gray-600">Gamma</div>
                    <div className="font-semibold">{result.greeks?.gamma?.toFixed(3)}</div>
                  </div>
                  <div>
                    <div className="text-gray-600">Theta</div>
                    <div className="font-semibold">{result.greeks?.theta?.toFixed(2)}</div>
                  </div>
                  <div>
                    <div className="text-gray-600">Vega</div>
                    <div className="font-semibold">{result.greeks?.vega?.toFixed(2)}</div>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <div className="text-sm font-medium mb-2">Individual Legs:</div>
                  {result.legs?.map((leg: any, i: number) => (
                    <div key={i} className="text-xs bg-gray-50 p-2 rounded mb-2">
                      <div className="font-semibold">
                        {leg.input.side.toUpperCase()} {leg.input.right.toUpperCase()} @${leg.input.strike}
                      </div>
                      <div>Price: ${leg.price.toFixed(2)} | Signed: ${leg.signed_price.toFixed(2)}</div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                Configure parameters and click Update Pricing
              </div>
            )}
          </CardContent>
        </Card>

        {/* Risk Metrics */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            {hedgeResult ? (
              <div className="space-y-3">
                <div className="text-lg font-semibold text-center">
                  Delta Hedge Results
                </div>
                <div className="grid grid-cols-1 gap-3 text-sm">
                  <div className="flex justify-between">
                    <span>Final Underlying:</span>
                    <span className="font-semibold">${hedgeResult.final_underlying?.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Option Payoff:</span>
                    <span className="font-semibold">${hedgeResult.option_payoff?.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Stock P&L:</span>
                    <span className={`font-semibold ${hedgeResult.stock_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ${hedgeResult.stock_pnl?.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Transaction Costs:</span>
                    <span className="font-semibold text-red-600">${hedgeResult.transaction_costs?.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t">
                    <span>Total P&L:</span>
                    <span className={`font-bold text-lg ${hedgeResult.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ${hedgeResult.total_pnl?.toFixed(2)}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 text-center">
                    Hedged over {hedgeResult.steps} time steps
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-gray-500 mb-4">Run delta hedge backtest to see risk metrics</div>
                <div className="text-xs text-gray-400">
                  Simulates hedge performance over time with transaction costs
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Payoff Chart */}
      {chartData && (
        <Card>
          <CardHeader>
            <CardTitle>Strategy Payoff Diagram</CardTitle>
          </CardHeader>
          <CardContent>
            <Plot
              data={chartData.data}
              layout={chartData.layout}
              style={{ width: '100%', height: '400px' }}
              config={{ displayModeBar: true, responsive: true }}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}