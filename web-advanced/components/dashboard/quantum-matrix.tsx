'use client'

import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { 
  Atom, 
  Zap, 
  Brain, 
  Target,
  Activity,
  Layers,
  GitBranch,
  Sparkles,
  Eye,
  Shuffle
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

interface QuantumState {
  id: string
  name: string
  probability: number
  energy: number
  coherence: number
  entanglement: string[]
  phase: number
  amplitude: number
}

interface DimensionalSignal {
  dimension: string
  strength: number
  frequency: number
  phase: number
  resonance: number
  color: string
}

const mockQuantumStates: QuantumState[] = [
  {
    id: '1',
    name: 'Bullish Superposition',
    probability: 0.73,
    energy: 85,
    coherence: 0.92,
    entanglement: ['BTC/USD', 'ETH/USD', 'Tech Stocks'],
    phase: 0.45,
    amplitude: 1.2
  },
  {
    id: '2',
    name: 'Bearish Interference',
    probability: 0.27,
    energy: 45,
    coherence: 0.68,
    entanglement: ['VIX', 'Bonds', 'Safe Haven'],
    phase: -0.32,
    amplitude: 0.8
  },
  {
    id: '3',
    name: 'Neutral Decoherence',
    probability: 0.15,
    energy: 25,
    coherence: 0.34,
    entanglement: ['Sideways', 'Low Vol'],
    phase: 0.0,
    amplitude: 0.3
  }
]

const mockDimensionalSignals: DimensionalSignal[] = [
  { dimension: 'Price', strength: 0.85, frequency: 2.3, phase: 0.45, resonance: 0.92, color: 'text-blue-500' },
  { dimension: 'Volume', strength: 0.67, frequency: 1.8, phase: -0.23, resonance: 0.78, color: 'text-green-500' },
  { dimension: 'Volatility', strength: 0.54, frequency: 3.1, phase: 0.67, resonance: 0.65, color: 'text-red-500' },
  { dimension: 'Momentum', strength: 0.78, frequency: 2.7, phase: 0.12, resonance: 0.83, color: 'text-purple-500' },
  { dimension: 'Sentiment', strength: 0.43, frequency: 1.2, phase: -0.45, resonance: 0.56, color: 'text-yellow-500' },
  { dimension: 'Time', strength: 0.91, frequency: 4.2, phase: 0.78, resonance: 0.94, color: 'text-indigo-500' }
]

export function QuantumMatrix() {
  const [activeTab, setActiveTab] = useState('states')
  const [isCollapsing, setIsCollapsing] = useState(false)
  const [selectedState, setSelectedState] = useState<string | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  // Quantum visualization effect
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight

    let animationId: number
    let time = 0

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      // Draw quantum field
      const centerX = canvas.width / 2
      const centerY = canvas.height / 2
      
      // Draw entangled particles
      for (let i = 0; i < 50; i++) {
        const angle = (i / 50) * Math.PI * 2 + time * 0.01
        const radius = 80 + Math.sin(time * 0.02 + i) * 20
        const x = centerX + Math.cos(angle) * radius
        const y = centerY + Math.sin(angle) * radius
        
        const opacity = 0.3 + Math.sin(time * 0.03 + i) * 0.2
        ctx.fillStyle = `rgba(25, 118, 210, ${opacity})`
        ctx.beginPath()
        ctx.arc(x, y, 2, 0, Math.PI * 2)
        ctx.fill()
        
        // Draw connections
        if (i % 5 === 0) {
          const nextAngle = ((i + 5) / 50) * Math.PI * 2 + time * 0.01
          const nextRadius = 80 + Math.sin(time * 0.02 + i + 5) * 20
          const nextX = centerX + Math.cos(nextAngle) * nextRadius
          const nextY = centerY + Math.sin(nextAngle) * nextRadius
          
          ctx.strokeStyle = `rgba(25, 118, 210, 0.1)`
          ctx.lineWidth = 1
          ctx.beginPath()
          ctx.moveTo(x, y)
          ctx.lineTo(nextX, nextY)
          ctx.stroke()
        }
      }
      
      time++
      animationId = requestAnimationFrame(animate)
    }
    
    animate()
    
    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId)
      }
    }
  }, [])

  const collapseWaveFunction = () => {
    setIsCollapsing(true)
    setTimeout(() => setIsCollapsing(false), 2000)
  }

  return (
    <Card className="cambo-card">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Atom className="h-5 w-5 text-indigo-500" />
              Quantum Matrix Engine
            </CardTitle>
            <CardDescription>
              Multi-dimensional market analysis using quantum-inspired algorithms
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="animate-pulse">
              <Sparkles className="h-3 w-3 mr-1" />
              Quantum
            </Badge>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={collapseWaveFunction}
              disabled={isCollapsing}
            >
              {isCollapsing ? (
                <Activity className="h-4 w-4 animate-spin" />
              ) : (
                <Target className="h-4 w-4" />
              )}
              Collapse
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="states">Quantum States</TabsTrigger>
            <TabsTrigger value="dimensions">Dimensions</TabsTrigger>
            <TabsTrigger value="field">Field View</TabsTrigger>
          </TabsList>

          <TabsContent value="states" className="space-y-4 mt-6">
            <div className="space-y-4">
              {mockQuantumStates.map((state, index) => (
                <motion.div
                  key={state.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ 
                    opacity: isCollapsing && state.probability > 0.5 ? 1 : state.probability,
                    scale: isCollapsing && state.probability > 0.5 ? 1.05 : 1
                  }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className={`p-4 rounded-lg border transition-all duration-500 cursor-pointer ${
                    selectedState === state.id 
                      ? 'border-primary bg-primary/5' 
                      : 'border-border hover:border-primary/50'
                  } ${isCollapsing && state.probability > 0.5 ? 'ring-2 ring-primary' : ''}`}
                  onClick={() => setSelectedState(selectedState === state.id ? null : state.id)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <div className="w-3 h-3 rounded-full bg-primary animate-pulse" />
                        <div className="absolute inset-0 w-3 h-3 rounded-full bg-primary animate-ping opacity-30" />
                      </div>
                      <h3 className="font-semibold">{state.name}</h3>
                    </div>
                    <Badge variant="outline">
                      P = {(state.probability * 100).toFixed(1)}%
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                    <div>
                      <p className="text-xs text-muted-foreground">Energy</p>
                      <div className="flex items-center gap-2">
                        <Progress value={state.energy} className="flex-1" />
                        <span className="text-sm font-medium">{state.energy}</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Coherence</p>
                      <div className="flex items-center gap-2">
                        <Progress value={state.coherence * 100} className="flex-1" />
                        <span className="text-sm font-medium">{(state.coherence * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Phase</p>
                      <p className="text-sm font-medium">{state.phase.toFixed(2)}π</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Amplitude</p>
                      <p className="text-sm font-medium">{state.amplitude.toFixed(1)}</p>
                    </div>
                  </div>

                  {selectedState === state.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="border-t pt-3 mt-3"
                    >
                      <p className="text-xs text-muted-foreground mb-2">Entangled Assets:</p>
                      <div className="flex flex-wrap gap-1">
                        {state.entanglement.map((asset, i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            <GitBranch className="h-3 w-3 mr-1" />
                            {asset}
                          </Badge>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              ))}
            </div>

            {isCollapsing && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 rounded-lg bg-primary/10 border border-primary/20"
              >
                <div className="flex items-center gap-2 mb-2">
                  <Target className="h-4 w-4 text-primary animate-spin" />
                  <span className="font-medium">Wave Function Collapse in Progress...</span>
                </div>
                <p className="text-sm text-muted-foreground">
                  Quantum superposition resolving to most probable state: Bullish Superposition (73%)
                </p>
              </motion.div>
            )}
          </TabsContent>

          <TabsContent value="dimensions" className="space-y-4 mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mockDimensionalSignals.map((signal, index) => (
                <motion.div
                  key={signal.dimension}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="p-4 rounded-lg border border-border hover:border-primary/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Layers className={`h-4 w-4 ${signal.color}`} />
                      <h3 className="font-semibold">{signal.dimension}</h3>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {signal.frequency.toFixed(1)} Hz
                    </Badge>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Signal Strength</span>
                        <span className="font-medium">{(signal.strength * 100).toFixed(0)}%</span>
                      </div>
                      <Progress value={signal.strength * 100} />
                    </div>

                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Resonance</span>
                        <span className="font-medium">{(signal.resonance * 100).toFixed(0)}%</span>
                      </div>
                      <Progress value={signal.resonance * 100} />
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Phase</p>
                        <p className="font-medium">{signal.phase.toFixed(2)}π</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Frequency</p>
                        <p className="font-medium">{signal.frequency.toFixed(1)} Hz</p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="field" className="space-y-4 mt-6">
            <div className="text-center mb-4">
              <h3 className="text-lg font-semibold mb-2">Quantum Field Visualization</h3>
              <p className="text-sm text-muted-foreground">
                Real-time visualization of market quantum field interactions
              </p>
            </div>

            <div className="relative">
              <canvas
                ref={canvasRef}
                className="w-full h-64 rounded-lg bg-muted/20 border"
                style={{ background: 'radial-gradient(circle, rgba(25,118,210,0.05) 0%, rgba(0,0,0,0) 70%)' }}
              />
              <div className="absolute top-4 left-4">
                <Badge variant="secondary" className="animate-pulse">
                  <Eye className="h-3 w-3 mr-1" />
                  Field Active
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="text-center p-3 rounded-lg bg-muted/30">
                <p className="text-sm text-muted-foreground">Entanglement</p>
                <p className="text-lg font-bold text-blue-500">92%</p>
              </div>
              <div className="text-center p-3 rounded-lg bg-muted/30">
                <p className="text-sm text-muted-foreground">Coherence</p>
                <p className="text-lg font-bold text-green-500">78%</p>
              </div>
              <div className="text-center p-3 rounded-lg bg-muted/30">
                <p className="text-sm text-muted-foreground">Interference</p>
                <p className="text-lg font-bold text-purple-500">45%</p>
              </div>
              <div className="text-center p-3 rounded-lg bg-muted/30">
                <p className="text-sm text-muted-foreground">Superposition</p>
                <p className="text-lg font-bold text-indigo-500">67%</p>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}