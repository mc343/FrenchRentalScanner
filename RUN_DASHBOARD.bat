@echo off
setlocal enabledelayedexpansion
title French Rental Scanner - Dashboard Launcher

echo.
echo ============================================
echo  French Rental Scanner Dashboard
echo  Smart Installer & Launcher
echo ============================================
echo.

:: Check if Python is installed
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo During installation, make sure to check:
    echo [x] Add Python to PATH
    echo.
    pause
    exit /b 1
)

:: Show Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

:: Check if pip is working
echo [2/4] Checking pip installation...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not working properly
    echo.
    echo Trying to install pip...
    python -m ensurepip --default-pip
    if errorlevel 1 (
        echo Failed to install pip. Please reinstall Python.
        pause
        exit /b 1
    )
)
echo [OK] pip is working
echo.

:: Check/install requirements
echo [3/4] Checking required packages...
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found!
    echo Please run this script from the French Rental Scanner directory.
    pause
    exit /b 1
)

:: Install requirements if needed
echo Installing/updating required packages...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo.
    echo WARNING: Some packages may have failed to install.
    echo Attempting to continue anyway...
    echo.
) else (
    echo [OK] All packages installed successfully
)
echo.

:: Launch the dashboard
echo [4/4] Starting Dashboard...
echo.
echo ============================================
echo  Dashboard will open in your browser
echo  Press Ctrl+C to stop the server
echo ============================================
echo.

:: Wait a moment for user to see the message
timeout /t 2 /nobreak >nul

:: Start the Streamlit dashboard
python -m streamlit run dashboard/app.py --server.address=127.0.0.1 --browser.gatherUsageStats false

:: If Streamlit exits with error
if errorlevel 1 (
    echo.
    echo ============================================
    echo ERROR: Failed to start dashboard
    echo ============================================
    echo.
    echo Common solutions:
    echo 1. Make sure you're in the correct directory
    echo 2. Try running: python -m pip install streamlit
    echo 3. Check that the dashboard/app.py file exists
    echo.
    pause
    exit /b 1
)

endlocal
