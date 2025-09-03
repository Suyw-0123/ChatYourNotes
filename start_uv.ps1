# ChatYourNotes UV 環境啟動腳本 (PowerShell)

Write-Host "正在啟動 ChatYourNotes (UV 環境)..." -ForegroundColor Green
Write-Host ""

# 確保在正確的目錄
Set-Location $PSScriptRoot

# 啟動 Flask 應用程序
uv run python app/app.py
