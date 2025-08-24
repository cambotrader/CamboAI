import { NextRequest, NextResponse } from "next/server";

// Minimal server-side OHLC proxy to avoid CORS and use no-key sources
// Supports: type=stock (Yahoo Finance) and type=crypto (Binance)

function json(data: any, init?: number) {
  return NextResponse.json(data, { status: init || 200 });
}

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const symbol = (searchParams.get("symbol") || "AAPL").toUpperCase();
    const type = (searchParams.get("type") || "stock").toLowerCase(); // 'stock' | 'crypto'
    const interval = searchParams.get("interval") || (type === "crypto" ? "1h" : "1d");
    const range = searchParams.get("range") || (type === "crypto" ? "1w" : "1mo");

    if (!symbol) return json({ error: "symbol is required" }, 400);

    if (type === "crypto") {
      // Binance klines
      const binanceIntervalMap: Record<string, string> = {
        "1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"
      };
      const iv = binanceIntervalMap[interval] || "1h";

      const url = `https://api.binance.com/api/v3/klines?symbol=${encodeURIComponent(symbol)}&interval=${iv}&limit=500`;
      const res = await fetch(url, { next: { revalidate: 60 } });
      if (!res.ok) return json({ error: "failed_fetch_binance", status: res.status }, 502);
      const raw = await res.json();

      // Binance returns array of arrays
      const candles = raw.map((k: any[]) => ({
        t: k[0],
        o: parseFloat(k[1]),
        h: parseFloat(k[2]),
        l: parseFloat(k[3]),
        c: parseFloat(k[4]),
        v: parseFloat(k[5])
      }));

      return json({ source: "binance", symbol, interval: iv, candles });
    } else {
      // Yahoo Finance chart API
      // range examples: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
      // interval examples: 1m,2m,5m,15m,1d,1wk,1mo
      const yfInterval = interval;
      const yfRange = range;
      const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?interval=${yfInterval}&range=${yfRange}`;
      const res = await fetch(url, { next: { revalidate: 60 } });
      if (!res.ok) return json({ error: "failed_fetch_yahoo", status: res.status }, 502);
      const data = await res.json();
      const result = data?.chart?.result?.[0];
      if (!result) return json({ error: "invalid_yahoo_response" }, 502);

      const timestamps: number[] = result.timestamp || [];
      const indicators = result.indicators?.quote?.[0] || {};
      const volumes: number[] = indicators.volume || [];
      const opens: number[] = indicators.open || [];
      const highs: number[] = indicators.high || [];
      const lows: number[] = indicators.low || [];
      const closes: number[] = indicators.close || [];

      const candles = timestamps.map((t: number, i: number) => ({
        t: t * 1000,
        o: opens[i] ?? null,
        h: highs[i] ?? null,
        l: lows[i] ?? null,
        c: closes[i] ?? null,
        v: volumes[i] ?? null,
      })).filter(c => c.o != null && c.h != null && c.l != null && c.c != null);

      return json({ source: "yahoo", symbol, interval: yfInterval, range: yfRange, candles });
    }
  } catch (err: any) {
    return json({ error: "unexpected_error", message: err?.message || String(err) }, 500);
  }
}