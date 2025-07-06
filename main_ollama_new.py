#!/usr/bin/env python3
import os
import json
import warnings
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv()

# For newer versions of langchain
try:
    from langchain_ollama import OllamaLLM
    print("Using langchain-ollama package")
except ImportError:
    from langchain_community.llms import Ollama as OllamaLLM
    print("Using langchain-community package")

from crewai import Agent, Task, Crew, Process
from kyc_agents import KYCAgents
from kyc_tasks import KYCTasks


class KYCAnalysisCrew:
    """KYC Analysis Crew with compatibility fixes"""
    
    def __init__(self):
        self.llm = self._get_llm()
        # Don't pass LLM to agents, let CrewAI handle it
        self.agents = KYCAgents(llm=None)
        self.tasks = KYCTasks()
        
    def _get_llm(self):
        """Get Ollama LLM configured for CrewAI compatibility"""
        model = os.getenv("OLLAMA_MODEL", "mistral")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        print(f"🔒 Configuring Ollama ({model})...")
        
        # For CrewAI compatibility, we need to set it as default
        os.environ["OPENAI_API_BASE"] = base_url + "/v1"
        os.environ["OPENAI_MODEL_NAME"] = model
        os.environ["OPENAI_API_KEY"] = "NA"  # Ollama doesn't need a key
        
        return OllamaLLM(
            model=model,
            base_url=base_url,
            temperature=0
        )
    
    def run_simple_test(self, client_info: Dict):
        """Run a simple test without full crew"""
        print("\n🧪 Testing simplified CrewAI setup...")
        
        try:
            # Create a very simple agent
            test_agent = Agent(
                role="Analyst",
                goal="Analyze information",
                backstory="I analyze data.",
                # Don't pass LLM, let CrewAI use defaults
                verbose=True,
                allow_delegation=False
            )
            
            # Simple task
            test_task = Task(
                description=f"Say this exactly: 'Analyzing {client_info['name']}'",
                expected_output="The exact phrase requested",
                agent=test_agent
            )
            
            # Minimal crew
            crew = Crew(
                agents=[test_agent],
                tasks=[test_task],
                process=Process.sequential,
                verbose=True,
                # Set the LLM at crew level
                language_model=self.llm
            )
            
            result = crew.kickoff()
            print(f"✅ Test successful: {result}")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {type(e).__name__}: {str(e)}")
            return False
    
    def run(self, client_info: Dict):
        """Run KYC analysis"""
        # First try the simple test
        if not self.run_simple_test(client_info):
            print("\n⚠️  CrewAI compatibility issue detected")
            print("Falling back to direct analysis...\n")
            
            from kyc_direct import DirectKYCAnalysis
            analyzer = DirectKYCAnalysis()
            return analyzer.analyze_client(client_info)
        
        print("\n✅ CrewAI is working! Running full analysis...")
        
        # If test passes, try full analysis
        try:
            # Create agents without passing LLM
            research_agent = Agent(
                role="KYC Research Analyst",
                goal="Research client background",
                backstory="I am a KYC analyst.",
                verbose=True,
                allow_delegation=False
            )
            
            # Create simple task
            research_task = Task(
                description=f"Analyze this client: {json.dumps(client_info, indent=2)}",
                expected_output="A brief analysis of the client",
                agent=research_agent
            )
            
            # Create crew with LLM at crew level
            crew = Crew(
                agents=[research_agent],
                tasks=[research_task],
                process=Process.sequential,
                verbose=True,
                language_model=self.llm
            )
            
            result = crew.kickoff()
            
            print(f"\n✅ CrewAI analysis completed: {result}")
            
            # Also run direct analysis for complete results
            print("\nRunning comprehensive analysis...")
            from kyc_direct import DirectKYCAnalysis
            analyzer = DirectKYCAnalysis()
            full_results = analyzer.analyze_client(client_info)
            
            return {
                'crewai_result': str(result),
                'full_analysis': full_results
            }
            
        except Exception as e:
            print(f"\n❌ Full analysis failed: {e}")
            print("Using direct analysis instead...\n")
            
            from kyc_direct import DirectKYCAnalysis
            analyzer = DirectKYCAnalysis()
            return analyzer.analyze_client(client_info)


def main():
    client_info = {
        "name": "John Doe",
        "entity_type": "individual",
        "date_of_birth": "1980-05-15",
        "nationality": "USA",
        "residence_country": "Switzerland",
        "occupation": "Software Engineer"
    }
    
    print("🏦 KYC Analysis System (Ollama Edition)")
    print("=" * 60)
    
    crew = KYCAnalysisCrew()
    result = crew.run(client_info)
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()