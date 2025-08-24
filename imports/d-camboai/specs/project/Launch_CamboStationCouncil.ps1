# 🚀 CamboStation™ Council Launcher (No Login Required)

# Inject toggle configurations for full system activation
$env:COUNCIL_AUTH = "enabled"
$env:COUNCIL_FUSION = "on"
$env:AI_RESPOND_MODE = "on"
$env:SENTIMENT_LOGIC = "on"
$env:AGENT_ROLE_SENTIMENT = "on"
$env:SCAN_ENGINE = "on"
$env:STRATEGY_ALL_ON = "true"
$env:ASSET_CONTROL_MODE = "on"

# 🧠 Launch full cockpit dashboard
streamlit run "$env:USERPROFILE\CamboStation_VisionCouncil.py"
