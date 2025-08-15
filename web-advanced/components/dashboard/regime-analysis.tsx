'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Eye,
  Zap,
  Target,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'

interface RegimeData {
  id: string
  name: string
  status: 'active' | 'transitioning' | 'dormant'
  confidence: number
  duration: string
  characteristics: string[]
  signals: number
  performance: number
}

interface ArchetypeData {
  name: string
  mood: string
  conviction: number
  activeSignals: number
  performance: number
  belief: string
  status: 'active' | 'resting' | 'conflicted'
}

const mockRegimes: RegimeData[] = [
  {
    id: '1',
    name: 'Momentum Expansion',
    status: 'active',
    confidence: 85,
    duration: '12 days',
    characteristics: ['High volatility', 'Trend continuation', 'Volume expansion'],
    signals: 23,
    performance: 12.5
  },
  {
    id: '2',
    name: 'Range Consolidation',
    status: 'transitioning',
    confidence: 45,
    duration: '3 days',
    characteristics: ['Low volatility', 'Sideways movement', 'Support/resistance'],
    signals: 8,
    performance: -2.1
  },
  {
    id: '3',
    name: 'Reversal Pattern',
    status: 'dormant',
    confidence: 25,
    duration: '0 days',
    characteristics: ['Divergence signals', 'Volume decline', 'Pattern completion'],
    signals: 2,
    performance: 0.0
  }
]

const mockArchetypes: ArchetypeData[] = [
  {
    name: 'Oracle',
    mood: 'Focused',
    conviction: 0.79,
    activeSignals: 5,
    performance: 15.2,
    belief: 'Bias reveals divergence patterns in market structure',
    status: 'active'
  },
  {
    name: 'Hunter',
    mood: 'Aggressive',
    conviction: 0.65,
    activeSignals: 8,
    performance: 8.7,
    belief: 'Momentum exhaustion creates opportunity windows',
    status: 'active'
  },
  {
    name: 'Prophet',
    mood: 'Cautious',
    conviction: 0.45,
    activeSignals: 2,
    performance: -1.2,
    belief: 'Regime transitions require patience and observation',
    status: 'resting'
  },
  {
    name: 'Ghost',
    mood: 'Mysterious',
    conviction: 0.88,
    activeSignals: 12,
    performance: 22.1,
    belief: 'Hidden patterns emerge in market inefficiencies',
    status: 'active'
  }
]

