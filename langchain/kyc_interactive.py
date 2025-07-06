#!/usr/bin/env python3
"""
Interactive LangChain KYC System with Web Search and Logging
Full workflow tracking and iterative search capabilities
"""
import os
import json
import logging
import warnings
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import time

warnings.filterwarnings("ignore")
load_dotenv()

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import Document


class WorkflowLogger:
    """Logs all workflow steps with timestamps"""
    
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"kyc_workflow_{timestamp}.log")
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()  # Also print to console
            ]
        )
        self.logger = logging.getLogger("KYC_Workflow")
        
    def log_step(self, step: str, details: Dict[str, Any]):
        """Log a workflow step"""
        self.logger.info(f"STEP: {step}")
        self.logger.info(f"Details: {json.dumps(details, indent=2)}")
        
    def log_search(self, query: str, results: List[Dict[str, Any]]):
        """Log web search"""
        self.logger.info(f"WEB SEARCH: {query}")
        self.logger.info(f"Results found: {len(results)}")
        for i, result in enumerate(results):
            self.logger.info(f"  {i+1}. {result.get('title', 'N/A')} - {result.get('url', 'N/A')}")
    
    def log_decision(self, decision_type: str, decision: str, reasoning: str):
        """Log analysis decisions"""
        self.logger.info(f"DECISION: {decision_type}")
        self.logger.info(f"Result: {decision}")
        self.logger.info(f"Reasoning: {reasoning}")
    
    def get_log_path(self) -> str:
        """Get the current log file path"""
        return self.log_file


