# Quick start Streamlit with minimal deps, cached
param(
  [int]$Port = 8501
)

Write-Host "Ensuring venv: .venv_streamlit" -ForegroundColor Cyan
if (-Not (Test-Path "d:\CamboAI\.venv_streamlit\Scripts\Activate.ps1")) {
  python -m venv "d:\CamboAI\.venv_streamlit"
}
. "d:\CamboAI\.venv_streamlit\Scripts\Activate.ps1"

# Minimal deps for Streamlit cockpit
pip install --quiet streamlit yfinance pandas plotly ta requests

# Optional: FinBERT if available (non-fatal)
try {
  pip install --quiet transformers torch | Out-Null
} catch {
  Write-Host "Skipping FinBERT heavy deps (optional)" -ForegroundColor Yellow
}

$env:HF_HOME = "d:\CamboAI\.cache\huggingface"
$env:TRANSFORMERS_CACHE = "d:\CamboAI\.cache\huggingface"
$env:HUGGINGFACE_HUB_CACHE = "d:\CamboAI\.cache\huggingface"
New-Item -ItemType Directory -Force -Path "d:\CamboAI\.cache\huggingface" | Out-Null

streamlit run "d:\CamboAI\streamlit_app.py" --server.port $Port --browser.gatherUsageStats false