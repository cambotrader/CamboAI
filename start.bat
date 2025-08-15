@echo off
cd /d "%~dp0"
set "PS_SCRIPT=%~dp0Start-CamboStation.ps1"
powershell -ExecutionPolicy Bypass -Command "& {& '%PS_SCRIPT%'}"
pause
