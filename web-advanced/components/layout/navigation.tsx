"use client";
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  TrendingUp,
  AlertCircle,
  BarChart3,
  PieChart,
  Newspaper,
  Settings,
  Activity,
  Target,
  Brain,
  Zap
} from 'lucide-react';

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    description: 'Main trading dashboard'
  },
  {
    name: 'Charts',
    href: '/dashboard/charts',
    icon: TrendingUp,
    description: 'Advanced charting with AI patterns'
  },
  {
    name: 'Options',
    href: '/dashboard/options',
    icon: PieChart,
    description: 'Options pricing & demo',
    children: [
      {
        name: 'Pricing Demo',
        href: '/dashboard/options',
        description: 'Basic options pricing'
      },
      {
        name: 'Strategies',
        href: '/dashboard/options/strategies',
        description: 'Advanced options strategies'
      }
    ]
  },
  {
    name: 'Alerts',
    href: '/dashboard/alerts',
    icon: AlertCircle,
    description: 'Smart price & pattern alerts'
  },
  {
    name: 'News & Sentiment',
    href: '/dashboard/news',
    icon: Newspaper,
    description: 'AI-powered market sentiment'
  },
  {
    name: 'Portfolio',
    href: '/dashboard/portfolio',
    icon: PieChart,
    description: 'Portfolio management & analysis'
  },
  {
    name: 'Risk',
    href: '/dashboard/risk',
    icon: Target,
    description: 'Risk management & VaR'
  },
  {
    name: 'Trading',
    href: '/dashboard/trading',
    icon: Activity,
    description: 'Order execution & management'
  },
  {
    name: 'War Room',
    href: '/dashboard/warroom',
    icon: Brain,
    description: 'AI agent debates & analysis'
  },
  {
    name: 'Learning',
    href: '/dashboard/learning',
    icon: Zap,
    description: 'Trading courses & education'
  }
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="space-y-1">
      {navigation.map((item) => {
        const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
        const Icon = item.icon;
        
        return (
          <div key={item.name}>
            <Link
              href={item.href}
              className={cn(
                'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors',
                isActive
                  ? 'bg-blue-100 text-blue-900 border border-blue-200'
                  : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
              )}
            >
              <Icon
                className={cn(
                  'mr-3 flex-shrink-0 h-5 w-5',
                  isActive ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'
                )}
              />
              <div className="flex-1">
                <div>{item.name}</div>
                <div className="text-xs text-gray-500">{item.description}</div>
              </div>
            </Link>
            
            {/* Sub-navigation */}
            {item.children && isActive && (
              <div className="ml-8 mt-1 space-y-1">
                {item.children.map((child) => (
                  <Link
                    key={child.name}
                    href={child.href}
                    className={cn(
                      'block px-2 py-1 text-xs rounded transition-colors',
                      pathname === child.href
                        ? 'bg-blue-50 text-blue-800 font-medium'
                        : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                    )}
                  >
                    {child.name}
                    <div className="text-gray-500">{child.description}</div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        );
      })}
      
      {/* Real-time Status Indicator */}
      <div className="pt-4 border-t">
        <div className="flex items-center px-2 py-2 text-xs text-gray-500">
          <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse" />
          Real-time updates active
        </div>
      </div>
    </nav>
  );
}