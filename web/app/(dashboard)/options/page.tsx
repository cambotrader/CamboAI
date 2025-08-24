export default function OptionsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Options</h1>
      <div className="grid gap-6">
        <section className="bg-slate-900/60 border border-slate-800 rounded-lg p-4">
          <h2 className="font-medium mb-2">Options Scanner</h2>
          <div className="text-slate-400 text-sm">Filters: IV, delta, theta, volume, OI…</div>
        </section>
        <section className="bg-slate-900/60 border border-slate-800 rounded-lg p-4">
          <h2 className="font-medium mb-2">Strategy Builder</h2>
          <div className="text-slate-400 text-sm">Straddle/strangle/spreads; payoff chart</div>
        </section>
        <section className="bg-slate-900/60 border border-slate-800 rounded-lg p-4">
          <h2 className="font-medium mb-2">Calculators</h2>
          <div className="text-slate-400 text-sm">Pricing, Greeks, IV rank</div>
        </section>
      </div>
    </div>
  )
}