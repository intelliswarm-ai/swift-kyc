#!/usr/bin/env python3
"""
Diagnose CrewAI-Ollama integration issues
"""
import os
import sys
import warnings
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings("ignore")

load_dotenv()

print("🔍 CrewAI-Ollama Diagnostic Tool")
print("=" * 60)

# Step 1: Check imports
print("\n1. Checking imports...")
try:
    from crewai import Agent, Task, Crew, Process
    print("   ✅ CrewAI imports successful")
except ImportError as e:
    print(f"   ❌ CrewAI import failed: {e}")
    sys.exit(1)

try:
    from langchain_community.llms import Ollama
    print("   ✅ Langchain Ollama import successful")
except ImportError as e:
    print(f"   ❌ Langchain import failed: {e}")
    sys.exit(1)

# Step 2: Test Ollama connection
print("\n2. Testing Ollama connection...")
try:
    import requests
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama2")
    
    response = requests.get(f"{base_url}/api/tags", timeout=5)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"   ✅ Ollama is running with {len(models)} models")
        model_names = [m['name'] for m in models]
        if any(model in mn for mn in model_names):
            print(f"   ✅ Model '{model}' is available")
        else:
            print(f"   ❌ Model '{model}' not found. Available: {model_names}")
    else:
        print(f"   ❌ Ollama API error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Cannot connect to Ollama: {e}")

# Step 3: Test basic Ollama LLM
print("\n3. Testing Ollama LLM...")
try:
    llm = Ollama(
        model=os.getenv("OLLAMA_MODEL", "llama2"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
        verbose=True
    )
    
    response = llm.invoke("Say 'Hello World' and nothing else.")
    print(f"   ✅ Basic LLM test passed")
    print(f"   Response: {response[:100]}")
except Exception as e:
    print(f"   ❌ Basic LLM test failed: {e}")
    print(f"   Error type: {type(e).__name__}")

# Step 4: Test with minimal CrewAI setup
print("\n4. Testing minimal CrewAI setup...")
try:
    # Create minimal agent
    test_agent = Agent(
        role="Test Agent",
        goal="Test the system",
        backstory="I am a test agent",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    print("   ✅ Agent created successfully")
    
    # Create minimal task
    test_task = Task(
        description="Reply with exactly: 'System OK'",
        expected_output="The exact phrase 'System OK'",
        agent=test_agent
    )
    print("   ✅ Task created successfully")
    
    # Create minimal crew
    test_crew = Crew(
        agents=[test_agent],
        tasks=[test_task],
        process=Process.sequential,
        verbose=True
    )
    print("   ✅ Crew created successfully")
    
    # Try to run
    print("\n   Attempting to run crew...")
    result = test_crew.kickoff()
    print(f"   ✅ Crew executed successfully!")
    print(f"   Result: {str(result)[:100]}")
    
except Exception as e:
    print(f"   ❌ CrewAI test failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    print("\n   Full traceback:")
    traceback.print_exc()

# Step 5: Test with different Ollama configurations
print("\n5. Testing alternative Ollama configurations...")

configs = [
    {
        "name": "Minimal config",
        "params": {
            "model": os.getenv("OLLAMA_MODEL", "llama2"),
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        }
    },
    {
        "name": "With timeout",
        "params": {
            "model": os.getenv("OLLAMA_MODEL", "llama2"),
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "timeout": 120
        }
    },
    {
        "name": "With request timeout",
        "params": {
            "model": os.getenv("OLLAMA_MODEL", "llama2"),
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "request_timeout": 120
        }
    }
]

for config in configs:
    print(f"\n   Testing: {config['name']}")
    try:
        test_llm = Ollama(**config['params'])
        response = test_llm.invoke("Say 'OK'")
        print(f"   ✅ {config['name']} works")
    except Exception as e:
        print(f"   ❌ {config['name']} failed: {type(e).__name__}")

# Step 6: Check CrewAI version compatibility
print("\n6. Version information...")
try:
    import crewai
    import langchain
    import langchain_community
    
    print(f"   CrewAI version: {getattr(crewai, '__version__', 'Unknown')}")
    print(f"   Langchain version: {getattr(langchain, '__version__', 'Unknown')}")
    print(f"   Langchain Community version: {getattr(langchain_community, '__version__', 'Unknown')}")
except Exception as e:
    print(f"   ❌ Could not get version info: {e}")

# Recommendations
print("\n" + "=" * 60)
print("💡 RECOMMENDATIONS:")
print("=" * 60)

print("\n1. If Ollama connection failed:")
print("   - Ensure Ollama is running: ollama serve")
print("   - Check if model is installed: ollama pull llama2")

print("\n2. If CrewAI integration failed:")
print("   - Try using mistral model: ollama pull mistral")
print("   - Update .env: OLLAMA_MODEL=mistral")
print("   - Consider using a chat model: ollama pull llama2:chat")

print("\n3. Alternative solutions:")
print("   - Use the direct KYC analysis: python kyc_direct.py")
print("   - Switch to OpenAI: USE_OLLAMA=false in .env")
print("   - Try a different CrewAI version: pip install crewai==0.30.11")

print("\n4. For debugging, try:")
print("   - Set CREWAI_DEBUG=true in environment")
print("   - Run with minimal agents and tasks")
print("   - Check Ollama logs for errors")