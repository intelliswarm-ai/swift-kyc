#!/usr/bin/env python3
"""
Check package versions for compatibility issues
"""
import subprocess
import sys

print("📦 Package Version Check")
print("="*60)

packages = [
    "crewai",
    "crewai-tools", 
    "langchain",
    "langchain-community",
    "langchain-openai",
    "pydantic",
    "openai",
    "requests",
]

print("\nInstalled versions:")
for package in packages:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Name:') or line.startswith('Version:'):
                    print(f"  {line}")
        else:
            print(f"  {package}: NOT INSTALLED")
    except Exception as e:
        print(f"  {package}: ERROR - {e}")

print("\n" + "="*60)
print("💡 Known working combinations:")
print("="*60)
print("""
Option 1 (Stable):
  crewai==0.30.11
  langchain==0.1.20
  langchain-community==0.0.38
  
Option 2 (Latest):
  crewai==0.41.1
  langchain==0.2.11
  langchain-community==0.2.10

To downgrade to stable versions:
  pip install crewai==0.30.11 langchain==0.1.20 langchain-community==0.0.38

To upgrade to latest:
  pip install --upgrade crewai langchain langchain-community
""")