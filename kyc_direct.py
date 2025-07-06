#!/usr/bin/env python3
"""
Direct KYC Analysis without CrewAI
This version uses the tools directly without the agent framework
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Import our tools
from tools.pep_tools_simple import PEPCheckTool
from tools.sanctions_tools_simple import SanctionsCheckTool
from tools.risk_assessment_tools_simple import RiskAssessmentTool

load_dotenv()


class DirectKYCAnalysis:
    """Direct KYC analysis using tools without CrewAI"""
    
    def __init__(self):
        self.pep_tool = PEPCheckTool()
        self.sanctions_tool = SanctionsCheckTool()
        self.risk_tool = RiskAssessmentTool()
        
    def analyze_client(self, client_info):
        """Perform KYC analysis on a client"""
        print(f"\n🔍 Analyzing client: {client_info['name']}")
        print("=" * 60)
        
        results = {}
        
        # 1. PEP Screening
        print("\n📋 Step 1: PEP Screening")
        print("-" * 40)
        try:
            pep_result = self.pep_tool._run(
                name=client_info['name'],
                date_of_birth=client_info.get('date_of_birth'),
                nationality=client_info.get('nationality'),
                fuzzy_match=True
            )
            pep_data = json.loads(pep_result)
            results['pep_screening'] = pep_data
            print(f"✅ PEP Status: {pep_data['pep_status']}")
            print(f"   Matches found: {pep_data['total_matches']}")
        except Exception as e:
            print(f"❌ PEP screening failed: {str(e)}")
            results['pep_screening'] = {'error': str(e), 'pep_status': 'Error'}
        
        # 2. Sanctions Screening
        print("\n📋 Step 2: Sanctions Screening")
        print("-" * 40)
        try:
            sanctions_result = self.sanctions_tool._run(
                name=client_info['name'],
                entity_type=client_info.get('entity_type', 'individual'),
                date_of_birth=client_info.get('date_of_birth'),
                country=client_info.get('nationality')
            )
            sanctions_data = json.loads(sanctions_result)
            results['sanctions_screening'] = sanctions_data
            print(f"✅ Sanctions Status: {sanctions_data['status']}")
            print(f"   Risk Level: {sanctions_data['risk_level']}")
            print(f"   Lists checked: {', '.join(sanctions_data['lists_checked'])}")
        except Exception as e:
            print(f"❌ Sanctions screening failed: {str(e)}")
            results['sanctions_screening'] = {'error': str(e), 'status': 'Error'}
        
        # 3. Risk Assessment
        print("\n📋 Step 3: Risk Assessment")
        print("-" * 40)
        try:
            # Use the results from previous screenings
            pep_status = results.get('pep_screening', {}).get('pep_status', 'Unknown')
            sanctions_status = results.get('sanctions_screening', {}).get('status', 'Unknown')
            
            risk_result = self.risk_tool._run(
                client_data=client_info,
                pep_status=pep_status,
                sanctions_status=sanctions_status,
                negative_news=[]  # Would come from research tool
            )
            risk_data = json.loads(risk_result)
            results['risk_assessment'] = risk_data
            
            overall_risk = risk_data['overall_risk']
            print(f"✅ Overall Risk Classification: {overall_risk['classification']}")
            print(f"   Risk Score: {overall_risk['overall_score']}")
            print(f"   Due Diligence Level: {overall_risk['due_diligence_level']}")
            
            # Print risk breakdown
            print("\n   Risk Component Breakdown:")
            for component, details in risk_data['risk_components'].items():
                print(f"   - {component.title()}: {details['assessment']} (score: {details['score']})")
                
        except Exception as e:
            print(f"❌ Risk assessment failed: {str(e)}")
            results['risk_assessment'] = {'error': str(e)}
        
        # 4. Generate Report
        print("\n📋 Step 4: Generating Compliance Report")
        print("-" * 40)
        
        report = self._generate_report(client_info, results)
        results['compliance_report'] = report
        
        # Save report
        self._save_report(client_info['name'], results)
        
        return results
    
    def _generate_report(self, client_info, results):
        """Generate a compliance report based on the analysis results"""
        
        # Extract key information
        pep_data = results.get('pep_screening', {})
        sanctions_data = results.get('sanctions_screening', {})
        risk_data = results.get('risk_assessment', {})
        
        # Determine overall recommendation
        if sanctions_data.get('risk_level') == 'Critical':
            recommendation = "REJECT - Sanctions hit detected"
        elif risk_data.get('overall_risk', {}).get('classification') == 'High Risk':
            recommendation = "PROCEED WITH CAUTION - Enhanced due diligence required"
        else:
            recommendation = "APPROVE - Subject to standard due diligence"
        
        report = {
            'executive_summary': {
                'client_name': client_info['name'],
                'date': datetime.now().isoformat(),
                'recommendation': recommendation,
                'risk_classification': risk_data.get('overall_risk', {}).get('classification', 'Unknown')
            },
            'screening_results': {
                'pep_status': pep_data.get('pep_status', 'Unknown'),
                'sanctions_status': sanctions_data.get('status', 'Unknown'),
                'sanctions_risk': sanctions_data.get('risk_level', 'Unknown')
            },
            'risk_summary': {
                'overall_score': risk_data.get('overall_risk', {}).get('overall_score', 0),
                'due_diligence_level': risk_data.get('overall_risk', {}).get('due_diligence_level', 'Unknown')
            },
            'recommendations': risk_data.get('recommendations', []),
            'monitoring_requirements': risk_data.get('monitoring_frequency', 'Annual review')
        }
        
        return report
    
    def _save_report(self, client_name, results):
        """Save the analysis report to file"""
        report_dir = os.getenv("REPORT_OUTPUT_DIR", "./reports")
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in client_name if c.isalnum() or c in [' ', '-', '_']).rstrip()
        filename = f"KYC_Direct_{safe_name}_{timestamp}.json"
        
        filepath = os.path.join(report_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Report saved to: {filepath}")


def main():
    """Main function"""
    print("\n🏦 Direct KYC Analysis System")
    print("=" * 60)
    print("This version runs without CrewAI for simpler operation")
    
    # Example client
    client_info = {
        "name": "John Doe",
        "entity_type": "individual",
        "date_of_birth": "1980-05-15",
        "nationality": "USA",
        "residence_country": "Switzerland",
        "business_countries": ["Switzerland", "USA", "UK"],
        "industry": "Technology",
        "customer_type": "individual",
        "occupation": "Software Engineer",
        "expected_transaction_volume": "Medium"
    }
    
    # Run analysis
    analyzer = DirectKYCAnalysis()
    results = analyzer.analyze_client(client_info)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 ANALYSIS COMPLETE")
    print("=" * 60)
    
    report = results.get('compliance_report', {})
    summary = report.get('executive_summary', {})
    
    print(f"\n🎯 Final Recommendation: {summary.get('recommendation', 'Unknown')}")
    print(f"📈 Risk Classification: {summary.get('risk_classification', 'Unknown')}")
    
    print("\n✅ Analysis completed successfully!")


if __name__ == "__main__":
    main()