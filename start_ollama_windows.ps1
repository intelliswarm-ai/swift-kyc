# PowerShell script to start Ollama for WSL access
Write-Host "Starting Ollama on all interfaces for WSL access..." -ForegroundColor Green
Write-Host ""

# Set environment variable
$env:OLLAMA_HOST = "0.0.0.0"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  OLLAMA_HOST: $env:OLLAMA_HOST"
Write-Host ""

Write-Host "Starting Ollama server..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop"
Write-Host ""

# Start Ollama
ollama serve