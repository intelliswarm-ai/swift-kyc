"""
Base tools for LangChain KYC system
"""
from typing import Dict, List, Optional, Any
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from datetime import datetime
import json
import re


class PEPCheckInput(BaseModel):
    """Input for PEP check tool"""
    name: str = Field(description="Full name of the person to check")
    nationality: Optional[str] = Field(default=None, description="Nationality of the person")
    date_of_birth: Optional[str] = Field(default=None, description="Date of birth (YYYY-MM-DD)")


class PEPCheckTool(BaseTool):
    """Tool for checking Politically Exposed Person status"""
    name = "pep_check"
    description = "Check if a person is a Politically Exposed Person (PEP)"
    args_schema = PEPCheckInput
    
    def _run(self, name: str, nationality: Optional[str] = None, 
             date_of_birth: Optional[str] = None) -> str:
        """Check PEP status"""
        # Simulated PEP database
        pep_database = {
            "high_risk_countries": ["Iran", "North Korea", "Syria", "Cuba", "Venezuela"],
            "pep_keywords": ["minister", "senator", "ambassador", "governor", "mayor", 
                           "judge", "general", "admiral", "president", "prime"]
        }
        
        result = {
            "name": name,
            "checked_at": datetime.now().isoformat(),
            "is_pep": False,
            "pep_level": None,
            "reasons": [],
            "family_members": [],
            "associates": []
        }
        
        # Check name against PEP keywords
        name_lower = name.lower()
        for keyword in pep_database["pep_keywords"]:
            if keyword in name_lower:
                result["is_pep"] = True
                result["pep_level"] = "HIGH"
                result["reasons"].append(f"Name contains PEP keyword: {keyword}")
        
        # Check nationality risk
        if nationality and nationality in pep_database["high_risk_countries"]:
            result["pep_level"] = "HIGH"
            result["reasons"].append(f"High-risk country: {nationality}")
        
        # Simulate some PEP matches
        if "doe" in name_lower and nationality == "USA":
            result["is_pep"] = False
            result["pep_level"] = "LOW"
        
        return json.dumps(result, indent=2)
    
    async def _arun(self, *args, **kwargs):
        """Async version"""
        return self._run(*args, **kwargs)


class SanctionsCheckInput(BaseModel):
    """Input for sanctions check tool"""
    name: str = Field(description="Name to check against sanctions lists")
    entity_type: str = Field(default="individual", description="Type: individual or entity")
    nationality: Optional[str] = Field(default=None, description="Nationality")


class SanctionsCheckTool(BaseTool):
    """Tool for checking sanctions lists"""
    name = "sanctions_check"
    description = "Check if a person or entity is on sanctions lists (OFAC, EU, UN, etc.)"
    args_schema = SanctionsCheckInput
    
    def _run(self, name: str, entity_type: str = "individual", 
             nationality: Optional[str] = None) -> str:
        """Check sanctions lists"""
        result = {
            "name": name,
            "entity_type": entity_type,
            "checked_at": datetime.now().isoformat(),
            "is_sanctioned": False,
            "sanctions_lists": [],
            "matches": []
        }
        
        # Simulate sanctions check
        lists_checked = ["OFAC", "EU", "UN", "SECO", "UK"]
        
        # Check for obvious sanctioned names (simulation)
        sanctioned_keywords = ["terrorist", "cartel", "wagner", "oligarch"]
        name_lower = name.lower()
        
        for keyword in sanctioned_keywords:
            if keyword in name_lower:
                result["is_sanctioned"] = True
                result["sanctions_lists"].append("OFAC")
                result["matches"].append({
                    "list": "OFAC",
                    "match_score": 0.95,
                    "reason": f"Name contains sanctioned keyword: {keyword}"
                })
        
        result["lists_checked"] = lists_checked
        
        return json.dumps(result, indent=2)
    
    async def _arun(self, *args, **kwargs):
        """Async version"""
        return self._run(*args, **kwargs)


class RiskAssessmentInput(BaseModel):
    """Input for risk assessment tool"""
    client_info: str = Field(description="JSON string of client information")
    pep_result: Optional[str] = Field(default=None, description="PEP check result")
    sanctions_result: Optional[str] = Field(default=None, description="Sanctions check result")


