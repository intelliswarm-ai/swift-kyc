#!/usr/bin/env python3
"""
Ollama Setup Helper for KYC Analysis System
Helps users configure and test Ollama for confidential KYC processing
"""
import os
import sys
import json
import requests
import subprocess
import time
from typing import List, Dict, Optional


class OllamaSetup:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.recommended_models = {
            "llama2": {
                "size": "3.8GB",
                "description": "Balanced performance and quality",
                "use_case": "General KYC analysis"
            },
            "mistral": {
                "size": "4.1GB",
                "description": "Fast and efficient",
                "use_case": "High-volume processing"
            },
            "mixtral": {
                "size": "26GB",
                "description": "Most capable but requires more resources",
                "use_case": "Complex analysis"
            },
            "neural-chat": {
                "size": "4.1GB",
                "description": "Optimized for conversational tasks",
                "use_case": "Interactive analysis"
            }
        }

    def check_ollama_installed(self) -> bool:
        """Check if Ollama is installed"""
        try:
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Ollama is installed: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
        
        print("❌ Ollama is not installed")
        return False

    def check_ollama_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama service is running")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print("❌ Ollama service is not running")
        return False

    def start_ollama_service(self) -> bool:
        """Attempt to start Ollama service"""
        print("🚀 Attempting to start Ollama service...")
        try:
            if sys.platform == "win32":
                subprocess.Popen(["ollama", "serve"], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(["ollama", "serve"], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
            # Wait for service to start
            for i in range(10):
                time.sleep(1)
                if self.check_ollama_running():
                    return True
                print(f"  Waiting... {i+1}/10")
            
        except Exception as e:
            print(f"❌ Failed to start Ollama: {str(e)}")
        
        return False

    def get_installed_models(self) -> List[Dict]:
        """Get list of installed models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('models', [])
        except:
            pass
        return []

    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama"""
        print(f"\n📥 Pulling model: {model_name}")
        print(f"   Size: {self.recommended_models.get(model_name, {}).get('size', 'Unknown')}")
        print("   This may take a few minutes...")
        
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Stream output
            for line in process.stdout:
                print(f"   {line.strip()}")
            
            process.wait()
            
            if process.returncode == 0:
                print(f"✅ Successfully pulled {model_name}")
                return True
            else:
                print(f"❌ Failed to pull {model_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error pulling model: {str(e)}")
            return False

    def test_model(self, model_name: str) -> bool:
        """Test a model with a simple KYC query"""
        print(f"\n🧪 Testing model: {model_name}")
        
        test_prompt = "What is KYC and why is it important for banks?"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": test_prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Model test successful!")
                print(f"   Response preview: {result['response'][:100]}...")
                return True
            else:
                print(f"❌ Model test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing model: {str(e)}")
            return False

    def setup_environment(self):
        """Setup .env file for Ollama"""
        env_file = ".env"
        
        if os.path.exists(env_file):
            print(f"\n📝 Updating {env_file} for Ollama...")
            
            # Read existing content
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Update Ollama settings
            updates = {
                "USE_OLLAMA": "true",
                "OLLAMA_BASE_URL": self.base_url
            }
            
            for key, value in updates.items():
                if f"{key}=" in content:
                    # Update existing
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith(f"{key}=") or line.startswith(f"# {key}="):
                            lines[i] = f"{key}={value}"
                    content = '\n'.join(lines)
                else:
                    # Add new
                    content += f"\n{key}={value}"
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ Environment file updated")
        else:
            print("⚠️  No .env file found. Creating from .env.example...")
            if os.path.exists('.env.example'):
                subprocess.run(["cp", ".env.example", ".env"])
                print("✅ Created .env file")

    def interactive_setup(self):
        """Run interactive setup"""
        print("\n🔧 KYC Analysis - Ollama Setup")
        print("="*50)
        
        # Check installation
        if not self.check_ollama_installed():
            print("\n📦 Please install Ollama first:")
            print("   macOS/Linux: curl -fsSL https://ollama.ai/install.sh | sh")
            print("   Windows: Download from https://ollama.ai/download/windows")
            return
        
        # Check/start service
        if not self.check_ollama_running():
            if not self.start_ollama_service():
                print("\n⚠️  Please start Ollama manually:")
                print("   Run: ollama serve")
                return
        
        # Check installed models
        installed_models = self.get_installed_models()
        if installed_models:
            print(f"\n📋 Installed models:")
            for model in installed_models:
                print(f"   - {model['name']} ({model.get('size', 'Unknown')})")
        else:
            print("\n📋 No models installed yet")
        
        # Recommend models
        print(f"\n🎯 Recommended models for KYC:")
        for model, info in self.recommended_models.items():
            print(f"\n   {model}:")
            print(f"   - Size: {info['size']}")
            print(f"   - Description: {info['description']}")
            print(f"   - Use case: {info['use_case']}")
        
        # Ask user to select model
        while True:
            print("\n❓ Which model would you like to install?")
            print("   (Enter model name or 'skip' to continue with existing models)")
            choice = input("   > ").strip().lower()
            
            if choice == 'skip':
                break
            
            if choice in self.recommended_models:
                if self.pull_model(choice):
                    self.test_model(choice)
                    
                    # Update .env with selected model
                    with open('.env', 'a') as f:
                        f.write(f"\nOLLAMA_MODEL={choice}")
                    print(f"✅ Set {choice} as default model")
                break
            else:
                print("❌ Invalid choice. Please try again.")
        
        # Setup environment
        self.setup_environment()
        
        print("\n✅ Setup complete!")
        print("\n📖 Next steps:")
        print("   1. Ensure Ollama is running: ollama serve")
        print("   2. Run KYC analysis: python main.py")
        print("   3. Or try examples: python example_usage.py")


def main():
    setup = OllamaSetup()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            setup.check_ollama_installed()
            setup.check_ollama_running()
            models = setup.get_installed_models()
            print(f"\nInstalled models: {len(models)}")
            
        elif command == "pull" and len(sys.argv) > 2:
            model = sys.argv[2]
            setup.pull_model(model)
            
        elif command == "test" and len(sys.argv) > 2:
            model = sys.argv[2]
            setup.test_model(model)
            
        else:
            print("Usage:")
            print("  python ollama_setup.py          # Interactive setup")
            print("  python ollama_setup.py check    # Check status")
            print("  python ollama_setup.py pull <model>  # Pull a model")
            print("  python ollama_setup.py test <model>  # Test a model")
    else:
        setup.interactive_setup()


if __name__ == "__main__":
    main()