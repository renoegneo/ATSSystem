@echo off
chcp 65001 > nul
title Автосервис — Сервер

echo ============================================
echo   Система учета AutoTruckService
echo ============================================
echo.

:: find python
where python > nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не найден.
    echo Установите Python с сайта python.org
    pause
    exit /b 1
)

:: find and show local IP address
echo Определяю IP адрес...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set RAW_IP=%%a
)
:: trim leading space
set SERVER_IP=%RAW_IP: =%

echo.
echo ============================================
echo   Адрес для подключения других компьютеров:
echo.
echo   http://%SERVER_IP%:8000
echo.
echo   Сохраните этот адрес или откройте файл
echo   адрес_сайта.txt на рабочем столе
echo ============================================
echo.

:: save address to desktop for convenience
echo http://%SERVER_IP%:8000 > "%USERPROFILE%\Desktop\адрес_сайта.txt"
echo [OK] Адрес сохранён в файл адрес_сайта.txt на рабочем столе
echo.

:: change to script directory so relative paths work
cd /d "%~dp0"

:: install dependencies if needed
echo Проверяю зависимости...
pip install -r requirements.txt --quiet
echo.

echo Запускаю сервер...
echo Для остановки нажмите Ctrl+C
echo.
python main.py

pause