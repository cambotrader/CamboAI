'use client'

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'

// Dynamically import motion to prevent SSR issues
const motion = dynamic(() => import('framer-motion').then(mod => ({
  default: mod.motion
})), { ssr: false })
import { 
  TrendingUp, 
  BarChart3, 
  Brain, 
  Zap, 
  Target, 
  Globe,
  Smartphone,
  Monitor,
  Database,
  Cloud,
  Shield,
  Rocket
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'
import NoSSR from '@/components/no-ssr'

const features = [
  {
    icon: <Brain className="h-8 w-8" />,
    title: "AI-Powered Analysis",
    description: "Advanced machine learning algorithms analyze market patterns and sentiment",
    color: "text-purple-500"
  },
  {
    icon: <TrendingUp className="h-8 w-8" />,
    title: "Real-Time Trading",
    description: "Execute trades with millisecond precision across multiple markets",
    color: "text-green-500"
  },
  {
    icon: <BarChart3 className="h-8 w-8" />,
    title: "Advanced Charts",
    description: "Professional-grade charting with 100+ technical indicators",
    color: "text-blue-500"
  },
  {
    icon: <Zap className="h-8 w-8" />,
    title: "Lightning Fast",
    description: "Sub-millisecond latency for high-frequency trading strategies",
    color: "text-yellow-500"
  },
  {
    icon: <Target className="h-8 w-8" />,
    title: "Risk Management",
    description: "Sophisticated risk controls and portfolio optimization",
    color: "text-red-500"
  },
  {
    icon: <Globe className="h-8 w-8" />,
    title: "Global Markets",
    description: "Access to stocks, forex, crypto, and commodities worldwide",
    color: "text-indigo-500"
  }
]

const platforms = [
  {
    icon: <Monitor className="h-6 w-6" />,
    title: "Web Platform",
    description: "Full-featured web application",
    status: "Live",
    link: "/dashboard"
  },
  {
    icon: <Smartphone className="h-6 w-6" />,
    title: "Mobile App",
    description: "iOS & Android native apps",
    status: "Live",
    link: "/mobile"
  },
  {
    icon: <Database className="h-6 w-6" />,
    title: "API Access",
    description: "RESTful API for developers",
    status: "Live",
    link: "/api"
  },
  {
    icon: <Cloud className="h-6 w-6" />,
    title: "Cloud Sync",
    description: "Sync across all devices",
    status: "Live",
    link: "/sync"
  }
]

export default function HomePage() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-cambo-gradient opacity-10" />
        <div className="relative container mx-auto px-4 py-20">
          <NoSSR fallback={<div className="text-center max-w-4xl mx-auto opacity-0">Loading...</div>}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center max-w-4xl mx-auto"
            >
            <Badge variant="secondary" className="mb-4">
              <Rocket className="h-4 w-4 mr-2" />
              Version 2.0 - Now Live
            </Badge>
            
            <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-primary via-purple-500 to-primary bg-clip-text text-transparent mb-6">
              CamboAI
            </h1>
            
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 leading-relaxed">
              The Ultimate Unified Trading Platform
            </p>
            
            <p className="text-lg text-muted-foreground mb-12 max-w-2xl mx-auto">
              Combining all your CamboStation projects into one powerful platform. 
              Advanced AI, real-time analytics, and professional trading tools - all in one place.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="cambo-button text-lg px-8 py-3">
                <Link href="/dashboard">
                  Launch Platform
                  <TrendingUp className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              
              <Button asChild variant="outline" size="lg" className="text-lg px-8 py-3">
                <Link href="/demo">
                  View Demo
                  <BarChart3 className="ml-2 h-5 w-5" />
                </Link>
              </Button>
            </div>
          </motion.div>
          </NoSSR>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Everything you need for professional trading, powered by cutting-edge AI
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="cambo-card h-full hover:cambo-glow transition-all duration-300">
                  <CardHeader>
                    <div className={`${feature.color} mb-4`}>
                      {feature.icon}
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Platforms Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">Multi-Platform Access</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Trade anywhere, anytime with our comprehensive platform ecosystem
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {platforms.map((platform, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="cambo-card text-center hover:scale-105 transition-transform duration-300">
                  <CardHeader>
                    <div className="mx-auto mb-4 p-3 bg-primary/10 rounded-full w-fit">
                      <div className="text-primary">
                        {platform.icon}
                      </div>
                    </div>
                    <CardTitle className="text-lg">{platform.title}</CardTitle>
                    <CardDescription>{platform.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Badge variant="secondary" className="mb-4">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2" />
                      {platform.status}
                    </Badge>
                    <Button asChild variant="outline" className="w-full">
                      <Link href={platform.link}>Access</Link>
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary/5">
        <div className="container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="max-w-3xl mx-auto"
          >
            <Shield className="h-16 w-16 mx-auto mb-6 text-primary" />
            <h2 className="text-4xl font-bold mb-6">Ready to Start Trading?</h2>
            <p className="text-xl text-muted-foreground mb-8">
              Join thousands of traders using CamboAI for professional trading. 
              Get started in minutes with our intuitive platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="cambo-button text-lg px-8 py-3">
                <Link href="/dashboard">
                  Start Trading Now
                  <Rocket className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="text-lg px-8 py-3">
                <Link href="/contact">
                  Contact Sales
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}