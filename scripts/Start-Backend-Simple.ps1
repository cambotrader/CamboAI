param(
  [int]$Port = 8000
)

# Activate venv if present
if (Test-Path "d:\CamboAI\backend\venv\Scripts\Activate.ps1") {
  . "d:\CamboAI\backend\venv\Scripts\Activate.ps1"
}

Set-Location "d:\CamboAI\backend"

# Ensure deps (simple set)
python -m pip install --upgrade pip
pip install -r requirements.simple.txt

# Run simple app
$env:UVICORN_LOG_LEVEL = "info"
$env:ENVIRONMENT = "development"
uvicorn app.main_simple:app --host 0.0.0.0 --port $Port --reload