'use client'

import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  BarChart3, 
  Maximize2, 
  Settings, 
  Download,
  RefreshCw,
  Eye,
  Layers,
  Target,
  Zap
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import dynamic from 'next/dynamic'

// Dynamically import chart components to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

interface ChartData {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface PatternSignal {
  type: string
  strength: number
  timestamp: string
  price: number
  description: string
}

// Mock data - replace with real API calls
const mockChartData: ChartData[] = Array.from({ length: 100 }, (_, i) => {
  const basePrice = 45000
  const timestamp = new Date(Date.now() - (100 - i) * 3600000).toISOString()
  const volatility = 0.02
  const trend = Math.sin(i * 0.1) * 0.01
  
  const open = basePrice * (1 + trend + (Math.random() - 0.5) * volatility)
  const close = open * (1 + (Math.random() - 0.5) * volatility)
  const high = Math.max(open, close) * (1 + Math.random() * volatility * 0.5)
  const low = Math.min(open, close) * (1 - Math.random() * volatility * 0.5)
  const volume = Math.random() * 1000000 + 500000

  return { timestamp, open, high, low, close, volume }
})

const mockPatterns: PatternSignal[] = [
  {
    type: 'Double Bottom',
    strength: 85,
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    price: 44800,
    description: 'Strong reversal pattern detected with volume confirmation'
  },
  {
    type: 'Bull Flag',
    strength: 72,
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    price: 45200,
    description: 'Continuation pattern suggesting upward momentum'
  },
  {
    type: 'Support Break',
    strength: 91,
    timestamp: new Date().toISOString(),
    price: 45100,
    description: 'Critical support level breached with high volume'
  }
]

export function AdvancedCharts() {
  const [activeTab, setActiveTab] = useState('candlestick')
  const [symbol, setSymbol] = useState('BTC/USD')
  const [timeframe, setTimeframe] = useState('1h')
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showPatterns, setShowPatterns] = useState(true)
  const [showVolume, setShowVolume] = useState(true)
  const chartRef = useRef<HTMLDivElement>(null)

  // Prepare candlestick data
  const candlestickData = {
    x: mockChartData.map(d => d.timestamp),
    open: mockChartData.map(d => d.open),
    high: mockChartData.map(d => d.high),
    low: mockChartData.map(d => d.low),
    close: mockChartData.map(d => d.close),
    type: 'candlestick' as const,
    name: symbol,
    increasing: { line: { color: '#00ff88' } },
    decreasing: { line: { color: '#ff4444' } }
  }

  // Prepare volume data
  const volumeData = {
    x: mockChartData.map(d => d.timestamp),
    y: mockChartData.map(d => d.volume),
    type: 'bar' as const,
    name: 'Volume',
    marker: { color: 'rgba(25, 118, 210, 0.3)' },
    yaxis: 'y2'
  }