class WebSearchTool:
    """Web search tool with multiple search engines"""
    
    def __init__(self, logger: WorkflowLogger):
        self.logger = logger
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def search_duckduckgo(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo HTML version"""
        try:
            url = "https://html.duckduckgo.com/html/"
            params = {'q': query}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for i, result in enumerate(soup.select('.result__body')):
                if i >= num_results:
                    break
                    
                title_elem = result.select_one('.result__title')
                snippet_elem = result.select_one('.result__snippet')
                url_elem = result.select_one('.result__url')
                
                if title_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                        'url': url_elem.get_text(strip=True) if url_elem else '',
                        'source': 'DuckDuckGo'
                    })
            
            self.logger.log_search(query, results)
            return results
            
        except Exception as e:
            self.logger.logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def search_news_api(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search news using NewsAPI (requires API key)"""
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return []
            
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': api_key,
                'sortBy': 'relevancy',
                'pageSize': num_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            if data.get('status') == 'ok':
                for article in data.get('articles', []):
                    results.append({
                        'title': article.get('title', ''),
                        'snippet': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', 'News'),
                        'published': article.get('publishedAt', '')
                    })
            
            self.logger.log_search(f"NewsAPI: {query}", results)
            return results
            
        except Exception as e:
            self.logger.logger.error(f"NewsAPI search error: {e}")
            return []
    
    def search_web(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Combined web search from multiple sources"""
        all_results = []
        
        # Search DuckDuckGo
        ddg_results = self.search_duckduckgo(query, num_results)
        all_results.extend(ddg_results)
        
        # Add NewsAPI if available
        news_results = self.search_news_api(query, num_results // 2)
        all_results.extend(news_results)
        
        return all_results


class InteractiveKYCSystem:
    """Interactive KYC system with web search and full logging"""
    
    def __init__(self):
        # Initialize logger
        self.logger = WorkflowLogger()
        self.logger.log_step("System Initialization", {"status": "starting"})
        
        # Get Ollama configuration
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://172.21.16.1:11434")
        self.model = os.getenv("OLLAMA_MODEL", "mistral")
        
        print(f"🔧 Initializing Interactive KYC System")
        print(f"   Ollama URL: {self.base_url}")
        print(f"   Model: {self.model}")
        print(f"   Log file: {self.logger.get_log_path()}")
        
        # Initialize LLM
        self.llm = OllamaLLM(
            model=self.model,
            base_url=self.base_url,
            temperature=0,
            format="json"
        )
        
        # Initialize web search
        self.web_search = WebSearchTool(self.logger)
        
        # Initialize memory for conversation
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            return_messages=True
        )
        
        self.logger.log_step("System Initialization", {"status": "completed"})
        print("✅ System ready")
    
    def get_client_info_interactive(self) -> Dict[str, Any]:
        """Get client information interactively"""
        print("\n" + "="*60)
        print("📝 Enter Client Information")
        print("="*60)
        
        client_info = {}
        
        # Essential information
        client_info["name"] = input("\n👤 Client Name (required): ").strip()
        while not client_info["name"]:
            print("❌ Name is required!")
            client_info["name"] = input("👤 Client Name: ").strip()
        
        # Optional information with prompts
        print("\n📋 Additional Information (press Enter to skip):")
        
        client_info["entity_type"] = input("   Entity Type (individual/company) [individual]: ").strip() or "individual"
        client_info["nationality"] = input("   Nationality: ").strip() or "Unknown"
        client_info["date_of_birth"] = input("   Date of Birth (YYYY-MM-DD): ").strip() or None
        client_info["residence_country"] = input("   Residence Country: ").strip() or "Unknown"
        
        # Business countries
        countries_input = input("   Business Countries (comma-separated): ").strip()
        client_info["business_countries"] = [c.strip() for c in countries_input.split(",")] if countries_input else []
        
        client_info["industry"] = input("   Industry/Sector: ").strip() or "Unknown"
        client_info["occupation"] = input("   Occupation/Position: ").strip() or "Unknown"
        
        # Additional search terms
        additional_terms = input("\n🔍 Additional search terms (comma-separated): ").strip()
        client_info["search_terms"] = [t.strip() for t in additional_terms.split(",")] if additional_terms else []
        
        self.logger.log_step("Client Information Collected", client_info)
        
        return client_info
    
    def iterative_web_search(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform iterative web searches with user interaction"""
        print("\n" + "="*60)
        print("🌐 Web Search Phase")
        print("="*60)
        
        search_results = {
            "searches_performed": [],
            "relevant_findings": [],
            "adverse_media": [],
            "positive_media": []
        }
        
        # Initial searches
        base_queries = [
            f'"{client_info["name"]}"',
            f'"{client_info["name"]}" {client_info.get("nationality", "")}',
            f'"{client_info["name"]}" {client_info.get("occupation", "")}',
            f'"{client_info["name"]}" scandal lawsuit investigation',
            f'"{client_info["name"]}" PEP "politically exposed"'
        ]
        
        # Add custom search terms
        for term in client_info.get("search_terms", []):
            base_queries.append(f'"{client_info["name"]}" {term}')
        
        continue_searching = True
        search_round = 1
        
        while continue_searching:
            print(f"\n🔄 Search Round {search_round}")
            print("-" * 40)
            
            if search_round == 1:
                # Use base queries for first round
                queries = base_queries[:3]  # Start with basic searches
            else:
                # Get custom query from user
                custom_query = input("\n🔍 Enter search query (or 'done' to finish): ").strip()
                if custom_query.lower() == 'done':
                    continue_searching = False
                    continue
                queries = [custom_query]
            
            # Perform searches
            for query in queries:
                print(f"\n🔎 Searching: {query}")
                results = self.web_search.search_web(query, num_results=5)
                
                search_results["searches_performed"].append({
                    "round": search_round,
                    "query": query,
                    "results_count": len(results),
                    "timestamp": datetime.now().isoformat()
                })
                
                if results:
                    print(f"\n📄 Found {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        print(f"\n{i}. {result['title']}")
                        print(f"   Source: {result.get('source', 'Web')}")
                        print(f"   URL: {result['url']}")
                        print(f"   Snippet: {result['snippet'][:150]}...")
                    
                    # Analyze results with LLM
                    analysis = self._analyze_search_results(client_info["name"], results)
                    
                    # Categorize findings
                    for result in results:
                        if analysis.get("has_adverse_media"):
                            search_results["adverse_media"].append(result)
                        elif analysis.get("has_positive_media"):
                            search_results["positive_media"].append(result)
                        
                        if analysis.get("is_relevant"):
                            search_results["relevant_findings"].append({
                                **result,
                                "analysis": analysis
                            })
                else:
                    print("❌ No results found")
            
            if search_round == 1:
                # Ask if user wants to continue with more searches
                print("\n" + "-" * 40)
                more = input("\n🤔 Perform additional searches? (y/n) [y]: ").strip().lower()
                if more == 'n':
                    continue_searching = False
                else:
                    print("\n💡 You can now enter custom search queries.")
                    print("   Tip: Try including company names, locations, or specific events.")
            
            search_round += 1
            
            # Prevent infinite loops
            if search_round > 10:
                print("\n⚠️  Maximum search rounds reached.")
                continue_searching = False
        
        self.logger.log_step("Web Search Completed", {
            "total_searches": len(search_results["searches_performed"]),
            "adverse_media_count": len(search_results["adverse_media"]),
            "positive_media_count": len(search_results["positive_media"])
        })
        
        return search_results
    
    def _analyze_search_results(self, client_name: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze search results using LLM"""
        prompt = PromptTemplate.from_template("""Analyze these search results for {client_name}:

{results_text}

Determine:
1. Is this relevant to the person we're investigating?
2. Does it contain adverse/negative information?
3. Does it contain positive information?
4. Are there any red flags for KYC?

Respond in JSON format:
{{
    "is_relevant": true/false,
    "has_adverse_media": true/false,
    "has_positive_media": true/false,
    "red_flags": ["flag1", "flag2"],
    "summary": "brief summary"
}}""")
        
        # Format results for analysis
        results_text = "\n".join([
            f"- {r['title']}: {r['snippet']}" 
            for r in results[:5]  # Analyze first 5
        ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "client_name": client_name,
                "results_text": results_text
            })
            
            return self._parse_json_response(response, {
                "is_relevant": False,
                "has_adverse_media": False,
                "has_positive_media": False,
                "red_flags": [],
                "summary": "Unable to analyze"
            })
        except Exception as e:
            self.logger.logger.error(f"Search analysis error: {e}")
            return {"is_relevant": False, "error": str(e)}
    
    def perform_pep_check(self, client_info: Dict[str, Any], search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced PEP check with search results"""
        print("\n" + "="*60)
        print("👔 PEP Screening")
        print("="*60)
        
        self.logger.log_step("PEP Screening Started", {"client": client_info["name"]})
        
        prompt = PromptTemplate.from_template("""Analyze PEP (Politically Exposed Person) status:

Client Information:
- Name: {name}
- Nationality: {nationality}
- Occupation: {occupation}

Web Search Findings:
{search_findings}

Consider:
1. Direct political positions (current or former)
2. Family members of PEPs
3. Close associates of PEPs
4. State-owned enterprise executives
5. High-ranking military/judiciary positions

Respond in JSON format:
{{
    "is_pep": true/false,
    "pep_type": "direct/family/associate/none",
    "confidence": "high/medium/low",
    "positions": ["position1", "position2"],
    "reasoning": "detailed explanation",
    "risk_level": "high/medium/low"
}}""")
        
        # Prepare search findings summary
        search_summary = self._summarize_search_results(search_results)
        
        chain = prompt | self.llm
        
        result = chain.invoke({
            "name": client_info["name"],
            "nationality": client_info.get("nationality", "Unknown"),
            "occupation": client_info.get("occupation", "Unknown"),
            "search_findings": search_summary
        })
        
        pep_result = self._parse_json_response(result, {
            "is_pep": False,
            "pep_type": "none",
            "confidence": "low",
            "positions": [],
            "reasoning": "Analysis completed",
            "risk_level": "low"
        })
        
        self.logger.log_decision("PEP Status", 
                                str(pep_result["is_pep"]), 
                                pep_result.get("reasoning", ""))
        
        # Display results
        print(f"\n📊 PEP Screening Results:")
        print(f"   Status: {'PEP IDENTIFIED' if pep_result['is_pep'] else 'Not a PEP'}")
        print(f"   Type: {pep_result.get('pep_type', 'N/A')}")
        print(f"   Confidence: {pep_result.get('confidence', 'N/A')}")
        print(f"   Risk Level: {pep_result.get('risk_level', 'N/A')}")
        
        if pep_result.get('positions'):
            print(f"   Positions: {', '.join(pep_result['positions'])}")
        
        return pep_result
    
    def perform_sanctions_check(self, client_info: Dict[str, Any], search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced sanctions check with search results"""
        print("\n" + "="*60)
        print("🚫 Sanctions Screening")
        print("="*60)
        
        self.logger.log_step("Sanctions Screening Started", {"client": client_info["name"]})
        
        prompt = PromptTemplate.from_template("""Analyze sanctions risk:

Client Information:
- Name: {name}
- Nationality: {nationality}
- Business Countries: {countries}

Web Search Findings:
{search_findings}

High-risk/Sanctioned countries: Iran, North Korea, Syria, Russia, Belarus, Myanmar, Cuba, Venezuela, Libya, Sudan

Consider:
1. Direct sanctions matches
2. Nationality or business in sanctioned countries
3. Association with sanctioned entities
4. Industry-specific sanctions

Respond in JSON format:
{{
    "sanctions_risk": "high/medium/low",
    "is_sanctioned": true/false,
    "matched_lists": ["list1", "list2"],
    "risk_factors": ["factor1", "factor2"],
    "flagged_countries": ["country1", "country2"],
    "recommendation": "approve/review/reject",
    "reasoning": "detailed explanation"
}}""")
        
        search_summary = self._summarize_search_results(search_results)
        countries = ", ".join(client_info.get("business_countries", []))
        
        chain = prompt | self.llm
        
        result = chain.invoke({
            "name": client_info["name"],
            "nationality": client_info.get("nationality", "Unknown"),
            "countries": countries or "None specified",
            "search_findings": search_summary
        })
        
        sanctions_result = self._parse_json_response(result, {
            "sanctions_risk": "low",
            "is_sanctioned": False,
            "matched_lists": [],
            "risk_factors": [],
            "flagged_countries": [],
            "recommendation": "approve",
            "reasoning": "No sanctions matches found"
        })
        
        self.logger.log_decision("Sanctions Status",
                                sanctions_result["recommendation"],
                                sanctions_result.get("reasoning", ""))
        
        # Display results
        print(f"\n📊 Sanctions Screening Results:")
        print(f"   Risk Level: {sanctions_result['sanctions_risk']}")
        print(f"   Sanctioned: {'YES' if sanctions_result['is_sanctioned'] else 'NO'}")
        print(f"   Recommendation: {sanctions_result['recommendation'].upper()}")
        
        if sanctions_result.get('flagged_countries'):
            print(f"   Flagged Countries: {', '.join(sanctions_result['flagged_countries'])}")
        
        return sanctions_result
    
    def perform_comprehensive_risk_assessment(self, client_info: Dict[str, Any], 
                                            pep_result: Dict[str, Any],
                                            sanctions_result: Dict[str, Any],
                                            search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive risk assessment with all findings"""
        print("\n" + "="*60)
        print("📊 Comprehensive Risk Assessment")
        print("="*60)
        
        self.logger.log_step("Risk Assessment Started", {"client": client_info["name"]})
        
        prompt = PromptTemplate.from_template("""Perform comprehensive KYC risk assessment:

Client Profile:
{client_profile}

PEP Screening Result:
{pep_result}

Sanctions Screening Result:
{sanctions_result}

Media Analysis:
- Adverse Media Found: {adverse_count}
- Positive Media Found: {positive_count}

Calculate overall risk considering:
1. Geographic risk (residence, business countries)
2. Industry/occupation risk
3. PEP exposure
4. Sanctions exposure
5. Adverse media
6. Transaction patterns

Provide comprehensive assessment in JSON format:
{{
    "overall_risk": "high/medium/low",
    "risk_score": 0.0-1.0,
    "risk_matrix": {{
        "geographic_risk": "high/medium/low",
        "industry_risk": "high/medium/low",
        "pep_risk": "high/medium/low",
        "sanctions_risk": "high/medium/low",
        "reputational_risk": "high/medium/low"
    }},
    "key_findings": ["finding1", "finding2"],
    "due_diligence_level": "standard/enhanced",
    "monitoring_frequency": "quarterly/semi-annual/annual",
    "final_recommendation": "approve/conditional_approve/reject",
    "conditions": ["condition1", "condition2"],
    "rationale": "detailed explanation"
}}""")
        
        chain = prompt | self.llm
        
        result = chain.invoke({
            "client_profile": json.dumps(client_info, indent=2),
            "pep_result": json.dumps(pep_result, indent=2),
            "sanctions_result": json.dumps(sanctions_result, indent=2),
            "adverse_count": len(search_results.get("adverse_media", [])),
            "positive_count": len(search_results.get("positive_media", []))
        })
        
        risk_assessment = self._parse_json_response(result, {
            "overall_risk": "medium",
            "risk_score": 0.5,
            "risk_matrix": {},
            "key_findings": ["Assessment completed"],
            "due_diligence_level": "enhanced",
            "monitoring_frequency": "semi-annual",
            "final_recommendation": "conditional_approve",
            "conditions": ["Additional documentation required"],
            "rationale": "Standard assessment completed"
        })
        
        self.logger.log_decision("Final Risk Assessment",
                                risk_assessment["final_recommendation"],
                                risk_assessment.get("rationale", ""))
        
        # Display results
        print(f"\n🎯 Risk Assessment Results:")
        print(f"   Overall Risk: {risk_assessment['overall_risk'].upper()}")
        print(f"   Risk Score: {risk_assessment['risk_score']}")
        print(f"   Due Diligence: {risk_assessment['due_diligence_level']}")
        print(f"   Recommendation: {risk_assessment['final_recommendation'].upper()}")
        
        if risk_assessment.get('conditions'):
            print(f"\n   Conditions:")
            for condition in risk_assessment['conditions']:
                print(f"   • {condition}")
        
        return risk_assessment
    
    def generate_detailed_report(self, client_info: Dict[str, Any],
                                search_results: Dict[str, Any],
                                pep_result: Dict[str, Any],
                                sanctions_result: Dict[str, Any],
                                risk_assessment: Dict[str, Any]) -> str:
        """Generate detailed compliance report"""
        
        report_template = """
# KYC COMPLIANCE REPORT

**Report ID:** {report_id}
**Generated:** {date}
**System:** Interactive LangChain KYC with Web Search

---

## EXECUTIVE SUMMARY

**Client:** {client_name}
**Final Recommendation:** {recommendation}
**Overall Risk Level:** {risk_level}
**Due Diligence Required:** {dd_level}

{executive_summary}

---

## CLIENT PROFILE

- **Name:** {client_name}
- **Type:** {entity_type}
- **Nationality:** {nationality}
- **Residence:** {residence}
- **Occupation:** {occupation}
- **Industry:** {industry}
- **Business Countries:** {countries}

---

## INVESTIGATION SUMMARY

### Web Search Analysis
- **Total Searches Performed:** {total_searches}
- **Relevant Results Found:** {relevant_results}
- **Adverse Media Identified:** {adverse_media}
- **Positive Media Identified:** {positive_media}

### Key Findings from Web Search:
{web_findings}

---

## SCREENING RESULTS

### PEP Screening
- **Status:** {pep_status}
- **Type:** {pep_type}
- **Confidence:** {pep_confidence}
- **Risk Level:** {pep_risk}

**Reasoning:** {pep_reasoning}

### Sanctions Screening
- **Risk Level:** {sanctions_risk}
- **Sanctioned:** {is_sanctioned}
- **Recommendation:** {sanctions_rec}
- **Flagged Countries:** {flagged_countries}

**Reasoning:** {sanctions_reasoning}

---

## RISK ASSESSMENT

### Risk Matrix
- **Geographic Risk:** {geo_risk}
- **Industry Risk:** {ind_risk}
- **PEP Risk:** {pep_risk_matrix}
- **Sanctions Risk:** {sanc_risk_matrix}
- **Reputational Risk:** {rep_risk}

### Overall Assessment
- **Risk Score:** {risk_score}
- **Risk Level:** {overall_risk}
- **Monitoring Frequency:** {monitoring}

### Key Risk Factors:
{risk_factors}

---

## COMPLIANCE DECISION

### Recommendation: {final_recommendation}

**Rationale:** {rationale}

### Conditions for Approval:
{conditions}

### Required Actions:
{actions}

---

## WORKFLOW AUDIT TRAIL

**Log File:** {log_file}
**Total Processing Time:** {processing_time}

### Investigation Steps:
1. Client information collected
2. {search_count} web searches performed
3. PEP screening completed
4. Sanctions screening completed
5. Risk assessment finalized
6. Report generated

---

## APPENDIX: SEARCH QUERIES

{search_queries}

---

*End of Report*
"""
        
        # Prepare data for report
        web_findings = "\n".join([
            f"- {finding.get('title', 'N/A')}: {finding.get('analysis', {}).get('summary', 'N/A')}"
            for finding in search_results.get('relevant_findings', [])[:5]
        ])
        
        risk_factors = "\n".join([
            f"- {factor}"
            for factor in risk_assessment.get('key_findings', [])
        ])
        
        conditions = "\n".join([
            f"- {condition}"
            for condition in risk_assessment.get('conditions', ['None'])
        ])
        
        search_queries = "\n".join([
            f"{s['round']}. {s['query']} ({s['results_count']} results)"
            for s in search_results.get('searches_performed', [])
        ])
        
        # Generate executive summary
        if risk_assessment['final_recommendation'] == 'approve':
            exec_summary = "Based on comprehensive screening and web search analysis, no significant risks were identified. The client can be onboarded with standard due diligence procedures."
        elif risk_assessment['final_recommendation'] == 'conditional_approve':
            exec_summary = "The analysis identified some risk factors that require additional scrutiny. The client may be onboarded subject to enhanced due diligence and the conditions listed below."
        else:
            exec_summary = "Significant risk factors were identified during the screening process. The client poses an unacceptable risk and should not be onboarded at this time."
        
        # Fill template
        report = report_template.format(
            report_id=f"KYC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            client_name=client_info['name'],
            recommendation=risk_assessment['final_recommendation'].upper(),
            risk_level=risk_assessment['overall_risk'].upper(),
            dd_level=risk_assessment['due_diligence_level'],
            executive_summary=exec_summary,
            entity_type=client_info.get('entity_type', 'N/A'),
            nationality=client_info.get('nationality', 'N/A'),
            residence=client_info.get('residence_country', 'N/A'),
            occupation=client_info.get('occupation', 'N/A'),
            industry=client_info.get('industry', 'N/A'),
            countries=", ".join(client_info.get('business_countries', [])) or 'N/A',
            total_searches=len(search_results.get('searches_performed', [])),
            relevant_results=len(search_results.get('relevant_findings', [])),
            adverse_media=len(search_results.get('adverse_media', [])),
            positive_media=len(search_results.get('positive_media', [])),
            web_findings=web_findings or "No significant findings",
            pep_status="PEP" if pep_result['is_pep'] else "Not a PEP",
            pep_type=pep_result.get('pep_type', 'N/A'),
            pep_confidence=pep_result.get('confidence', 'N/A'),
            pep_risk=pep_result.get('risk_level', 'N/A'),
            pep_reasoning=pep_result.get('reasoning', 'N/A'),
            sanctions_risk=sanctions_result.get('sanctions_risk', 'N/A'),
            is_sanctioned="YES" if sanctions_result.get('is_sanctioned') else "NO",
            sanctions_rec=sanctions_result.get('recommendation', 'N/A'),
            flagged_countries=", ".join(sanctions_result.get('flagged_countries', [])) or 'None',
            sanctions_reasoning=sanctions_result.get('reasoning', 'N/A'),
            geo_risk=risk_assessment.get('risk_matrix', {}).get('geographic_risk', 'N/A'),
            ind_risk=risk_assessment.get('risk_matrix', {}).get('industry_risk', 'N/A'),
            pep_risk_matrix=risk_assessment.get('risk_matrix', {}).get('pep_risk', 'N/A'),
            sanc_risk_matrix=risk_assessment.get('risk_matrix', {}).get('sanctions_risk', 'N/A'),
            rep_risk=risk_assessment.get('risk_matrix', {}).get('reputational_risk', 'N/A'),
            risk_score=risk_assessment.get('risk_score', 'N/A'),
            overall_risk=risk_assessment.get('overall_risk', 'N/A'),
            monitoring=risk_assessment.get('monitoring_frequency', 'N/A'),
            risk_factors=risk_factors or "Standard risk profile",
            final_recommendation=risk_assessment['final_recommendation'].upper(),
            rationale=risk_assessment.get('rationale', 'N/A'),
            conditions=conditions,
            actions="1. Complete KYC documentation\n2. Set up monitoring schedule\n3. Document decision rationale",
            log_file=self.logger.get_log_path(),
            processing_time="See log file for details",
            search_count=len(search_results.get('searches_performed', [])),
            search_queries=search_queries
        )
        
        return report
    
    def _summarize_search_results(self, search_results: Dict[str, Any]) -> str:
        """Summarize search results for LLM analysis"""
        summary_parts = []
        
        if search_results.get('adverse_media'):
            summary_parts.append(f"Adverse media found ({len(search_results['adverse_media'])} articles):")
            for item in search_results['adverse_media'][:3]:
                summary_parts.append(f"- {item['title']}")
        
        if search_results.get('positive_media'):
            summary_parts.append(f"\nPositive media found ({len(search_results['positive_media'])} articles):")
            for item in search_results['positive_media'][:3]:
                summary_parts.append(f"- {item['title']}")
        
        if search_results.get('relevant_findings'):
            summary_parts.append(f"\nOther relevant findings ({len(search_results['relevant_findings'])} items)")
        
        if not summary_parts:
            return "No significant web search findings"
        
        return "\n".join(summary_parts)
    
    def _parse_json_response(self, response: str, default: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON from LLM response with fallback"""
        try:
            return json.loads(response)
        except:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
        return default
    
    def save_report(self, report: str, client_name: str) -> str:
        """Save report to file"""
        report_dir = "./reports"
        os.makedirs(report_dir, exist_ok=True)
        
        safe_name = "".join(c for c in client_name if c.isalnum() or c in " -_").rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save text report
        txt_file = os.path.join(report_dir, f"KYC_Interactive_{safe_name}_{timestamp}.txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Also save as markdown
        md_file = os.path.join(report_dir, f"KYC_Interactive_{safe_name}_{timestamp}.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return txt_file
    
    def run_interactive_analysis(self):
        """Run the complete interactive KYC analysis"""
        try:
            # Welcome message
            print("\n" + "="*60)
            print("🏦 Interactive KYC Analysis System")
            print("="*60)
            print("This system will guide you through a comprehensive KYC check")
            print("with iterative web searches and full workflow logging.")
            
            # Get client information
            client_info = self.get_client_info_interactive()
            
            # Start timer
            start_time = time.time()
            
            # Perform web searches
            search_results = self.iterative_web_search(client_info)
            
            # Perform screenings
            pep_result = self.perform_pep_check(client_info, search_results)
            sanctions_result = self.perform_sanctions_check(client_info, search_results)
            
            # Risk assessment
            risk_assessment = self.perform_comprehensive_risk_assessment(
                client_info, pep_result, sanctions_result, search_results
            )
            
            # Generate report
            print("\n" + "="*60)
            print("📝 Generating Compliance Report")
            print("="*60)
            
            report = self.generate_detailed_report(
                client_info, search_results, pep_result, 
                sanctions_result, risk_assessment
            )
            
            # Save report
            report_path = self.save_report(report, client_info['name'])
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Final summary
            print("\n" + "="*60)
            print("✅ KYC ANALYSIS COMPLETE")
            print("="*60)
            print(f"\n📊 Summary:")
            print(f"   Client: {client_info['name']}")
            print(f"   Final Recommendation: {risk_assessment['final_recommendation'].upper()}")
            print(f"   Risk Level: {risk_assessment['overall_risk'].upper()}")
            print(f"   Processing Time: {processing_time:.2f} seconds")
            print(f"\n📄 Reports saved:")
            print(f"   Report: {report_path}")
            print(f"   Log: {self.logger.get_log_path()}")
            
            # Log completion
            self.logger.log_step("Analysis Completed", {
                "client": client_info['name'],
                "recommendation": risk_assessment['final_recommendation'],
                "processing_time": f"{processing_time:.2f} seconds"
            })
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Analysis interrupted by user")
            self.logger.log_step("Analysis Interrupted", {"reason": "User cancelled"})
        except Exception as e:
            print(f"\n❌ Error during analysis: {type(e).__name__}: {str(e)}")
            self.logger.logger.error(f"Fatal error: {e}", exc_info=True)
            raise


def main():
    """Main function"""
    system = InteractiveKYCSystem()
    system.run_interactive_analysis()


if __name__ == "__main__":
    main()