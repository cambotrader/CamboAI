"use client";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import dynamic from 'next/dynamic';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

type RiskMetrics = {
  var_95: number;
  var_99: number;
  expected_shortfall: number;
  max_drawdown: number;
  volatility: number;
  beta: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  calmar_ratio: number;
  risk_score: number;
};

type RiskAlert = {
  id: string;
  type: 'warning' | 'danger' | 'info';
  title: string;
  message: string;
  recommendation: string;
};

export default function RiskPage() {
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null);
  const [alerts, setAlerts] = useState<RiskAlert[]>([]);
  const [correlationMatrix, setCorrelationMatrix] = useState<any>(null);
  const [stressTest, setStressTest] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [analysisType, setAnalysisType] = useState<'portfolio' | 'individual'>('portfolio');

  useEffect(() => {
    loadRiskAnalysis();
  }, [analysisType]);

  const loadRiskAnalysis = async () => {
    setLoading(true);
    try {
      // Mock API call - replace with real API to /api/risk/portfolio/analysis
      await Promise.all([
        loadRiskMetrics(),
        loadRiskAlerts(),
        loadCorrelationMatrix(),
        loadStressTestResults()
      ]);
    } catch (error) {
      console.error('Failed to load risk analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRiskMetrics = async () => {
    // Mock risk metrics
    setRiskMetrics({
      var_95: -12500,  // 95% VaR
      var_99: -18750,  // 99% VaR
      expected_shortfall: -22100,  // Expected Shortfall (CVaR)
      max_drawdown: -15.8,  // Maximum Drawdown %
      volatility: 18.5,  // Annualized volatility %
      beta: 1.15,  // Portfolio beta vs market
      sharpe_ratio: 1.42,  // Risk-adjusted return
      sortino_ratio: 2.18,  // Downside risk-adjusted return
      calmar_ratio: 0.89,  // Return/Max Drawdown
      risk_score: 72  // Overall risk score (0-100)
    });
  };

  const loadRiskAlerts = async () => {
    const mockAlerts: RiskAlert[] = [
      {
        id: '1',
        type: 'warning',
        title: 'High Concentration Risk',
        message: 'GOOGL position represents 35% of portfolio value',
        recommendation: 'Consider reducing position size to below 25% of portfolio'
      },
      {
        id: '2',
        type: 'danger',
        title: 'Elevated VaR',
        message: '99% VaR exceeds risk tolerance threshold',
        recommendation: 'Reduce leverage or add hedging positions'
      },
      {
        id: '3',
        type: 'info',
        title: 'Low Diversification',
        message: 'Portfolio concentrated in technology sector (78%)',
        recommendation: 'Add positions in other sectors for better diversification'
      }
    ];
    setAlerts(mockAlerts);
  };

  const loadCorrelationMatrix = async () => {
    // Mock correlation data
    const symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA'];
    const correlations = [
      [1.00, 0.65, 0.72, 0.48],
      [0.65, 1.00, 0.58, 0.42],
      [0.72, 0.58, 1.00, 0.51],
      [0.48, 0.42, 0.51, 1.00]
    ];

    setCorrelationMatrix({
      data: [{
        z: correlations,
        x: symbols,
        y: symbols,
        type: 'heatmap',
        colorscale: 'RdYlBu',
        reversescale: true,
        zmin: -1,
        zmax: 1,
        text: correlations.map(row => 
          row.map(val => val.toFixed(2))
        ),
        texttemplate: '%{text}',
        textfont: { color: 'white', size: 12 }
      }],
      layout: {
        title: 'Position Correlation Matrix',
        height: 400,
        xaxis: { title: 'Symbols' },
        yaxis: { title: 'Symbols' },
        plot_bgcolor: '#FFFFFF',
        paper_bgcolor: '#FFFFFF'
      }
    });
  };

  const loadStressTestResults = async () => {
    // Mock stress test scenarios
    const scenarios = ['Market Crash (-30%)', 'Tech Selloff (-40%)', 'Interest Rate Spike', 'VIX > 40'];
    const impacts = [-25400, -31200, -8900, -18500];

    setStressTest({
      data: [{
        x: scenarios,
        y: impacts,
        type: 'bar',
        marker: {
          color: impacts.map(val => val < -20000 ? '#EF4444' : val < -15000 ? '#F59E0B' : '#10B981')
        }
      }],
      layout: {
        title: 'Stress Test Results',
        xaxis: { title: 'Scenario' },
        yaxis: { title: 'Portfolio Impact ($)' },
        height: 400,
        plot_bgcolor: '#F9FAFB',
        paper_bgcolor: '#FFFFFF'
      }
    });
  };

  const getRiskScoreColor = (score: number) => {
    if (score >= 80) return 'text-red-600 bg-red-50';
    if (score >= 60) return 'text-orange-600 bg-orange-50';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  const getRiskScoreLabel = (score: number) => {
    if (score >= 80) return 'High Risk';
    if (score >= 60) return 'Medium-High Risk';
    if (score >= 40) return 'Medium Risk';
    return 'Low Risk';
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">⚠️ Risk Management</h1>
        <div className="flex space-x-2">
          <Button
            variant={analysisType === 'portfolio' ? 'default' : 'outline'}
            onClick={() => setAnalysisType('portfolio')}
            size="sm"
          >
            Portfolio Risk
          </Button>
          <Button
            variant={analysisType === 'individual' ? 'default' : 'outline'}
            onClick={() => setAnalysisType('individual')}
            size="sm"
          >
            Position Risk
          </Button>
          <Button onClick={loadRiskAnalysis} disabled={loading}>
            {loading ? 'Updating...' : '🔄 Refresh'}
          </Button>
        </div>
      </div>

      {/* Risk Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <Alert key={alert.id} className={`border-l-4 ${
              alert.type === 'danger' ? 'border-red-500 bg-red-50' :
              alert.type === 'warning' ? 'border-orange-500 bg-orange-50' :
              'border-blue-500 bg-blue-50'
            }`}>
              <AlertDescription>
                <div className="font-semibold">{alert.title}</div>
                <div className="text-sm mt-1">{alert.message}</div>
                <div className="text-xs text-gray-600 mt-2">💡 {alert.recommendation}</div>
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {/* Risk Metrics Dashboard */}
      {riskMetrics && (
        <>
          {/* Risk Score & Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className={`border-2 ${getRiskScoreColor(riskMetrics.risk_score)}`}>
              <CardHeader>
                <CardTitle className="text-center">Overall Risk Score</CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <div className="text-6xl font-bold mb-2">{riskMetrics.risk_score}</div>
                <div className="text-lg font-semibold">{getRiskScoreLabel(riskMetrics.risk_score)}</div>
                <Progress value={riskMetrics.risk_score} className="mt-4" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Value at Risk (VaR)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>95% VaR (1 day):</span>
                    <span className="font-bold text-red-600">${riskMetrics.var_95.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>99% VaR (1 day):</span>
                    <span className="font-bold text-red-700">${riskMetrics.var_99.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between border-t pt-2">
                    <span>Expected Shortfall:</span>
                    <span className="font-bold text-red-800">${riskMetrics.expected_shortfall.toLocaleString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Risk-Adjusted Returns</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Sharpe Ratio:</span>
                    <span className="font-bold">{riskMetrics.sharpe_ratio.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Sortino Ratio:</span>
                    <span className="font-bold">{riskMetrics.sortino_ratio.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Calmar Ratio:</span>
                    <span className="font-bold">{riskMetrics.calmar_ratio.toFixed(2)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Risk Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-600">Max Drawdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{riskMetrics.max_drawdown}%</div>
                <p className="text-xs text-gray-500">Peak-to-trough decline</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-600">Volatility</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{riskMetrics.volatility}%</div>
                <p className="text-xs text-gray-500">Annualized</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-600">Portfolio Beta</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{riskMetrics.beta}</div>
                <p className="text-xs text-gray-500">vs S&P 500</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-600">Risk Level</CardTitle>
              </CardHeader>
              <CardContent>
                <Badge className={getRiskScoreColor(riskMetrics.risk_score)}>
                  {getRiskScoreLabel(riskMetrics.risk_score)}
                </Badge>
                <p className="text-xs text-gray-500 mt-1">Composite score</p>
              </CardContent>
            </Card>
          </div>
        </>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Correlation Matrix */}
        {correlationMatrix && (
          <Card>
            <CardHeader>
              <CardTitle>Position Correlations</CardTitle>
            </CardHeader>
            <CardContent>
              <Plot
                data={correlationMatrix.data}
                layout={correlationMatrix.layout}
                style={{ width: '100%', height: '400px' }}
                config={{ displayModeBar: false, responsive: true }}
              />
            </CardContent>
          </Card>
        )}

        {/* Stress Test Results */}
        {stressTest && (
          <Card>
            <CardHeader>
              <CardTitle>Stress Test Scenarios</CardTitle>
            </CardHeader>
            <CardContent>
              <Plot
                data={stressTest.data}
                layout={stressTest.layout}
                style={{ width: '100%', height: '400px' }}
                config={{ displayModeBar: false, responsive: true }}
              />
            </CardContent>
          </Card>
        )}
      </div>

      {/* Risk Management Actions */}
      <Card>
        <CardHeader>
          <CardTitle>🛡️ Risk Management Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="h-auto p-4 flex flex-col space-y-2">
              <span className="text-2xl">🔄</span>
              <span className="font-semibold">Rebalance Portfolio</span>
              <span className="text-xs text-gray-500">Adjust position sizes</span>
            </Button>
            <Button variant="outline" className="h-auto p-4 flex flex-col space-y-2">
              <span className="text-2xl">🛡️</span>
              <span className="font-semibold">Add Hedge</span>
              <span className="text-xs text-gray-500">VIX calls, Put protection</span>
            </Button>
            <Button variant="outline" className="h-auto p-4 flex flex-col space-y-2">
              <span className="text-2xl">📊</span>
              <span className="font-semibold">Diversify</span>
              <span className="text-xs text-gray-500">Add uncorrelated assets</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}