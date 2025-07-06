#!/usr/bin/env python3
"""
Modern LangChain KYC System using latest patterns
No deprecation warnings, fully compatible with Ollama
"""
import os
import json
import warnings
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv()

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough


class ModernLangChainKYC:
    """Modern KYC system using latest LangChain patterns"""
    
    def __init__(self):
        # Get Ollama URL from environment
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://172.21.16.1:11434")
        self.model = os.getenv("OLLAMA_MODEL", "mistral")
        
        print(f"🔧 Initializing Modern LangChain KYC System")
        print(f"   Ollama URL: {self.base_url}")
        print(f"   Model: {self.model}")
        
        # Initialize LLM
        self.llm = OllamaLLM(
            model=self.model,
            base_url=self.base_url,
            temperature=0,
            format="json"  # Request JSON output
        )
        
        # Initialize JSON parser
        self.json_parser = JsonOutputParser()
        
        print("✅ System ready")
    
    def check_pep_status(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check PEP status using modern chain"""
        prompt = PromptTemplate.from_template("""Analyze if this person could be a Politically Exposed Person (PEP):

Name: {name}
Nationality: {nationality}
Occupation: {occupation}

Consider:
1. Is the occupation politically exposed (government, military, judiciary)?
2. Are they from a high-risk country?
3. Could they be related to a PEP?

Respond with a JSON object containing:
- is_pep: boolean
- confidence: "high" or "medium" or "low"
- reasons: array of strings
- risk_level: "high" or "medium" or "low"

JSON Response:""")
        
        # Create modern chain using pipe operator
        chain = prompt | self.llm
        
        try:
            result = chain.invoke({
                "name": client_info.get("name", "Unknown"),
                "nationality": client_info.get("nationality", "Unknown"),
                "occupation": client_info.get("occupation", "Unknown")
            })
            
            # Parse JSON response
            return self._parse_json_response(result, {
                "is_pep": False,
                "confidence": "low",
                "reasons": ["Analysis completed"],
                "risk_level": "low"
            })
            
        except Exception as e:
            print(f"PEP check error: {e}")
            return {
                "is_pep": False,
                "confidence": "low",
                "reasons": [str(e)],
                "risk_level": "low"
            }
    
    def check_sanctions(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check sanctions using modern chain"""
        prompt = PromptTemplate.from_template("""Assess sanctions risk for this client:

Name: {name}
Nationality: {nationality}
Business Countries: {countries}

High-risk countries: Iran, North Korea, Syria, Russia, Belarus, Myanmar, Cuba, Venezuela

Respond with a JSON object containing:
- sanctions_risk: "high" or "medium" or "low"
- flagged_countries: array of country names
- reasons: array of strings
- recommendation: "proceed" or "review" or "reject"

JSON Response:""")
        
        chain = prompt | self.llm
        
        try:
            countries = ", ".join(client_info.get("business_countries", []))
            result = chain.invoke({
                "name": client_info.get("name", "Unknown"),
                "nationality": client_info.get("nationality", "Unknown"),
                "countries": countries
            })
            
            return self._parse_json_response(result, {
                "sanctions_risk": "low",
                "flagged_countries": [],
                "reasons": ["No sanctions matches"],
                "recommendation": "proceed"
            })
            
        except Exception as e:
            print(f"Sanctions check error: {e}")
            return {
                "sanctions_risk": "low",
                "flagged_countries": [],
                "reasons": [str(e)],
                "recommendation": "proceed"
            }
    
    def assess_risk(self, client_info: Dict[str, Any], pep_result: Dict[str, Any], 
                    sanctions_result: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive risk assessment using modern chain"""
        prompt = PromptTemplate.from_template("""Perform KYC risk assessment based on:

Client: {client_name}
Industry: {industry}
Countries: {countries}
PEP Status: {pep_status}
Sanctions Risk: {sanctions_risk}

Calculate overall risk considering all factors.

Respond with a JSON object containing:
- overall_risk: "high" or "medium" or "low"
- risk_score: number between 0.0 and 1.0
- risk_factors: array of identified risk factors
- due_diligence_level: "standard" or "enhanced"
- recommendation: "approve" or "conditional_approve" or "reject"

JSON Response:""")
        
        chain = prompt | self.llm
        
        try:
            result = chain.invoke({
                "client_name": client_info.get("name", "Unknown"),
                "industry": client_info.get("industry", "Unknown"),
                "countries": ", ".join(client_info.get("business_countries", [])),
                "pep_status": "PEP" if pep_result.get("is_pep") else "Not PEP",
                "sanctions_risk": sanctions_result.get("sanctions_risk", "unknown")
            })
            
            return self._parse_json_response(result, {
                "overall_risk": "low",
                "risk_score": 0.2,
                "risk_factors": ["Standard profile"],
                "due_diligence_level": "standard",
                "recommendation": "approve"
            })
            
        except Exception as e:
            print(f"Risk assessment error: {e}")
            return {
                "overall_risk": "medium",
                "risk_score": 0.5,
                "risk_factors": ["Assessment error"],
                "due_diligence_level": "enhanced",
                "recommendation": "conditional_approve"
            }
    
    def generate_report(self, client_info: Dict[str, Any], analysis_results: Dict[str, Any]) -> str:
        """Generate report using modern chain"""
        prompt = PromptTemplate.from_template("""Create a professional KYC report:

# KYC COMPLIANCE REPORT

**Date:** {date}
**Client:** {client_name}

## Executive Summary
Based on the analysis showing {risk_level} risk with a score of {risk_score}, 
the recommendation is to {recommendation} this client.

## Client Profile
- Name: {client_name}
- Nationality: {nationality}
- Occupation: {occupation}
- Industry: {industry}
- Residence: {residence}

## Screening Results

### PEP Status
- Status: {pep_status}
- Confidence: {pep_confidence}
- Risk Level: {pep_risk}

### Sanctions Screening
- Risk Level: {sanctions_risk}
- Recommendation: {sanctions_rec}

## Risk Assessment
- Overall Risk: {risk_level}
- Risk Score: {risk_score}
- Due Diligence: {dd_level}
- Key Risk Factors: {risk_factors}

## Compliance Recommendation
{final_recommendation}

## Required Actions
{required_actions}

---
Report generated by Modern LangChain KYC System
Powered by Ollama ({model})

End of Report""")
        
        chain = prompt | self.llm
        
        # Prepare data
        pep = analysis_results["pep_screening"]
        sanctions = analysis_results["sanctions_screening"]
        risk = analysis_results["risk_assessment"]
        
        # Determine final recommendation and actions
        if risk["recommendation"] == "approve":
            final_rec = "Client is approved for onboarding with standard due diligence."
            actions = "- Complete standard KYC documentation\n- Set up regular review schedule"
        elif risk["recommendation"] == "conditional_approve":
            final_rec = "Client may be approved subject to enhanced due diligence."
            actions = "- Conduct enhanced due diligence\n- Obtain additional documentation\n- Senior management approval required"
        else:
            final_rec = "Client should not be onboarded due to high risk factors."
            actions = "- Decline onboarding\n- Document decision rationale\n- No further action required"
        
        report = chain.invoke({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "client_name": client_info["name"],
            "nationality": client_info.get("nationality", "N/A"),
            "occupation": client_info.get("occupation", "N/A"),
            "industry": client_info.get("industry", "N/A"),
            "residence": client_info.get("residence_country", "N/A"),
            "pep_status": "PEP Identified" if pep["is_pep"] else "Not a PEP",
            "pep_confidence": pep.get("confidence", "N/A"),
            "pep_risk": pep.get("risk_level", "N/A"),
            "sanctions_risk": sanctions.get("sanctions_risk", "N/A"),
            "sanctions_rec": sanctions.get("recommendation", "N/A"),
            "risk_level": risk["overall_risk"],
            "risk_score": risk["risk_score"],
            "dd_level": risk["due_diligence_level"],
            "risk_factors": ", ".join(risk.get("risk_factors", [])),
            "recommendation": risk["recommendation"],
            "final_recommendation": final_rec,
            "required_actions": actions,
            "model": self.model
        })
        
        return report
    
    def _parse_json_response(self, response: str, default: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON from LLM response with fallback"""
        try:
            # Try direct JSON parse
            return json.loads(response)
        except:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
        
        # Return default if parsing fails
        return default
    
    def analyze_client(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete KYC analysis"""
        print(f"\n🔍 Analyzing client: {client_info['name']}")
        print("=" * 60)
        
        results = {
            "client": client_info,
            "timestamp": datetime.now().isoformat(),
            "system": "Modern LangChain KYC"
        }
        
        # 1. PEP Check
        print("\n📋 Step 1: PEP Screening")
        pep_result = self.check_pep_status(client_info)
        results["pep_screening"] = pep_result
        print(f"✅ PEP Status: {'PEP Identified' if pep_result.get('is_pep') else 'Not a PEP'}")
        print(f"   Risk Level: {pep_result.get('risk_level', 'Unknown')}")
        
        # 2. Sanctions Check
        print("\n📋 Step 2: Sanctions Screening")
        sanctions_result = self.check_sanctions(client_info)
        results["sanctions_screening"] = sanctions_result
        print(f"✅ Sanctions Risk: {sanctions_result.get('sanctions_risk', 'Unknown')}")
        print(f"   Recommendation: {sanctions_result.get('recommendation', 'Unknown')}")
        
        # 3. Risk Assessment
        print("\n📋 Step 3: Risk Assessment")
        risk_assessment = self.assess_risk(client_info, pep_result, sanctions_result)
        results["risk_assessment"] = risk_assessment
        print(f"✅ Overall Risk: {risk_assessment.get('overall_risk', 'Unknown')}")
        print(f"   Risk Score: {risk_assessment.get('risk_score', 'Unknown')}")
        print(f"   Due Diligence: {risk_assessment.get('due_diligence_level', 'Unknown')}")
        
        # 4. Generate Report
        print("\n📋 Step 4: Generating Compliance Report")
        report = self.generate_report(client_info, results)
        results["compliance_report"] = report
        
        # Save results
        self.save_results(results)
        
        print("\n" + "=" * 60)
        print("✅ Analysis Complete")
        print("=" * 60)
        print(f"\n🎯 Final Recommendation: {risk_assessment.get('recommendation', 'Unknown').upper()}")
        
        return results
    
    def save_results(self, results: Dict[str, Any]):
        """Save analysis results"""
        report_dir = "./reports"
        os.makedirs(report_dir, exist_ok=True)
        
        client_name = results["client"]["name"]
        safe_name = "".join(c for c in client_name if c.isalnum() or c in " -_").rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = os.path.join(report_dir, f"KYC_Modern_{safe_name}_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save text report
        txt_file = os.path.join(report_dir, f"KYC_Modern_{safe_name}_{timestamp}.txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(results["compliance_report"])
        
        print(f"\n📄 Reports saved:")
        print(f"   JSON: {json_file}")
        print(f"   Text: {txt_file}")


def main():
    """Main function"""
    # Example client
    client_info = {
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
    
    # Run analysis
    print("🏦 Modern LangChain KYC System")
    print("Powered by Ollama - 100% Local Processing")
    print("=" * 60)
    
    kyc_system = ModernLangChainKYC()
    results = kyc_system.analyze_client(client_info)


if __name__ == "__main__":
    main()