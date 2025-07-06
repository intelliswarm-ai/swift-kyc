#!/usr/bin/env python3
"""
Test script to verify Ollama setup and compatibility with CrewAI
"""
import os
import requests
from langchain_community.llms import Ollama
from dotenv import load_dotenv

load_dotenv()


def test_ollama_api():
    """Test Ollama API connection"""
    print("1. Testing Ollama API connection...")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"   ✅ Connected to Ollama")
            print(f"   Available models: {[m['name'] for m in models]}")
            return True
        else:
            print(f"   ❌ Ollama API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to Ollama: {str(e)}")
        return False


def test_langchain_ollama():
    """Test Langchain Ollama integration"""
    print("\n2. Testing Langchain Ollama integration...")
    
    model = os.getenv("OLLAMA_MODEL", "llama2")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    try:
        llm = Ollama(model=model, base_url=base_url, temperature=0)
        
        # Simple test
        response = llm.invoke("What is KYC in one sentence?")
        print(f"   ✅ Langchain Ollama working")
        print(f"   Response: {response[:200]}...")
        return True
    except Exception as e:
        print(f"   ❌ Langchain Ollama failed: {str(e)}")
        return False


def test_crewai_compatibility():
    """Test CrewAI compatibility with Ollama"""
    print("\n3. Testing CrewAI compatibility...")
    
    try:
        from crewai import Agent, Task, Crew
        from langchain_community.llms import Ollama
        
        # Create a simple LLM
        llm = Ollama(
            model=os.getenv("OLLAMA_MODEL", "llama2"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0
        )
        
        # Create a simple agent
        test_agent = Agent(
            role="Test Agent",
            goal="Test if the system is working",
            backstory="I am a test agent",
            llm=llm,
            verbose=True
        )
        
        # Create a simple task
        test_task = Task(
            description="Say 'Hello, KYC system is ready!' in exactly those words.",
            expected_output="The exact phrase requested",
            agent=test_agent
        )
        
        # Create and run a simple crew
        test_crew = Crew(
            agents=[test_agent],
            tasks=[test_task],
            verbose=True
        )
        
        result = test_crew.kickoff()
        print(f"   ✅ CrewAI with Ollama working")
        print(f"   Result: {str(result)[:200]}...")
        return True
        
    except Exception as e:
        print(f"   ❌ CrewAI compatibility test failed: {str(e)}")
        return False


def suggest_fixes():
    """Suggest fixes for common issues"""
    print("\n4. Suggestions:")
    print("   - If Ollama is not running: ollama serve")
    print("   - If model is not installed: ollama pull llama2")
    print("   - Try a smaller model: ollama pull mistral")
    print("   - For better performance: ollama pull llama2:7b-chat")
    print("   - Check firewall settings if connection fails")


def main():
    print("🧪 Testing Ollama Setup for KYC System")
    print("=" * 50)
    
    # Run tests
    api_ok = test_ollama_api()
    
    if api_ok:
        langchain_ok = test_langchain_ollama()
        
        if langchain_ok:
            crewai_ok = test_crewai_compatibility()
            
            if crewai_ok:
                print("\n✅ All tests passed! Your system is ready.")
                print("\nYou can now run: python main.py")
            else:
                print("\n⚠️  CrewAI compatibility issue detected.")
                suggest_fixes()
        else:
            print("\n⚠️  Langchain integration issue detected.")
            suggest_fixes()
    else:
        print("\n❌ Ollama is not accessible.")
        print("\nPlease ensure Ollama is running:")
        print("1. Open a new terminal")
        print("2. Run: ollama serve")
        print("3. Then try this test again")


if __name__ == "__main__":
    main()