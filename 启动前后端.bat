@echo off
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" "scripts\start_dev.py"
) else (
  python "scripts\start_dev.py"
)
