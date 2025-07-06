@echo off
echo ========================================
echo KYC Analysis System - Web UI
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update requirements
echo Installing requirements...
pip install -r requirements.txt

REM Check if Ollama is accessible
echo.
echo Checking Ollama connection...
curl -s http://172.21.16.1:11434/api/version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Cannot connect to Ollama at http://172.21.16.1:11434
    echo Make sure Ollama is running with: ollama serve
    echo.
)

REM Set environment variables
set OLLAMA_BASE_URL=http://172.21.16.1:11434
set OLLAMA_MODEL=mistral

REM Run Streamlit
echo.
echo Starting KYC Web UI...
echo Access the application at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================
streamlit run streamlit_app.py