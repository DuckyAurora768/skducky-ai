@echo off
echo ==========================================
echo SkDucky AI - Ollama Setup and Status Check
echo ==========================================
echo.

echo 🔍 Checking if Ollama is installed...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama is not installed
    echo.
    echo 📥 To install Ollama:
    echo 1. Go to: https://ollama.ai/download
    echo 2. Download and install Ollama for Windows
    echo 3. Restart this script
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Ollama is installed
    ollama --version
)

echo.
echo 🔍 Checking if Ollama service is running...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama service is not running
    echo.
    echo 🚀 Starting Ollama service...
    echo Please wait while Ollama starts up...
    start /B ollama serve
    timeout /t 5 >nul
    
    echo 🔄 Checking again...
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if errorlevel 1 (
        echo ❌ Failed to start Ollama service
        echo Please start Ollama manually: ollama serve
        pause
        exit /b 1
    )
)

echo ✅ Ollama service is running!

echo.
echo 🔍 Checking if codellama model is installed...
ollama list | findstr codellama >nul 2>&1
if errorlevel 1 (
    echo ❌ codellama model is not installed
    echo.
    echo 📥 Installing codellama model (this may take a while)...
    echo Please be patient, this is a large download...
    ollama pull codellama
    if errorlevel 1 (
        echo ❌ Failed to install codellama model
        echo You can try: ollama pull codellama
        pause
        exit /b 1
    )
) else (
    echo ✅ codellama model is installed
)

echo.
echo 🎉 Ollama is ready for SkDucky AI!
echo 🦆 Your duck is ready to use advanced AI features!
echo.
echo Available models:
ollama list

echo.
echo 🌐 You can now use Ollama features in SkDucky AI
echo Press any key to continue...
pause >nul
