#!/usr/bin/env python3
"""
Test different import patterns to find what works
"""
import sys

print("Testing Ollama imports...")

# Test 1: Old style import
try:
    from langchain.llms import Ollama
    print("✅ Success: from langchain.llms import Ollama")
    ollama1 = Ollama(model="mistral")
    print("   Can create instance: Yes")
except Exception as e:
    print(f"❌ Failed: from langchain.llms import Ollama - {type(e).__name__}")

# Test 2: Community import
try:
    from langchain_community.llms import Ollama
    print("✅ Success: from langchain_community.llms import Ollama")
    ollama2 = Ollama(model="mistral")
    print("   Can create instance: Yes")
except Exception as e:
    print(f"❌ Failed: from langchain_community.llms import Ollama - {type(e).__name__}")

# Test 3: New ollama package
try:
    from langchain_ollama import OllamaLLM
    print("✅ Success: from langchain_ollama import OllamaLLM")
    ollama3 = OllamaLLM(model="mistral")
    print("   Can create instance: Yes")
except Exception as e:
    print(f"❌ Failed: from langchain_ollama import OllamaLLM - {type(e).__name__}")

print("\nChecking installed packages...")
import subprocess
for pkg in ["langchain", "langchain-community", "langchain-ollama", "crewai"]:
    result = subprocess.run([sys.executable, "-m", "pip", "show", pkg], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                print(f"{pkg}: {line.split(':')[1].strip()}")
    else:
        print(f"{pkg}: NOT INSTALLED")