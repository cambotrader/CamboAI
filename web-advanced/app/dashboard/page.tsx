'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Brain, 
  Zap, 
  Target,
  Activity,
  DollarSign,
  Users,
  AlertTriangle,
  Eye,
  Settings,
  Maximize2,
  RefreshCw
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { MarketOverview } from '@/components/dashboard/market-overview'
import { TradingPanel } from '@/components/dashboard/trading-panel'
import { PortfolioSummary } from '@/components/dashboard/portfolio-summary'
import { AIInsights } from '@/components/dashboard/ai-insights'
import { RegimeAnalysis } from '@/components/dashboard/regime-analysis'
import { SignalFeed } from '@/components/dashboard/signal-feed'
import { RiskMetrics } from '@/components/dashboard/risk-metrics'
import { AdvancedCharts } from '@/components/dashboard/advanced-charts'
import { QuantumMatrix } from '@/components/dashboard/quantum-matrix'
import { BeliefSystem } from '@/components/dashboard/belief-system'
import { NarrativeEngine } from '@/components/dashboard/narrative-engine'

// Mock data - replace with real API calls
const mockMetrics = {
  totalValue: 125430.50,
  dailyPnL: 2340.25,
  dailyPnLPercent: 1.9,
  totalReturn: 15430.75,
  totalReturnPercent: 14.1,
  winRate: 68.5,
  sharpeRatio: 1.85,
  maxDrawdown: -5.2,
  activeTrades: 12,
  watchlistItems: 45
}

const mockSignals = [
  {
    id: '1',
    timestamp: new Date().toISOString(),
    symbol: 'BTC/USD',
    signal: 'BUY',
    archetype: 'Oracle',
    mood: 'Focused',
    conviction: 0.79,
    price: 45000,
    reason: 'Bias reveals divergence pattern'
  },
  {
    id: '2',
    timestamp: new Date(Date.now() - 300000).toISOString(),
    symbol: 'ETH/USD',
    signal: 'SELL',
    archetype: 'Hunter',
    mood: 'Aggressive',
    conviction: 0.65,
    price: 3200,
    reason: 'Momentum exhaustion detected'
  },
  {
    id: '3',
    timestamp: new Date(Date.now() - 600000).toISOString(),
    symbol: 'AAPL',
    signal: 'HOLD',
    archetype: 'Prophet',
    mood: 'Cautious',
    conviction: 0.45,
    price: 175,
    reason: 'Regime transition in progress'
  }
]

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState(new Date())

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => setIsLoading(false), 1000)
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    // Update timestamp every minute
    const interval = setInterval(() => {
      setLastUpdate(new Date())
    }, 60000)
    return () => clearInterval(interval)
  }, [])

  const refreshData = () => {
    setIsLoading(true)
    setTimeout(() => {
      setIsLoading(false)
      setLastUpdate(new Date())
    }, 1000)
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-lg text-muted-foreground">Loading CamboAI Dashboard...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">CamboAI Dashboard</h1>
            <p className="text-muted-foreground">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={refreshData}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card className="cambo-card">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Portfolio</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${mockMetrics.totalValue.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">
                  +{mockMetrics.totalReturnPercent}% from last month
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card className="cambo-card">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Daily P&L</CardTitle>
                <TrendingUp className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-500">
                  +${mockMetrics.dailyPnL.toLocaleString()}
                </div>
                <p className="text-xs text-muted-foreground">
                  +{mockMetrics.dailyPnLPercent}% today
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card className="cambo-card">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{mockMetrics.winRate}%</div>
                <Progress value={mockMetrics.winRate} className="mt-2" />
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card className="cambo-card">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Trades</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{mockMetrics.activeTrades}</div>
                <p className="text-xs text-muted-foreground">
                  {mockMetrics.watchlistItems} in watchlist
                </p>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="trading">Trading</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
            <TabsTrigger value="regime">Regime</TabsTrigger>
            <TabsTrigger value="quantum">Quantum</TabsTrigger>
            <TabsTrigger value="narrative">Narrative</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <MarketOverview />
              <PortfolioSummary />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <AdvancedCharts />
              </div>
              <div className="space-y-6">
                <AIInsights />
                <RiskMetrics />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="trading" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <TradingPanel />
              </div>
              <SignalFeed signals={mockSignals} />
            </div>
          </TabsContent>

          <TabsContent value="analysis" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AdvancedCharts />
              <AIInsights />
            </div>
            <RiskMetrics />
          </TabsContent>

          <TabsContent value="regime" className="space-y-6">
            <RegimeAnalysis />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <BeliefSystem />
              <SignalFeed signals={mockSignals} />
            </div>
          </TabsContent>

          <TabsContent value="quantum" className="space-y-6">
            <QuantumMatrix />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <BeliefSystem />
              <AIInsights />
            </div>
          </TabsContent>

          <TabsContent value="narrative" className="space-y-6">
            <NarrativeEngine />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <RegimeAnalysis />
              <SignalFeed signals={mockSignals} />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}