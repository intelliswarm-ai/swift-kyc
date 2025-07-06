#!/usr/bin/env python3
"""
Working CrewAI + Ollama configuration based on official examples
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Based on CrewAI examples - use the older import style
from langchain.llms import Ollama
from crewai import Agent, Task, Crew, Process

# Import our custom tools
from tools.pep_tools_simple import PEPCheckTool
from tools.sanctions_tools_simple import SanctionsCheckTool
from tools.risk_assessment_tools_simple import RiskAssessmentTool


class WorkingKYCAnalysis:
    """KYC Analysis using the pattern from CrewAI examples"""
    
    def __init__(self):
        # Initialize Ollama following the stock_analysis example pattern
        self.ollama_model = Ollama(model="mistral")  # or "openhermes" as shown in example
        
        # Initialize tools
        self.pep_tool = PEPCheckTool()
        self.sanctions_tool = SanctionsCheckTool()
        self.risk_tool = RiskAssessmentTool()
    
    def create_agents(self):
        """Create agents following the example pattern"""
        
        # Research Agent - simplified version
        research_agent = Agent(
            role='KYC Research Analyst',
            goal='Gather information about the client',
            backstory="""You are an experienced KYC analyst working for a Swiss bank.
            Your job is to research clients and identify any risks.""",
            verbose=True,
            allow_delegation=False,
            llm=self.ollama_model  # Pass Ollama model as shown in example
        )
        
        # Compliance Agent
        compliance_agent = Agent(
            role='Compliance Officer',
            goal='Assess compliance risks and make recommendations',
            backstory="""You are a senior compliance officer with expertise in
            Swiss banking regulations and international KYC standards.""",
            verbose=True,
            allow_delegation=False,
            llm=self.ollama_model,
            tools=[self.pep_tool, self.sanctions_tool, self.risk_tool]
        )
        
        return research_agent, compliance_agent
    
    def create_tasks(self, client_info, research_agent, compliance_agent):
        """Create tasks for the agents"""
        
        # Research task
        research_task = Task(
            description=f"""
            Research the following client and provide a summary:
            
            Name: {client_info['name']}
            Type: {client_info['entity_type']}
            Nationality: {client_info.get('nationality', 'Unknown')}
            Occupation: {client_info.get('occupation', 'Unknown')}
            
            Provide a brief overview of any findings.
            """,
            agent=research_agent,
            expected_output="A brief research summary about the client"
        )
        
        # Compliance task
        compliance_task = Task(
            description=f"""
            Perform compliance checks for this client:
            
            {json.dumps(client_info, indent=2)}
            
            Use the available tools to:
            1. Check PEP status
            2. Screen sanctions lists
            3. Assess overall risk
            
            Provide a compliance recommendation.
            """,
            agent=compliance_agent,
            expected_output="A compliance assessment with clear recommendations"
        )
        
        return [research_task, compliance_task]
    
    def run_analysis(self, client_info):
        """Run the KYC analysis"""
        print("\n🚀 Running KYC Analysis (CrewAI + Ollama)")
        print("=" * 60)
        
        try:
            # Create agents
            research_agent, compliance_agent = self.create_agents()
            
            # Create tasks
            tasks = self.create_tasks(client_info, research_agent, compliance_agent)
            
            # Create crew
            crew = Crew(
                agents=[research_agent, compliance_agent],
                tasks=tasks,
                verbose=True,
                process=Process.sequential
            )
            
            # Execute
            print("\nStarting crew execution...")
            result = crew.kickoff()
            
            print("\n✅ Crew execution completed!")
            return {
                'status': 'success',
                'result': str(result),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
            
            # Fallback to direct analysis
            print("\nFalling back to direct tool execution...")
            return self.direct_analysis(client_info)
    
    def direct_analysis(self, client_info):
        """Direct analysis without CrewAI if needed"""
        from kyc_direct import DirectKYCAnalysis
        analyzer = DirectKYCAnalysis()
        return analyzer.analyze_client(client_info)


def test_ollama():
    """Test if Ollama is working"""
    try:
        print("Testing Ollama connection...")
        ollama = Ollama(model="mistral")
        response = ollama("Say 'Ollama is working'")
        print(f"✅ Ollama test successful: {response}")
        return True
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False


def main():
    # Test Ollama first
    if not test_ollama():
        print("\nPlease ensure Ollama is running and mistral model is installed:")
        print("  ollama serve")
        print("  ollama pull mistral")
        return
    
    # Example client
    client_info = {
        "name": "John Doe",
        "entity_type": "individual",
        "date_of_birth": "1980-05-15",
        "nationality": "USA",
        "residence_country": "Switzerland",
        "occupation": "Software Engineer",
        "industry": "Technology"
    }
    
    # Run analysis
    analyzer = WorkingKYCAnalysis()
    result = analyzer.run_analysis(client_info)
    
    print("\n" + "=" * 60)
    print("✅ Analysis Complete")
    print("=" * 60)
    
    # Save results
    if isinstance(result, dict) and 'compliance_report' in result:
        # Direct analysis result
        report_path = result.get('compliance_report', {})
        print(f"\nFull report saved to: ./reports/")
    else:
        # CrewAI result
        print(f"\nResult: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()