# 🚀 CamboStation™ Vision

**CamboStation™ Vision** is a next-generation, modular, AI-powered personal trading cockpit designed for solo deployment using free-tier APIs, open-source tools, and elite-grade automation. It enables traders to educate, simulate, strategize, analyze, and execute across all major asset classes — including stocks, crypto, options, forex, futures, commodities, bonds, T-bills, and warrants — while evolving alongside your skills and insights.

---

## 🧠 System Highlights

- Streamlit frontend + FastAPI backend + Docker Compose orchestration  
- PostgreSQL/Supabase + Redis for stateful storage and caching  
- Toggle-ready AI agents: Copilot, ChatGPT, Gemini, Grok, TradeGPT, Claude, DeepSeek, LangChain, CrewAI, Perplexity  
- Fully modular: charting, education, screener, sentiment, execution, journaling, simulation  
- Works with free data feeds, community-tier brokers, and self-hosted environments  
- Compatible with mobile (PWA mode), voice control, and mentor-led learning  

---

## 📦 Core Modules (Plug & Play Tabs)

- 📊 **Market Chart Panel**  
  Real-time charts (candlestick, OHLC, Heikin Ashi, Renko, DOM) with overlays (RSI, MACD, Bollinger, VWAP, SuperTrend). Sources: TradingView, TC2000, Plotly, TrendSpider, Investing.com, Binance, Coinbase, NinjaTrader, ThinkorSwim, and more. All sources toggle-enabled with sign-in options via API, OAuth, or iframe embed.

- 🕯️ **Candlestick Pattern Lab**  
  Detects 50+ candlestick patterns, classifies bias 🟢🔴⚪🌀, and annotates confidence, breakout zones, and sentiment overlays using FinBERT/VADER.

- 📘 **Chart Pattern Recognizer**  
  Tags and explains Head & Shoulders, Cup & Handle, Flags, Triangles, Broadening Wedges, Diamond Tops, Island Reversals, and more — with volume validation and trade-ready overlays.

- 🧠 **Options Strategy Hub**  
  Strategy builder with payoff graphs, risk tables, IV maps, stop-loss logic. Strategies categorized by bias: Bullish, Bearish, Neutral, Volatile, Advanced. Includes Jade Lizards, Iron Flies, Diagonals, Collars, Box Spreads.

- 🔍 **AI Strategy Engine & Screener**  
  Combines TA logic, sentiment overlays, macro triggers, insider data, and volume conditions to build actionable strategies with AI grading and auto-routing to execution panels.

- 📉 **Sentiment & News Intelligence**  
  Live data from Reddit, Twitter/X, StockTwits, NewsAPI.org, Whale Alert, OpenInsider, EDGAR, analyst notes. Emoji tone scoring, timestamp tagging, influencer heatmaps, and macro interpretation included.

- 💼 **Broker Integration Panel**  
  Sync with Alpaca, TDAmeritrade, Interactive Brokers, Robinhood, Fidelity, Binance, Coinbase, Kraken, eToro, Webull, NinjaTrader. Features include live trading, Level 2/3, order templates, DOM viewer, equity curves.

- 🧪 **Backtesting & Simulation Lab**  
  Replay trade setups with Backtrader, vectorbt, mlfinlab, TA-Lib. View strategy metrics (CAGR, Sharpe, Max Drawdown) and use scenario builder for AI-ranked outcomes.

- 🎓 **Advanced Education Center**  
  Learn to trade stocks, crypto, options, forex, commodities, T-bills, warrants. Includes short- and long-term investing, macro theory, risk profiling, trading psychology. Quizzes, flashcards, mentorship mode, Ask-AI explainers, and simulation-based learning included.

- 📔 **AI Trading Journal & Journey Analyzer**  
  Logs trades, emotions, chart states, strategies, and outcomes. AI detects performance habits, emotion patterns, and suggests improvements. Supports voice input, screenshot grading, markdown export, and tax tagging.

---

## 🧩 Add-on Extensions (Toggle-Based)

- 📱 Mobile PWA Mode  
- 🔁 Trade Replay Engine  
- 🎙️ Voice Ask Mode  
- 📡 Macro Radar Panel  
- 📊 Strategy Snapshot Manager  
- 📈 Strategy Forecast Engine  
- 📥 Pattern Image Learner  
- 🧬 Psychology Profiler  
- 📚 Mentorship Mode  
- 🔁 Scenario Builder  
- 🧾 Tax Dashboard + Form 8949  
- 💬 AI Feedback Thread  
- 📤 Broker Aggregator  
- 🔗 Webhook Automation Center  
- 🧠 CrewAI Multi-Agent Hub  
- 🧪 LangChain Plugin Expansion  
- 🎬 Video Annotator (Coming Soon)  
- 🖥️ Layout Bookmarks & Workspace Profiles

---

## 🔐 AI Selector Panel

Choose your AI co-pilot per task. Supported integrations:

- Microsoft Copilot  
- ChatGPT  
- Gemini  
- Grok (X AI)  
- TradeGPT  
- TTG AI  
- DeepSeek  
- Claude  
- CrewAI  
- LangChain  
- Perplexity AI

Supports sign-in via API keys, OAuth, browser session, iframe, or plugin token.

---

## ⚙️ Stack Summary

| Layer        | Technology                                         |
|--------------|----------------------------------------------------|
| Frontend     | Streamlit, React, Plotly, Tailwind, Chart.js       |
| Backend      | FastAPI, Node.js, Docker Compose                   |
| Storage      | PostgreSQL, Supabase, SQLite, Redis (Free Tier)    |
| AI & NLP     | FinBERT, VADER, LangChain, CrewAI, mlfinlab        |
| Brokers      | Alpaca, IBKR, TDA, Robinhood, Binance, Coinbase    |

---

## 🚀 Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Launch CamboStation Vision
streamlit run dashboard.py