  // Chart layout
  const layout = {
    title: `${symbol} - ${timeframe.toUpperCase()}`,
    xaxis: { 
      title: 'Time',
      rangeslider: { visible: false },
      type: 'date' as const
    },
    yaxis: { 
      title: 'Price ($)',
      domain: showVolume ? [0.3, 1] : [0, 1]
    },
    yaxis2: showVolume ? {
      title: 'Volume',
      domain: [0, 0.25],
      side: 'right' as const
    } : undefined,
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)',
    font: { color: 'currentColor' },
    showlegend: true,
    height: isFullscreen ? 600 : 400,
    margin: { t: 50, r: 50, b: 50, l: 50 }
  }

  const config = {
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
    responsive: true
  }

  return (
    <Card className="cambo-card">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-500" />
              Advanced Charts
            </CardTitle>
            <CardDescription>
              Professional trading charts with pattern recognition
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="animate-pulse">
              <Eye className="h-3 w-3 mr-1" />
              Live
            </Badge>
            <Button variant="outline" size="sm" onClick={() => setIsFullscreen(!isFullscreen)}>
              <Maximize2 className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Controls */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Select value={symbol} onValueChange={setSymbol}>
                <SelectTrigger className="w-32">
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

              <Select value={timeframe} onValueChange={setTimeframe}>
                <SelectTrigger className="w-20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1m">1m</SelectItem>
                  <SelectItem value="5m">5m</SelectItem>
                  <SelectItem value="15m">15m</SelectItem>
                  <SelectItem value="1h">1h</SelectItem>
                  <SelectItem value="4h">4h</SelectItem>
                  <SelectItem value="1d">1d</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant={showPatterns ? "default" : "outline"}
                size="sm"
                onClick={() => setShowPatterns(!showPatterns)}
              >
                <Target className="h-4 w-4 mr-1" />
                Patterns
              </Button>
              <Button
                variant={showVolume ? "default" : "outline"}
                size="sm"
                onClick={() => setShowVolume(!showVolume)}
              >
                <Layers className="h-4 w-4 mr-1" />
                Volume
              </Button>
              <Button variant="outline" size="sm">
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="candlestick">Candlestick</TabsTrigger>
              <TabsTrigger value="line">Line Chart</TabsTrigger>
              <TabsTrigger value="heatmap">Heatmap</TabsTrigger>
              <TabsTrigger value="patterns">Patterns</TabsTrigger>
            </TabsList>

            <TabsContent value="candlestick" className="mt-4">
              <div ref={chartRef} className="chart-container">
                <Plot
                  data={showVolume ? [candlestickData, volumeData] : [candlestickData]}
                  layout={layout}
                  config={config}
                  style={{ width: '100%', height: '100%' }}
                />
              </div>
            </TabsContent>

            <TabsContent value="line" className="mt-4">
              <div className="chart-container">
                <Plot
                  data={[{
                    x: mockChartData.map(d => d.timestamp),
                    y: mockChartData.map(d => d.close),
                    type: 'scatter',
                    mode: 'lines',
                    name: symbol,
                    line: { color: '#1976d2', width: 2 }
                  }]}
                  layout={{
                    ...layout,
                    yaxis: { title: 'Price ($)' }
                  }}
                  config={config}
                  style={{ width: '100%', height: '100%' }}
                />
              </div>
            </TabsContent>

            <TabsContent value="heatmap" className="mt-4">
              <div className="chart-container flex items-center justify-center">
                <div className="text-center">
                  <Zap className="h-12 w-12 mx-auto mb-4 text-primary" />
                  <h3 className="text-lg font-semibold mb-2">Market Heatmap</h3>
                  <p className="text-muted-foreground">
                    Advanced heatmap visualization coming soon
                  </p>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="patterns" className="mt-4">
              <div className="space-y-4">
                <div className="text-center mb-6">
                  <h3 className="text-lg font-semibold mb-2">Pattern Recognition</h3>
                  <p className="text-sm text-muted-foreground">
                    AI-powered pattern detection and analysis
                  </p>
                </div>

                {mockPatterns.map((pattern, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="p-4 rounded-lg border border-border hover:border-primary/50 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Target className="h-4 w-4 text-primary" />
                        <h4 className="font-semibold">{pattern.type}</h4>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">
                          {pattern.strength}% confidence
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          ${pattern.price.toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {pattern.description}
                    </p>
                    <div className="flex justify-between items-center text-xs text-muted-foreground">
                      <span>Detected: {new Date(pattern.timestamp).toLocaleString()}</span>
                      <div className="flex items-center gap-1">
                        <div className={`w-2 h-2 rounded-full ${
                          pattern.strength > 80 ? 'bg-green-500' :
                          pattern.strength > 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`} />
                        <span>
                          {pattern.strength > 80 ? 'Strong' :
                           pattern.strength > 60 ? 'Moderate' : 'Weak'}
                        </span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </CardContent>
    </Card>
  )
}