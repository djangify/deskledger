@echo off
title DeskLedger
color 0A

echo.
echo  =============================================
echo   DeskLedger - Bookkeeping Software
echo  =============================================
echo.

:: -----------------------------------------------
:: CHECK PYTHON IS INSTALLED
:: -----------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  ERROR: Python is not installed or not on your PATH.
    echo.
    echo  Please download and install Python from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During install, tick "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  Python %PYVER% found.
echo.

:: -----------------------------------------------
:: SET UP VIRTUAL ENVIRONMENT
:: -----------------------------------------------
if not exist "venv\Scripts\activate.bat" (
    echo  Setting up virtual environment for the first time...
    python -m venv venv
    if errorlevel 1 (
        color 0C
        echo  ERROR: Could not create virtual environment.
        pause
        exit /b 1
    )
    echo  Virtual environment created.
    echo.
)

:: Activate venv
call venv\Scripts\activate.bat

:: -----------------------------------------------
:: INSTALL / UPDATE DEPENDENCIES
:: -----------------------------------------------
echo  Checking dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    color 0C
    echo.
    echo  ERROR: Failed to install dependencies.
    echo  Check your internet connection and try again.
    echo.
    pause
    exit /b 1
)
echo  Dependencies OK.
echo.

:: -----------------------------------------------
:: CREATE DATA DIRECTORIES
:: -----------------------------------------------
if not exist "data\db" mkdir data\db
if not exist "data\media\receipts" mkdir data\media\receipts
if not exist "data\db\backups" mkdir data\db\backups

:: -----------------------------------------------
:: RUN DATABASE MIGRATIONS
:: -----------------------------------------------
echo  Checking database...
python manage.py migrate --noinput --verbosity 0
if errorlevel 1 (
    color 0C
    echo  ERROR: Database migration failed. See the message above.
    pause
    exit /b 1
)
echo  Database OK.
echo.

:: -----------------------------------------------
:: FIRST-RUN LOGIN (random password, shown once)
:: -----------------------------------------------
python manage.py create_default_user
if errorlevel 1 (
    color 0C
    echo  ERROR: Could not create the first login. See the message above.
    pause
    exit /b 1
)
echo.

:: -----------------------------------------------
:: COLLECT STATIC FILES (only if staticfiles folder missing)
:: -----------------------------------------------
if not exist "staticfiles" (
    echo  Collecting static files...
    python manage.py collectstatic --noinput --verbosity 0
    echo  Static files OK.
    echo.
)

:: -----------------------------------------------
:: OPEN BROWSER AFTER SHORT DELAY
:: -----------------------------------------------
echo  Starting DeskLedger...
echo.
echo  Opening your browser to http://localhost:8000
echo  (If it doesn't open automatically, go there manually)
echo.
echo  To stop DeskLedger: close this window or press Ctrl+C
echo.
echo  =============================================
echo.

:: Wait 2 seconds then open browser in background
start "" cmd /c "timeout /t 2 >nul && start http://localhost:8000"

:: -----------------------------------------------
:: START DJANGO SERVER
:: -----------------------------------------------
python manage.py runserver 8000

:: If we get here the server stopped
echo.
echo  DeskLedger has stopped.
pause
