#!/usr/bin/env python3
"""
Easy runner for LangChain KYC System
"""
import os
import sys
import json
from datetime import datetime

# Add langchain directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'langchain'))

def print_banner():
    """Print welcome banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║          🏦 LangChain KYC Analysis System 🏦                 ║
║                                                              ║
║  ✅ 100% Compatible with Ollama                             ║
║  ✅ Fully Local Processing                                  ║
║  ✅ No CrewAI Dependencies                                  ║
║  ✅ Professional Compliance Reports                         ║
╚══════════════════════════════════════════════════════════════╝
    """)

def get_client_info():
    """Get client information interactively or use default"""
    print("\nClient Information")
    print("-" * 40)
    
    use_default = input("Use default client data? (y/n): ").lower() == 'y'
    
    if use_default:
        return {
            "name": "John Doe",
            "entity_type": "individual",
            "date_of_birth": "1980-05-15",
            "nationality": "USA",
            "residence_country": "Switzerland",
            "business_countries": ["Switzerland", "USA", "UK"],
            "industry": "Technology",
            "occupation": "Software Engineer",
            "expected_transaction_volume": "Medium",
            "source_of_funds": "Employment income and investments"
        }
    else:
        client_info = {}
        client_info["name"] = input("Client Name: ") or "Unknown Client"
        client_info["entity_type"] = input("Entity Type (individual/company): ") or "individual"
        client_info["nationality"] = input("Nationality: ") or "Unknown"
        client_info["residence_country"] = input("Residence Country: ") or "Unknown"
        
        countries = input("Business Countries (comma-separated): ")
        client_info["business_countries"] = [c.strip() for c in countries.split(",")] if countries else []
        
        client_info["industry"] = input("Industry: ") or "Unknown"
        client_info["occupation"] = input("Occupation: ") or "Unknown"
        
        return client_info

def main():
    """Main function"""
    print_banner()
    
    # Check Ollama connection
    print("\n🔍 Checking Ollama connection...")
    import requests
    
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://172.21.16.1:11434")
    
    try:
        response = requests.get(f"{ollama_url}/api/version", timeout=5)
        if response.status_code == 200:
            print(f"✅ Ollama connected at: {ollama_url}")
        else:
            print(f"❌ Ollama not responding at: {ollama_url}")
            print("\nPlease ensure Ollama is running:")
            print("  Windows: ollama serve")
            print("  WSL: Use Windows IP (see WSL_SETUP_GUIDE.md)")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("\nPlease start Ollama first!")
        return
    
    # Choose version
    print("\n📋 Select KYC System Version:")
    print("1. Modern (Recommended) - Latest LangChain patterns")
    print("2. Simple - Basic implementation")
    print("3. Full Agents - Complex agent system")
    
    choice = input("\nEnter choice (1-3): ") or "1"
    
    # Get client information
    client_info = get_client_info()
    
    print(f"\n🚀 Running KYC Analysis for: {client_info['name']}")
    print("=" * 60)
    
    try:
        if choice == "1":
            from kyc_modern import ModernLangChainKYC
            system = ModernLangChainKYC()
            results = system.analyze_client(client_info)
            
        elif choice == "2":
            from kyc_simple import SimpleLangChainKYC
            system = SimpleLangChainKYC()
            results = system.analyze_client(client_info)
            
        elif choice == "3":
            from main import LangChainKYCSystem
            system = LangChainKYCSystem()
            results = system.run_complete_analysis(client_info)
            
        else:
            print("Invalid choice, using Modern version")
            from kyc_modern import ModernLangChainKYC
            system = ModernLangChainKYC()
            results = system.analyze_client(client_info)
        
        # Display summary
        if "risk_assessment" in results:
            risk = results["risk_assessment"]
            print("\n" + "=" * 60)
            print("📊 ANALYSIS SUMMARY")
            print("=" * 60)
            print(f"Client: {client_info['name']}")
            print(f"Overall Risk: {risk.get('overall_risk', 'Unknown').upper()}")
            print(f"Risk Score: {risk.get('risk_score', 'N/A')}")
            print(f"Recommendation: {risk.get('recommendation', 'Unknown').upper()}")
            print(f"Due Diligence: {risk.get('due_diligence_level', 'Unknown')}")
            print("\n✅ Analysis complete! Check reports folder for detailed results.")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {type(e).__name__}: {str(e)}")
        print("\nTrying fallback to direct analysis...")
        
        # Use the original direct analysis as fallback
        sys.path.append(os.path.dirname(__file__))
        from kyc_direct import DirectKYCAnalysis
        analyzer = DirectKYCAnalysis()
        analyzer.analyze_client(client_info)

if __name__ == "__main__":
    main()