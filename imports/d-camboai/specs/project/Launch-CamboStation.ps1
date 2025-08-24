# CamboStation Launch Script

Set-Location "C:\Users\johnl\CamboStation-Vision"

# Activate virtual environment
& .\venv\Scripts\Activate

# Upgrade pip (optional)
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Launch dashboard
streamlit run main.py --server.port 8501
