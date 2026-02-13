@echo off
REM Download dan Setup Python 3 Portable untuk iClock Server
echo ========================================
echo iClock Server - Python 3 Portable Setup
echo ========================================
echo.

set PYTHON_VERSION=3.11.7
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip
set DOWNLOAD_DIR=%~dp0python3-portable
set ZIP_FILE=%~dp0python-embed.zip

echo Downloading Python %PYTHON_VERSION% Portable...
echo This may take a few minutes...
echo.

REM Download Python portable using PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%ZIP_FILE%'}"

if not exist "%ZIP_FILE%" (
    echo Error: Failed to download Python
    echo.
    echo Please manually download Python from:
    echo https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

echo Download complete!
echo.

echo Extracting Python...
powershell -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%DOWNLOAD_DIR%' -Force"

echo Cleaning up...
del "%ZIP_FILE%"

echo.
echo ========================================
echo Python 3 Portable Installed!
echo ========================================
echo Location: %DOWNLOAD_DIR%
echo.
echo Next: Run setup-with-portable.bat
echo.
pause
