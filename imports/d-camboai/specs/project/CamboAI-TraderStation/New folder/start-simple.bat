@echo off
echo Starting CamboStation...

echo Checking if Python is available...
python --version
if %errorlevel% neq 0 (
    echo Python not found! Please install Python.
    pause
    exit /b 1
)

echo Checking if Node.js is available...
node --version
if %errorlevel% neq 0 (
    echo Node.js not found! Please install Node.js.
    pause
    exit /b 1
)

echo Starting backend...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt

echo Starting backend server...
start "Backend" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

cd ..\frontend
echo Installing frontend dependencies...
call npm install

echo Starting frontend server...
start "Frontend" cmd /k "set PORT=3000 && npm start"

echo Services started. Backend: http://localhost:8000, Frontend: http://localhost:3000
pause
