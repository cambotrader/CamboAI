# Error Budgets and SLOs (Draft)

## Services
- Signals v2 API: /api/v2/signals
- Sentiment v2 API: /api/v2/sentiment/aggregate
- Risk v2 API: /api/v2/risk/summary
- Market Data Router (providers + cache)

## SLIs (per 5m window)
- Availability (success rate): 1 - (5xx + network_errors) / total_requests
- Latency p95: request duration at 95th percentile
- Freshness: market data last_updated_age_seconds (Gauge) under threshold
- Cache hit rate: cache_hits_total / (cache_hits_total + cache_misses_total)

## SLOs
- Availability: >= 99.9% monthly for v2 APIs
- Latency: p95 <= 300ms intra-region (excludes data vendor latency); p99 <= 800ms
- Freshness: OHLCV data age <= 10s for real-time; <= 60s for end-of-day
- Cache Hit Rate: >= 70% for repeated symbol/interval queries

## Error Budgets (per 30 days)
- Availability: 0.1% budget (~43m downtime or 0.1% error responses)
- Latency: 5% budget where p95 exceeds SLO

## Policies
- Burn >50% in 7 days: Freeze feature rollouts, focus on reliability
- Burn >80% anytime: Immediate incident review and rollback risky changes

## Alerting (Prometheus rules examples)
- Availability breach (5m):
  - expr: (sum(rate(http_request_total{status=~"5.."}[5m])) / sum(rate(http_request_total[5m]))) > 0.001
- Latency p95 breach (10m):
  - expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[10m])) by (le)) > 0.3
- Cache efficiency low (30m):
  - expr: (rate(cache_hits_total[30m]) / (rate(cache_hits_total[30m]) + rate(cache_misses_total[30m]))) < 0.5

## Dashboards
- Request rate, error rate, latency (p50/p95/p99)
- Market data provider mix and cache hit ratio
- Sentiment v2 throughput and response distributions
- Risk v2 compute time and fallback usage

## Next Steps
- Add RED/USE panels (per endpoint) to Grafana
- Add per-endpoint labels to metrics (already present) in dashboards
- Wire alerts to Slack/Email