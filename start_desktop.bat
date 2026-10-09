@echo off
title DeskLedger (Desktop)
color 0A

echo.
echo  =============================================
echo   DeskLedger - opening in its own window
echo  =============================================
echo.

:: -----------------------------------------------
:: CHECK PYTHON
:: -----------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  ERROR: Python is not installed or not on your PATH.
    echo  Install it from https://www.python.org/downloads/
    echo  ^(tick "Add Python to PATH" during install^)
    pause
    exit /b 1
)

:: -----------------------------------------------
:: VIRTUAL ENVIRONMENT
:: -----------------------------------------------
if not exist "venv\Scripts\activate.bat" (
    echo  Setting up virtual environment for the first time...
    python -m venv venv
)
call venv\Scripts\activate.bat

:: -----------------------------------------------
:: DEPENDENCIES
:: -----------------------------------------------
echo  Checking dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    color 0C
    echo  ERROR: Failed to install dependencies. Check your connection.
    pause
    exit /b 1
)

:: -----------------------------------------------
:: LAUNCH THE DESKTOP WINDOW
:: -----------------------------------------------
echo  Starting DeskLedger...
python desktop.py

echo.
echo  DeskLedger has closed.
