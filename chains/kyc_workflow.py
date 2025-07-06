"""
LangChain workflow for KYC analysis
"""
from typing import Dict, Any, List, Optional
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain.memory import SimpleMemory
from datetime import datetime
import json
import os


class KYCWorkflow:
    """Orchestrates the KYC analysis workflow using LangChain"""
    
    def __init__(self, llm: OllamaLLM):
        self.llm = llm
        self.memory = SimpleMemory()
        
    def create_research_chain(self) -> LLMChain:
        """Create chain for initial research"""
        prompt = PromptTemplate(
            input_variables=["client_info"],
            template="""As a KYC Research Analyst, analyze this client information and identify key areas for investigation:

Client Information:
{client_info}

Provide a research plan that includes:
1. Key risk indicators to investigate
2. Specific searches to perform
3. Red flags to watch for
4. Additional information needed

Research Plan:"""
        )
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_key="research_plan",
            verbose=True
        )
    
    def create_screening_chain(self) -> LLMChain:
        """Create chain for compliance screening"""
        prompt = PromptTemplate(
            input_variables=["client_info", "research_plan"],
            template="""As a Compliance Officer, based on the research plan and client information, 
determine what compliance checks are needed:

Client Information:
{client_info}

Research Plan:
{research_plan}

List the specific compliance checks required:
1. PEP screening requirements
2. Sanctions lists to check
3. Adverse media search terms
4. Risk factors to assess

Compliance Screening Plan:"""
        )
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_key="screening_plan",
            verbose=True
        )
    
    def create_analysis_chain(self) -> LLMChain:
        """Create chain for risk analysis"""
        prompt = PromptTemplate(
            input_variables=["client_info", "screening_results"],
            template="""As a Risk Analyst, analyze the screening results and assess the overall risk:

Client Information:
{client_info}

Screening Results:
{screening_results}

Provide a comprehensive risk analysis including:
1. Overall risk score (0-1)
2. Risk level (LOW/MEDIUM/HIGH)
3. Key risk factors identified
4. Due diligence level required
5. Risk mitigation recommendations

Risk Analysis:"""
        )
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_key="risk_analysis",
            verbose=True
        )
    
    def create_report_chain(self) -> LLMChain:
        """Create chain for report generation"""
        prompt = PromptTemplate(
            input_variables=["client_info", "research_plan", "screening_results", "risk_analysis"],
            template="""As a Compliance Report Writer, create a comprehensive KYC report:

Client Information:
{client_info}

Research Findings:
{research_plan}

Screening Results:
{screening_results}

Risk Analysis:
{risk_analysis}

Generate a professional KYC Compliance Report with the following sections:

# KYC COMPLIANCE REPORT

## Executive Summary
[Brief overview of findings and recommendation]

## Client Profile
[Summary of client information]

## Screening Results
### PEP Status
[PEP screening findings]

### Sanctions Screening
[Sanctions check results]

### Adverse Media
[Media search findings]

## Risk Assessment
[Comprehensive risk analysis]

## Compliance Recommendation
[Clear recommendation: APPROVE / REJECT / CONDITIONAL APPROVAL]

## Required Actions
[Any follow-up actions required]

## Report Metadata
- Report Date: {date}
- Analyst: KYC AI System
- Status: Final

Full Report:"""
        )
        
        # Add current date to the template
        prompt.template = prompt.template.format(date=datetime.now().strftime("%Y-%m-%d"))
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_key="compliance_report",
            verbose=True
        )
    
    def create_workflow(self) -> SequentialChain:
        """Create the complete workflow chain"""
        # Create individual chains
        research_chain = self.create_research_chain()
        screening_chain = self.create_screening_chain()
        analysis_chain = self.create_analysis_chain()
        report_chain = self.create_report_chain()
        
        # Create sequential chain
        workflow = SequentialChain(
            chains=[research_chain, screening_chain, analysis_chain, report_chain],
            input_variables=["client_info", "screening_results"],
            output_variables=["research_plan", "screening_plan", "risk_analysis", "compliance_report"],
            verbose=True
        )
        
        return workflow
    
    def run_workflow(self, client_info: Dict[str, Any], screening_results: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete KYC workflow"""
        workflow = self.create_workflow()
        
        # Convert inputs to strings
        client_info_str = json.dumps(client_info, indent=2)
        screening_results_str = json.dumps(screening_results, indent=2)
        
        # Run workflow
        results = workflow({
            "client_info": client_info_str,
            "screening_results": screening_results_str
        })
        
        return results


class KYCReportGenerator:
    """Generates formatted KYC reports"""
    
    @staticmethod
    def generate_report(
        client_info: Dict[str, Any],
        screening_results: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        compliance_report: str
    ) -> Dict[str, Any]:
        """Generate structured KYC report"""
        
        report = {
            "report_id": f"KYC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "client": client_info,
            "screening": screening_results,
            "risk_assessment": risk_analysis,
            "narrative_report": compliance_report,
            "metadata": {
                "system": "LangChain KYC System",
                "version": "1.0",
                "llm": "Ollama/Mistral"
            }
        }
        
        return report
    
    @staticmethod
    def save_report(report: Dict[str, Any], output_dir: str = "./reports") -> str:
        """Save report to file"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        client_name = report["client"].get("name", "Unknown")
        safe_name = "".join(c for c in client_name if c.isalnum() or c in " -_").rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"KYC_LangChain_{safe_name}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Save report
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath