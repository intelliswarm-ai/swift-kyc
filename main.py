#!/usr/bin/env python3
import os
import json
from datetime import datetime
from typing import Dict, Optional, Union
from crewai import Crew, Process
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from kyc_agents import KYCAgents
from kyc_tasks import KYCTasks

# Load environment variables
load_dotenv()


class KYCAnalysisCrew:
    """KYC Analysis Crew for comprehensive client due diligence"""
    
    def __init__(self, llm: Optional[Union[ChatOpenAI, Ollama]] = None):
        """Initialize the KYC Analysis Crew"""
        self.llm = llm or self._get_llm()
        self.agents = KYCAgents(self.llm)
        self.tasks = KYCTasks()
        
    def _get_llm(self) -> Union[ChatOpenAI, Ollama]:
        """Get the configured LLM (Ollama or OpenAI)"""
        use_ollama = os.getenv("USE_OLLAMA", "true").lower() == "true"
        
        if use_ollama:
            # Use Ollama for local processing
            model_name = os.getenv("OLLAMA_MODEL", "llama2")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            
            print(f"🔒 Using Ollama ({model_name}) for confidential local processing")
            
            return Ollama(
                model=model_name,
                base_url=base_url,
                temperature=0,
                # Additional parameters for better performance
                num_ctx=4096,  # Context window
                num_predict=2048,  # Max tokens to generate
                top_k=10,
                top_p=0.95,
                repeat_penalty=1.1
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
        """
        Run the KYC analysis for a client
        
        Args:
            client_info: Dictionary containing client information
                Required fields:
                - name: Full name
                - entity_type: 'individual' or 'corporate'
                Optional fields:
                - date_of_birth: YYYY-MM-DD format
                - nationality: Country
                - residence_country: Current residence
                - business_countries: List of countries
                - industry: Business industry
                - customer_type: Type of customer
        
        Returns:
            Dictionary containing the complete KYC analysis results
        """
        
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
            "{research_findings}"  # Will be populated by crew
        )
        
        sanctions_task = self.tasks.check_sanctions_lists(
            sanctions_agent,
            json.dumps(client_info, indent=2)
        )
        
        risk_task = self.tasks.assess_client_risk(
            risk_agent,
            json.dumps(client_info, indent=2),
            "{all_findings}"  # Will be populated by crew
        )
        
        compliance_task = self.tasks.compile_kyc_report(
            compliance_agent,
            json.dumps(client_info, indent=2),
            "{all_assessments}"  # Will be populated by crew
        )
        
        # Create and run the crew
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
            verbose=True
        )
        
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
    
    def _save_report(self, client_name: str, report_content: str):
        """Save the KYC report to file"""
        report_dir = os.getenv("REPORT_OUTPUT_DIR", "./reports")
        os.makedirs(report_dir, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in client_name if c.isalnum() or c in [' ', '-', '_']).rstrip()
        filename = f"KYC_Report_{safe_name}_{timestamp}.json"
        
        filepath = os.path.join(report_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'client_name': client_name,
                'report': report_content
            }, f, indent=2)
        
        print(f"\nReport saved to: {filepath}")


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
        print("\n✅ KYC Analysis completed successfully!")
        print(f"Report saved to: {os.getenv('REPORT_OUTPUT_DIR', './reports')}")
        
    except Exception as e:
        print(f"\n❌ Error during KYC analysis: {str(e)}")
        raise


if __name__ == "__main__":
    main()