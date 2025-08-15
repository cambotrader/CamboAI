import { FootprintBar, FootprintLevel, FootprintCalcOptions, ProcessedFootprintBar } from "../types/footprint";

// Helper: round price to nearest valid tick
const roundToTick = (p: number, tick: number) => Math.round(p / tick) * tick;

// Build empty price ladder between low/high inclusive using tick size
function buildLadder(low: number, high: number, tick: number): FootprintLevel[] {
  const ladder: FootprintLevel[] = [];
  // Ensure correct ordering high -> low (descending) for display
  for (let price = high; price >= low - 1e-9; price = +(price - tick).toFixed(10)) {
    ladder.push({ price: +price.toFixed(10), bid: 0, ask: 0 });
  }
  return ladder;
}

// Merge existing ladder with trades (mock). Real implementation should allocate per-trade volumes.
// For now we accept an optional granular trades array later; here we just proportionally distribute volume.
export interface BasicBarInput {
  time: number; open: number; high: number; low: number; close: number; volume: number;
}

export function buildFootprintFromBars(bars: BasicBarInput[], opts: FootprintCalcOptions): ProcessedFootprintBar[] {
  return bars.map(bar => buildSingleFootprintBar(bar, opts));
}

function buildSingleFootprintBar(bar: BasicBarInput, opts: FootprintCalcOptions): ProcessedFootprintBar {
  const { tickSize, imbalanceMultiplier, minDeltaAbs, clampLevels } = opts;
  const low = Math.floor(bar.low / tickSize) * tickSize;
  const high = Math.ceil(bar.high / tickSize) * tickSize;
  let ladder = buildLadder(low, high, tickSize);

  // Naive distribution: allocate half volume to ask for up move segments and half to bid (placeholder)
  // TODO: Replace with actual bid/ask trade data when available.
  const totalLevels = ladder.length;
  ladder.forEach((lvl, idx) => {
    // Simple skew: closer to high -> more ask, closer to low -> more bid
    const weight = totalLevels <= 1 ? 0.5 : idx / (totalLevels - 1);
    const askPortion = 0.4 + 0.6 * (1 - weight); // inverted for descending loop
    const askVol = Math.round(bar.volume * askPortion / totalLevels);
    const bidVol = Math.round(bar.volume / totalLevels - askVol);
    lvl.ask += Math.max(0, askVol);
    lvl.bid += Math.max(0, bidVol);
    lvl.delta = lvl.ask - lvl.bid;
  });

  // Imbalance detection (common rule: ask at level > multiplier * bid at previous level => bullish imbalance)
  for (let i = 0; i < ladder.length; i++) {
    const cur = ladder[i];
    const nextBelow = ladder[i + 1];
    if (nextBelow) {
      // Upward imbalance: current ask vs next bid
      if (nextBelow.bid > 0 && cur.ask / nextBelow.bid >= imbalanceMultiplier && Math.abs(cur.ask - nextBelow.bid) >= minDeltaAbs) {
        cur.imbalanceUp = true;
      }
      // Downward imbalance: current bid vs next ask
      if (cur.bid > 0 && nextBelow.ask / cur.bid >= imbalanceMultiplier && Math.abs(nextBelow.ask - cur.bid) >= minDeltaAbs) {
        nextBelow.imbalanceDown = true;
      }
    }
  }

  // Clamp depth if requested
  if (clampLevels && ladder.length > clampLevels) {
    ladder = ladder.slice(0, clampLevels);
  }

  const totalVolume = ladder.reduce((s, l) => s + l.ask + l.bid, 0);
  const totalDelta = ladder.reduce((s, l) => s + (l.delta || 0), 0);
  const maxAbsDelta = Math.max(...ladder.map(l => Math.abs(l.delta || 0)));

  return {
    time: bar.time,
    open: bar.open,
    high: bar.high,
    low: bar.low,
    close: bar.close,
    levels: ladder,
    totalVolume,
    totalDelta,
    maxAbsDelta,
  };
}
