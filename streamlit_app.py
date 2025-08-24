import streamlit as st
import requests
import pandas as pd

# CamboAI TraderStation (temporary Streamlit cockpit)
st.set_page_config(page_title='CamboAI TraderStation', layout='wide', initial_sidebar_state='expanded')
st.title('🚀 CamboAI TraderStation — Complete AI Trading Platform')
st.caption('📈 Charts • 🕯️ Pattern Detection • 🧠 AI Signals • 📰 Sentiment • 📚 Education')

# Check if running in standalone mode (no backend)
def is_backend_available(url="http://localhost:8000"):
    try:
        response = requests.get(f"{url}/health", timeout=1)
        return response.status_code == 200
    except:
        return False

# Display mode indicator
if is_backend_available():
    st.success("🔗 Connected to CamboAI Backend API")
else:
    st.info("🚀 **Standalone Mode** - Charts & sentiment analysis working independently (Backend API not required)")

st.sidebar.header('Control Panel')
# Basic inputs
symbol = st.sidebar.text_input('Ticker', value='AAPL').upper()
interval = st.sidebar.selectbox('Interval', ['1d', '1h', '15m', '5m'], index=0)
period = st.sidebar.selectbox('History', ['1y', '6mo', '3mo', '1mo'], index=0)
api_key = st.sidebar.text_input('X-API-Key (optional, for backend calls)', value='', type='password')

show_bands = st.sidebar.checkbox('Show Bollinger Bands', value=True)
show_rsi = st.sidebar.checkbox('Compute RSI (tooltip only)', value=False)
show_sentiment = st.sidebar.checkbox('Show Sentiment Panel', value=True)

status_exp = st.sidebar.expander('Backend Status (Optional)', expanded=False)
with status_exp:
    st.caption("⚡ App works independently - Backend connection is optional for enhanced features")
    backend_url = st.text_input('Backend URL', value='http://localhost:8000')
    if st.button('Test Backend Connection', key='check_backend'):
        headers = {'X-API-Key': api_key} if api_key else {}
        try:
            h = requests.get(f"{backend_url}/health", headers=headers, timeout=3)
            r = requests.get(f"{backend_url}/ready", headers=headers, timeout=3)
            st.write('Health:', h.status_code, h.json() if str(h.headers.get('content-type','')).startswith('application/json') else h.text)
            st.write('Ready:', r.status_code, r.json() if str(r.headers.get('content-type','')).startswith('application/json') else r.text)
            if h.ok and r.ok:
                st.success('✅ Backend API connected successfully!')
            else:
                st.warning('⚠️ Backend returned non-OK status codes')
        except Exception as e:
            st.info(f'ℹ️ Backend not available: {e}\n\n**No worries!** The app works perfectly in standalone mode.')

st.divider()

# Tabs - Full CamboAI TraderStation
chart_tab, pattern_tab, signal_tab, sentiment_tab, education_tab = st.tabs(["📈 Chart", "🕯️ Patterns", "🧠 AI Signals", "📰 Sentiment", "📚 Education"])

with chart_tab:
    st.subheader('Price & Volume')
    import yfinance as yf
    from modules.chart_module import render_chart
    with st.spinner('Loading price data...'):
        try:
            df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
            # Fix multi-level columns issue
            if hasattr(df.columns, 'nlevels') and df.columns.nlevels > 1:
                df.columns = df.columns.droplevel(1)
            # Ensure columns are properly named and 1D
            if not df.empty:
                expected_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                for col in expected_cols:
                    if col in df.columns:
                        # Flatten any multi-dimensional columns
                        df[col] = df[col].squeeze()
        except Exception as e:
            df = pd.DataFrame()
            st.warning(f'Unable to fetch data: {e}')
    if df is None or df.empty:
        # Provide a small fallback synthetic dataset
        st.info('No data received. Showing a small sample dataset.')
        try:
            dates = pd.date_range(end=pd.Timestamp.utcnow(), periods=60, freq='D')
            base = 150.0
            close = pd.Series(base + pd.Series(range(60)).rolling(5, min_periods=1).mean().fillna(0).values).clip(lower=1)
            df = pd.DataFrame({
                'Open': close + 0.5,
                'High': close + 1.0,
                'Low': close - 1.0,
                'Close': close,
                'Volume': 1_000_000,
            }, index=dates)
        except Exception:
            df = pd.DataFrame()
    if df is None or df.empty:
        st.warning('Still no data. Try another symbol or period.')
    else:
        try:
            fig = render_chart(df, title=f"{symbol} Tactical Chart", show_bands=show_bands, show_rsi=show_rsi)
            st.plotly_chart(fig, use_container_width=True)
            st.caption('Overlays: MA50, MA200, optional Bollinger Bands. RSI computed if enabled.')
        except Exception as e:
            st.error(f'Chart error: {e}')

