// Footprint (bid/ask volume at price) data structures
export interface FootprintLevel {
  price: number;          // price level
  bid: number;            // bid volume traded at this price
  ask: number;            // ask volume traded at this price
  delta?: number;         // ask - bid
  imbalanceUp?: boolean;  // true if upward imbalance (ask >> prior bid)
  imbalanceDown?: boolean;// true if downward imbalance (bid >> next ask)
}

export interface FootprintBar {
  time: number;           // epoch ms
  open: number;
  high: number;
  low: number;
  close: number;
  levels: FootprintLevel[]; // sorted DESC by price
  totalVolume?: number;
  totalDelta?: number;    // sum of level deltas
  maxAbsDelta?: number;   // largest |delta| among levels
}

export interface ImbalanceConfig {
  tickSize: number;            // e.g. 0.25, 1, etc.
  imbalanceMultiplier: number; // e.g. 3 => 300%
  minDeltaAbs: number;         // e.g. 100 (imbDelta1)
}

export interface FootprintCalcOptions extends ImbalanceConfig {
  clampLevels?: number;        // optionally limit depth (imprintCount)
}

export interface ProcessedFootprintBar extends FootprintBar {
  vah?: number; // optional future enhancements
  val?: number;
  pocPrice?: number;
}
