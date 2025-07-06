@echo off
echo Starting Ollama on all interfaces for WSL access...
echo.

REM Set Ollama to listen on all interfaces
set OLLAMA_HOST=0.0.0.0

echo Configuration:
echo   OLLAMA_HOST=%OLLAMA_HOST%
echo.

echo Starting Ollama server...
ollama serve

pause