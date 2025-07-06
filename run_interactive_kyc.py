#!/usr/bin/env python3
"""
Run the Interactive KYC System with Web Search
"""
import os
import sys

# Add langchain directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'langchain'))

def main():
    print("""
╔════════════════════════════════════════════════════════════════════╗
║     🔍 Interactive KYC Analysis System with Web Search 🔍          ║
║                                                                    ║
║  Features:                                                         ║
║  ✅ Interactive client information input                           ║
║  ✅ Iterative web searches with multiple engines                   ║
║  ✅ Full workflow logging and tracking                             ║
║  ✅ PEP and sanctions screening with web data                      ║
║  ✅ Comprehensive risk assessment                                  ║
║  ✅ Detailed compliance reports                                    ║
║                                                                    ║
║  This system will:                                                 ║
║  1. Ask for client information interactively                       ║
║  2. Perform web searches (you control the process)                 ║
║  3. Analyze findings for KYC compliance                            ║
║  4. Generate a detailed report with full audit trail               ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check if running in correct directory
    if not os.path.exists("langchain/kyc_interactive.py"):
        print("❌ Error: Please run this script from the swift-kyc directory")
        print("   Current directory:", os.getcwd())
        return
    
    # Import and run the interactive system
    try:
        from kyc_interactive import InteractiveKYCSystem
        
        system = InteractiveKYCSystem()
        system.run_interactive_analysis()
        
    except KeyboardInterrupt:
        print("\n\n👋 Analysis cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running")
        print("2. Check your internet connection")
        print("3. Review the error message above")

if __name__ == "__main__":
    main()