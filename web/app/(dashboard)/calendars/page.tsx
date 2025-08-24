export default function CalendarsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Calendars</h1>
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="bg-slate-900/60 border border-slate-800 rounded-lg p-4">
          <h2 className="font-medium mb-2">Economic Calendar</h2>
          <div className="text-slate-400 text-sm">Region/importance filters</div>
        </section>
        <section className="bg-slate-900/60 border border-slate-800 rounded-lg p-4">
          <h2 className="font-medium mb-2">Earnings Calendar</h2>
          <div className="text-slate-400 text-sm">Upcoming earnings, surprises</div>
        </section>
      </div>
    </div>
  )
}