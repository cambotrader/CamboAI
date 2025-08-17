'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
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
  Rocket,
  ArrowRight
} from 'lucide-react'

const features = [
  {
    icon: <Brain className="h-8 w-8" />,
    title: "AI-Powered Analysis",
    description: "Advanced machine learning algorithms analyze market patterns and sentiment in real-time",
    color: "text-purple-500"
  },
  {
    icon: <TrendingUp className="h-8 w-8" />,
    title: "Real-Time Trading",
    description: "Execute trades with millisecond precision across multiple global markets",
    color: "text-green-500"
  },
  {
    icon: <BarChart3 className="h-8 w-8" />,
    title: "Advanced Charts",
    description: "Professional-grade charting with 100+ technical indicators and patterns",
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
    description: "Sophisticated risk controls and portfolio optimization algorithms",
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
    description: "Full-featured web application with all trading tools",
    status: "Live",
    link: "/trading"
  },
  {
    icon: <Smartphone className="h-6 w-6" />,
    title: "Mobile App",
    description: "iOS & Android native apps for trading on-the-go",
    status: "Live", 
    link: "/mobile"
  },
  {
    icon: <Database className="h-6 w-6" />,
    title: "API Access",
    description: "RESTful API for algorithmic trading and integrations",
    status: "Live",
    link: "/api"
  },
  {
    icon: <Cloud className="h-6 w-6" />,
    title: "Cloud Sync",
    description: "Seamlessly sync your data across all devices",
    status: "Live",
    link: "/profile"
  }
]

export default function HomePage() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="animate-pulse text-center">
          <div className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mb-4">
            CamboAI TraderStation
          </div>
          <div className="text-gray-400">Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-blue-600/20" />
        <div className="relative container mx-auto px-4 py-20">
          <div className="text-center max-w-4xl mx-auto">
            <Badge variant="secondary" className="mb-6 bg-blue-500/20 text-blue-300 border-blue-500/30">
              <Rocket className="h-4 w-4 mr-2" />
              CamboAI TraderStation - Now Live
            </Badge>
            
            <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 bg-clip-text text-transparent mb-6">
              CamboAI
            </h1>
            
            <h2 className="text-2xl md:text-3xl font-semibold text-gray-200 mb-4">
              TraderStation
            </h2>
            
            <p className="text-xl md:text-2xl text-gray-300 mb-8 leading-relaxed">
              Trade with Vision, Learn with Purpose, Evolve with AI
            </p>
            
            <p className="text-lg text-gray-400 mb-12 max-w-2xl mx-auto">
              The ultimate AI-powered trading intelligence platform. Advanced analytics, 
              real-time coaching, and professional-grade tools - all in one place.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-lg px-8 py-3">
                <Link href="/trading">
                  Start Trading Now
                  <TrendingUp className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              
              <Button asChild variant="outline" size="lg" className="text-lg px-8 py-3 border-gray-600 text-gray-300 hover:bg-gray-800">
                <Link href="/projects">
                  View Projects
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-slate-800/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Powerful AI Features</h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Everything you need for professional trading, powered by cutting-edge artificial intelligence
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="bg-slate-800/80 border-slate-700 hover:border-slate-600 transition-all duration-300 hover:transform hover:scale-105">
                <CardHeader>
                  <div className={`${feature.color} mb-4`}>
                    {feature.icon}
                  </div>
                  <CardTitle className="text-xl text-white">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base text-gray-300">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Platforms Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Multi-Platform Access</h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Trade anywhere, anytime with our comprehensive platform ecosystem
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {platforms.map((platform, index) => (
              <Card key={index} className="bg-slate-800/80 border-slate-700 text-center hover:border-slate-600 transition-all duration-300 hover:transform hover:scale-105">
                <CardHeader>
                  <div className="mx-auto mb-4 p-3 bg-blue-500/20 rounded-full w-fit">
                    <div className="text-blue-400">
                      {platform.icon}
                    </div>
                  </div>
                  <CardTitle className="text-lg text-white">{platform.title}</CardTitle>
                  <CardDescription className="text-gray-300">{platform.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Badge variant="secondary" className="mb-4 bg-green-500/20 text-green-400 border-green-500/30">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2" />
                    {platform.status}
                  </Badge>
                  <Button asChild variant="outline" className="w-full border-slate-600 text-gray-300 hover:bg-slate-700">
                    <Link href={platform.link}>Access Platform</Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-blue-600/20">
        <div className="container mx-auto px-4 text-center">
          <div className="max-w-3xl mx-auto">
            <Shield className="h-16 w-16 mx-auto mb-6 text-blue-400" />
            <h2 className="text-4xl font-bold text-white mb-6">Ready to Transform Your Trading?</h2>
            <p className="text-xl text-gray-300 mb-8">
              Join the future of intelligent trading with CamboAI TraderStation. 
              Get started in minutes with our intuitive AI-powered platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-lg px-8 py-3">
                <Link href="/trading">
                  Launch Trading Platform
                  <Rocket className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="text-lg px-8 py-3 border-gray-600 text-gray-300 hover:bg-gray-800">
                <Link href="/profile">
                  View Portfolio
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <p className="text-gray-400 mb-2">
              © 2024 CamboAI TraderStation. All rights reserved.
            </p>
            <p className="text-gray-500 text-sm">
              Trade with Vision, Learn with Purpose, Evolve with AI
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}