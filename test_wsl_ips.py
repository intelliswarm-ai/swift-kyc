#!/usr/bin/env python3
"""
Test different IPs to find Ollama from WSL
"""
import requests
import subprocess
import re

print("🔍 Testing different IPs to reach Ollama from WSL")
print("=" * 60)

# Get various IPs to test
ips_to_test = []

# 1. From /etc/resolv.conf
try:
    with open("/etc/resolv.conf", "r") as f:
        content = f.read()
        match = re.search(r'nameserver\s+(\d+\.\d+\.\d+\.\d+)', content)
        if match:
            ips_to_test.append(("resolv.conf nameserver", match.group(1)))
except:
    pass

# 2. From ip route (gateway)
try:
    result = subprocess.run(['ip', 'route', 'show'], capture_output=True, text=True)
    if result.returncode == 0:
        match = re.search(r'default via (\d+\.\d+\.\d+\.\d+)', result.stdout)
        if match:
            ips_to_test.append(("Gateway IP", match.group(1)))
except:
    pass

# 3. Common WSL2 IPs
common_ips = [
    ("WSL2 default", "172.17.0.1"),
    ("WSL2 alternative", "172.18.0.1"),
    ("WSL2 alternative", "172.19.0.1"),
    ("WSL2 alternative", "172.20.0.1"),
    ("WSL2 alternative", "172.21.0.1"),
    ("Docker Desktop", "host.docker.internal"),
]

for name, ip in common_ips:
    ips_to_test.append((name, ip))

# Test each IP
working_ip = None
for name, ip in ips_to_test:
    print(f"\n📡 Testing {name}: {ip}")
    try:
        url = f"http://{ip}:11434/api/version"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"✅ SUCCESS! Ollama found at {ip}:11434")
            print(f"   Version: {response.json()}")
            working_ip = ip
            
            # Test models
            response = requests.get(f"http://{ip}:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"   Models: {[m['name'] for m in models]}")
            break
        else:
            print(f"❌ Got status code: {response.status_code}")
    except requests.exceptions.ConnectTimeout:
        print(f"❌ Timeout")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection refused")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}")

if working_ip:
    print(f"\n✅ Found working Ollama at: http://{working_ip}:11434")
    
    # Save to .env
    print("\n💾 Updating .env file...")
    env_content = f"""# Ollama Configuration for WSL
USE_OLLAMA=true
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://{working_ip}:11434

# Report Output
REPORT_OUTPUT_DIR=./reports
"""
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ .env file updated")
    
    # Test generation
    print("\n🧪 Testing text generation...")
    try:
        data = {
            "model": "mistral",
            "prompt": "Say 'Hello from WSL'",
            "stream": False
        }
        response = requests.post(f"http://{working_ip}:11434/api/generate", json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generation successful: {result.get('response', '')[:100]}")
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        
else:
    print("\n❌ Could not find Ollama on any IP")
    print("\n💡 Troubleshooting:")
    print("1. Make sure Windows Firewall allows ollama.exe")
    print("2. Try restarting Ollama on Windows")
    print("3. Check if any antivirus is blocking connections")