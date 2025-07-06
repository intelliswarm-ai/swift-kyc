#!/usr/bin/env python3
import os
import json
import warnings
from datetime import datetime
from typing import Dict, Optional
from crewai import Crew, Process
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_community.llms import Ollama

from kyc_agents import KYCAgents
from kyc_tasks import KYCTasks

# Load environment variables
load_dotenv()


class KYCAnalysisCrew:
    """KYC Analysis Crew for comprehensive client due diligence"""
    
    def __init__(self, llm=None):
        """Initialize the KYC Analysis Crew"""
        self.llm = llm or self._get_llm()
        self.agents = KYCAgents(self.llm)
        self.tasks = KYCTasks()
        
    def _get_llm(self):
        """Get the configured LLM (Ollama or OpenAI)"""
        use_ollama = os.getenv("USE_OLLAMA", "true").lower() == "true"
        
        if use_ollama:
            # Use Ollama for local processing with minimal parameters
            model_name = os.getenv("OLLAMA_MODEL", "llama2")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            
            print(f"🔒 Using Ollama ({model_name}) for confidential local processing")
            
            # Simplified Ollama configuration
            return Ollama(
                model=model_name,
                base_url=base_url,
                temperature=0
            )
        else:
            # Fallback to OpenAI if explicitly disabled
            model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
            print(f"⚠️  Using OpenAI ({model_name}) - Data will be sent to external API")
            
            return ChatOpenAI(
                model_name=model_name,
                temperature=0
            )
    
    def run(self, client_info: Dict) -> Dict:
        """Run the KYC analysis for a client"""
        
        # Validate required fields
        if 'name' not in client_info:
            raise ValueError("Client name is required")
        if 'entity_type' not in client_info:
            client_info['entity_type'] = 'individual'
        
        # Create agents
        research_agent = self.agents.research_analyst()
        pep_agent = self.agents.pep_screening_specialist()
        sanctions_agent = self.agents.sanctions_compliance_officer()
        risk_agent = self.agents.risk_assessment_analyst()
        compliance_agent = self.agents.compliance_report_writer()
        
        # Create tasks
        research_task = self.tasks.research_client_background(
            research_agent,
            json.dumps(client_info, indent=2)
        )
        
        pep_task = self.tasks.screen_pep_status(
            pep_agent,
            json.dumps(client_info, indent=2),
            "{research_findings}"
        )
        
        sanctions_task = self.tasks.check_sanctions_lists(
            sanctions_agent,
            json.dumps(client_info, indent=2)
        )
        
        risk_task = self.tasks.assess_client_risk(
            risk_agent,
            json.dumps(client_info, indent=2),
            "{all_findings}"
        )
        
        compliance_task = self.tasks.compile_kyc_report(
            compliance_agent,
            json.dumps(client_info, indent=2),
            "{all_assessments}"
        )
        
        # Create and run the crew with error handling
        crew = Crew(
            agents=[
                research_agent,
                pep_agent,
                sanctions_agent,
                risk_agent,
                compliance_agent
            ],
            tasks=[
                research_task,
                pep_task,
                sanctions_task,
                risk_task,
                compliance_task
            ],
            process=Process.sequential,
            verbose=True,
            max_iter=3  # Limit iterations to prevent infinite loops
        )
        
        try:
            # Execute the crew
            result = crew.kickoff()
            
            # Save the report
            self._save_report(client_info['name'], result)
            
            return {
                'status': 'completed',
                'timestamp': datetime.now().isoformat(),
                'client': client_info,
                'report': result
            }
        except Exception as e:
            print(f"\n⚠️  Error during crew execution: {str(e)}")
            
            # Return partial result
            return {
                'status': 'partial',
                'timestamp': datetime.now().isoformat(),
                'client': client_info,
                'error': str(e),
                'report': 'Analysis could not be completed due to an error.'
            }
    
    def _save_report(self, client_name: str, report_content):
        """Save the KYC report to file"""
        report_dir = os.getenv("REPORT_OUTPUT_DIR", "./reports")
        os.makedirs(report_dir, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in client_name if c.isalnum() or c in [' ', '-', '_']).rstrip()
        filename = f"KYC_Report_{safe_name}_{timestamp}.json"
        
        filepath = os.path.join(report_dir, filename)
        
        # Handle both string and object report content
        if isinstance(report_content, str):
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'client_name': client_name,
                'report': report_content
            }
        else:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'client_name': client_name,
                'report': str(report_content)
            }
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nReport saved to: {filepath}")


def test_ollama_connection():
    """Test if Ollama is properly configured"""
    try:
        ollama = Ollama(model="llama2", base_url="http://localhost:11434")
        response = ollama.invoke("Hello, are you working?")
        print(f"✅ Ollama test successful. Response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Ollama test failed: {str(e)}")
        return False


def main():
    """Main function to run KYC analysis"""
    
    # Check if Ollama is running
    if os.getenv("USE_OLLAMA", "true").lower() == "true":
        import requests
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        try:
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    print(f"✅ Ollama is running with models: {[m['name'] for m in models]}")
                    
                    # Test Ollama connection
                    print("\nTesting Ollama connection...")
                    if not test_ollama_connection():
                        print("\n⚠️  Ollama connection test failed. Please check your setup.")
                        return
                else:
                    print("⚠️  Ollama is running but no models found. Run: ollama pull llama2")
                    return
            else:
                print("❌ Ollama is not responding properly")
                return
        except Exception as e:
            print(f"❌ Cannot connect to Ollama at {ollama_url}")
            print("Please ensure Ollama is running: ollama serve")
            return
    
    # Example client information
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
    
    print("\n🔍 Starting KYC Analysis...")
    print(f"Client: {client_info['name']}")
    print("-" * 50)
    
    # Initialize and run the crew
    kyc_crew = KYCAnalysisCrew()
    
    try:
        result = kyc_crew.run(client_info)
        
        if result['status'] == 'completed':
            print("\n✅ KYC Analysis completed successfully!")
        else:
            print("\n⚠️  KYC Analysis completed with errors")
            
        print(f"Report saved to: {os.getenv('REPORT_OUTPUT_DIR', './reports')}")
        
    except Exception as e:
        print(f"\n❌ Error during KYC analysis: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Try a different model: export OLLAMA_MODEL=mistral")
        print("3. Check if the model supports the required context length")
        print("4. Consider using OpenAI by setting USE_OLLAMA=false in .env")


if __name__ == "__main__":
    main()