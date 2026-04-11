@echo off
echo ======================================================================
echo   French Rental Scanner - Build EXE
echo ======================================================================
echo.
echo This will create a standalone executable file.
echo The build process may take a few minutes...
echo.
pause

echo.
echo Installing PyInstaller if needed...
py -3 -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    py -3 -m pip install pyinstaller
)

echo.
echo Building executable...
echo.

py -3 -m PyInstaller --clean FrenchRentalScanner.spec

if errorlevel 1 (
    echo.
    echo Build failed! Please check the errors above.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo   Build Complete!
echo ======================================================================
echo.
echo Your executable is ready: dist\FrenchRentalScanner.exe
echo.
echo You can now:
echo   1. Copy the exe to anywhere on your computer
echo   2. Double-click to run (no installation needed)
echo   3. Your data will be saved in the same folder as the exe
echo.
echo To create a portable package:
echo   - Copy FrenchRentalScanner.exe to a folder
echo   - The app will create rental_listings.db in that folder
echo   - All your data stays local and private
echo.
pause
