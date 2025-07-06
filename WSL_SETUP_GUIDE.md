# WSL Setup Guide for KYC Analysis with CrewAI + Ollama

## The Issue
When running Python in WSL (Windows Subsystem for Linux) and Ollama on Windows, they can't communicate because Ollama only listens on Windows localhost by default.

## Solution Steps

### Step 1: Configure Ollama on Windows

You need to make Ollama listen on all network interfaces, not just localhost.

#### Option A: Using Command Prompt
```cmd
cd D:\Intelliswarm.ai\swift-kyc
start_ollama_windows.bat
```

#### Option B: Using PowerShell
```powershell
cd D:\Intelliswarm.ai\swift-kyc
.\start_ollama_windows.ps1
```

#### Option C: Manual Setup
1. Open Command Prompt or PowerShell on Windows
2. Set the environment variable:
   ```cmd
   set OLLAMA_HOST=0.0.0.0
   ```
   Or in PowerShell:
   ```powershell
   $env:OLLAMA_HOST="0.0.0.0"
   ```
3. Start Ollama:
   ```
   ollama serve
   ```

### Step 2: Configure Windows Firewall

1. Open Windows Security
2. Go to "Firewall & network protection"
3. Click "Allow an app through firewall"
4. Click "Change settings" (admin required)
5. Find "ollama" in the list or click "Allow another app..."
6. Browse to ollama.exe location (usually in AppData\Local\Programs\Ollama)
7. Check both "Private" and "Public" networks
8. Click OK

### Step 3: Find Your Windows IP from WSL

Run this in WSL terminal:
```bash
cd /mnt/d/Intelliswarm.ai/swift-kyc
python find_windows_ip.py
```

This will create a `.env` file with the correct configuration.

### Step 4: Test the Connection

```bash
python diagnose_ollama_connection.py
```

### Step 5: Run the KYC Analysis

```bash
# Activate virtual environment
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 in PowerShell

# Run the WSL-optimized version
python main_crewai_wsl.py
```

## Troubleshooting

### "Connection refused" error
1. Make sure Ollama is running on Windows with `OLLAMA_HOST=0.0.0.0`
2. Check Windows Firewall settings
3. Try manually setting the IP in `.env`:
   ```
   OLLAMA_BASE_URL=http://YOUR_WINDOWS_IP:11434
   ```

### Finding Windows IP manually
1. On Windows, run `ipconfig`
2. Look for "Ethernet adapter vEthernet (WSL)" or similar
3. Use that IP address

### Model not found
```bash
# On Windows
ollama pull mistral
ollama pull llama2
```

## Quick Test Script

Create `test_wsl_ollama.py`:
```python
import requests

# Get Windows IP from WSL
with open("/etc/resolv.conf", "r") as f:
    for line in f:
        if "nameserver" in line:
            windows_ip = line.split()[1]
            break

# Test connection
url = f"http://{windows_ip}:11434/api/version"
try:
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        print(f"✅ Success! Ollama at: {url}")
        print(f"Version: {response.json()}")
    else:
        print(f"❌ Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")
```

## Environment Variables

Your `.env` file should contain:
```
# For WSL users - replace with your Windows IP
OLLAMA_BASE_URL=http://172.21.16.1:11434
OLLAMA_MODEL=mistral
USE_OLLAMA=true
REPORT_OUTPUT_DIR=./reports
```

## Common Windows IPs in WSL

- Default WSL2: Often `172.x.x.1` (check `/etc/resolv.conf`)
- WSL1: Usually same as Windows host IP
- Can also try: `host.docker.internal` if Docker Desktop is installed

## Alternative: Run Everything on Windows

If WSL connectivity issues persist:
1. Install Python on Windows
2. Use Windows Command Prompt or PowerShell
3. Run all commands natively on Windows

## Success Indicators

When everything is working correctly, you should see:
```
✅ Ollama found at: http://172.21.16.1:11434
✅ Available models: ['mistral:latest', 'llama2:latest']
✅ Ollama response: Connection successful
🚀 Launching CrewAI analysis...
```