class RiskAssessmentTool(BaseTool):
    """Tool for assessing overall client risk"""
    name = "risk_assessment"
    description = "Calculate comprehensive risk score based on client information and screening results"
    args_schema = RiskAssessmentInput
    
    def _run(self, client_info: str, pep_result: Optional[str] = None, 
             sanctions_result: Optional[str] = None) -> str:
        """Calculate risk score"""
        try:
            client = json.loads(client_info) if isinstance(client_info, str) else client_info
        except:
            client = {"name": client_info}
        
        # Risk factors and weights
        risk_score = 0.0
        risk_factors = []
        
        # Geographic risk
        high_risk_countries = ["Iran", "North Korea", "Syria", "Afghanistan", "Yemen"]
        medium_risk_countries = ["Russia", "Belarus", "Myanmar", "Venezuela", "Cuba"]
        
        residence = client.get("residence_country", "")
        if residence in high_risk_countries:
            risk_score += 0.3
            risk_factors.append(f"High-risk residence: {residence}")
        elif residence in medium_risk_countries:
            risk_score += 0.2
            risk_factors.append(f"Medium-risk residence: {residence}")
        
        # Business countries risk
        business_countries = client.get("business_countries", [])
        for country in business_countries:
            if country in high_risk_countries:
                risk_score += 0.2
                risk_factors.append(f"High-risk business country: {country}")
            elif country in medium_risk_countries:
                risk_score += 0.1
                risk_factors.append(f"Medium-risk business country: {country}")
        
        # Industry risk
        high_risk_industries = ["Cryptocurrency", "Gaming", "Cannabis", "Arms"]
        industry = client.get("industry", "")
        if industry in high_risk_industries:
            risk_score += 0.2
            risk_factors.append(f"High-risk industry: {industry}")
        
        # PEP risk
        if pep_result:
            try:
                pep_data = json.loads(pep_result)
                if pep_data.get("is_pep"):
                    risk_score += 0.3
                    risk_factors.append("PEP identified")
            except:
                pass
        
        # Sanctions risk
        if sanctions_result:
            try:
                sanctions_data = json.loads(sanctions_result)
                if sanctions_data.get("is_sanctioned"):
                    risk_score += 0.5
                    risk_factors.append("Sanctions match found")
            except:
                pass
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "HIGH"
            due_diligence = "Enhanced Due Diligence Required"
        elif risk_score >= 0.4:
            risk_level = "MEDIUM"
            due_diligence = "Enhanced Due Diligence Recommended"
        else:
            risk_level = "LOW"
            due_diligence = "Standard Due Diligence"
        
        result = {
            "client_name": client.get("name", "Unknown"),
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "due_diligence_level": due_diligence,
            "risk_factors": risk_factors,
            "assessment_date": datetime.now().isoformat()
        }
        
        return json.dumps(result, indent=2)
    
    async def _arun(self, *args, **kwargs):
        """Async version"""
        return self._run(*args, **kwargs)


class WebSearchInput(BaseModel):
    """Input for web search tool"""
    query: str = Field(description="Search query")
    num_results: int = Field(default=5, description="Number of results to return")


class WebSearchTool(BaseTool):
    """Tool for searching web for adverse media"""
    name = "web_search"
    description = "Search the web for news, adverse media, or public information about a person or entity"
    args_schema = WebSearchInput
    
    def _run(self, query: str, num_results: int = 5) -> str:
        """Simulate web search"""
        # In production, this would use a real search API
        results = {
            "query": query,
            "searched_at": datetime.now().isoformat(),
            "results": []
        }
        
        # Simulate some search results
        if "john doe" in query.lower():
            results["results"] = [
                {
                    "title": "John Doe Appointed as Tech Industry Leader",
                    "snippet": "John Doe, a prominent software engineer, has been recognized...",
                    "url": "https://example.com/article1",
                    "sentiment": "positive"
                },
                {
                    "title": "Local Tech Professional Makes Forbes List",
                    "snippet": "Switzerland-based John Doe featured in Forbes 30 under 30...",
                    "url": "https://example.com/article2",
                    "sentiment": "positive"
                }
            ]
        
        results["adverse_media_found"] = False
        results["total_results"] = len(results["results"])
        
        return json.dumps(results, indent=2)
    
    async def _arun(self, *args, **kwargs):
        """Async version"""
        return self._run(*args, **kwargs)


# Create tool instances
def get_kyc_tools() -> List[BaseTool]:
    """Get all KYC tools"""
    return [
        PEPCheckTool(),
        SanctionsCheckTool(),
        RiskAssessmentTool(),
        WebSearchTool()
    ]