export type ApiPreset = 'fast' | 'balanced' | 'high'

function base(): string {
  const env = process.env.NEXT_PUBLIC_API_BASE
  if (env && env.length > 0) return env
  // Next.js rewrites will proxy /api/* to backend in dev
  return ''
}

export async function priceMultiLeg(payload: any) {
  const res = await fetch(`${base()}/api/options/price/multi-leg`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    cache: 'no-store',
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getPresets() {
  const res = await fetch(`${base()}/api/options/presets`, { cache: 'no-store' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// Alerts API
export async function getAlertRules() {
  const res = await fetch(`${base()}/api/alerts/rules`, { cache: 'no-store' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function createAlertRule(payload: any) {
  const res = await fetch(`${base()}/api/alerts/rules`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    cache: 'no-store',
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function runAlerts() {
  const res = await fetch(`${base()}/api/alerts/run`, {
    method: 'POST',
    cache: 'no-store',
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// Hedging API
export async function deltaHedgeBacktest(payload: any) {
  const res = await fetch(`${base()}/api/options/hedging/delta`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    cache: 'no-store',
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}