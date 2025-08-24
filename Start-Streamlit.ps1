# Start Streamlit temporary cockpit
param(
  [int]$Port = 8501
)

Write-Host "Activating venv: .venv_streamlit" -ForegroundColor Cyan
if (-Not (Test-Path "d:\CamboAI\.venv_streamlit\Scripts\Activate.ps1")) {
  Write-Host "Creating virtual environment..." -ForegroundColor Yellow
  python -m venv "d:\CamboAI\.venv_streamlit"
}

. "d:\CamboAI\.venv_streamlit\Scripts\Activate.ps1"

Write-Host "Installing requirements (root requirements.txt)..." -ForegroundColor Cyan
pip install -r "d:\CamboAI\requirements.txt" --quiet

Write-Host "Launching Streamlit on port $Port" -ForegroundColor Green
streamlit run "d:\CamboAI\streamlit_app.py" --server.port $Port --browser.gatherUsageStats false