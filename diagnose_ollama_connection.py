#!/usr/bin/env python3
"""
Diagnose Ollama connection issues
"""
import requests
import json
import os

print("🔍 Diagnosing Ollama Connection")
print("=" * 60)

# Check different possible Ollama URLs
urls_to_test = [
    "http://localhost:11434",
    "http://127.0.0.1:11434",
    "http://host.docker.internal:11434",  # For WSL
    "http://172.17.0.1:11434"  # Docker bridge
]

ollama_url = None

for url in urls_to_test:
    print(f"\n📡 Testing {url}...")
    try:
        response = requests.get(f"{url}/api/version", timeout=2)
        if response.status_code == 200:
            print(f"✅ SUCCESS! Ollama found at {url}")
            print(f"   Version: {response.json()}")
            ollama_url = url
            
            # Test models endpoint
            response = requests.get(f"{url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"   Models: {[m['name'] for m in models]}")
            break
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection refused")
    except requests.exceptions.Timeout:
        print(f"❌ Timeout")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")

if not ollama_url:
    print("\n❌ Could not connect to Ollama on any tested URL")
    print("\n💡 Troubleshooting steps:")
    print("1. Make sure Ollama is running: ollama serve")
    print("2. Check Windows Firewall settings")
    print("3. If using WSL, Ollama might be running on Windows host")
else:
    print(f"\n✅ Ollama is accessible at: {ollama_url}")
    
    # Test generation endpoint
    print("\n🧪 Testing generation endpoint...")
    try:
        data = {
            "model": "mistral",
            "prompt": "Say 'Hello from Ollama'",
            "stream": False
        }
        response = requests.post(f"{ollama_url}/api/generate", json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generation successful: {result.get('response', '')[:100]}")
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Generation error: {type(e).__name__}: {str(e)}")
    
    # Test with different models
    print("\n🧪 Testing available models...")
    for model in ["mistral", "llama2"]:
        try:
            data = {
                "model": model,
                "prompt": "Hi",
                "stream": False
            }
            response = requests.post(f"{ollama_url}/api/generate", json=data, timeout=10)
            if response.status_code == 200:
                print(f"✅ Model '{model}' works")
            else:
                print(f"❌ Model '{model}' failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Model '{model}' error: {type(e).__name__}")

# Check environment
print("\n📋 Environment Information:")
print(f"   OS: {os.name}")
print(f"   Platform: {os.sys.platform}")
print(f"   Working Directory: {os.getcwd()}")

# WSL detection
if os.path.exists("/proc/version"):
    with open("/proc/version", "r") as f:
        if "microsoft" in f.read().lower():
            print("   ✅ Running in WSL")
            print("\n💡 For WSL users:")
            print("   - Ollama might be running on Windows host")
            print("   - Try accessing Windows host IP instead of localhost")
            print("   - Check Windows Firewall allows connections from WSL")

# Save configuration
if ollama_url:
    print(f"\n💾 Saving working configuration...")
    config = {
        "OLLAMA_BASE_URL": ollama_url,
        "OLLAMA_MODEL": "mistral",
        "USE_OLLAMA": "true"
    }
    
    with open(".env.ollama", "w") as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")
    
    print("✅ Configuration saved to .env.ollama")
    print("\n📝 To use this configuration, add to your .env file:")
    print(f"   OLLAMA_BASE_URL={ollama_url}")