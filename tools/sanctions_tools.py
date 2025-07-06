import json
import os
from typing import Dict, List, Optional
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime
from difflib import SequenceMatcher
import re


class SanctionsCheckInput(BaseModel):
    name: str = Field(..., description="Name of person or entity to check")
    entity_type: str = Field("individual", description="Type: 'individual' or 'entity'")
    date_of_birth: Optional[str] = Field(None, description="Date of birth for individuals")
    country: Optional[str] = Field(None, description="Country of origin or registration")
    fuzzy_threshold: float = Field(0.85, description="Threshold for fuzzy matching (0.0-1.0)")


class SanctionsCheckTool(BaseTool):
    name: str = "Sanctions List Check"
    description: str = """
    Checks individuals and entities against comprehensive sanctions lists including
    SECO (Swiss), EU, OFAC (US), UN, and other international sanctions databases.
    Supports fuzzy matching to catch name variations and aliases.
    """
    args_schema: type[BaseModel] = SanctionsCheckInput

    def __init__(self):
        super().__init__()
        self.sanctions_path = os.getenv("SANCTIONS_LIST_PATH", "./data/sanctions_lists.json")
        self._load_sanctions_data()

    def _load_sanctions_data(self):
        """Load sanctions data from file or initialize with sample data"""
        if os.path.exists(self.sanctions_path):
            with open(self.sanctions_path, 'r') as f:
                self.sanctions_data = json.load(f)
        else:
            # Initialize with sample sanctions data
            self.sanctions_data = {
                "lists": {
                    "OFAC": {
                        "entries": [
                            {
                                "id": "OFAC-001",
                                "name": "Bad Actor Company Ltd",
                                "type": "entity",
                                "aliases": ["BA Company", "Bad Actor Co"],
                                "sanctions_program": "CYBER2",
                                "listing_date": "2023-06-15",
                                "country": "Russia",
                                "additional_info": "Cyber criminal organization"
                            }
                        ],
                        "last_updated": "2024-01-20"
                    },
                    "EU": {
                        "entries": [
                            {
                                "id": "EU-001",
                                "name": "Ivan Petrov",
                                "type": "individual",
                                "date_of_birth": "1975-04-20",
                                "sanctions_program": "Ukraine-related",
                                "listing_date": "2022-03-01",
                                "nationality": "Russia"
                            }
                        ],
                        "last_updated": "2024-01-18"
                    },
                    "SECO": {
                        "entries": [],
                        "last_updated": "2024-01-19"
                    },
                    "UN": {
                        "entries": [],
                        "last_updated": "2024-01-17"
                    }
                },
                "version": "1.0"
            }

    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        # Remove special characters and extra spaces
        name = re.sub(r'[^\w\s-]', ' ', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip().lower()

    def _calculate_match_score(self, search_name: str, entry_name: str, 
                             search_dob: Optional[str], entry_dob: Optional[str]) -> float:
        """Calculate match score between search criteria and sanctions entry"""
        # Name similarity
        norm_search = self._normalize_name(search_name)
        norm_entry = self._normalize_name(entry_name)
        
        name_score = SequenceMatcher(None, norm_search, norm_entry).ratio()
        
        # Check for partial matches (e.g., "John Smith" in "John Adam Smith")
        if norm_search in norm_entry or norm_entry in norm_search:
            name_score = max(name_score, 0.85)
        
        # Date of birth matching (if applicable)
        if search_dob and entry_dob:
            if search_dob == entry_dob:
                return min(name_score + 0.1, 1.0)  # Boost score for DOB match
            else:
                return name_score * 0.9  # Slight reduction for DOB mismatch
        
        return name_score

    def _check_sanctions_lists(self, name: str, entity_type: str, 
                             date_of_birth: Optional[str], country: Optional[str],
                             fuzzy_threshold: float) -> List[Dict]:
        """Check all sanctions lists for matches"""
        all_matches = []
        
        for list_name, list_data in self.sanctions_data['lists'].items():
            for entry in list_data.get('entries', []):
                # Skip if entity type doesn't match
                if entry.get('type') != entity_type:
                    continue
                
                # Skip if country filter is applied and doesn't match
                if country:
                    entry_country = entry.get('country') or entry.get('nationality')
                    if entry_country and entry_country.lower() != country.lower():
                        continue
                
                # Check main name
                match_score = self._calculate_match_score(
                    name, entry['name'], 
                    date_of_birth, entry.get('date_of_birth')
                )
                
                # Check aliases
                for alias in entry.get('aliases', []):
                    alias_score = self._calculate_match_score(
                        name, alias,
                        date_of_birth, entry.get('date_of_birth')
                    )
                    match_score = max(match_score, alias_score)
                
                # Record match if above threshold
                if match_score >= fuzzy_threshold:
                    all_matches.append({
                        'list_name': list_name,
                        'match_score': round(match_score, 3),
                        'entry': entry,
                        'match_type': 'Exact' if match_score >= 0.95 else 'Fuzzy',
                        'matched_name': entry['name']
                    })
        
        return sorted(all_matches, key=lambda x: x['match_score'], reverse=True)

    def _run(self, name: str, entity_type: str = "individual",
             date_of_birth: Optional[str] = None, country: Optional[str] = None,
             fuzzy_threshold: float = 0.85) -> str:
        
        # Perform sanctions check
        matches = self._check_sanctions_lists(
            name, entity_type, date_of_birth, country, fuzzy_threshold
        )
        
        # Determine overall status
        if not matches:
            status = "Clear - No Matches Found"
            risk_level = "Low"
        elif any(m['match_score'] >= 0.95 for m in matches):
            status = "Hit - Exact Match Found"
            risk_level = "Critical"
        elif any(m['match_score'] >= 0.90 for m in matches):
            status = "Potential Hit - High Similarity"
            risk_level = "High"
        else:
            status = "Possible Match - Manual Review Required"
            risk_level = "Medium"
        
        # Prepare result
        result = {
            'search_parameters': {
                'name': name,
                'entity_type': entity_type,
                'date_of_birth': date_of_birth,
                'country': country,
                'fuzzy_threshold': fuzzy_threshold
            },
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'risk_level': risk_level,
            'total_matches': len(matches),
            'matches': matches[:10],  # Top 10 matches
            'lists_checked': list(self.sanctions_data['lists'].keys()),
            'recommendation': self._get_recommendation(status, matches)
        }
        
        return json.dumps(result, indent=2)

    def _get_recommendation(self, status: str, matches: List[Dict]) -> str:
        """Generate recommendation based on sanctions check results"""
        if "Clear" in status:
            return "No sanctions concerns identified. Proceed with standard due diligence."
        elif "Exact Match" in status:
            return "DO NOT PROCEED. Exact sanctions match found. Reject application and file SAR if required."
        elif "High Similarity" in status:
            return "HIGH RISK. Conduct enhanced due diligence and manual verification before proceeding."
        else:
            return "MEDIUM RISK. Manual review required to confirm identity and assess sanctions risk."

    async def _arun(self, name: str, entity_type: str = "individual",
                    date_of_birth: Optional[str] = None, country: Optional[str] = None,
                    fuzzy_threshold: float = 0.85) -> str:
        return self._run(name, entity_type, date_of_birth, country, fuzzy_threshold)