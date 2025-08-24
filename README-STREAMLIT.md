# CamboAI Streamlit Cockpit (Temporary)

Quick way to run the platform UI locally while production stack (Vercel/Render/Cloudflare) is prepared.

## Prerequisites
- Python 3.9+
- Windows PowerShell

## Start
1. Open PowerShell
2. Run (full deps from root requirements):
   ```powershell
   d:\CamboAI\Start-Streamlit.ps1 -Port 8501
   ```
   Or quick minimal install:
   ```powershell
   d:\CamboAI\Start-Streamlit-Quick.ps1 -Port 8501
   ```
3. Open: http://localhost:8501

## Notes
- Uses venv `.venv_streamlit` separate from backend runtime.
- Charting uses yfinance; if rate-limited, app falls back to a sample dataset.
- Sentiment tries FinBERT; if not available, a lightweight heuristic is used.
- Sidebar has Backend Status checker for /health and /ready with optional X-API-Key.