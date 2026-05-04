@echo off
chcp 65001 >nul
title 校園論壇與設施評價系統

echo ========================================
echo   校園論壇與設施評價系統 - 啟動中...
echo ========================================
echo.

REM 切換到腳本所在的資料夾
cd /d "%~dp0"

REM 檢查並安裝相依套件
echo [1/3] 正在檢查相依套件...
py -m pip install -r requirements.txt --quiet 2>nul
if %errorlevel% neq 0 (
    python -m pip install -r requirements.txt --quiet 2>nul
)
echo       套件檢查完成！

REM 延遲 1 秒後開啟瀏覽器
echo [2/3] 正在開啟瀏覽器...
start "" http://127.0.0.1:5000

REM 啟動 Flask 伺服器
echo [3/3] 正在啟動 Flask 伺服器...
echo.
echo ========================================
echo   伺服器已啟動！請在瀏覽器中操作。
echo   關閉此視窗即可停止伺服器。
echo ========================================
echo.

py app.py 2>nul
if %errorlevel% neq 0 (
    python app.py
)

pause
