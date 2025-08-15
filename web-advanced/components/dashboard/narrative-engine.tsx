'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  BookOpen, 
  Feather, 
  Sparkles, 
  Brain,
  MessageSquare,
  Clock,
  TrendingUp,
  AlertCircle,
  Play,
  Pause,
  SkipForward,
  Volume2,
  Eye,
  Zap
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'

interface MarketNarrative {
  id: string
  title: string
  story: string
  mood: string
  confidence: number
  timestamp: string
  archetype: string
  symbols: string[]
  sentiment: 'bullish' | 'bearish' | 'neutral'
  conviction: number
}

interface BeliefSystem {
  id: string
  belief: string
  strength: number
  evidence: string[]
  conflicts: string[]
  evolution: number
  archetype: string
}

interface StorySession {
  id: string
  title: string
  duration: string
  narratives: number
  mood: string
  outcome: string
  performance: number
}

const mockNarratives: MarketNarrative[] = [
  {
    id: '1',
    title: 'The Oracle\'s Vision',
    story: 'In the depths of market chaos, patterns emerge like constellations in the night sky. The Oracle sees beyond the noise, recognizing that bias reveals divergence patterns in market structure. Current price action suggests a hidden accumulation phase, where smart money quietly positions for the next major move.',
    mood: 'Focused',
    confidence: 85,
    timestamp: new Date().toISOString(),
    archetype: 'Oracle',
    symbols: ['BTC/USD', 'ETH/USD'],
    sentiment: 'bullish',
    conviction: 0.79
  },
  {
    id: '2',
    title: 'The Hunter\'s Pursuit',
    story: 'Momentum exhaustion creates opportunity windows that only the prepared can exploit. The Hunter stalks through volatile markets, sensing weakness in overextended positions. Volume patterns suggest institutional distribution, creating perfect conditions for contrarian plays.',
    mood: 'Aggressive',
    confidence: 72,
    timestamp: new Date(Date.now() - 1800000).toISOString(),
    archetype: 'Hunter',
    symbols: ['AAPL', 'TSLA', 'NVDA'],
    sentiment: 'bearish',
    conviction: 0.65
  },
  {
    id: '3',
    title: 'The Ghost\'s Whisper',
    story: 'Hidden patterns emerge in market inefficiencies, visible only to those who understand the language of shadows. The Ghost moves through dark pools and after-hours sessions, finding opportunities where others see emptiness. Algorithmic footprints reveal institutional intentions.',
    mood: 'Mysterious',
    confidence: 91,
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    archetype: 'Ghost',
    symbols: ['SPY', 'QQQ', 'IWM'],
    sentiment: 'neutral',
    conviction: 0.88
  }
]

const mockBeliefs: BeliefSystem[] = [
  {
    id: '1',
    belief: 'Market structure reveals institutional intentions through volume and price divergence',
    strength: 92,
    evidence: ['Volume profile analysis', 'Dark pool activity', 'Options flow'],
    conflicts: ['Random walk theory', 'Efficient market hypothesis'],
    evolution: 15,
    archetype: 'Oracle'
  },
  {
    id: '2',
    belief: 'Momentum exhaustion creates predictable reversal opportunities',
    strength: 78,
    evidence: ['RSI divergence', 'Volume decline', 'Sentiment extremes'],
    conflicts: ['Trend continuation bias', 'Momentum persistence'],
    evolution: 8,
    archetype: 'Hunter'
  },
  {
    id: '3',
    belief: 'Hidden patterns exist in market microstructure and order flow',
    strength: 95,
    evidence: ['Algorithmic signatures', 'Latency arbitrage', 'Liquidity patterns'],
    conflicts: ['Market randomness', 'Noise trading'],
    evolution: 23,
    archetype: 'Ghost'
  }
]

const mockSessions: StorySession[] = [
  {
    id: '1',
    title: 'Morning Revelation',
    duration: '2h 15m',
    narratives: 8,
    mood: 'Focused',
    outcome: 'Bullish Consensus',
    performance: 12.5
  },
  {
    id: '2',
    title: 'Midday Conflict',
    duration: '1h 45m',
    narratives: 5,
    mood: 'Conflicted',
    outcome: 'Regime Transition',
    performance: -2.1
  },
  {
    id: '3',
    title: 'Evening Synthesis',
    duration: '3h 30m',
    narratives: 12,
    mood: 'Mysterious',
    outcome: 'Hidden Opportunity',
    performance: 8.7
  }
]

