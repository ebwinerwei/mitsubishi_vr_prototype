@echo off
chcp 65001 > nul
cd /d "%~dp0.."
python tools\build_203_dzi.py
pause
