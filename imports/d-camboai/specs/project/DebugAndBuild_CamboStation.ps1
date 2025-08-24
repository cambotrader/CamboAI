# DebugAndBuild_CamboStation.ps1
# Scans your consolidated CamboStationVision folder for key modules,
# prints where they live (or flags missing), then generates streamlit_app.py.

$Root = Join-Path $env:USERPROFILE 'CamboStationVision'
Write-Host "🔍 Scanning folder:" $Root

$patterns = @{
  'Council (PulsePanel.py)'             = 'PulsePanel.py'
  'Signal (PulseDash_v2.py)'            = 'PulseDash_v2.py'
  'Volatility (PulseDash_v3.py)'        = 'PulseDash_v3.py'
  'Symbols (SymbolScanner.py)'          = 'SymbolScanner.py'
  'MentorDeck (MentorDeckCompiler.ps1)' = 'MentorDeckCompiler.ps1'
}

$found = @{}
foreach($label in $patterns.Keys) {
  $file = Get-ChildItem -Path $Root -Filter $patterns[$label] -Recurse -ErrorAction SilentlyContinue |
            Select-Object -First 1
  if ($file) {
    Write-Host "✅ Found $label at:" $file.FullName
    $found[$label] = $file.FullName
  }
  else {
    Write-Host "❌ MISSING $label ($($patterns[$label]))"
  }
}

if ($found.Count -ne $patterns.Count) {
  Write-Host "`n✋ One or more modules are missing. Fix your folder structure and re-run."
  exit 1
}

# Build streamlit_app.py
$launcher = @"
import streamlit as st
import subprocess
from pathlib import Path

def launch(path: Path):
    if not path.exists():
        st.error(f'Missing: {path}')
        return
    subprocess.run(['streamlit','run', str(path)]) if path.suffix == '.py' else subprocess.run(['powershell','-File', str(path)])

st.set_page_config('CamboStation™ Vision', layout='wide')
st.sidebar.title('🚀 CamboStationVision')
tabs = st.tabs(['🎭 Council','📊 Signal','🧮 Volatility','🔍 Symbols','📘 Mentor Deck'])

with tabs[0]:
    st.subheader('🎭 Council')
    p = Path(r'$($found[''Council (PulsePanel.py)''])')
    if st.button('Launch Council'): launch(p)

with tabs[1]:
    st.subheader('📊 Signal')
    s = Path(r'$($found[''Signal (PulseDash_v2.py)''])')
    if st.button('Launch Signal'): launch(s)

with tabs[2]:
    st.subheader('🧮 Volatility')
    v = Path(r'$($found[''Volatility (PulseDash_v3.py)''])')
    if st.button('Launch Volatility'): launch(v)

with tabs[3]:
    st.subheader('🔍 Symbols')
    sy = Path(r'$($found[''Symbols (SymbolScanner.py)''])')
    if st.button('Launch Symbol Scanner'): launch(sy)

with tabs[4]:
    st.subheader('📘 Mentor Deck')
    m = Path(r'$($found[''MentorDeck (MentorDeckCompiler.ps1)''])')
    if st.button('Compile Mentor Deck'): launch(m)
"@

# Save launcher
$launcherPath = Join-Path $Root 'streamlit_app.py'
Set-Content -Path $launcherPath -Value $launcher -Encoding UTF8
Write-Host "`n✅ Generated Streamlit launcher at:" $launcherPath

# Run it
Write-Host "`n🚀 Starting Streamlit..."
cd $Root
streamlit run $launcherPath
