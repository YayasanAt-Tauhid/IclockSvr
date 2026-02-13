@echo off
REM iClock Server - Windows Development Setup Script
REM Run this script to setup local development environment

echo ================================
echo iClock Server - Local Setup
echo ================================
echo.

REM Check Python version
echo [1/7] Checking Python installation...
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if Python 3
python -c "import sys; exit(0 if sys.version_info[0] >= 3 else 1)" 2>nul
if errorlevel 1 (
    echo ERROR: Python 3 is required. Found Python 2.x
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo Python is installed!
echo.

REM Create virtual environment
echo [2/7] Creating virtual environment...
if not exist venv (
    python -m venv venv
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
python -m pip install --upgrade pip --quiet
echo.

REM Install dependencies
echo [5/7] Installing dependencies...
pip install -r requirements-dev.txt --quiet
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
python manage.py makemigrations --noinput
python manage.py migrate --noinput
echo Database setup complete!
echo.

REM Collect static files
python manage.py collectstatic --noinput --clear

echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. Create superuser: python manage.py createsuperuser
echo 2. Run server: python manage.py runserver
echo 3. Open browser: http://127.0.0.1:8000
echo.
echo To create admin user now, press any key...
pause

REM Create superuser
echo.
echo Creating superuser...
python manage.py createsuperuser

echo.
echo ================================
echo Ready to run!
echo ================================
echo.
echo Start the development server with:
echo   python manage.py runserver
echo.
echo Then open: http://127.0.0.1:8000
echo Admin panel: http://127.0.0.1:8000/admin/
echo.
pause