with pattern_tab:
    st.subheader('🕯️ Candlestick Pattern Detection')
    if not df.empty:
        try:
            from modules.pattern_engine import analyze
            with st.spinner('Analyzing candlestick patterns...'):
                pattern_result = analyze(df)
                patterns = pattern_result.get('signals', [])
                
            if patterns:
                st.success(f"🎯 **{len(patterns)} patterns detected** on latest candle")
                
                # Display patterns in columns
                cols = st.columns(min(3, len(patterns)))
                for i, pattern in enumerate(patterns[:6]):  # Show max 6 patterns
                    with cols[i % 3]:
                        direction_emoji = "🟢" if pattern.get('direction') == 'bullish' else "🔴" if pattern.get('direction') == 'bearish' else "🟡"
                        confidence = pattern.get('confidence', 0.5)
                        
                        st.metric(
                            label=f"{direction_emoji} {pattern.get('type', 'Unknown').replace('_', ' ').title()}",
                            value=f"{confidence:.1%}",
                            delta=pattern.get('direction', 'neutral').title()
                        )
                        
                        if pattern.get('meta'):
                            st.caption(f"Details: {pattern['meta']}")
                
                # Pattern summary table
                st.divider()
                pattern_df = pd.DataFrame(patterns)
                st.dataframe(pattern_df[['type', 'direction', 'confidence', 'meta']], use_container_width=True)
                
            else:
                st.info("No significant patterns detected on the latest candle.")
                
        except Exception as e:
            st.error(f'Pattern detection error: {e}')
    else:
        st.warning("No price data available for pattern analysis.")

