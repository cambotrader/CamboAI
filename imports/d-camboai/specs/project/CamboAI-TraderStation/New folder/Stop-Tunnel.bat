@echo off
REM Stop the last CamboStation Quick Tunnel started from this folder
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy\Stop-QuickTunnel.ps1"