export function NarrativeEngine() {
  const [activeTab, setActiveTab] = useState('stories')
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentNarrative, setCurrentNarrative] = useState(0)
  const [customStory, setCustomStory] = useState('')
  const [storyProgress, setStoryProgress] = useState(0)

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isPlaying) {
      interval = setInterval(() => {
        setStoryProgress(prev => {
          if (prev >= 100) {
            setCurrentNarrative(prev => (prev + 1) % mockNarratives.length)
            return 0
          }
          return prev + 2
        })
      }, 100)
    }
    return () => clearInterval(interval)
  }, [isPlaying])

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'bullish':
        return 'text-green-500 bg-green-500/10 border-green-500/20'
      case 'bearish':
        return 'text-red-500 bg-red-500/10 border-red-500/20'
      case 'neutral':
        return 'text-gray-500 bg-gray-500/10 border-gray-500/20'
      default:
        return 'text-muted-foreground'
    }
  }

  const getMoodIcon = (mood: string) => {
    switch (mood) {
      case 'Focused':
        return <Eye className="h-4 w-4" />
      case 'Aggressive':
        return <Zap className="h-4 w-4" />
      case 'Mysterious':
        return <Sparkles className="h-4 w-4" />
      case 'Conflicted':
        return <AlertCircle className="h-4 w-4" />
      default:
        return <Brain className="h-4 w-4" />
    }
  }

  return (
    <Card className="cambo-card">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-amber-500" />
              Narrative Engine
            </CardTitle>
            <CardDescription>
              AI-powered market storytelling and belief system analysis
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="animate-pulse">
              <Feather className="h-3 w-3 mr-1" />
              Composing
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsPlaying(!isPlaying)}
            >
              {isPlaying ? (
                <Pause className="h-4 w-4" />
              ) : (
                <Play className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="stories">Stories</TabsTrigger>
            <TabsTrigger value="beliefs">Beliefs</TabsTrigger>
            <TabsTrigger value="sessions">Sessions</TabsTrigger>
            <TabsTrigger value="compose">Compose</TabsTrigger>
          </TabsList>

          <TabsContent value="stories" className="space-y-4 mt-6">
            <div className="space-y-4">
              <AnimatePresence mode="wait">
                {mockNarratives.map((narrative, index) => (
                  <motion.div
                    key={narrative.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ 
                      opacity: currentNarrative === index ? 1 : 0.7,
                      y: 0,
                      scale: currentNarrative === index ? 1.02 : 1
                    }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                    className={`p-4 rounded-lg border transition-all duration-300 ${
                      currentNarrative === index 
                        ? 'border-primary bg-primary/5 shadow-lg' 
                        : 'border-border'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2">
                          {getMoodIcon(narrative.mood)}
                          <h3 className="font-semibold">{narrative.title}</h3>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {narrative.archetype}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getSentimentColor(narrative.sentiment)}>
                          {narrative.sentiment}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {new Date(narrative.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>

                    <p className="text-sm text-muted-foreground mb-4 leading-relaxed italic">
                      "{narrative.story}"
                    </p>

                    <div className="flex items-center justify-between">
                      <div className="flex flex-wrap gap-1">
                        {narrative.symbols.map((symbol, i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            {symbol}
                          </Badge>
                        ))}
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Confidence: </span>
                          <span className="font-medium">{narrative.confidence}%</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Conviction: </span>
                          <span className="font-medium">{(narrative.conviction * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>

                    {currentNarrative === index && isPlaying && (
                      <div className="mt-3 pt-3 border-t">
                        <div className="flex items-center gap-2 mb-2">
                          <Volume2 className="h-4 w-4 text-primary" />
                          <span className="text-sm font-medium">Narrating...</span>
                        </div>
                        <Progress value={storyProgress} className="h-2" />
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </TabsContent>

          <TabsContent value="beliefs" className="space-y-4 mt-6">
            <div className="space-y-4">
              {mockBeliefs.map((belief, index) => (
                <motion.div
                  key={belief.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="p-4 rounded-lg border border-border hover:border-primary/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Brain className="h-4 w-4 text-purple-500" />
                      <Badge variant="outline" className="text-xs">
                        {belief.archetype}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">Strength:</span>
                      <span className="font-medium">{belief.strength}%</span>
                    </div>
                  </div>

                  <p className="text-sm mb-4 font-medium">
                    {belief.belief}
                  </p>

                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Supporting Evidence:</p>
                      <div className="flex flex-wrap gap-1">
                        {belief.evidence.map((evidence, i) => (
                          <Badge key={i} variant="secondary" className="text-xs">
                            ✓ {evidence}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Conflicts:</p>
                      <div className="flex flex-wrap gap-1">
                        {belief.conflicts.map((conflict, i) => (
                          <Badge key={i} variant="outline" className="text-xs text-red-500">
                            ✗ {conflict}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t">
                      <div>
                        <span className="text-xs text-muted-foreground">Evolution: </span>
                        <span className="text-sm font-medium">+{belief.evolution}% this month</span>
                      </div>
                      <Progress value={belief.strength} className="w-24 h-2" />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="sessions" className="space-y-4 mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {mockSessions.map((session, index) => (
                <motion.div
                  key={session.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="p-4 rounded-lg border border-border hover:border-primary/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold">{session.title}</h3>
                    <Badge variant="outline" className="text-xs">
                      {session.duration}
                    </Badge>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Narratives:</span>
                      <span className="font-medium">{session.narratives}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Mood:</span>
                      <span className="font-medium">{session.mood}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Outcome:</span>
                      <span className="font-medium">{session.outcome}</span>
                    </div>
                  </div>

                  <div className="pt-3 border-t">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Performance:</span>
                      <span className={`font-medium ${
                        session.performance > 0 ? 'text-green-500' : 
                        session.performance < 0 ? 'text-red-500' : 'text-gray-500'
                      }`}>
                        {session.performance > 0 ? '+' : ''}{session.performance}%
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="compose" className="space-y-4 mt-6">
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-2">Compose New Narrative</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Create a custom market story or let the AI generate one based on current conditions
                </p>
              </div>

              <Textarea
                placeholder="Write your market narrative here... or click 'Generate' for AI assistance"
                value={customStory}
                onChange={(e) => setCustomStory(e.target.value)}
                className="min-h-32"
              />

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm">
                    <Sparkles className="h-4 w-4 mr-2" />
                    Generate AI Story
                  </Button>
                  <Button variant="outline" size="sm">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Analyze Sentiment
                  </Button>
                </div>
                <Button disabled={!customStory.trim()}>
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Publish Narrative
                </Button>
              </div>

              <div className="p-4 rounded-lg bg-muted/30 border">
                <div className="flex items-center gap-2 mb-2">
                  <Brain className="h-4 w-4 text-primary" />
                  <span className="font-medium">AI Writing Assistant</span>
                </div>
                <p className="text-sm text-muted-foreground">
                  The AI can help you craft compelling market narratives by analyzing current market conditions, 
                  sentiment data, and technical patterns. Use the generate button to get started.
                </p>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}