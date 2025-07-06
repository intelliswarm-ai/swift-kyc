#!/usr/bin/env python3
"""
Find Windows host IP from WSL
"""
import subprocess
import re
import requests

print("🔍 Finding Windows Host IP from WSL")
print("=" * 60)

# Method 1: Get Windows IP from /etc/resolv.conf
print("\n📡 Method 1: Checking /etc/resolv.conf...")
try:
    with open("/etc/resolv.conf", "r") as f:
        content = f.read()
        # Look for nameserver line
        match = re.search(r'nameserver\s+(\d+\.\d+\.\d+\.\d+)', content)
        if match:
            windows_ip = match.group(1)
            print(f"✅ Found Windows IP: {windows_ip}")
            
            # Test Ollama connection
            try:
                response = requests.get(f"http://{windows_ip}:11434/api/version", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Ollama is accessible at: http://{windows_ip}:11434")
                    print(f"   Version: {response.json()}")
                    
                    # Save to .env
                    with open(".env", "w") as env_file:
                        env_file.write(f"# Ollama Configuration for WSL\n")
                        env_file.write(f"USE_OLLAMA=true\n")
                        env_file.write(f"OLLAMA_MODEL=mistral\n")
                        env_file.write(f"OLLAMA_BASE_URL=http://{windows_ip}:11434\n")
                        env_file.write(f"\n# Report Output\n")
                        env_file.write(f"REPORT_OUTPUT_DIR=./reports\n")
                    
                    print(f"\n✅ Configuration saved to .env")
                    print(f"\n📝 Your Ollama URL for WSL: http://{windows_ip}:11434")
                    
                    # Test models
                    response = requests.get(f"http://{windows_ip}:11434/api/tags", timeout=5)
                    if response.status_code == 200:
                        models = response.json().get('models', [])
                        print(f"\n📋 Available models: {[m['name'] for m in models]}")
                    
                    # Windows IP found and working
                else:
                    print(f"❌ Ollama not responding at http://{windows_ip}:11434")
            except Exception as e:
                print(f"❌ Cannot connect to Ollama: {e}")
                print(f"\n⚠️  Make sure:")
                print(f"   1. Ollama is running on Windows: ollama serve")
                print(f"   2. Windows Firewall allows connections from WSL")
                print(f"   3. Ollama is listening on all interfaces (not just localhost)")
except Exception as e:
    print(f"❌ Error reading /etc/resolv.conf: {e}")

# Method 2: Use ip route
print("\n📡 Method 2: Using ip route...")
try:
    result = subprocess.run(['ip', 'route', 'show'], capture_output=True, text=True)
    if result.returncode == 0:
        # Look for default route
        match = re.search(r'default via (\d+\.\d+\.\d+\.\d+)', result.stdout)
        if match:
            gateway_ip = match.group(1)
            print(f"✅ Found gateway IP: {gateway_ip}")
except Exception as e:
    print(f"❌ Error running ip route: {e}")

# Method 3: hostname -I
print("\n📡 Method 3: Getting WSL IP...")
try:
    result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
    if result.returncode == 0:
        wsl_ip = result.stdout.strip().split()[0]
        print(f"✅ WSL IP: {wsl_ip}")
except Exception as e:
    print(f"❌ Error getting hostname: {e}")

print("\n💡 To make Ollama accessible from WSL:")
print("1. On Windows, set Ollama to listen on all interfaces:")
print("   set OLLAMA_HOST=0.0.0.0")
print("   ollama serve")
print("\n2. Or use PowerShell:")
print("   $env:OLLAMA_HOST=\"0.0.0.0\"")
print("   ollama serve")
print("\n3. Allow through Windows Firewall:")
print("   - Windows Security > Firewall & network protection")
print("   - Allow an app > ollama.exe")
print("   - Check both Private and Public networks")