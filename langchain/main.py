#!/usr/bin/env python3
"""
LangChain-based KYC Analysis System
Fully compatible with Ollama for local, confidential processing
"""
import os
import sys
import json
import warnings
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

warnings.filterwarnings("ignore")
load_dotenv()

from langchain_ollama import OllamaLLM
from langchain.callbacks import StdOutCallbackHandler
from tools.base_tools import get_kyc_tools
from agents.kyc_agents import KYCAgentFactory
from chains.kyc_workflow import KYCWorkflow, KYCReportGenerator


class LangChainKYCSystem:
    """Complete KYC analysis system using LangChain"""
    
    def __init__(self, model_name: str = "mistral", base_url: Optional[str] = None):
        """Initialize the KYC system"""
        # Use base URL from environment or parameter
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://172.21.16.1:11434")
        self.model_name = model_name
        
        print(f"🔧 Initializing LangChain KYC System")
        print(f"   Model: {self.model_name}")
        print(f"   Ollama URL: {self.base_url}")
        
        # Initialize LLM
        self.llm = OllamaLLM(
            model=self.model_name,
            base_url=self.base_url,
            temperature=0,
            callbacks=[StdOutCallbackHandler()]
        )
        
        # Initialize tools
        self.tools = get_kyc_tools()
        
        # Initialize agent factory
        self.agent_factory = KYCAgentFactory(self.llm)
        
        # Initialize workflow
        self.workflow = KYCWorkflow(self.llm)
        
        print("✅ System initialized successfully")
    
    def test_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            print("\n🧪 Testing Ollama connection...")
            response = self.llm.invoke("Say 'LangChain KYC System Ready'")
            print(f"✅ Ollama response: {response}")
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def run_agent_based_analysis(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Run analysis using LangChain agents"""
        print(f"\n🤖 Running Agent-Based Analysis for: {client_info['name']}")
        print("=" * 60)
        
        results = {
            "client": client_info,
            "research": {},
            "screening": {},
            "risk_assessment": {},
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # 1. Research Agent
            print("\n📚 Phase 1: Research Agent")
            research_agent = self.agent_factory.create_research_agent(
                [tool for tool in self.tools if tool.name == "web_search"]
            )
            
            research_query = f"Research background information about {client_info['name']}, {client_info.get('occupation', '')}, {client_info.get('nationality', '')}"
            research_result = research_agent.run(research_query)
            results["research"] = {"findings": research_result}
            
            # 2. Compliance Agent
            print("\n🔍 Phase 2: Compliance Screening Agent")
            compliance_agent = self.agent_factory.create_compliance_agent(self.tools)
            
            compliance_query = f"""Screen this client for compliance:
            Name: {client_info['name']}
            Nationality: {client_info.get('nationality', 'Unknown')}
            Date of Birth: {client_info.get('date_of_birth', 'Unknown')}
            
            Perform PEP check, sanctions screening, and risk assessment."""
            
            compliance_result = compliance_agent.run(compliance_query)
            results["screening"] = {"result": compliance_result}
            
            # 3. Risk Analysis Agent
            print("\n📊 Phase 3: Risk Analysis Agent")
            risk_agent = self.agent_factory.create_risk_analyst_agent(self.tools)
            
            risk_query = f"""Analyze the overall risk for client {client_info['name']} based on:
            Client Info: {json.dumps(client_info)}
            Screening Results: {compliance_result}
            
            Provide comprehensive risk assessment and recommendations."""
            
            risk_result = risk_agent.run(risk_query)
            results["risk_assessment"] = {"analysis": risk_result}
            
            return results
            
        except Exception as e:
            print(f"\n❌ Agent analysis error: {type(e).__name__}: {str(e)}")
            results["error"] = str(e)
            return results
    
    def run_workflow_analysis(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Run analysis using LangChain workflow chains"""
        print(f"\n⚙️  Running Workflow-Based Analysis for: {client_info['name']}")
        print("=" * 60)
        
        try:
            # First, run tool-based screening
            print("\n🔧 Running automated screening tools...")
            
            screening_results = {}
            
            # PEP Check
            pep_tool = next(tool for tool in self.tools if tool.name == "pep_check")
            pep_result = pep_tool.run({
                "name": client_info["name"],
                "nationality": client_info.get("nationality"),
                "date_of_birth": client_info.get("date_of_birth")
            })
            screening_results["pep_check"] = json.loads(pep_result)
            
            # Sanctions Check
            sanctions_tool = next(tool for tool in self.tools if tool.name == "sanctions_check")
            sanctions_result = sanctions_tool.run({
                "name": client_info["name"],
                "entity_type": client_info.get("entity_type", "individual"),
                "nationality": client_info.get("nationality")
            })
            screening_results["sanctions_check"] = json.loads(sanctions_result)
            
            # Risk Assessment
            risk_tool = next(tool for tool in self.tools if tool.name == "risk_assessment")
            risk_result = risk_tool.run({
                "client_info": json.dumps(client_info),
                "pep_result": pep_result,
                "sanctions_result": sanctions_result
            })
            screening_results["risk_assessment"] = json.loads(risk_result)
            
            # Web Search
            search_tool = next(tool for tool in self.tools if tool.name == "web_search")
            search_result = search_tool.run({
                "query": f"{client_info['name']} {client_info.get('nationality', '')} news",
                "num_results": 5
            })
            screening_results["adverse_media"] = json.loads(search_result)
            
            print("\n📋 Running workflow chains...")
            # Run workflow
            workflow_results = self.workflow.run_workflow(client_info, screening_results)
            
            # Generate report
            report = KYCReportGenerator.generate_report(
                client_info=client_info,
                screening_results=screening_results,
                risk_analysis=screening_results["risk_assessment"],
                compliance_report=workflow_results.get("compliance_report", "")
            )
            
            # Save report
            filepath = KYCReportGenerator.save_report(report)
            print(f"\n📄 Report saved to: {filepath}")
            
            return report
            
        except Exception as e:
            print(f"\n❌ Workflow error: {type(e).__name__}: {str(e)}")
            return {"error": str(e)}
    
    def run_complete_analysis(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete KYC analysis combining agents and workflows"""
        print(f"\n🏦 LangChain KYC Analysis System")
        print(f"🔍 Analyzing: {client_info['name']}")
        print("=" * 60)
        
        # Test connection first
        if not self.test_connection():
            return {"error": "Failed to connect to Ollama"}
        
        # Run workflow-based analysis (more reliable)
        print("\n" + "=" * 60)
        print("Starting Comprehensive KYC Analysis")
        print("=" * 60)
        
        results = self.run_workflow_analysis(client_info)
        
        return results


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
    
    try:
        # Initialize system
        kyc_system = LangChainKYCSystem()
        
        # Run analysis
        results = kyc_system.run_complete_analysis(client_info)
        
        if "error" not in results:
            print("\n" + "=" * 60)
            print("✅ Analysis Complete!")
            print("=" * 60)
            print(f"\nReport ID: {results.get('report_id', 'N/A')}")
            print(f"Risk Level: {results.get('risk_assessment', {}).get('risk_level', 'N/A')}")
            print(f"Recommendation: See full report for details")
        else:
            print(f"\n❌ Analysis failed: {results['error']}")
            
    except Exception as e:
        print(f"\n❌ System error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()