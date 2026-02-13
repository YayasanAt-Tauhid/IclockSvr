@echo off
REM iClock Server - Windows Development Setup Script
REM Python 3 SAFE VERSION (for systems with Python 2 & 3)

echo ================================
echo iClock Server - Local Setup
echo ================================
echo.

REM Check Python 3
echo [1/7] Checking Python 3 installation...
py -3 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3 is not available
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)
echo Python 3 detected!
echo.

REM Create virtual environment
echo [2/7] Creating virtual environment...
if not exist venv (
    py -3 -m venv venv
    echo Virtual environment created!
) else (
    echo Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo [4/7] Upgrading pip...
py -3 -m pip install --upgrade pip --quiet
echo.

REM Install dependencies
echo [5/7] Installing dependencies...
py -3 -m pip install -r requirements-dev.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed!
echo.

REM Setup environment file
echo [6/7] Setting up environment configuration...
if not exist .env (
    copy .env.dev .env
    echo Environment file created (.env)
) else (
    echo Environment file already exists.
)
echo.

REM Create necessary directories
if not exist logs mkdir logs
if not exist media mkdir media
if not exist staticfiles mkdir staticfiles

REM Run migrations
echo [7/7] Setting up database...
py -3 manage.py makemigrations --noinput
py -3 manage.py migrate --noinput
echo Database setup complete!
echo.

REM Collect static files
py -3 manage.py collectstatic --noinput --clear

echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. Create superuser: py -3 manage.py createsuperuser
echo 2. Run server: py -3 manage.py runserver
echo 3. Open browser: http://127.0.0.1:8000
echo.
pause

REM Create superuser
echo.
echo Creating superuser...
py -3 manage.py createsuperuser

echo.
echo ================================
echo Ready to run!
echo ================================
echo.
echo Start the development server with:
echo   py -3 manage.py runserver
echo.
echo Then open: http://127.0.0.1:8000
echo Admin panel: http://127.0.0.1:8000/admin/
echo.
pause
