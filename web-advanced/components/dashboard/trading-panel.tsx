'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Target,
  Zap,
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  Activity,
  Settings,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Switch } from '@/components/ui/switch'

interface Trade {
  id: string
  symbol: string
  side: 'buy' | 'sell'
  quantity: number
  price: number
  status: 'pending' | 'filled' | 'cancelled'
  timestamp: string
  pnl?: number
}

interface Position {
  symbol: string
  quantity: number
  avgPrice: number
  currentPrice: number
  pnl: number
  pnlPercent: number
}

interface Strategy {
  id: string
  name: string
  status: 'active' | 'paused' | 'stopped'
  performance: number
  trades: number
  winRate: number
  description: string
}

const mockTrades: Trade[] = [
  {
    id: '1',
    symbol: 'BTC/USD',
    side: 'buy',
    quantity: 0.1,
    price: 45000,
    status: 'filled',
    timestamp: new Date().toISOString(),
    pnl: 250
  },
  {
    id: '2',
    symbol: 'ETH/USD',
    side: 'sell',
    quantity: 2,
    price: 3200,
    status: 'pending',
    timestamp: new Date(Date.now() - 300000).toISOString()
  },
  {
    id: '3',
    symbol: 'AAPL',
    side: 'buy',
    quantity: 10,
    price: 175,
    status: 'filled',
    timestamp: new Date(Date.now() - 600000).toISOString(),
    pnl: -50
  }
]

const mockPositions: Position[] = [
  {
    symbol: 'BTC/USD',
    quantity: 0.25,
    avgPrice: 44800,
    currentPrice: 45100,
    pnl: 75,
    pnlPercent: 0.67
  },
  {
    symbol: 'ETH/USD',
    quantity: 5,
    avgPrice: 3180,
    currentPrice: 3220,
    pnl: 200,
    pnlPercent: 1.26
  },
  {
    symbol: 'AAPL',
    quantity: 50,
    avgPrice: 176,
    currentPrice: 174,
    pnl: -100,
    pnlPercent: -1.14
  }
]

const mockStrategies: Strategy[] = [
  {
    id: '1',
    name: 'Oracle Vision',
    status: 'active',
    performance: 15.2,
    trades: 45,
    winRate: 68,
    description: 'Bias reveals divergence patterns'
  },
  {
    id: '2',
    name: 'Hunter Momentum',
    status: 'active',
    performance: 8.7,
    trades: 32,
    winRate: 72,
    description: 'Momentum exhaustion detection'
  },
  {
    id: '3',
    name: 'Ghost Arbitrage',
    status: 'paused',
    performance: 22.1,
    trades: 18,
    winRate: 89,
    description: 'Hidden pattern exploitation'
  }
]

