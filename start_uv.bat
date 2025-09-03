@echo off
REM ChatYourNotes UV 環境啟動腳本

echo 正在啟動 ChatYourNotes (UV 環境)...
echo.

REM 確保在正確的目錄
cd /d "%~dp0"

REM 啟動 Flask 應用程序
uv run python app/app.py

pause
