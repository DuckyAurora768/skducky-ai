@echo off
echo ==========================================
echo SkDucky AI Setup for Windows
echo ==========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created!
) else (
    echo Virtual environment already exists!
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install pydantic==2.5.0
pip install python-multipart==0.0.6
pip install aiofiles==23.2.1

echo.
echo Installing AI dependencies (this may take a few minutes)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers==4.35.0
pip install numpy==1.24.3

echo.
echo Creating necessary directories...
if not exist "models" mkdir models
if not exist "data\examples" mkdir data\examples
if not exist "data\training_data" mkdir data\training_data
if not exist "services" mkdir services
if not exist "routes" mkdir routes

echo.
echo Creating __init__.py files...
type nul > services\__init__.py
type nul > routes\__init__.py

echo.
echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo To start SkDucky AI:
echo 1. Run: start.bat
echo 2. Open: http://localhost:8000 in your browser
echo.
pause