"use client";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ConnectDataPanel } from '@/components/dashboard/connect-data-panel';

type Order = {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  order_type: 'market' | 'limit' | 'stop' | 'stop_limit';
  price?: number;
  stop_price?: number;
  status: 'pending' | 'filled' | 'cancelled' | 'rejected';
  created_at: string;
  filled_at?: string;
  filled_price?: number;
  filled_quantity?: number;
};

type OrderForm = {
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  order_type: 'market' | 'limit' | 'stop' | 'stop_limit';
  price: number;
  stop_price: number;
  time_in_force: 'day' | 'gtc' | 'ioc' | 'fok';
};

export default function TradingPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [orderForm, setOrderForm] = useState<OrderForm>({
    symbol: 'AAPL',
    side: 'buy',
    quantity: 100,
    order_type: 'market',
    price: 0,
    stop_price: 0,
    time_in_force: 'day'
  });
  const [currentPrice, setCurrentPrice] = useState<number>(175.50);
  const [loading, setLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [buyingPower, setBuyingPower] = useState(62140.25);
  const [orderAlert, setOrderAlert] = useState<{type: 'success' | 'error', message: string} | null>(null);

  useEffect(() => {
    loadOrders();
    loadCurrentPrice();
  }, [selectedSymbol]);

  const loadOrders = async () => {
    // Mock orders - replace with real API call to /api/trading/orders
    const mockOrders: Order[] = [
      {
        id: '1',
        symbol: 'AAPL',
        side: 'buy',
        quantity: 100,
        order_type: 'limit',
        price: 170.00,
        status: 'pending',
        created_at: new Date().toISOString()
      },
      {
        id: '2',
        symbol: 'MSFT',
        side: 'sell',
        quantity: 50,
        order_type: 'market',
        status: 'filled',
        created_at: new Date(Date.now() - 3600000).toISOString(),
        filled_at: new Date(Date.now() - 3500000).toISOString(),
        filled_price: 285.75,
        filled_quantity: 50
      },
      {
        id: '3',
        symbol: 'TSLA',
        side: 'buy',
        quantity: 25,
        order_type: 'stop_limit',
        price: 200.00,
        stop_price: 195.00,
        status: 'cancelled',
        created_at: new Date(Date.now() - 7200000).toISOString()
      }
    ];
    setOrders(mockOrders);
  };

  const loadCurrentPrice = async () => {
    // Mock price data - replace with real API call
    const prices: {[key: string]: number} = {
      'AAPL': 175.50,
      'MSFT': 285.75,
      'GOOGL': 2950.25,
      'TSLA': 195.80,
      'NVDA': 865.40
    };
    setCurrentPrice(prices[selectedSymbol] || 100);
  };

  const calculateOrderValue = (): number => {
    if (orderForm.order_type === 'market') {
      return currentPrice * orderForm.quantity;
    } else {
      return orderForm.price * orderForm.quantity;
    }
  };

  const placeOrder = async () => {
    setLoading(true);
    setOrderAlert(null);
    
    try {
      // Validate order
      const orderValue = calculateOrderValue();
      if (orderForm.side === 'buy' && orderValue > buyingPower) {
        throw new Error('Insufficient buying power');
      }

      // Mock API call - replace with real API call to /api/trading/order
      const newOrder: Order = {
        id: Date.now().toString(),
        symbol: orderForm.symbol.toUpperCase(),
        side: orderForm.side,
        quantity: orderForm.quantity,
        order_type: orderForm.order_type,
        price: orderForm.order_type !== 'market' ? orderForm.price : undefined,
        stop_price: orderForm.order_type.includes('stop') ? orderForm.stop_price : undefined,
        status: 'pending',
        created_at: new Date().toISOString()
      };

      // Simulate order processing
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (orderForm.order_type === 'market') {
        newOrder.status = 'filled';
        newOrder.filled_at = new Date().toISOString();
        newOrder.filled_price = currentPrice;
        newOrder.filled_quantity = orderForm.quantity;
      }

      setOrders(prev => [newOrder, ...prev]);
      setOrderAlert({ type: 'success', message: 'Order placed successfully!' });
      
      // Reset form
      setOrderForm({
        symbol: orderForm.symbol,
        side: 'buy',
        quantity: 100,
        order_type: 'market',
        price: 0,
        stop_price: 0,
        time_in_force: 'day'
      });

    } catch (error: any) {
      setOrderAlert({ type: 'error', message: error.message });
    } finally {
      setLoading(false);
    }
  };

  const cancelOrder = async (orderId: string) => {
    setLoading(true);
    try {
      // Mock API call - replace with real API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setOrders(prev => 
        prev.map(order => 
          order.id === orderId 
            ? { ...order, status: 'cancelled' as const }
            : order
        )
      );
      
      setOrderAlert({ type: 'success', message: 'Order cancelled successfully!' });
    } catch (error: any) {
      setOrderAlert({ type: 'error', message: 'Failed to cancel order' });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'filled': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'cancelled': return 'bg-gray-100 text-gray-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  const pendingOrders = orders.filter(o => o.status === 'pending');
  const recentOrders = orders.filter(o => o.status === 'filled').slice(0, 5);

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">💰 Trading Execution</h1>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-sm text-gray-600">Buying Power</div>
            <div className="text-xl font-bold">${buyingPower.toLocaleString()}</div>
          </div>
          <Button onClick={loadOrders} disabled={loading}>
            {loading ? 'Refreshing...' : '🔄 Refresh'}
          </Button>
        </div>
      </div>

      <ConnectDataPanel />

      {orderAlert && (
        <Alert className={`border-l-4 ${
          orderAlert.type === 'success' ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'
        }`}>
          <AlertDescription>{orderAlert.message}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Order Entry Form */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>📊 Place Order</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Symbol & Side */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1">Symbol</label>
                  <Input
                    value={orderForm.symbol}
                    onChange={(e) => setOrderForm({...orderForm, symbol: e.target.value.toUpperCase()})}
                    placeholder="AAPL"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Side</label>
                  <select
                    value={orderForm.side}
                    onChange={(e) => setOrderForm({...orderForm, side: e.target.value as any})}
                    className="w-full p-2 border rounded"
                  >
                    <option value="buy">Buy</option>
                    <option value="sell">Sell</option>
                  </select>
                </div>
              </div>

              {/* Current Price Display */}
              <div className="p-3 bg-blue-50 rounded border">
                <div className="text-sm text-blue-600">Current Price</div>
                <div className="text-2xl font-bold text-blue-800">${currentPrice.toFixed(2)}</div>
              </div>

              {/* Quantity & Order Type */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1">Quantity</label>
                  <Input
                    type="number"
                    value={orderForm.quantity}
                    onChange={(e) => setOrderForm({...orderForm, quantity: Number(e.target.value)})}
                    min="1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Order Type</label>
                  <select
                    value={orderForm.order_type}
                    onChange={(e) => setOrderForm({...orderForm, order_type: e.target.value as any})}
                    className="w-full p-2 border rounded"
                  >
                    <option value="market">Market</option>
                    <option value="limit">Limit</option>
                    <option value="stop">Stop</option>
                    <option value="stop_limit">Stop Limit</option>
                  </select>
                </div>
              </div>

              {/* Price Fields */}
              {orderForm.order_type !== 'market' && (
                <div>
                  <label className="block text-sm font-medium mb-1">Limit Price</label>
                  <Input
                    type="number"
                    step="0.01"
                    value={orderForm.price}
                    onChange={(e) => setOrderForm({...orderForm, price: Number(e.target.value)})}
                  />
                </div>
              )}

              {orderForm.order_type.includes('stop') && (
                <div>
                  <label className="block text-sm font-medium mb-1">Stop Price</label>
                  <Input
                    type="number"
                    step="0.01"
                    value={orderForm.stop_price}
                    onChange={(e) => setOrderForm({...orderForm, stop_price: Number(e.target.value)})}
                  />
                </div>
              )}

              {/* Time in Force */}
              <div>
                <label className="block text-sm font-medium mb-1">Time in Force</label>
                <select
                  value={orderForm.time_in_force}
                  onChange={(e) => setOrderForm({...orderForm, time_in_force: e.target.value as any})}
                  className="w-full p-2 border rounded"
                >
                  <option value="day">Day</option>
                  <option value="gtc">Good Till Cancelled</option>
                  <option value="ioc">Immediate or Cancel</option>
                  <option value="fok">Fill or Kill</option>
                </select>
              </div>

              {/* Order Summary */}
              <div className="p-3 bg-gray-50 rounded border">
                <div className="text-sm font-medium mb-2">Order Summary</div>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>Estimated Value:</span>
                    <span className="font-bold">${calculateOrderValue().toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Available:</span>
                    <span>${buyingPower.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Place Order Button */}
              <Button 
                onClick={placeOrder} 
                disabled={loading || (orderForm.side === 'buy' && calculateOrderValue() > buyingPower)}
                className={`w-full ${orderForm.side === 'buy' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}`}
              >
                {loading ? 'Placing...' : `${orderForm.side.toUpperCase()} ${orderForm.symbol}`}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Orders List */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>📋 Orders & Executions</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="pending">
              <TabsList>
                <TabsTrigger value="pending">Pending ({pendingOrders.length})</TabsTrigger>
                <TabsTrigger value="recent">Recent Fills</TabsTrigger>
                <TabsTrigger value="all">All Orders</TabsTrigger>
              </TabsList>
              
              <TabsContent value="pending" className="mt-4">
                {pendingOrders.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No pending orders
                  </div>
                ) : (
                  <div className="space-y-3">
                    {pendingOrders.map((order) => (
                      <div key={order.id} className="p-4 border rounded bg-yellow-50">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-semibold text-lg">
                              {order.side.toUpperCase()} {order.quantity} {order.symbol}
                            </div>
                            <div className="text-sm text-gray-600">
                              {order.order_type.toUpperCase()} 
                              {order.price && ` @ $${order.price.toFixed(2)}`}
                              {order.stop_price && ` (Stop: $${order.stop_price.toFixed(2)})`}
                            </div>
                            <div className="text-xs text-gray-500">
                              Created: {new Date(order.created_at).toLocaleString()}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge className={getStatusColor(order.status)}>
                              {order.status.toUpperCase()}
                            </Badge>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => cancelOrder(order.id)}
                              disabled={loading}
                            >
                              Cancel
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="recent" className="mt-4">
                <div className="space-y-3">
                  {recentOrders.map((order) => (
                    <div key={order.id} className="p-4 border rounded bg-green-50">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-semibold text-lg">
                            {order.side.toUpperCase()} {order.filled_quantity || order.quantity} {order.symbol}
                          </div>
                          <div className="text-sm text-gray-600">
                            Filled @ ${order.filled_price?.toFixed(2)}
                          </div>
                          <div className="text-xs text-gray-500">
                            {order.filled_at && new Date(order.filled_at).toLocaleString()}
                          </div>
                        </div>
                        <Badge className={getStatusColor(order.status)}>
                          FILLED
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </TabsContent>
              
              <TabsContent value="all" className="mt-4">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left text-gray-500">
                        <th className="pb-2">Symbol</th>
                        <th className="pb-2">Side</th>
                        <th className="pb-2">Quantity</th>
                        <th className="pb-2">Type</th>
                        <th className="pb-2">Price</th>
                        <th className="pb-2">Status</th>
                        <th className="pb-2">Created</th>
                      </tr>
                    </thead>
                    <tbody>
                      {orders.map((order) => (
                        <tr key={order.id} className="border-b">
                          <td className="py-2 font-semibold">{order.symbol}</td>
                          <td className={`py-2 ${order.side === 'buy' ? 'text-green-600' : 'text-red-600'}`}>
                            {order.side.toUpperCase()}
                          </td>
                          <td className="py-2">{order.quantity}</td>
                          <td className="py-2">{order.order_type.toUpperCase()}</td>
                          <td className="py-2">
                            {order.price ? `$${order.price.toFixed(2)}` : 'Market'}
                          </td>
                          <td className="py-2">
                            <Badge className={getStatusColor(order.status)}>
                              {order.status.toUpperCase()}
                            </Badge>
                          </td>
                          <td className="py-2 text-gray-500">
                            {new Date(order.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>⚡ Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['AAPL', 'MSFT', 'GOOGL', 'TSLA'].map((symbol) => (
              <Button
                key={symbol}
                variant="outline"
                className="h-auto p-4 flex flex-col space-y-2"
                onClick={() => setOrderForm({...orderForm, symbol})}
              >
                <span className="font-bold text-lg">{symbol}</span>
                <span className="text-sm text-gray-500">Quick Order</span>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}