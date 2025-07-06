#!/usr/bin/env python3
"""
Simplified LangChain KYC System
Direct tool execution with LLM analysis
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
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


class SimpleLangChainKYC:
    """Simplified KYC system using LangChain and Ollama"""
    
    def __init__(self):
        # Get Ollama URL from environment
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://172.21.16.1:11434")
        self.model = os.getenv("OLLAMA_MODEL", "mistral")
        
        print(f"🔧 Initializing Simplified LangChain KYC")
        print(f"   Ollama URL: {self.base_url}")
        print(f"   Model: {self.model}")
        
        # Initialize LLM
        self.llm = OllamaLLM(
            model=self.model,
            base_url=self.base_url,
            temperature=0
        )
        
        print("✅ System ready")
    
    def check_pep_status(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check PEP status using LLM"""
        prompt = PromptTemplate(
            input_variables=["name", "nationality", "occupation"],
            template="""Analyze if this person could be a Politically Exposed Person (PEP):

Name: {name}
Nationality: {nationality}
Occupation: {occupation}

Consider:
1. Is the occupation politically exposed (government, military, judiciary)?
2. Are they from a high-risk country?
3. Could they be related to a PEP?

Provide your analysis in JSON format:
{{
    "is_pep": true/false,
    "confidence": "high/medium/low",
    "reasons": ["reason1", "reason2"],
    "risk_level": "high/medium/low"
}}

Analysis:"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            result = chain.run(
                name=client_info.get("name", "Unknown"),
                nationality=client_info.get("nationality", "Unknown"),
                occupation=client_info.get("occupation", "Unknown")
            )
            
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "is_pep": False,
                    "confidence": "low",
                    "reasons": ["Could not parse response"],
                    "risk_level": "low"
                }
        except Exception as e:
            print(f"PEP check error: {e}")
            return {
                "is_pep": False,
                "confidence": "low", 
                "reasons": [str(e)],
                "risk_level": "low"
            }
    
    def check_sanctions(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check sanctions status using LLM"""
        prompt = PromptTemplate(
            input_variables=["name", "nationality", "countries"],
            template="""Assess sanctions risk for this client:

Name: {name}
Nationality: {nationality}
Business Countries: {countries}

Consider:
1. Is the nationality or any business country under sanctions?
2. Does the name suggest any sanctioned entity?
3. Are there any red flags?

High-risk countries include: Iran, North Korea, Syria, Russia, Belarus, Myanmar

Provide analysis in JSON format:
{{
    "sanctions_risk": "high/medium/low",
    "flagged_countries": ["country1", "country2"],
    "reasons": ["reason1", "reason2"],
    "recommendation": "proceed/review/reject"
}}

Analysis:"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            countries = ", ".join(client_info.get("business_countries", []))
            result = chain.run(
                name=client_info.get("name", "Unknown"),
                nationality=client_info.get("nationality", "Unknown"),
                countries=countries
            )
            
            # Parse JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "sanctions_risk": "low",
                    "flagged_countries": [],
                    "reasons": ["Could not parse response"],
                    "recommendation": "proceed"
                }
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
        """Comprehensive risk assessment"""
        prompt = PromptTemplate(
            input_variables=["client_info", "pep_result", "sanctions_result"],
            template="""Perform comprehensive KYC risk assessment:

Client Information:
{client_info}

PEP Screening Result:
{pep_result}

Sanctions Screening Result:
{sanctions_result}

Provide a comprehensive risk assessment in JSON format:
{{
    "overall_risk": "high/medium/low",
    "risk_score": 0.0-1.0,
    "risk_factors": ["factor1", "factor2"],
    "due_diligence_level": "standard/enhanced",
    "recommendation": "approve/conditional_approve/reject",
    "additional_checks_required": ["check1", "check2"]
}}

Assessment:"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            result = chain.run(
                client_info=json.dumps(client_info, indent=2),
                pep_result=json.dumps(pep_result, indent=2),
                sanctions_result=json.dumps(sanctions_result, indent=2)
            )
            
            # Parse JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Default low risk
                return {
                    "overall_risk": "low",
                    "risk_score": 0.2,
                    "risk_factors": ["Standard profile"],
                    "due_diligence_level": "standard",
                    "recommendation": "approve",
                    "additional_checks_required": []
                }
        except Exception as e:
            print(f"Risk assessment error: {e}")
            return {
                "overall_risk": "medium",
                "risk_score": 0.5,
                "risk_factors": ["Assessment error"],
                "due_diligence_level": "enhanced",
                "recommendation": "conditional_approve",
                "additional_checks_required": ["Manual review"]
            }
    
    def generate_report(self, client_info: Dict[str, Any], pep_result: Dict[str, Any],
                       sanctions_result: Dict[str, Any], risk_assessment: Dict[str, Any]) -> str:
        """Generate compliance report"""
        prompt = PromptTemplate(
            input_variables=["client_name", "client_info", "pep_result", 
                           "sanctions_result", "risk_assessment", "date"],
            template="""Generate a professional KYC Compliance Report:

# KYC COMPLIANCE REPORT

**Date:** {date}
**Client:** {client_name}

## Executive Summary
Provide a brief summary of the KYC analysis and final recommendation.

## Client Profile
{client_info}

## Screening Results

### PEP Status
{pep_result}

### Sanctions Screening
{sanctions_result}

## Risk Assessment
{risk_assessment}

## Compliance Recommendation
Based on the analysis, provide a clear recommendation with any conditions.

## Required Actions
List any follow-up actions or additional documentation required.

---
Generated by LangChain KYC System

Full Report:"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        report = chain.run(
            client_name=client_info["name"],
            client_info=json.dumps(client_info, indent=2),
            pep_result=json.dumps(pep_result, indent=2),
            sanctions_result=json.dumps(sanctions_result, indent=2),
            risk_assessment=json.dumps(risk_assessment, indent=2),
            date=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        
        return report
    
    def analyze_client(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete KYC analysis"""
        print(f"\n🔍 Analyzing client: {client_info['name']}")
        print("=" * 60)
        
        results = {
            "client": client_info,
            "timestamp": datetime.now().isoformat(),
            "system": "LangChain KYC"
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
        report = self.generate_report(client_info, pep_result, sanctions_result, risk_assessment)
        results["compliance_report"] = report
        
        # Save results
        self.save_results(results)
        
        print("\n" + "=" * 60)
        print("✅ Analysis Complete")
        print("=" * 60)
        
        return results
    
    def save_results(self, results: Dict[str, Any]):
        """Save analysis results"""
        report_dir = "./reports"
        os.makedirs(report_dir, exist_ok=True)
        
        client_name = results["client"]["name"]
        safe_name = "".join(c for c in client_name if c.isalnum() or c in " -_").rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = os.path.join(report_dir, f"KYC_LangChain_{safe_name}_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save text report
        txt_file = os.path.join(report_dir, f"KYC_LangChain_{safe_name}_{timestamp}.txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(results["compliance_report"])
        
        print(f"\n✅ Reports saved:")
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
    kyc_system = SimpleLangChainKYC()
    results = kyc_system.analyze_client(client_info)
    
    # Print recommendation
    print(f"\n🎯 Final Recommendation: {results['risk_assessment'].get('recommendation', 'Unknown')}")


if __name__ == "__main__":
    main()