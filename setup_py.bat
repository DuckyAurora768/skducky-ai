@echo off
echo ==========================================
echo SkDucky AI - Full Setup with Learning AI
echo ==========================================
echo.

echo Checking requirements...
echo.

echo [1/3] Checking Python...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed
    pause
    exit /b 1
)
py --version

echo.
echo [2/3] Checking Rust...
cargo --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Rust/Cargo is not installed
    echo Please install from https://rustup.rs/
    pause
    exit /b 1
)
cargo --version

echo.
echo [3/3] Creating virtual environment...
if not exist "venv" (
    py -m venv venv
    echo Virtual environment created!
) else (
    echo Virtual environment already exists!
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing core dependencies...
python -m pip install --upgrade pip
python -m pip install wheel setuptools

echo.
echo Installing FastAPI and web dependencies...
python -m pip install fastapi==0.104.1
python -m pip install uvicorn[standard]==0.24.0
python -m pip install pydantic==2.5.0
python -m pip install python-multipart==0.0.6
python -m pip install aiofiles==23.2.1
python -m pip install numpy==1.24.3

echo.
echo Installing PyTorch (CPU version)...
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo Installing Transformers and AI libraries...
python -m pip install transformers==4.35.0
python -m pip install tokenizers==0.15.0
python -m pip install datasets==2.14.6
python -m pip install accelerate==0.24.1
python -m pip install sentencepiece==0.1.99
python -m pip install protobuf==4.24.4

echo.
echo Creating necessary directories...
if not exist "models" mkdir models
if not exist "models\cache" mkdir models\cache
if not exist "data\examples" mkdir data\examples
if not exist "data\training_data" mkdir data\training_data
if not exist "services" mkdir services
if not exist "routes" mkdir routes

echo.
echo Creating __init__.py files...
type nul > services\__init__.py
type nul > routes\__init__.py

echo.
echo Setting up model cache directory...
set TRANSFORMERS_CACHE=%cd%\models\cache
setx TRANSFORMERS_CACHE %cd%\models\cache >nul 2>&1

echo.
echo ==========================================
echo ✅ Setup Complete! Full AI Version
echo ==========================================
echo.
echo The first run will download AI models (~500MB)
echo This is a one-time download.
echo.
echo To start SkDucky AI:
echo 1. Run: start.bat
echo 2. Open: http://localhost:8000
echo.
echo 🚀 Your AI can now learn and adapt!
echo.
pause