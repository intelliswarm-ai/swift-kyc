#!/usr/bin/env python3
"""
Enhanced LangChain KYC System with all CrewAI functionality
Complete multi-agent system with enhanced tools
"""
import os
import sys
import json
import warnings
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv()

from langchain_ollama import OllamaLLM
from langchain.callbacks import StdOutCallbackHandler
from tools_langchain.enhanced_tools import get_enhanced_kyc_tools
from agents.enhanced_agents import EnhancedKYCAgents
from chains.kyc_workflow import KYCWorkflow, KYCReportGenerator


class EnhancedLangChainKYC:
    """Complete KYC system with all CrewAI functionality in LangChain"""
    
    def __init__(self):
        # Configuration
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://172.21.16.1:11434")
        self.model = os.getenv("OLLAMA_MODEL", "mistral")
        
        print(f"🔧 Initializing Enhanced LangChain KYC System")
        print(f"   Ollama URL: {self.base_url}")
        print(f"   Model: {self.model}")
        
        # Initialize LLM
        self.llm = OllamaLLM(
            model=self.model,
            base_url=self.base_url,
            temperature=0,
            callbacks=[StdOutCallbackHandler()]
        )
        
        # Initialize enhanced tools
        self.tools = get_enhanced_kyc_tools()
        self.tool_dict = {tool.name: tool for tool in self.tools}
        
        # Initialize agent factory
        self.agent_factory = EnhancedKYCAgents(self.llm)
        
        # Initialize workflow
        self.workflow = KYCWorkflow(self.llm)
        
        print("✅ Enhanced system initialized with all features")
    
    def run_multi_agent_analysis(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Run full multi-agent KYC analysis like CrewAI"""
        print(f"\n🤖 Running Multi-Agent KYC Analysis")
        print(f"Client: {client_info['name']}")
        print("=" * 60)
        
        results = {
            "client": client_info,
            "timestamp": datetime.now().isoformat(),
            "agents_results": {},
            "consolidated_findings": {}
        }
        
        try:
            # 1. Research Agent - Gather background information
            print("\n📚 Agent 1: Research Analyst")
            print("-" * 40)
            research_tools = [
                self.tool_dict["browser_search"],
                self.tool_dict["enhanced_pep_check"]  # Can also search
            ]
            research_agent = self.agent_factory.create_research_analyst(research_tools)
            
            research_input = f"""
            Research client: {json.dumps(client_info, indent=2)}
            
            Perform comprehensive background research including:
            1. Business activities and affiliations
            2. Public profile and media presence
            3. Corporate relationships
            4. Any red flags or concerns
            """
            
            research_result = research_agent.invoke({"input": research_input})
            results["agents_results"]["research"] = research_result
            
            # 2. PEP Screening Agent
            print("\n👔 Agent 2: PEP Screening Specialist")
            print("-" * 40)
            pep_tools = [
                self.tool_dict["enhanced_pep_check"],
                self.tool_dict["browser_search"]
            ]
            pep_agent = self.agent_factory.create_pep_screening_specialist(pep_tools)
            
            pep_input = f"""
            Screen for PEP status: {json.dumps(client_info, indent=2)}
            
            Previous research findings: {research_result.get('output', 'No findings')}
            
            Check:
            1. Direct PEP status
            2. Family members
            3. Close associates
            4. Political connections
            """
            
            pep_result = pep_agent.invoke({"input": pep_input})
            results["agents_results"]["pep_screening"] = pep_result
            
            # 3. Sanctions Screening Agent
            print("\n🚫 Agent 3: Sanctions Compliance Officer")
            print("-" * 40)
            sanctions_tools = [
                self.tool_dict["enhanced_sanctions_check"]
            ]
            sanctions_agent = self.agent_factory.create_sanctions_compliance_officer(sanctions_tools)
            
            sanctions_input = f"""
            Screen for sanctions: {json.dumps(client_info, indent=2)}
            
            Check all major lists:
            - OFAC
            - EU
            - UN
            - UK
            - Swiss SECO
            """
            
            sanctions_result = sanctions_agent.invoke({"input": sanctions_input})
            results["agents_results"]["sanctions"] = sanctions_result
            
            # 4. Risk Assessment Agent
            print("\n📊 Agent 4: Risk Assessment Analyst")
            print("-" * 40)
            risk_tools = [
                self.tool_dict["enhanced_risk_assessment"]
            ]
            risk_agent = self.agent_factory.create_risk_assessment_analyst(risk_tools)
            
            # Prepare findings for risk assessment
            all_findings = {
                "research": research_result.get("output", ""),
                "pep_screening": pep_result.get("output", ""),
                "sanctions_screening": sanctions_result.get("output", "")
            }
            
            risk_input = f"""
            Assess overall risk for: {json.dumps(client_info, indent=2)}
            
            Based on findings:
            {json.dumps(all_findings, indent=2)}
            
            Calculate comprehensive risk score and provide recommendations.
            """
            
            risk_result = risk_agent.invoke({"input": risk_input})
            results["agents_results"]["risk_assessment"] = risk_result
            
            # 5. Compliance Report Writer
            print("\n📝 Agent 5: Compliance Report Writer")
            print("-" * 40)
            report_agent = self.agent_factory.create_compliance_report_writer([])
            
            report_input = f"""
            Create comprehensive KYC report for: {json.dumps(client_info, indent=2)}
            
            Findings:
            - Research: {research_result.get('output', 'N/A')}
            - PEP Status: {pep_result.get('output', 'N/A')}
            - Sanctions: {sanctions_result.get('output', 'N/A')}
            - Risk Assessment: {risk_result.get('output', 'N/A')}
            
            Create professional compliance report with clear recommendations.
            """
            
            report_result = report_agent.invoke({"input": report_input})
            results["agents_results"]["report"] = report_result
            
            # 6. Quality Review (Optional)
            print("\n✅ Agent 6: Quality Review")
            print("-" * 40)
            review_agent = self.agent_factory.create_quality_review_agent([])
            
            review_input = f"""
            Review KYC analysis completeness:
            
            Client: {client_info['name']}
            Agents completed: Research, PEP, Sanctions, Risk, Report
            
            Verify all requirements are met.
            """
            
            review_result = review_agent.invoke({"input": review_input})
            results["agents_results"]["quality_review"] = review_result
            
            # Consolidate findings
            results["consolidated_findings"] = self._consolidate_findings(results["agents_results"])
            
            # Save comprehensive report
            self._save_enhanced_report(results)
            
            return results
            
        except Exception as e:
            print(f"\n❌ Multi-agent analysis error: {type(e).__name__}: {str(e)}")
            results["error"] = str(e)
            return results
    
    def run_enhanced_tools_demo(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Demonstrate all enhanced tools functionality"""
        print(f"\n🔧 Running Enhanced Tools Demonstration")
        print("=" * 60)
        
        demo_results = {}
        
        # 1. Enhanced PEP Check
        print("\n1️⃣ Enhanced PEP Check Tool")
        pep_tool = self.tool_dict["enhanced_pep_check"]
        pep_result = pep_tool.run({
            "name": client_info["name"],
            "nationality": client_info.get("nationality"),
            "fuzzy_match": True,
            "online_search": False  # For demo
        })
        demo_results["enhanced_pep"] = json.loads(pep_result)
        print(f"Result: {demo_results['enhanced_pep']['pep_status']}")
        
        # 2. Enhanced Sanctions Check
        print("\n2️⃣ Enhanced Sanctions Check Tool")
        sanctions_tool = self.tool_dict["enhanced_sanctions_check"]
        sanctions_result = sanctions_tool.run({
            "name": client_info["name"],
            "entity_type": client_info.get("entity_type", "individual"),
            "nationality": client_info.get("nationality")
        })
        demo_results["enhanced_sanctions"] = json.loads(sanctions_result)
        print(f"Result: {demo_results['enhanced_sanctions']['risk_level']} risk")
        
        # 3. Enhanced Risk Assessment
        print("\n3️⃣ Enhanced Risk Assessment Tool")
        risk_tool = self.tool_dict["enhanced_risk_assessment"]
        risk_result = risk_tool.run({
            "client_info": json.dumps(client_info),
            "pep_result": pep_result,
            "sanctions_result": sanctions_result
        })
        demo_results["enhanced_risk"] = json.loads(risk_result)
        print(f"Result: Risk score {demo_results['enhanced_risk']['risk_score']}")
        
        # 4. Browser Search Tool
        print("\n4️⃣ Browser Search Tool")
        browser_tool = self.tool_dict["browser_search"]
        search_result = browser_tool.run({
            "query": f"{client_info['name']} {client_info.get('nationality', '')}",
            "search_type": "pep",
            "num_results": 3
        })
        demo_results["browser_search"] = json.loads(search_result)
        print(f"Result: Found {demo_results['browser_search']['results_count']} results")
        
        # 5. Database Update Tool
        print("\n5️⃣ Database Update Tool")
        update_tool = self.tool_dict["database_update"]
        update_result = update_tool.run({
            "update_type": "all",
            "source": None
        })
        demo_results["database_update"] = json.loads(update_result)
        print(f"Result: {demo_results['database_update']['message']}")
        
        return demo_results
    
    def _consolidate_findings(self, agents_results: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate findings from all agents"""
        consolidated = {
            "summary": {},
            "key_findings": [],
            "risk_indicators": [],
            "recommendations": []
        }
        
        # Extract key information from each agent
        for agent_name, result in agents_results.items():
            output = result.get("output", "")
            
            # Add to summary
            consolidated["summary"][agent_name] = output[:200] + "..." if len(output) > 200 else output
            
            # Extract risk indicators (simplified)
            if "high risk" in output.lower():
                consolidated["risk_indicators"].append(f"{agent_name}: High risk identified")
            elif "medium risk" in output.lower():
                consolidated["risk_indicators"].append(f"{agent_name}: Medium risk identified")
            
            # Extract recommendations
            if "recommend" in output.lower():
                # This is simplified - in production, parse more carefully
                consolidated["recommendations"].append(f"From {agent_name}")
        
        return consolidated
    
    def _save_enhanced_report(self, results: Dict[str, Any]):
        """Save enhanced multi-agent report"""
        report_dir = "./reports"
        os.makedirs(report_dir, exist_ok=True)
        
        client_name = results["client"]["name"]
        safe_name = "".join(c for c in client_name if c.isalnum() or c in " -_").rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON report
        json_file = os.path.join(report_dir, f"KYC_Enhanced_{safe_name}_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Create summary report
        summary_file = os.path.join(report_dir, f"KYC_Enhanced_{safe_name}_{timestamp}_summary.txt")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("ENHANCED KYC ANALYSIS SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Client: {client_name}\n")
            f.write(f"Date: {results['timestamp']}\n\n")
            
            f.write("AGENT FINDINGS:\n")
            f.write("-" * 40 + "\n")
            for agent, finding in results.get("consolidated_findings", {}).get("summary", {}).items():
                f.write(f"\n{agent.upper()}:\n{finding}\n")
            
            f.write("\n\nRISK INDICATORS:\n")
            f.write("-" * 40 + "\n")
            for indicator in results.get("consolidated_findings", {}).get("risk_indicators", []):
                f.write(f"- {indicator}\n")
        
        print(f"\n📄 Reports saved:")
        print(f"   Detailed: {json_file}")
        print(f"   Summary: {summary_file}")


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
    
    print("🏦 Enhanced LangChain KYC System")
    print("All CrewAI functionality migrated to LangChain")
    print("=" * 60)
    
    system = EnhancedLangChainKYC()
    
    # Run full multi-agent analysis
    print("\n🚀 Starting Multi-Agent Analysis...")
    results = system.run_multi_agent_analysis(client_info)
    
    # Also demonstrate enhanced tools
    print("\n\n🔧 Enhanced Tools Demonstration...")
    tools_demo = system.run_enhanced_tools_demo(client_info)
    
    print("\n" + "=" * 60)
    print("✅ Enhanced KYC Analysis Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()