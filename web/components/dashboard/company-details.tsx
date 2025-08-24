"use client"
import { useEffect, useMemo, useState } from "react"
import { ChevronDown, ChevronRight, Pin, PinOff } from "lucide-react"

// Placeholder props; later wire to backend/company profile API
export interface CompanyDetailsProps {
  symbol?: string
}

const LS_KEY = "companyDetails.pinned"

export default function CompanyDetails({ symbol = "AAPL" }: CompanyDetailsProps) {
  const [open, setOpen] = useState<boolean>(false)
  const [pinned, setPinned] = useState<boolean>(false)

  useEffect(() => {
    const saved = localStorage.getItem(LS_KEY)
    if (saved) setPinned(saved === "1")
    // UX: default collapsed on small screens unless pinned
    if (window.innerWidth >= 1024 || saved === "1") setOpen(true)
  }, [])

  useEffect(() => {
    localStorage.setItem(LS_KEY, pinned ? "1" : "0")
  }, [pinned])

  return (
    <section className="bg-slate-900/60 border border-slate-800 rounded-lg">
      <header className="flex items-center justify-between px-4 py-2 border-b border-slate-800">
        <button
          className="flex items-center gap-2 select-none"
          onClick={() => setOpen(v => !v)}
          aria-expanded={open}
        >
          {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          <span className="font-medium">Company Details</span>
          <span className="ml-2 text-xs text-slate-400">({symbol})</span>
        </button>
        <button
          className="text-slate-300 hover:text-white"
          title={pinned ? "Unpin panel" : "Pin panel (remember open)"}
          onClick={() => setPinned(p => !p)}
        >
          {pinned ? <Pin className="h-4 w-4" /> : <PinOff className="h-4 w-4" />}
        </button>
      </header>

      {open && (
        <div className="p-4 grid gap-4 md:grid-cols-2">
          {/* Left column */}
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-slate-400">Company</span><span className="text-slate-200">Apple Inc.</span></div>
            <div className="flex justify-between"><span className="text-slate-400">CEO</span><span className="text-slate-200">Tim Cook</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Sector</span><span className="text-slate-200">Technology</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Market Cap</span><span className="text-slate-200">$3.0T</span></div>
            <div className="flex justify-between"><span className="text-slate-400">52W High</span><span className="text-green-400">$199.62</span></div>
            <div className="flex justify-between"><span className="text-slate-400">52W Low</span><span className="text-red-400">$164.07</span></div>
          </div>

          {/* Right column */}
          <div className="space-y-3 text-sm">
            <div>
              <div className="text-slate-400 mb-1">Filings</div>
              <ul className="list-disc list-inside text-slate-300 space-y-1">
                <li>10-K FY2024 • Feb 02</li>
                <li>10-Q Q1 2025 • May 01</li>
              </ul>
            </div>
            <div>
              <div className="text-slate-400 mb-1">Earnings</div>
              <ul className="list-disc list-inside text-slate-300 space-y-1">
                <li>EPS: 2.19 (beat 3%) • May 01</li>
                <li>Next: Aug 01 (est)</li>
              </ul>
            </div>
          </div>

          <div className="md:col-span-2 text-xs text-slate-400">Sample data — will wire to provider APIs.</div>
        </div>
      )}
    </section>
  )
}