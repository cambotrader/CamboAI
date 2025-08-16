param(
  [int]$Port = 8000
)

# Activate venv if present
if (Test-Path "d:\CamboAI\backend\venv\Scripts\Activate.ps1") {
  . "d:\CamboAI\backend\venv\Scripts\Activate.ps1"
}

Set-Location "d:\CamboAI\backend"

# Ensure deps
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run full app
$env:UVICORN_LOG_LEVEL = "info"
$env:ENVIRONMENT = "development"
uvicorn app.main:app --host 0.0.0.0 --port $Port --reload