export function RegimeAnalysis() {
  const [activeTab, setActiveTab] = useState('regimes')
  const [selectedRegime, setSelectedRegime] = useState<string | null>(null)
  const [toneDrift, setToneDrift] = useState({
    Focused: 0.35,
    Aggressive: 0.28,
    Cautious: 0.22,
    Mysterious: 0.15
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'transitioning':
        return <Clock className="h-4 w-4 text-yellow-500" />
      case 'dormant':
        return <Minus className="h-4 w-4 text-gray-500" />
      case 'resting':
        return <Eye className="h-4 w-4 text-blue-500" />
      case 'conflicted':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      default:
        return <Activity className="h-4 w-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/10 text-green-500 border-green-500/20'
      case 'transitioning':
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
      case 'dormant':
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20'
      case 'resting':
        return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
      case 'conflicted':
        return 'bg-red-500/10 text-red-500 border-red-500/20'
      default:
        return 'bg-muted'
    }
  }

  return (
    <Card className="cambo-card">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-500" />
              Regime Analysis Engine
            </CardTitle>
            <CardDescription>
              Advanced market regime detection and archetype analysis
            </CardDescription>
          </div>
          <Badge variant="secondary" className="animate-pulse">
            <Activity className="h-3 w-3 mr-1" />
            Live
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="regimes">Market Regimes</TabsTrigger>
            <TabsTrigger value="archetypes">Archetypes</TabsTrigger>
            <TabsTrigger value="drift">Tone Drift</TabsTrigger>
          </TabsList>

          <TabsContent value="regimes" className="space-y-4 mt-6">
            <div className="space-y-4">
              {mockRegimes.map((regime, index) => (
                <motion.div
                  key={regime.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className={`p-4 rounded-lg border transition-all duration-200 cursor-pointer ${
                    selectedRegime === regime.id 
                      ? 'border-primary bg-primary/5' 
                      : 'border-border hover:border-primary/50'
                  }`}
                  onClick={() => setSelectedRegime(selectedRegime === regime.id ? null : regime.id)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(regime.status)}
                      <h3 className="font-semibold">{regime.name}</h3>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(regime.status)}>
                        {regime.status}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {regime.duration}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-3">
                    <div>
                      <p className="text-xs text-muted-foreground">Confidence</p>
                      <div className="flex items-center gap-2">
                        <Progress value={regime.confidence} className="flex-1" />
                        <span className="text-sm font-medium">{regime.confidence}%</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Signals</p>
                      <p className="text-sm font-medium">{regime.signals}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Performance</p>
                      <p className={`text-sm font-medium ${
                        regime.performance > 0 ? 'text-green-500' : 
                        regime.performance < 0 ? 'text-red-500' : 'text-gray-500'
                      }`}>
                        {regime.performance > 0 ? '+' : ''}{regime.performance}%
                      </p>
                    </div>
                  </div>

                  {selectedRegime === regime.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="border-t pt-3 mt-3"
                    >
                      <p className="text-xs text-muted-foreground mb-2">Characteristics:</p>
                      <div className="flex flex-wrap gap-1">
                        {regime.characteristics.map((char, i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            {char}
                          </Badge>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="archetypes" className="space-y-4 mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mockArchetypes.map((archetype, index) => (
                <motion.div
                  key={archetype.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="p-4 rounded-lg border border-border hover:border-primary/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-primary to-purple-500 flex items-center justify-center">
                        <span className="text-xs font-bold text-white">
                          {archetype.name[0]}
                        </span>
                      </div>
                      <div>
                        <h3 className="font-semibold">{archetype.name}</h3>
                        <p className="text-xs text-muted-foreground">{archetype.mood}</p>
                      </div>
                    </div>
                    <Badge className={getStatusColor(archetype.status)}>
                      {archetype.status}
                    </Badge>
                  </div>

                  <div className="space-y-2 mb-3">
                    <div className="flex justify-between text-sm">
                      <span>Conviction</span>
                      <span className="font-medium">{(archetype.conviction * 100).toFixed(0)}%</span>
                    </div>
                    <Progress value={archetype.conviction * 100} />
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
                    <div>
                      <p className="text-muted-foreground">Active Signals</p>
                      <p className="font-medium">{archetype.activeSignals}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Performance</p>
                      <p className={`font-medium ${
                        archetype.performance > 0 ? 'text-green-500' : 
                        archetype.performance < 0 ? 'text-red-500' : 'text-gray-500'
                      }`}>
                        {archetype.performance > 0 ? '+' : ''}{archetype.performance}%
                      </p>
                    </div>
                  </div>

                  <div className="text-xs text-muted-foreground italic">
                    "{archetype.belief}"
                  </div>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="drift" className="space-y-4 mt-6">
            <div className="space-y-4">
              <div className="text-center mb-6">
                <h3 className="text-lg font-semibold mb-2">Market Tone Drift Analysis</h3>
                <p className="text-sm text-muted-foreground">
                  Real-time analysis of market sentiment and mood distribution
                </p>
              </div>

              {Object.entries(toneDrift).map(([mood, weight], index) => (
                <motion.div
                  key={mood}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="flex items-center justify-between p-3 rounded-lg bg-muted/30"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${
                      mood === 'Focused' ? 'bg-blue-500' :
                      mood === 'Aggressive' ? 'bg-red-500' :
                      mood === 'Cautious' ? 'bg-yellow-500' :
                      'bg-purple-500'
                    }`} />
                    <span className="font-medium">{mood}</span>
                  </div>
                  <div className="flex items-center gap-3 flex-1 ml-6">
                    <Progress value={weight * 100} className="flex-1" />
                    <span className="text-sm font-medium w-12 text-right">
                      {(weight * 100).toFixed(0)}%
                    </span>
                  </div>
                </motion.div>
              ))}

              <div className="mt-6 p-4 rounded-lg bg-primary/5 border border-primary/20">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="h-4 w-4 text-primary" />
                  <span className="font-medium">Dominant Mood: Focused</span>
                </div>
                <p className="text-sm text-muted-foreground">
                  Current market conditions favor focused, analytical approaches. 
                  Oracle and Ghost archetypes showing highest conviction levels.
                </p>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}