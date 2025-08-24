# CamboAI Build Checklist

Status keys: [x] done, [~] in progress, [ ] pending

## Backend (FastAPI)
- [x] Core routers: market data (crypto/fx/options), patterns, sentiment, signals, analysis, risk (v1/v2), portfolio (v1), trading, providers, community chat
- [x] Metrics: Prometheus counters/histograms/gauges; /metrics endpoint
- [x] Health/Readiness: /health, /ready endpoints
- [x] Caching: Redis optional TTL; cache hit/miss metrics
- [x] Secret encryption utility (Fernet); tests present
- [~] Central HTTP client (timeouts, retries/backoff, UA, request-id propagation)
- [~] Circuit breakers for external providers (Polygon/Yahoo)
- [ ] Batch OHLCV endpoints (multi-symbol) + pagination and rate limits
- [ ] PAT endpoints + middleware and quotas
- [ ] Supabase JWT verification (feature-flagged)
- [ ] Embed token issuance (scoped, short TTL)
- [ ] Provider health checks integrated into /ready
- [ ] Tests for retries/circuit breakers/auth; k6 load baseline

## Frontend — web (Next.js)
- [x] App structure: landing, auth, dashboard, profile, projects, trading
- [x] Supabase SSR client scaffolding (lib/supabase)
- [ ] Wire Supabase auth flows (after keys)
- [ ] Hook modules to API: Signals, Risk, Patterns, Education
- [ ] Configure API base for prod via NEXT_PUBLIC_API_URL or rewrites

## Frontend — web-advanced (Next.js)
- [x] API client for options/alerts/hedging/portfolio/risk/trading/learning
- [ ] Supabase auth wiring
- [ ] Hydration safeguards + proxy rewrites
- [ ] Embed-ready components

## Dashboard (Streamlit)
- [x] Basic app, charts, indicators, API utils, Dockerfile
- [ ] Align auth and API base; optional free tier support

## Mobile (Expo/React Native)
- [x] Project scaffold, src/config, EAS
- [ ] Supabase auth integration
- [ ] Screens hooked to API, deep links

## DevOps / Infra
- [x] Dockerfiles, compose variants, Render/Vercel scripts
- [x] Cloudflare tunnel scripts, Prometheus/Grafana configs
- [ ] DNS: api.camboai.com -> Render; camboai.com/www -> Vercel
- [ ] Env setup: Supabase vars, API URL, SECRET_ENC_KEY on Render/Vercel
- [ ] CI gates: lint/type/test, preview deployments

## Website/Marketing
- [ ] Polished landing, pricing, signup; CTAs into app; analytics

## Security/Compliance
- [x] Basic headers, rate limiter middleware registrations
- [ ] JWT verification (Supabase JWKs), PAT quotas
- [ ] Secret scrubber, masked logs, HSTS

---

Last updated: {update_date}