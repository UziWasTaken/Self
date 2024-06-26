@echo off
echo Installing required Python packages...

REM Ensure the correct Python version is used
SET PYTHON=python

REM Check if python is installed
%PYTHON% --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python before running this script.
    pause
    exit /b 1
)

REM Install the required packages
%PYTHON% -m pip install --upgrade pip
%PYTHON% -m pip install requests
%PYTHON% -m pip install aiohttp
%PYTHON% -m pip install websockets

echo Required packages installed successfully.
pause
