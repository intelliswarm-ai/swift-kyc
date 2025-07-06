#!/usr/bin/env python3
"""
Test Ollama on Windows
"""
import requests
import json
import os

print("🔍 Testing Ollama on Windows")
print("=" * 60)

# Test connection
url = "http://localhost:11434"
print(f"\n📡 Testing connection to: {url}")

try:
    # Check version
    response = requests.get(f"{url}/api/version", timeout=5)
    if response.status_code == 200:
        print(f"✅ Ollama is running!")
        print(f"   Version: {response.json()}")
    else:
        print(f"❌ Ollama returned status code: {response.status_code}")
        
    # Check models
    print("\n📋 Checking available models...")
    response = requests.get(f"{url}/api/tags", timeout=5)
    if response.status_code == 200:
        models = response.json().get('models', [])
        if models:
            print("✅ Available models:")
            for model in models:
                print(f"   - {model['name']} ({model.get('size', 'unknown size')})")
        else:
            print("⚠️  No models installed")
            print("\n📝 To install a model:")
            print("   ollama pull mistral")
            print("   ollama pull llama2")
    
    # Test generation
    print("\n🧪 Testing text generation...")
    data = {
        "model": "mistral",
        "prompt": "Say exactly: 'Hello from Ollama'",
        "stream": False
    }
    
    response = requests.post(f"{url}/api/generate", json=data, timeout=30)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Generation successful!")
        print(f"   Response: {result.get('response', '').strip()}")
    else:
        print(f"❌ Generation failed: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ Cannot connect to Ollama!")
    print("\n📝 To start Ollama:")
    print("  1. Open a new terminal")
    print("  2. Run: ollama serve")
    print("\n⚠️  Make sure Ollama is installed:")
    print("  Download from: https://ollama.ai/download")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {str(e)}")

# Test with langchain-ollama
print("\n\n🧪 Testing langchain-ollama integration...")
try:
    from langchain_ollama import OllamaLLM
    print("✅ langchain-ollama imported successfully")
    
    # Create LLM instance
    llm = OllamaLLM(model="mistral")
    print("✅ OllamaLLM instance created")
    
    # Test invoke
    response = llm.invoke("Say 'Integration test successful'")
    print(f"✅ LLM response: {response}")
    
except ImportError:
    print("❌ langchain-ollama not installed")
    print("   Run: pip install langchain-ollama")
except Exception as e:
    print(f"❌ LLM test failed: {type(e).__name__}: {str(e)}")

print("\n" + "=" * 60)
print("Test complete!")