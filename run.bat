@echo off
echo Starting the self bot...

REM Ensure the correct Python version is used
SET PYTHON=python

REM Check if python is installed
%PYTHON% --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python before running this script.
    pause
    exit /b 1
)

REM Run the Python script
%PYTHON% self_bot.py

echo Bot has stopped.
pause
