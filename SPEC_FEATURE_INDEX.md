# CamboAI Spec Feature Index (Derived from Attached TXT Specs)

Generated: 2025-08-24
Source folders scanned: docs/specs/D_project, D_TraderStation, User_TraderStation, Desktop (selected strategic *.txt files provided in attachments).

## Legend
Status:
- EXISTS: Implemented in current codebase (at least basic module present)
- PARTIAL: Some capability present; fuller vision in specs
- MISSING: Not yet implemented
- PLANNED: Scaffold created this session
Priority (P1 = immediate high-impact, P2 = near-term, P3 = later / nice-to-have)

## Core Engine & Visualization
| Feature | Spec Name(s) | Status | Priority | Notes / Gap | Suggested Module Path | First MVP Action |
|---------|--------------|--------|----------|-------------|------------------------|------------------|
| Multi-Source Chart Engine | Charting Systems Module, Vision Modular | PARTIAL | P1 | Basic Plotly in `streamlit_app.py`; missing provider toggles (TradingView embed, TrendSpider, etc.) | `modules/chart_module.py` + new `modules/panels/chart_sources.py` | Add provider registry + toggle UI + embed TradingView iframe |
| Candlestick Pattern Lab | Vision Modular, Pattern Lab | PARTIAL | P1 | Current `pattern_engine` limited; need 50+ pattern catalog & volume confirmation | `modules/pattern_engine.py` | Expand pattern list + volume filter + bias tags |
| Chart Pattern Recognizer | Vision Modular | MISSING | P1 | Only candlestick patterns now; no advanced chart shapes | `modules/pattern_engine.py` or new `modules/chart_patterns.py` | Implement H&S / Triangles via swing point detection |
| Options Intelligence Hub | Options Intelligence, Project Ultimate AI | MISSING | P2 | No options greeks/strategies module present | `modules/options/` | Create basic payoff calculator (call/put spreads) |
| MacroMap Panel | MacroMap, Macro Radar | MISSING | P2 | No macro data ingestion shown | `modules/macro/` | Add FRED / economic API fetch + simple dashboard |
| Display Mode / Layout Manager | Display Mode, Vision Modular | MISSING | P2 | Single Streamlit layout only | `modules/layout/manager.py` | Add layout state + tab/inline toggle registry |

## AI & Strategy
| Feature | Spec Reference | Status | Priority | Notes / Gap | Path | MVP Action |
| AI Strategist War Room (multi-agent debate) | Sidebar Modules, War Room | MISSING | P2 | Need agent orchestration & consensus scoring | `modules/ai/war_room.py` | Stub agents + vote weighting |
| AI Strategy Engine & Screener | strategy_engine.py (spec) | PLANNED | P1 | Scaffold dir made; logic absent | `modules/strategy/strategy_engine.py` | Define strategy interface + simple rule engine |
| Scanner (order flow / sentiment / macro) | Sidebar Modules, Institutional Detection | MISSING | P1 | Need pluggable data sources | `modules/scan/scanner.py` | Framework class + dummy sentiment + volume spike rule |
| Institutional Activity Detection | How AI Detects Institutional Activity | MISSING | P2 | Microstructure & dark pool analytics absent | `modules/institutional/` | Data model + placeholder detectors |
| Pattern Generator AI (auto-labeler) | Expansion Injectors | MISSING | P3 | Could leverage ML; not required early | `modules/pattern_ml/` | Store screenshots + placeholder label fn |
| Strategy Forecast Engine | Add-ons list | MISSING | P3 | Predictive modeling not present | `modules/strategy/forecast.py` | Simple moving average crossover forecast |
| Trade Plan Generator | Sidebar Modules | MISSING | P1 | Compose entry/exit narrative & SL/TP from signals | `modules/strategy/plan_generator.py` | Template builder assembling current pattern + sentiment |
| Signal Fusion / Sentiment Integration | Connect pattern & sentiment, fusion | PARTIAL | P1 | Basic sentiment folded into signals; no modular fusion weights | `modules/fusion_engine.py` | Add weighted config + JSON schema |

## Sentiment, News, Education
| Feature | Spec | Status | Priority | Notes | Path | MVP Action |
| Sentiment & News Intelligence | Project Ultimate AI, Vision | PARTIAL | P1 | Existing `news_sentiment` minimal; needs multi-source & FinBERT zones | `modules/news_sentiment.py` | Add provider adapters & FinBERT stub interface |
| FinBERT Sentiment Zones | Cockpit Master, Sentiment upgrades | MISSING | P1 | No model integration currently | `modules/sentiment/finbert.py` | Placeholder scoring function + zone bucketing |
| Education Center (curriculum, levels) | education_module variants | PARTIAL | P2 | Present patterns & tutorials; lacks quizzes, flashcards | `modules/education_module.py` | Add quiz data structure |
| AI Trading Journal & Journey Analyzer | Project Ultimate AI | MISSING | P2 | No journal module | `modules/journal/journal_module.py` | Basic trade entry dataclass + JSON persistence |
| Psychology Profiler / Emotional Grid | Emotional Grid, Core Tenets | MISSING | P3 | Narrative / belief engine absent | `modules/psychology/profiler.py` | Track simple metrics (streaks, win rate) |