export function TradingPanel() {
  const [activeTab, setActiveTab] = useState('manual')
  const [orderType, setOrderType] = useState('market')
  const [side, setSide] = useState<'buy' | 'sell'>('buy')
  const [symbol, setSymbol] = useState('BTC/USD')
  const [quantity, setQuantity] = useState('')
  const [price, setPrice] = useState('')
  const [autoTrading, setAutoTrading] = useState(false)
  const [riskLevel, setRiskLevel] = useState('medium')

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'filled':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />
      case 'cancelled':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      case 'active':
        return <Play className="h-4 w-4 text-green-500" />
      case 'paused':
        return <Pause className="h-4 w-4 text-yellow-500" />
      case 'stopped':
        return <RotateCcw className="h-4 w-4 text-red-500" />
      default:
        return <Activity className="h-4 w-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'filled':
      case 'active':
        return 'bg-green-500/10 text-green-500 border-green-500/20'
      case 'pending':
      case 'paused':
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
      case 'cancelled':
      case 'stopped':
        return 'bg-red-500/10 text-red-500 border-red-500/20'
      default:
        return 'bg-muted'
    }
  }

  const handlePlaceOrder = () => {
    // Order placement logic
    console.log('Placing order:', { symbol, side, quantity, price, orderType })
  }

  return (
    <Card className="cambo-card">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-orange-500" />
              Trading Panel
            </CardTitle>
            <CardDescription>
              Execute trades and manage strategies
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              <Label htmlFor="auto-trading" className="text-sm">Auto Trading</Label>
              <Switch
                id="auto-trading"
                checked={autoTrading}
                onCheckedChange={setAutoTrading}
              />
            </div>
            <Badge variant={autoTrading ? "default" : "secondary"}>
              {autoTrading ? 'ON' : 'OFF'}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="manual">Manual</TabsTrigger>
            <TabsTrigger value="positions">Positions</TabsTrigger>
            <TabsTrigger value="orders">Orders</TabsTrigger>
            <TabsTrigger value="strategies">Strategies</TabsTrigger>
          </TabsList>

          <TabsContent value="manual" className="space-y-4 mt-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="symbol">Symbol</Label>
                  <Select value={symbol} onValueChange={setSymbol}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="BTC/USD">BTC/USD</SelectItem>
                      <SelectItem value="ETH/USD">ETH/USD</SelectItem>
                      <SelectItem value="AAPL">AAPL</SelectItem>
                      <SelectItem value="TSLA">TSLA</SelectItem>
                      <SelectItem value="SPY">SPY</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="order-type">Order Type</Label>
                  <Select value={orderType} onValueChange={setOrderType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="market">Market</SelectItem>
                      <SelectItem value="limit">Limit</SelectItem>
                      <SelectItem value="stop">Stop</SelectItem>
                      <SelectItem value="stop-limit">Stop Limit</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="quantity">Quantity</Label>
                  <Input
                    id="quantity"
                    type="number"
                    placeholder="0.00"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                  />
                </div>

                {orderType !== 'market' && (
                  <div>
                    <Label htmlFor="price">Price</Label>
                    <Input
                      id="price"
                      type="number"
                      placeholder="0.00"
                      value={price}
                      onChange={(e) => setPrice(e.target.value)}
                    />
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div>
                  <Label>Side</Label>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    <Button
                      variant={side === 'buy' ? 'default' : 'outline'}
                      onClick={() => setSide('buy')}
                      className="w-full"
                    >
                      <TrendingUp className="h-4 w-4 mr-2" />
                      Buy
                    </Button>
                    <Button
                      variant={side === 'sell' ? 'default' : 'outline'}
                      onClick={() => setSide('sell')}
                      className="w-full"
                    >
                      <TrendingDown className="h-4 w-4 mr-2" />
                      Sell
                    </Button>
                  </div>
                </div>

                <div>
                  <Label htmlFor="risk-level">Risk Level</Label>
                  <Select value={riskLevel} onValueChange={setRiskLevel}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low Risk</SelectItem>
                      <SelectItem value="medium">Medium Risk</SelectItem>
                      <SelectItem value="high">High Risk</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="pt-4">
                  <Button 
                    onClick={handlePlaceOrder}
                    className="w-full"
                    size="lg"
                    disabled={!quantity}
                  >
                    <Target className="h-4 w-4 mr-2" />
                    Place {side.toUpperCase()} Order
                  </Button>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-muted/30 border">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="h-4 w-4 text-primary" />
                <span className="font-medium">Risk Management</span>
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Max Position Size</p>
                  <p className="font-medium">$10,000</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Daily Loss Limit</p>
                  <p className="font-medium">$500</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Available Balance</p>
                  <p className="font-medium">$25,430</p>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="positions" className="space-y-4 mt-6">
            <div className="space-y-3">
              {mockPositions.map((position, index) => (
                <motion.div
                  key={position.symbol}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="p-4 rounded-lg border border-border hover:border-primary/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold">{position.symbol}</h3>
                    <Badge variant={position.pnl >= 0 ? "default" : "destructive"}>
                      {position.pnl >= 0 ? '+' : ''}${position.pnl}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Quantity</p>
                      <p className="font-medium">{position.quantity}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Avg Price</p>
                      <p className="font-medium">${position.avgPrice}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Current Price</p>
                      <p className="font-medium">${position.currentPrice}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">P&L %</p>
                      <p className={`font-medium ${
                        position.pnlPercent >= 0 ? 'text-green-500' : 'text-red-500'
                      }`}>
                        {position.pnlPercent >= 0 ? '+' : ''}{position.pnlPercent.toFixed(2)}%
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="orders" className="space-y-4 mt-6">
            <div className="space-y-3">
              {mockTrades.map((trade, index) => (
                <motion.div
                  key={trade.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="p-4 rounded-lg border border-border hover:border-primary/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(trade.status)}
                      <h3 className="font-semibold">{trade.symbol}</h3>
                      <Badge variant={trade.side === 'buy' ? 'default' : 'destructive'}>
                        {trade.side.toUpperCase()}
                      </Badge>
                    </div>
                    <Badge className={getStatusColor(trade.status)}>
                      {trade.status}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Quantity</p>
                      <p className="font-medium">{trade.quantity}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Price</p>
                      <p className="font-medium">${trade.price}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Time</p>
                      <p className="font-medium">{new Date(trade.timestamp).toLocaleTimeString()}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">P&L</p>
                      {trade.pnl !== undefined ? (
                        <p className={`font-medium ${
                          trade.pnl >= 0 ? 'text-green-500' : 'text-red-500'
                        }`}>
                          {trade.pnl >= 0 ? '+' : ''}${trade.pnl}
                        </p>
                      ) : (
                        <p className="font-medium text-muted-foreground">-</p>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="strategies" className="space-y-4 mt-6">
            <div className="space-y-4">
              {mockStrategies.map((strategy, index) => (
                <motion.div
                  key={strategy.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="p-4 rounded-lg border border-border hover:border-primary/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(strategy.status)}
                      <h3 className="font-semibold">{strategy.name}</h3>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(strategy.status)}>
                        {strategy.status}
                      </Badge>
                      <Button variant="outline" size="sm">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <p className="text-sm text-muted-foreground mb-3 italic">
                    "{strategy.description}"
                  </p>

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Performance</p>
                      <p className={`font-medium ${
                        strategy.performance >= 0 ? 'text-green-500' : 'text-red-500'
                      }`}>
                        {strategy.performance >= 0 ? '+' : ''}{strategy.performance}%
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Trades</p>
                      <p className="font-medium">{strategy.trades}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Win Rate</p>
                      <div className="flex items-center gap-2">
                        <Progress value={strategy.winRate} className="flex-1" />
                        <span className="font-medium">{strategy.winRate}%</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}