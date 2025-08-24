@echo off
echo Starting Cambo AI Trader Station...

echo.
echo Starting Backend Server...
cd /d "%~dp0backend"
start "Backend" cmd /k "python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo.
echo Starting Frontend Server...
cd /d "%~dp0frontend"
start "Frontend" cmd /k "npm start"

echo.
echo Services starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause >nul
