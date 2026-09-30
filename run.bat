@echo off
chcp 65001 >nul
title Gemini TTS Deck

echo ======================================================
echo           Gemini TTS Deck - Windows Launcher
echo ======================================================
echo.

where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [Info] uv package manager not found. Installing uv automatically...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    echo Installation complete. Please rerun run.bat to launch Gemini TTS Deck!
    pause
    exit /b
)

echo [1/2] Checking and syncing virtual environment dependencies...
uv pip install -e . >nul 2>nul

echo [2/2] Launching Gemini TTS Deck service...
uv run python run.py

if %errorlevel% neq 0 (
    echo.
    echo [Error] Startup failed. Please check configuration and try again.
    pause
)
