@echo off
title DeskLedger - Build Desktop App
color 0B

echo.
echo  =============================================
echo   Building DeskLedger.exe (desktop app)
echo  =============================================
echo.

:: -----------------------------------------------
:: VIRTUAL ENVIRONMENT
:: -----------------------------------------------
if not exist "venv\Scripts\activate.bat" (
    echo  Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

:: -----------------------------------------------
:: DEPENDENCIES (app + build tools)
:: -----------------------------------------------
echo  Installing dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check
pip install pyinstaller --quiet --disable-pip-version-check
if errorlevel 1 (
    color 0C
    echo  ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

:: -----------------------------------------------
:: COLLECT STATIC FILES (bundled into the build)
:: -----------------------------------------------
echo  Collecting static files...
python manage.py collectstatic --noinput --verbosity 0

:: -----------------------------------------------
:: GATHER THIRD-PARTY LICENCE TEXTS (required when redistributing the .exe)
:: -----------------------------------------------
echo  Collecting third-party licences...
python tools\collect_licenses.py
if errorlevel 1 (
    color 0C
    echo  ERROR: Could not collect third-party licences.
    pause
    exit /b 1
)

:: -----------------------------------------------
:: BUILD
:: -----------------------------------------------
echo  Running PyInstaller...
pyinstaller deskledger.spec --noconfirm
if errorlevel 1 (
    color 0C
    echo  ERROR: Build failed. Re-run after setting console=True in deskledger.spec
    echo  to see the underlying error.
    pause
    exit /b 1
)

copy /Y LICENSE dist\DeskLedger\LICENSE.txt >nul
copy /Y THIRD_PARTY_NOTICES.md dist\DeskLedger\THIRD_PARTY_NOTICES.md >nul
copy /Y DeskLedger-Reset-Password.bat dist\DeskLedger\DeskLedger-Reset-Password.bat >nul
copy /Y HOW-TO-OPEN-DESKLEDGER.md dist\DeskLedger\HOW-TO-OPEN-DESKLEDGER.md >nul
xcopy /E /I /Y build_licenses dist\DeskLedger\third_party_licenses >nul

echo.
echo  =============================================
echo   Done. Your app is in:  dist\DeskLedger\DeskLedger.exe
echo   Ship the whole dist\DeskLedger folder.
echo  =============================================
echo.
pause
