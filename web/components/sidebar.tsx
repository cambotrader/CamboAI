"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Home, ListTree, Brain, BarChart3, Wallet, Calendar, Bell, BookOpen, Settings, LineChart, Activity } from "lucide-react"

// Simple utility until a central cn exists
function clsx(...parts: (string | false | null | undefined)[]) {
  return parts.filter(Boolean).join(" ")
}

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/screener", label: "Screener", icon: Activity },
  { href: "/ai-watchlist", label: "AI Watchlist", icon: Brain },
  { href: "/portfolio", label: "Portfolio", icon: Wallet },
  { href: "/options", label: "Options", icon: LineChart },
  { href: "/calendars", label: "Calendars", icon: Calendar },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/education", label: "Education", icon: BookOpen },
  { href: "/settings", label: "Settings", icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()
  return (
    <aside className="hidden md:flex md:flex-col w-64 bg-slate-900 border-r border-slate-800 text-gray-200">
      <div className="h-16 flex items-center px-4 border-b border-slate-800 text-lg font-semibold">
        Cambo AI
      </div>
      <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
        {nav.map(({ href, label, icon: Icon }) => {
          const active = pathname?.startsWith(href)
          return (
            <Link key={href} href={href} className={clsx(
              "flex items-center gap-3 px-3 py-2 rounded-md text-sm hover:bg-slate-800",
              active && "bg-slate-800 text-white"
            )}>
              <Icon className="h-4 w-4" />
              <span>{label}</span>
            </Link>
          )
        })}
      </nav>
      <div className="p-3 text-xs text-slate-400">v0 preview</div>
    </aside>
  )
}