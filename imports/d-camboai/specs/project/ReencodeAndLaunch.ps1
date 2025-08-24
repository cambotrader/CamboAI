# ReencodeAndLaunch.ps1
# Reads streamlit_app.py as ANSI, writes it back as UTF-8, then starts Streamlit.

$path = Join-Path $env:USERPROFILE 'CamboStationVision\streamlit_app.py'

# Re‐encode from Windows ANSI (Default) into UTF-8
(Get-Content $path -Raw -Encoding Default) |
  Set-Content    $path -Encoding UTF8

Write-Host "✅ Re-encoded $path as UTF-8"

# Launch Streamlit from that folder
cd (Split-Path $path)
streamlit run (Split-Path $path -Leaf)
