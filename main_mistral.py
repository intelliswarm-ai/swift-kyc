#!/usr/bin/env python3
import os
import json
import warnings
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# Set environment variable to ensure CrewAI uses the right format
os.environ["OPENAI_API_BASE"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
os.environ["OPENAI_API_KEY"] = "dummy"  # Ollama doesn't need a key

from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama


class SimpleKYCAnalysis:
    """Simplified KYC Analysis using CrewAI with Mistral"""
    
    def __init__(self):
        # Create Ollama LLM with Mistral
        self.llm = Ollama(
            model="mistral",
            base_url="http://localhost:11434",
            temperature=0,
            # Keep responses focused
            system="You are a helpful KYC analyst. Be concise and direct in your responses.",
            # Mistral-specific parameters
            mirostat=0,
            mirostat_tau=5.0,
            mirostat_eta=0.1,
            repeat_penalty=1.1,
            top_k=40,
            top_p=0.9,
        )
        
    def create_simple_agent(self):
        """Create a simple agent that should work with Mistral"""
        return Agent(
            role="KYC Analyst",
            goal="Analyze client information for compliance",
            backstory="You are an experienced KYC analyst working for a Swiss bank.",
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=1,  # Prevent loops
            # Simplified tools approach
            tools=[]  # No tools for now to avoid complexity
        )
    
    def run_analysis(self, client_info: Dict):
        """Run a simplified analysis"""
        print("\n🚀 Starting Simplified CrewAI Analysis with Mistral...")
        
        try:
            # Create agent
            analyst = self.create_simple_agent()
            
            # Create a simple task
            task = Task(
                description=f"""
                Analyze this client for KYC compliance:
                
                Name: {client_info['name']}
                Type: {client_info['entity_type']}
                Nationality: {client_info.get('nationality', 'Unknown')}
                
                Provide a brief risk assessment with:
                1. Risk level (Low/Medium/High)
                2. Key factors
                3. Recommendation
                
                Keep your response under 100 words.
                """,
                expected_output="A brief risk assessment",
                agent=analyst
            )
            
            # Create minimal crew
            crew = Crew(
                agents=[analyst],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            # Execute
            print("\nExecuting crew...")
            result = crew.kickoff()
            
            print(f"\n✅ CrewAI Result: {result}")
            
            # Now run the full direct analysis
            print("\n" + "="*60)
            print("Running Full KYC Analysis...")
            print("="*60)
            
            from kyc_direct import DirectKYCAnalysis
            analyzer = DirectKYCAnalysis()
            full_results = analyzer.analyze_client(client_info)
            
            return {
                'crewai_test': 'success',
                'crewai_result': str(result),
                'full_analysis': full_results
            }
            
        except Exception as e:
            print(f"\n❌ CrewAI Error: {type(e).__name__}: {str(e)}")
            print("\nFalling back to direct analysis...")
            
            from kyc_direct import DirectKYCAnalysis
            analyzer = DirectKYCAnalysis()
            return analyzer.analyze_client(client_info)


def test_basic_mistral():
    """Test basic Mistral functionality"""
    print("Testing basic Mistral LLM...")
    try:
        llm = Ollama(model="mistral", base_url="http://localhost:11434")
        response = llm.invoke("Say 'Mistral is working' and nothing else.")
        print(f"✅ Mistral test: {response}")
        return True
    except Exception as e:
        print(f"❌ Mistral test failed: {e}")
        return False


def main():
    # Test Mistral first
    if not test_basic_mistral():
        print("\nPlease ensure Mistral is working with: ollama run mistral")
        return
    
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
    analyzer = SimpleKYCAnalysis()
    results = analyzer.run_analysis(client_info)
    
    print("\n" + "="*60)
    print("✅ COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()