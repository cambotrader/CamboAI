import Link from "next/link"

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 space-y-6">
          <section className="bg-slate-900/60 border border-slate-800 rounded-lg p-4">
            <h2 className="font-medium mb-2">Inline Chart</h2>
            <div className="h-64 grid place-items-center text-slate-400">Chart placeholder</div>
          </section>
          {/* Collapsible, pin-able panel */}
          <section className="bg-transparent p-0">
            {/* @ts-expect-error Server/Client boundary is fine here */}
            {/* eslint-disable-next-line @next/next/no-sync-scripts */}
            <div>
              {/* Company Details */}
              <div className="mt-0">
                {/* dynamic import kept simple for now */}
                {/* eslint-disable-next-line @typescript-eslint/ban-ts-comment */}
                {/* @ts-ignore */}
                {require("@/components/dashboard/company-details").default({ symbol: "AAPL" })}
              </div>
            </div>
          </section>
          <section className="bg-slate-900/60 border border-slate-800 rounded-lg p-4">
            <h2 className="font-medium mb-2">My Watchlist</h2>
            <div className="text-slate-400 text-sm">User-defined symbols with mini charts</div>
          </section>
          <section className="bg-slate-900/60 border border-slate-800 rounded-lg p-4">
            <h2 className="font-medium mb-2">Cambo AI Watchlist</h2>
            <div className="text-slate-400 text-sm">AI-ranked setups by timeframe</div>
          </section>
        </div>
        <div className="lg:col-span-4 space-y-6">
          <section className="bg-slate-900/60 border border-slate-800 rounded-lg p-4">
            <h2 className="font-medium mb-2">Top Movers</h2>
            <div className="text-slate-400 text-sm">Top gainers/losers</div>
          </section>
          <section className="bg-slate-900/60 border border-slate-800 rounded-lg p-4">
            <h2 className="font-medium mb-2">Economic Calendar</h2>
            <div className="text-slate-400 text-sm">Today / This week</div>
          </section>
          <section className="bg-slate-900/60 border border-slate-800 rounded-lg p-4">
            <h2 className="font-medium mb-2">Earnings Calendar</h2>
            <div className="text-slate-400 text-sm">Upcoming earnings</div>
          </section>
        </div>
      </div>
    </div>
  )
}