with signal_tab:
    st.subheader('🧠 AI Trading Signals (Fusion Engine)')
    if not df.empty:
        try:
            from modules.ai_engine_switcher import get_signal
            from modules.news_sentiment import get_headlines, score_headlines
            
            # Get sentiment score for fusion
            sentiment_score = 0.0
            try:
                with st.spinner('Getting sentiment data...'):
                    headlines = get_headlines(symbol)
                    scored_headlines = score_headlines(headlines)
                    if scored_headlines:
                        # Calculate average sentiment
                        sentiments = [h.get('sentiment_score', 0.0) for h in scored_headlines if h.get('sentiment_score')]
                        if sentiments:
                            sentiment_score = sum(sentiments) / len(sentiments)
            except:
                sentiment_score = 0.0
            
            with st.spinner('Generating AI trading signal...'):
                signal_result = get_signal(df, sentiment_score)
            
            # Display main signal
            signal_label = signal_result.get('label', 'NEUTRAL')
            signal_score = signal_result.get('score', 0.0)
            confidence = signal_result.get('confidence', 0.0)
            
            # Color coding
            if signal_label == 'BUY':
                color = 'green'
                emoji = '📈'
            elif signal_label == 'SELL':
                color = 'red'
                emoji = '📉'
            else:
                color = 'gray'
                emoji = '⚖️'
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 Signal", f"{emoji} {signal_label}", f"Score: {signal_score:.2f}")
            with col2:
                st.metric("🔒 Confidence", f"{confidence:.1%}")
            with col3:
                st.metric("📊 Sentiment", f"{sentiment_score:.2f}", "Market mood")
            
            # Signal breakdown
            st.divider()
            detail = signal_result.get('detail', {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Pattern Analysis")
                pattern_score = detail.get('pattern_score', 0.0)
                st.write(f"**Pattern Score:** {pattern_score:.2f}")
                if 'pattern_contributions' in detail:
                    for contrib in detail['pattern_contributions'][:5]:  # Top 5
                        st.write(f"• {contrib}")
            
            with col2:
                st.subheader("Signal Details")
                engine = detail.get('engine', 'unknown')
                st.write(f"**Engine Used:** {engine.title()}")
                if 'fallback' in detail:
                    st.info(f"Fallback mode: {detail['fallback']}")
                if 'engine_error' in detail:
                    st.warning(f"Engine error: {detail['engine_error']}")
            
            # Risk disclaimer
            st.divider()
            st.caption("⚠️ **Risk Disclaimer:** This is AI-generated analysis for educational purposes only. Not financial advice. Always do your own research and consider your risk tolerance.")
            
        except Exception as e:
            st.error(f'AI signal generation error: {e}')
    else:
        st.warning("No price data available for AI signal generation.")

with sentiment_tab:
    if show_sentiment:
        st.subheader('News & Sentiment (FinBERT fallback to heuristics)')
        from modules.news_sentiment import get_headlines, score_headlines, build_sentiment_zones
        with st.spinner('Fetching headlines...'):
            try:
                items = get_headlines(symbol)
                scored = score_headlines(items)
            except Exception as e:
                scored = []
                st.error(f'Sentiment error: {e}')
        if not scored:
            st.info('No headlines available right now.')
        else:
            st.dataframe(pd.DataFrame([
                {"time": i.get("time"), "publisher": i.get("publisher"), "tone": f"{i.get('emoji')} {i.get('tone')}", "title": i.get("title"), "link": i.get("link")}
                for i in scored
            ]))
    else:
        st.info('Enable Sentiment Panel from the sidebar.')

with education_tab:
    st.subheader('📚 CamboAI Trading Education Hub')
    
    # Import education module
    from modules.education_module import pattern_glossary, TUTORIALS, TIP_MAP
    
    tab1, tab2, tab3 = st.tabs(["🔍 Pattern Glossary", "📖 Tutorials", "💡 Tips & Tricks"])
    
    with tab1:
        st.subheader("Candlestick Pattern Reference")
        glossary = pattern_glossary()
        
        # Search functionality
        search_term = st.text_input("🔍 Search patterns:", placeholder="e.g., hammer, doji, engulfing")
        
        if search_term:
            filtered_glossary = {k: v for k, v in glossary.items() 
                               if search_term.lower() in k.lower() or search_term.lower() in v.lower()}
        else:
            filtered_glossary = glossary
        
        # Display patterns in expandable cards
        for pattern_name, description in filtered_glossary.items():
            with st.expander(f"🕯️ {pattern_name}"):
                st.write(description)
                
                # Add visual indicators for pattern type
                if "bullish" in description.lower():
                    st.success("📈 **Bullish Pattern** - Potential upward movement")
                elif "bearish" in description.lower():
                    st.error("📉 **Bearish Pattern** - Potential downward movement")
                else:
                    st.info("⚖️ **Neutral Pattern** - Context-dependent interpretation")
        
        if not filtered_glossary:
            st.info("No patterns found matching your search term.")
    
    with tab2:
        st.subheader("Trading Curriculum")
        
        # Level filter
        level_filter = st.selectbox("Filter by level:", ["All", "Beginner", "Intermediate", "Advanced"])
        
        filtered_tutorials = TUTORIALS if level_filter == "All" else [t for t in TUTORIALS if t["level"] == level_filter]
        
        for i, tutorial in enumerate(filtered_tutorials, 1):
            level_emoji = {"Beginner": "🌱", "Intermediate": "🚀", "Advanced": "🎯"}.get(tutorial["level"], "📚")
            
            with st.expander(f"{i}. {level_emoji} {tutorial['title']} ({tutorial['level']})"):
                st.write(tutorial["content"])
                
                # Progress tracking (simple demo)
                if st.button(f"Mark as completed", key=f"tutorial_{i}"):
                    st.success(f"✅ Completed: {tutorial['title']}")
    
    with tab3:
        st.subheader("Professional Trading Tips")
        
        tip_category = st.selectbox("Select category:", ["All"] + list(TIP_MAP.keys()))
        
        if tip_category == "All":
            for category, tip in TIP_MAP.items():
                st.info(f"**{category.title()}**: {tip}")
        else:
            st.info(f"**{tip_category.title()}**: {TIP_MAP[tip_category]}")
        
        st.divider()
        st.subheader("Quick Reference Card")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **🟢 Bullish Signals**
            - Hammer after downtrend
            - Bullish engulfing
            - Golden cross (MA)
            - RSI oversold recovery
            """)
        
        with col2:
            st.markdown("""
            **🔴 Bearish Signals**
            - Shooting star after uptrend
            - Bearish engulfing
            - Death cross (MA)
            - RSI overbought decline
            """)
        
        st.divider()
        st.markdown("""
        ### 🎯 **Risk Management Essentials**
        1. **Position Sizing**: Never risk more than 1-2% per trade
        2. **Stop Losses**: Always define your exit before entry
        3. **Risk/Reward**: Target at least 2:1 reward-to-risk ratio
        4. **Diversification**: Don't put all eggs in one basket
        5. **Emotional Control**: Stick to your plan, avoid FOMO
        """)
        
        st.caption("💡 Remember: Consistent small wins beat occasional big wins in trading!"))
