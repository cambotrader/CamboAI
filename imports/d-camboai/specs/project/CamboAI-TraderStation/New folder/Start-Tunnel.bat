@echo off
REM Start CamboStation Quick Tunnel from the new folder without keeping a console open
powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0deploy\Start-QuickTunnel.ps1" -Port 8000
