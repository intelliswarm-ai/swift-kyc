#!/usr/bin/env python3
"""
KYC Analysis System - Main Entry Point
Powered by LangChain and Ollama
"""
import os
import sys


def print_banner():
    """Print welcome banner"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                   🏦 KYC Analysis System 🏦                        ║
║                                                                    ║
║  Powered by LangChain + Ollama                                     ║
║  100% Local Processing | Full Compliance                           ║
╚════════════════════════════════════════════════════════════════════╝
    """)


def show_menu():
    """Show main menu"""
    print("\nSelect an option:")
    print("1. 🚀 Run Enhanced Multi-Agent Analysis (Full CrewAI functionality)")
    print("2. 🔍 Run Interactive Analysis with Web Search")
    print("3. 📊 Run Modern KYC Analysis")
    print("4. 🎯 Run Simple KYC Analysis")
    print("5. 📋 View Documentation")
    print("6. 🔧 Check System Status")
    print("0. Exit")
    
    return input("\nEnter your choice (0-6): ")


def main():
    """Main function"""
    print_banner()
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            print("\n🚀 Starting Enhanced Multi-Agent Analysis...")
            from kyc_enhanced import main as enhanced_main
            enhanced_main()
            
        elif choice == "2":
            print("\n🔍 Starting Interactive Analysis...")
            from kyc_interactive import main as interactive_main
            interactive_main()
            
        elif choice == "3":
            print("\n📊 Starting Modern KYC Analysis...")
            from kyc_modern import main as modern_main
            modern_main()
            
        elif choice == "4":
            print("\n🎯 Starting Simple KYC Analysis...")
            from kyc_simple import main as simple_main
            simple_main()
            
        elif choice == "5":
            print("\n📋 Documentation:")
            print("  - README.md: General project overview")
            print("  - README_LANGCHAIN.md: LangChain implementation details")
            print("  - INTERACTIVE_KYC_GUIDE.md: Interactive system guide")
            print("  - PROJECT_SUMMARY.md: Complete project summary")
            
        elif choice == "6":
            print("\n🔧 Checking system status...")
            import requests
            
            # Check Ollama
            try:
                ollama_url = os.getenv("OLLAMA_BASE_URL", "http://172.21.16.1:11434")
                response = requests.get(f"{ollama_url}/api/version", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Ollama is running at {ollama_url}")
                else:
                    print("❌ Ollama is not responding")
            except:
                print("❌ Cannot connect to Ollama")
            
            # Check directories
            for dir_name in ["reports", "logs", "data"]:
                if os.path.exists(dir_name):
                    print(f"✅ Directory '{dir_name}' exists")
                else:
                    print(f"⚠️  Directory '{dir_name}' not found")
            
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
