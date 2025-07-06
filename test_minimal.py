#!/usr/bin/env python3
"""
Minimal test to check Ollama functionality
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_ollama_direct():
    """Test Ollama directly via API"""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama2")
    
    print(f"Testing Ollama at {base_url} with model {model}")
    
    # Test 1: Check if Ollama is running
    try:
        response = requests.get(f"{base_url}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama is running with models: {[m['name'] for m in models]}")
            
            # Check if our model is available
            model_names = [m['name'] for m in models]
            if not any(model in mn for mn in model_names):
                print(f"❌ Model '{model}' not found. Available models: {model_names}")
                return False
        else:
            print(f"❌ Ollama returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("\nMake sure Ollama is running: ollama serve")
        return False
    
    # Test 2: Try to generate a response
    print(f"\nTesting generation with {model}...")
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": "What is KYC? Answer in one sentence.",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generation successful!")
            print(f"Response: {result.get('response', '')[:200]}...")
            return True
        else:
            print(f"❌ Generation failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return False

def test_with_openai():
    """Test with OpenAI instead"""
    print("\n" + "="*50)
    print("Alternative: Testing with OpenAI")
    print("="*50)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OpenAI API key found in .env")
        print("To use OpenAI, add: OPENAI_API_KEY=your_key_here")
        return
    
    print("✅ OpenAI API key found")
    print("To use OpenAI instead of Ollama:")
    print("1. Set USE_OLLAMA=false in your .env file")
    print("2. Run: python main.py")

if __name__ == "__main__":
    print("🧪 Minimal Ollama Test")
    print("="*50 + "\n")
    
    success = test_ollama_direct()
    
    if not success:
        print("\n💡 Troubleshooting:")
        print("1. Is Ollama running? Start it with: ollama serve")
        print("2. Is the model installed? Install with: ollama pull llama2")
        print("3. Try a different model: ollama pull mistral")
        print("4. Check if firewall is blocking port 11434")
        
        test_with_openai()
    else:
        print("\n✅ Ollama is working correctly!")
        print("\nThe issue might be with CrewAI compatibility.")
        print("Try using a different model or OpenAI instead.")