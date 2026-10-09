@echo off
title DeskLedger - Reset password
echo.
echo  This gives your DeskLedger login a NEW random password.
echo  Your books and receipts are not changed.
echo  Close DeskLedger first if it is open.
echo.
pause
if exist "%~dp0DeskLedger.exe" (
    "%~dp0DeskLedger.exe" --reset-password
) else (
    if exist "%~dp0venv\Scripts\python.exe" (
        "%~dp0venv\Scripts\python.exe" "%~dp0manage.py" create_default_user --reset
    ) else (
        echo  Could not find DeskLedger.exe or the venv folder next to this file.
    )
)
echo.
echo  The new password is in first_login.txt (it opens in Notepad for the app version).
echo  Log in, change your password in Settings, then delete first_login.txt.
pause
