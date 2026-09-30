@echo off
chcp 65001 >nul
title Gemini TTS Deck

echo ======================================================
echo           Gemini TTS Deck - Windows Launcher
echo ======================================================
echo.

where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [提示] 未检测到 uv 环境，正在为您自动安装 uv 包管理器...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    echo 安装完成，请重新双击 run.bat 启动 Gemini TTS Deck！
    pause
    exit /b
)

echo [1/2] 正在检查并同步虚拟环境依赖...
uv pip install -e . >nul 2>nul

echo [2/2] 正在启动 Gemini TTS Deck 服务...
uv run python run.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 启动异常，请检查配置后重试。
    pause
)
