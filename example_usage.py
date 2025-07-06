#!/usr/bin/env python3
"""
Example usage of the KYC Analysis CrewAI system
"""
import json
from main import KYCAnalysisCrew


def analyze_individual_client():
    """Example: Analyze an individual client"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Individual Client Analysis")
    print("="*60)
    
    client_info = {
        "name": "Maria Rodriguez",
        "entity_type": "individual",
        "date_of_birth": "1975-08-22",
        "nationality": "Spain",
        "residence_country": "Switzerland",
        "occupation": "Investment Advisor",
        "expected_transaction_volume": "High",
        "source_of_wealth": "Professional income and investments"
    }
    
    print(f"\nAnalyzing: {client_info['name']}")
    print(f"Type: {client_info['entity_type']}")
    print(f"Nationality: {client_info['nationality']}")
    
    kyc_crew = KYCAnalysisCrew()
    result = kyc_crew.run(client_info)
    
    print("\n✅ Analysis completed!")
    return result


def analyze_corporate_client():
    """Example: Analyze a corporate client"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Corporate Client Analysis")
    print("="*60)
    
    client_info = {
        "name": "TechVentures International Ltd",
        "entity_type": "corporate",
        "registration_number": "CHE-123.456.789",
        "registration_country": "Switzerland",
        "business_countries": ["Switzerland", "Germany", "USA", "Singapore"],
        "industry": "Technology and Software Development",
        "customer_type": "corporate",
        "complex_structure": True,
        "offshore_elements": False,
        "expected_transaction_volume": "Very High",
        "ultimate_beneficial_owners": [
            {"name": "John Smith", "ownership": "35%"},
            {"name": "Liu Wei", "ownership": "30%"},
            {"name": "Investment Fund ABC", "ownership": "35%"}
        ]
    }
    
    print(f"\nAnalyzing: {client_info['name']}")
    print(f"Type: {client_info['entity_type']}")
    print(f"Industry: {client_info['industry']}")
    print(f"Countries: {', '.join(client_info['business_countries'])}")
    
    kyc_crew = KYCAnalysisCrew()
    result = kyc_crew.run(client_info)
    
    print("\n✅ Analysis completed!")
    return result


def analyze_high_risk_client():
    """Example: Analyze a potentially high-risk client"""
    print("\n" + "="*60)
    print("EXAMPLE 3: High-Risk Client Analysis")
    print("="*60)
    
    client_info = {
        "name": "Global Trading Solutions",
        "entity_type": "corporate",
        "registration_country": "UAE",
        "business_countries": ["UAE", "Iran", "Turkey", "Russia"],
        "industry": "Import/Export Trading",
        "customer_type": "corporate",
        "complex_structure": True,
        "offshore_elements": True,
        "expected_transaction_volume": "Very High",
        "business_description": "International commodity trading"
    }
    
    print(f"\nAnalyzing: {client_info['name']}")
    print(f"Type: {client_info['entity_type']}")
    print(f"Risk Factors: Complex structure, Offshore elements, High-risk countries")
    
    kyc_crew = KYCAnalysisCrew()
    result = kyc_crew.run(client_info)
    
    print("\n✅ Analysis completed!")
    return result


def batch_analysis():
    """Example: Analyze multiple clients in batch"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Batch Client Analysis")
    print("="*60)
    
    clients = [
        {
            "name": "Alice Johnson",
            "entity_type": "individual",
            "nationality": "Canada",
            "residence_country": "Switzerland"
        },
        {
            "name": "Tech Innovations AG",
            "entity_type": "corporate",
            "registration_country": "Switzerland",
            "industry": "Technology"
        },
        {
            "name": "Robert Chen",
            "entity_type": "individual",
            "nationality": "Singapore",
            "residence_country": "Switzerland",
            "occupation": "Entrepreneur"
        }
    ]
    
    kyc_crew = KYCAnalysisCrew()
    results = []
    
    for client in clients:
        print(f"\nAnalyzing: {client['name']} ({client['entity_type']})")
        try:
            result = kyc_crew.run(client)
            results.append({
                'client': client['name'],
                'status': 'completed',
                'result': result
            })
        except Exception as e:
            results.append({
                'client': client['name'],
                'status': 'error',
                'error': str(e)
            })
    
    print("\n📊 Batch Analysis Summary:")
    print("-" * 40)
    for r in results:
        status_emoji = "✅" if r['status'] == 'completed' else "❌"
        print(f"{status_emoji} {r['client']}: {r['status']}")
    
    return results


def main():
    """Run all examples"""
    print("\n🏦 KYC Analysis CrewAI - Example Usage")
    print("=" * 60)
    
    # Example menu
    print("\nSelect an example to run:")
    print("1. Individual Client Analysis")
    print("2. Corporate Client Analysis")
    print("3. High-Risk Client Analysis")
    print("4. Batch Client Analysis")
    print("5. Run All Examples")
    
    choice = input("\nEnter your choice (1-5): ")
    
    if choice == "1":
        analyze_individual_client()
    elif choice == "2":
        analyze_corporate_client()
    elif choice == "3":
        analyze_high_risk_client()
    elif choice == "4":
        batch_analysis()
    elif choice == "5":
        print("\nRunning all examples...")
        analyze_individual_client()
        analyze_corporate_client()
        analyze_high_risk_client()
        batch_analysis()
    else:
        print("Invalid choice. Please run the script again.")


if __name__ == "__main__":
    main()