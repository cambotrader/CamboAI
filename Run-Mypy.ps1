# Run mypy with local config
param(
  [string]$Path = "d:\CamboAI\backend"
)

Write-Host "Running mypy on $Path" -ForegroundColor Cyan
python -m mypy --config-file "d:\CamboAI\mypy.ini" "$Path"