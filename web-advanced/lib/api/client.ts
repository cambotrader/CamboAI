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

// Portfolio API
export async function getPortfolioPositions() {
  const res = await fetch(`${base()}/api/portfolio/positions`, { cache: 'no-store' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getPortfolioSummary() {
  const res = await fetch(`${base()}/api/portfolio/summary`, { cache: 'no-store' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getPortfolioPerformance(days: number = 90) {
  const res = await fetch(`${base()}/api/portfolio/performance?days=${days}`, { cache: 'no-store' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// Risk API
export async function getPortfolioRisk(portfolioId: string, days: number = 90) {
  const res = await fetch(`${base()}/api/risk/portfolio/${portfolioId}/analysis?days=${days}`, { cache: 'no-store' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// Trading API
export async function placeOrder(order: any) {
  const res = await fetch(`${base()}/api/trading/order`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(order),
    cache: 'no-store',
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getTradingPositions() {
  const res = await fetch(`${base()}/api/trading/positions`, { cache: 'no-store' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getOrders() {
  const res = await fetch(`${base()}/api/trading/orders`, { cache: 'no-store' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// War Room API
export async function runDebate(payload: any) {
  const res = await fetch(`${base()}/api/war-room/debate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    cache: 'no-store',
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// Learning API
export async function getCourses() {
  const res = await fetch(`${base()}/api/learning/courses`, { cache: 'no-store' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getCourseDetails(courseId: string) {
  const res = await fetch(`${base()}/api/learning/courses/${courseId}`, { cache: 'no-store' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}