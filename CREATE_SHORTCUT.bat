@echo off
setlocal enabledelayedexpansion
title French Rental Scanner - Desktop Shortcut Creator

echo.
echo ============================================
echo  Create Desktop Shortcut
echo ============================================
echo.
echo This will create a shortcut on your desktop
echo to launch the French Rental Scanner dashboard.
echo.

:: Get the current directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Remove quotes for the shortcut path
set "TARGET_PATH=%SCRIPT_DIR%\RUN_DASHBOARD.bat"

:: Desktop path
set "DESKTOP_PATH=%USERPROFILE%\Desktop"
set "SHORTCUT_PATH=%DESKTOP_PATH%\French Rental Scanner.lnk"

:: Create a temporary VBScript to create the shortcut
set "VBS_FILE=%TEMP%\create_shortcut.vbs"

echo Set WSHShell = WScript.CreateObject("WScript.Shell") > "%VBS_FILE%"
echo Set Shortcut = WSHShell.CreateShortcut("%SHORTCUT_PATH%") >> "%VBS_FILE%"
echo Shortcut.TargetPath = "%TARGET_PATH%" >> "%VBS_FILE%"
echo Shortcut.WorkingDirectory = "%SCRIPT_DIR%" >> "%VBS_FILE%"
echo Shortcut.Description = "Launch French Rental Scanner Dashboard" >> "%VBS_FILE%"
echo Shortcut.IconLocation = "%SystemRoot%\System32\shell32.dll,13" >> "%VBS_FILE%"
echo Shortcut.Save >> "%VBS_FILE%"

:: Execute the VBScript
cscript //nologo "%VBS_FILE%"

:: Clean up
del "%VBS_FILE%"

echo.
echo [SUCCESS] Desktop shortcut created!
echo.
echo Look for "French Rental Scanner" on your desktop.
echo Double-click it to launch the dashboard.
echo.
pause
