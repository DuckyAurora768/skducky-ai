@echo off
echo ==========================================
echo Starting SkDucky AI Server
echo ==========================================
echo.

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Verify that the environment works
py --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Virtual environment doesn't work correctly
    echo 🔧 Try running: py -m venv venv
    pause
    exit /b 1
)

echo ✅ Virtual environment active
echo 📍 Server: http://localhost:8000
echo 📚 Documentation: http://localhost:8000/docs  
echo 🛑 Press Ctrl+C to stop the server
echo.

REM Open browser after 3 seconds (optional)
echo 🌐 Opening browser in 3 seconds...
timeout /t 3 >nul
start http://localhost:8000

REM Start server
py main.py

REM If the server closes unexpectedly
echo.
echo ⚠️ The server has closed
echo 📋 If there were errors, check the messages above
pause