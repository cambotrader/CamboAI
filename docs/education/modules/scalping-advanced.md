# Scalping Advanced

## Advanced Objectives
- Optimize entries using microstructure (tape, level 2, footprint)
- Identify high-probability “impulse windows” around session opens/overlaps
- Manage execution risk with queue position and partial fills (where applicable)

## Tools & Data
- DOM/Level 2 and Time & Sales (if available)
- Footprint/cumulative delta for futures/FX proxies
- Session VWAP + bands, Anchored VWAP at key events
- 9/20 EMA for momentum bias, ATR(14) for volatility bounds

## Advanced Setups
- VWAP Reclaim + Delta Confirmation: pullback holds above VWAP, delta increasing, tight risk below reclaim
- Liquidity Sweep + Reversal: sweep prior low, immediate absorption, HL structure + MACD hist uptick
- Opening Range Break + Retest: ORB with measured move; enter on retest with tight invalidation

## Risk & Trade Management
- Micro stops (structure-based) + quick invalidation; expect win rate > expectancy via tight stops
- Scale out at +1R and +2R; leave runner to VWAP band/structure
- Daily circuit breaker: max 2–3R

## Metrics to Track
- Time in trade, slippage, spread cost, adverse excursion, % entries at micro pullback vs breakout

## Drills
- Replay: enter only on pullback to 9/20 EMA after reclaim, 50 samples
- Footprint: mark absorption vs continuation examples, 50 samples