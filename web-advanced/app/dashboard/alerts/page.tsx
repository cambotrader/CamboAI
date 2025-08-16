"use client";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

type AlertRule = {
  id: string;
  rule: {
    type: string;
    symbol?: string;
    op?: string;
    threshold?: number;
    window?: string;
  };
  active: boolean;
  created_at: string;
};

type AlertFormData = {
  symbol: string;
  type: 'price_cross' | 'percent_move';
  op: '>' | '<' | '>=' | '<=' | '==';
  threshold: number;
  window?: string;
};

export default function AlertsPage() {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [triggered, setTriggered] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<AlertFormData>({
    symbol: 'AAPL',
    type: 'price_cross',
    op: '>',
    threshold: 150,
    window: '1d'
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    try {
      const response = await fetch('/api/alerts/rules');
      if (response.ok) {
        const data = await response.json();
        setRules(data.items || []);
      }
    } catch (error) {
      console.error('Failed to load rules:', error);
    }
  };

  const createRule = async () => {
    setLoading(true);
    try {
      const payload = {
        rule: {
          type: formData.type,
          symbol: formData.symbol.toUpperCase(),
          op: formData.op,
          threshold: formData.threshold,
          ...(formData.type === 'percent_move' && { window: formData.window })
        },
        active: true
      };

      const response = await fetch('/api/alerts/rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        await loadRules();
        setShowForm(false);
        setFormData({ symbol: 'AAPL', type: 'price_cross', op: '>', threshold: 150, window: '1d' });
      }
    } catch (error) {
      console.error('Failed to create rule:', error);
    } finally {
      setLoading(false);
    }
  };

  const runAlerts = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/alerts/run', { method: 'POST' });
      if (response.ok) {
        const data = await response.json();
        setTriggered(data.triggered || []);
      }
    } catch (error) {
      console.error('Failed to run alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">🔔 Smart Alerts</h1>
        <div className="space-x-2">
          <Button onClick={runAlerts} disabled={loading}>
            {loading ? 'Running...' : 'Run Alerts'}
          </Button>
          <Button onClick={() => setShowForm(!showForm)} variant="outline">
            {showForm ? 'Cancel' : '+ New Alert'}
          </Button>
        </div>
      </div>

      {/* Triggered Alerts */}
      {triggered.length > 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="text-orange-800">🚨 Triggered Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {triggered.map((alert, i) => (
                <div key={i} className="p-3 bg-white rounded border border-orange-200">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-orange-900">{alert.symbol}</span>
                    <Badge variant="destructive">{alert.type}</Badge>
                  </div>
                  <div className="text-sm text-orange-700 mt-1">
                    Price: ${alert.price?.toFixed(2)} 
                    {alert.pct && ` (${alert.pct > 0 ? '+' : ''}${alert.pct.toFixed(2)}%)`}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create New Alert Form */}
      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Alert</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Symbol</label>
                <input
                  type="text"
                  value={formData.symbol}
                  onChange={(e) => setFormData({...formData, symbol: e.target.value})}
                  className="w-full p-2 border rounded"
                  placeholder="AAPL"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Alert Type</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({...formData, type: e.target.value as any})}
                  className="w-full p-2 border rounded"
                >
                  <option value="price_cross">Price Cross</option>
                  <option value="percent_move">Percent Move</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Operator</label>
                <select
                  value={formData.op}
                  onChange={(e) => setFormData({...formData, op: e.target.value as any})}
                  className="w-full p-2 border rounded"
                >
                  <option value=">">Greater than</option>
                  <option value="<">Less than</option>
                  <option value=">=">Greater or equal</option>
                  <option value="<=">Less or equal</option>
                  <option value="==">Equal to</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  {formData.type === 'price_cross' ? 'Price Threshold' : 'Percent Threshold'}
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.threshold}
                  onChange={(e) => setFormData({...formData, threshold: parseFloat(e.target.value)})}
                  className="w-full p-2 border rounded"
                />
              </div>
              {formData.type === 'percent_move' && (
                <div>
                  <label className="block text-sm font-medium mb-1">Time Window</label>
                  <select
                    value={formData.window}
                    onChange={(e) => setFormData({...formData, window: e.target.value})}
                    className="w-full p-2 border rounded"
                  >
                    <option value="1h">1 Hour</option>
                    <option value="4h">4 Hours</option>
                    <option value="1d">1 Day</option>
                    <option value="7d">7 Days</option>
                  </select>
                </div>
              )}
            </div>
            <div className="mt-4">
              <Button onClick={createRule} disabled={loading} className="w-full">
                {loading ? 'Creating...' : 'Create Alert'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Active Rules */}
      <Card>
        <CardHeader>
          <CardTitle>Active Alert Rules ({rules.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {rules.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No alert rules configured</p>
          ) : (
            <div className="space-y-3">
              {rules.map((rule) => (
                <div key={rule.id} className="p-4 border rounded bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold text-lg">{rule.rule.symbol}</div>
                      <div className="text-sm text-gray-600">
                        {rule.rule.type === 'price_cross' ? 'Price' : 'Percent'} {rule.rule.op} {rule.rule.threshold}
                        {rule.rule.type === 'percent_move' && ` over ${rule.rule.window}`}
                      </div>
                      <div className="text-xs text-gray-400 mt-1">
                        Created: {new Date(rule.created_at).toLocaleString()}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant={rule.active ? 'default' : 'secondary'}>
                        {rule.active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}