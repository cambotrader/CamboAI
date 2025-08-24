# CamboStation Genesis Launcher

Set-Location "C:\Users\johnl\CamboStation-Vision"
& .\venv\Scripts\Activate

# Optional: Upgrade pip
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Run the dashboard
streamlit run main.py --server.port 8501
