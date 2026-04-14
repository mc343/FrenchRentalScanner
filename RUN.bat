@echo off
setlocal
echo ======================================================================
echo   French Rental Scanner - Interactive Interface
echo ======================================================================
echo.
echo Starting application...
echo.
set "PYTHON_EXE=python"
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python312\python.exe"
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python311\python.exe"

"%PYTHON_EXE%" interactive.py
pause
