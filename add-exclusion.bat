@echo off
echo ======================================================================
echo   French Rental Scanner - Windows Defender Exclusion
echo ======================================================================
echo.
echo This script will help you add FrenchRentalScanner to Windows
echo Defender exclusions so the "Unknown Publisher" warning won't appear.
echo.
echo This will require Administrator privileges.
echo.
pause

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo This script requires Administrator privileges.
    echo.
    echo Please:
    echo   1. Right-click this file
    echo   2. Select "Run as administrator"
    echo.
    pause
    exit /b 1
)

:: Get current directory
set APP_DIR=%~dp0
set APP_DIR=%APP_DIR:~0,-1%

echo.
echo Adding to Windows Defender exclusions...
echo Folder: %APP_DIR%
echo.

:: Add folder exclusion using PowerShell
powershell -Command "
try {
    Add-MpPreference -ExclusionPath '%APP_DIR%' -Force
    Write-Host 'Success!' -ForegroundColor Green
    Write-Host ''
    Write-Host 'The exclusion has been added.' -ForegroundColor Cyan
    Write-Host 'You can now run FrenchRentalScanner.exe without warnings.' -ForegroundColor Green
    Write-Host ''
    Write-Host 'Note: This only affects YOUR computer.' -ForegroundColor Yellow
    Write-Host 'Others who download the exe will still see the warning once.' -ForegroundColor Yellow
} catch {
    Write-Host 'Failed:' -ForegroundColor Red
    Write-Host $_.Exception.Message
}
"

echo.
echo ======================================================================
echo   Instructions
echo ======================================================================
echo.
echo 1. The folder has been added to Windows Defender exclusions
echo 2. You can now run FrenchRentalScanner.exe without warnings
echo 3. The "Unknown Publisher" warning will still appear ONCE
echo 4. Click "Run anyway" the first time
echo 5. Windows will remember and won't show it again
echo.
echo To remove the exclusion later:
echo   - Open Windows Security
echo   - Go to Virus & threat protection
echo   - Go to Exclusions
echo   - Remove the FrenchRentalScanner folder
echo.
pause