## Execution, Integration & Ops
| Feature | Spec | Status | Priority | Notes | Path | MVP Action |
| Broker API Adapter | Injectors list | MISSING | P2 | No broker integration aside from placeholders | `modules/broker/adapters/alpaca.py` | Mock submit_order() |
| Backtesting & Simulation Lab | Project Ultimate AI | MISSING | P2 | No backtesting engine integrated | `modules/backtest/` | Wrap vectorbt/backtrader optional dependency guard |
| Alerts & Notifications | Project Ultimate AI | MISSING | P2 | No alert dispatch layer | `modules/alerts/dispatcher.py` | Simple rule triggers + print/webhook |
| Signal Broadcast Layer | Injectors | MISSING | P2 | Requires multi-channel output | `modules/alerts/broadcast.py` | Slack/Webhook stub |
| Integrity Monitor | Injectors | MISSING | P3 | System health & config drift | `modules/ops/integrity.py` | Validate versions + env keys |
| Automation & Webhook Center | Add-ons | MISSING | P3 | Orchestrate event actions | `modules/automation/center.py` | Register event -> webhook map |
| CrewAI / Multi-Agent Hub | Add-ons | MISSING | P3 | External agent frameworks | `modules/ai/agents.py` | Config stub referencing providers |
| Voice Interface | voice_interface module ref | MISSING | P3 | No voice command parsing now | `modules/voice/interface.py` | Parse command strings -> actions |

## Data & Macro
| Feature | Spec | Status | Priority | Notes | Path | MVP Action |
| Volatility Sync Engine | Injectors | MISSING | P2 | No VIX or ATR integration beyond basic indicators | `modules/volatility/sync.py` | Fetch VIX from yfinance + attach to signals |
| Macro Radar Panel | Add-ons & MacroMap | MISSING | P2 | Need economic calendar | `modules/macro/radar.py` | Pull FRED series sample |
| Alternative Data Integrations | Institutional toolkit | MISSING | P3 | Satellite/credit card data out-of-scope early | `modules/altdata/` | Placeholder loaders |

## Layout, UX & Orchestration
| Feature | Spec | Status | Priority | Notes | Path | MVP Action |
| Display Mode (inline/tab/window) | Sidebar Modules | MISSING | P2 | Need dynamic panel registry | `modules/layout/manager.py` | Registry + toggle-state serialization |
| Layout Bookmarking / Workspace Profiles | Add-ons | MISSING | P3 | Save/restore UI state | `modules/layout/profiles.py` | Save selected modules to JSON |
| Mobile PWA Mode | Add-ons | MISSING | P3 | Needs frontend changes (web-advanced) | frontend (Next.js) | Add manifest + service worker |

## Security & Governance
| Feature | Spec | Status | Priority | Notes | Path | MVP Action |
| API Key Security (already present) | Not specifically in spec | EXISTS | P1 | Implemented env key check | backend/app/core/api_key.py | Harden prefix rules |
| Audit / Logging Enhancements | Implied by scaling | PARTIAL | P2 | Logging utilities exist; no structured event bus | `backend/app/core/logging.py` | Add structured JSON logs |

## Spec Meta / Memory
| Feature | Spec | Status | Priority | Notes | Path | MVP Action |
| Project Memory Log / Belief System | How I'll Remember Everything, Core Tenets | MISSING | P3 | Could store evolving doctrine & strategy context | `modules/psychology/memory_log.py` | Append log entries with timestamp & tag |

## Summary Counts
- EXISTING: 2
- PARTIAL: 7
- PLANNED: 1
- MISSING (to implement): 30+

## Recommended Immediate Implementation Order (Next 5)
1. Strategy Engine scaffold (`modules/strategy/strategy_engine.py`) + simple rule-based signal aggregator.
2. Trade Plan Generator (narrative + entry/exit formatting) feeding Streamlit signals tab.
3. Scanner framework with pluggable data sources (price, pattern, sentiment).
4. Expanded Sentiment (multi-source adapters + FinBERT zone stub).
5. Chart Pattern Recognizer (H&S + Triangle detection MVP).

## Cross-Cutting Architecture Notes
- Introduce a central Feature Registry (dict of feature_id -> capability object) for toggles & layout manager.
- Adopt dataclasses or Pydantic models for StrategySignal, PatternDetection, SentimentSnapshot.
- Provide async-friendly adapters (use httpx) for external API calls.
- Use a light plugin interface for future broker & alert channels.
- Defer heavy ML (pattern ML generator, advanced institutional detection) until core deterministic modules stable.

---
Generated automatically; update this index as modules are added.
