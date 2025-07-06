import json
import os
from typing import Dict, List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime
from difflib import SequenceMatcher


class PEPCheckInput(BaseModel):
    name: str = Field(..., description="Full name of the person to check")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    nationality: Optional[str] = Field(None, description="Nationality or country")
    fuzzy_match: bool = Field(True, description="Enable fuzzy matching for name variations")


class PEPCheckTool(BaseTool):
    name: str = "PEP Database Check"
    description: str = """
    Checks if a person is a Politically Exposed Person (PEP) or related to a PEP.
    Searches through comprehensive PEP databases including current and former
    political figures, their family members, and close associates.
    """
    args_schema: type[BaseModel] = PEPCheckInput

    def _load_pep_database(self) -> Dict:
        """Load PEP database from file or create default"""
        pep_database_path = os.getenv("PEP_DATABASE_PATH", "./data/pep_database.json")
        
        if os.path.exists(pep_database_path):
            with open(pep_database_path, 'r') as f:
                return json.load(f)
        else:
            # Create default database
            default_db = {
                "peps": [
                    {
                        "id": "PEP001",
                        "name": "John Smith",
                        "aliases": ["J. Smith", "John A. Smith"],
                        "date_of_birth": "1965-03-15",
                        "nationality": "USA",
                        "positions": [
                            {
                                "title": "Senator",
                                "country": "USA",
                                "start_date": "2015-01-01",
                                "end_date": None,
                                "current": True
                            }
                        ],
                        "family_members": [
                            {"name": "Jane Smith", "relationship": "Spouse"},
                            {"name": "Michael Smith", "relationship": "Son"}
                        ],
                        "risk_level": "High",
                        "last_updated": "2024-01-15"
                    }
                ],
                "version": "1.0",
                "last_updated": "2024-01-15"
            }
            
            # Create directory if needed
            os.makedirs(os.path.dirname(pep_database_path), exist_ok=True)
            
            # Save default database
            with open(pep_database_path, 'w') as f:
                json.dump(default_db, f, indent=2)
            
            return default_db

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity score between two names"""
        name1 = name1.lower().strip()
        name2 = name2.lower().strip()
        
        # Direct match
        if name1 == name2:
            return 1.0
        
        # Check if one name contains the other
        if name1 in name2 or name2 in name1:
            return 0.9
        
        # Use sequence matcher for fuzzy matching
        return SequenceMatcher(None, name1, name2).ratio()

    def _check_pep_match(self, search_name: str, pep_entry: Dict, fuzzy_match: bool) -> Optional[Dict]:
        """Check if a PEP entry matches the search criteria"""
        match_score = 0.0
        match_type = None
        
        # Check main name
        name_score = self._calculate_name_similarity(search_name, pep_entry['name'])
        if name_score > 0.8 or (fuzzy_match and name_score > 0.7):
            match_score = name_score
            match_type = "Direct PEP"
        
        # Check aliases
        for alias in pep_entry.get('aliases', []):
            alias_score = self._calculate_name_similarity(search_name, alias)
            if alias_score > match_score:
                match_score = alias_score
                match_type = "Direct PEP (Alias)"
        
        # Check family members
        for family_member in pep_entry.get('family_members', []):
            family_score = self._calculate_name_similarity(search_name, family_member['name'])
            if family_score > 0.8 or (fuzzy_match and family_score > 0.7):
                if family_score > match_score:
                    match_score = family_score
                    match_type = f"PEP Relative ({family_member['relationship']})"
        
        if match_score > 0:
            return {
                'match_score': match_score,
                'match_type': match_type,
                'pep_details': pep_entry
            }
        
        return None

    def _run(self, name: str, date_of_birth: Optional[str] = None, 
             nationality: Optional[str] = None, fuzzy_match: bool = True) -> str:
        
        # Load database
        pep_database = self._load_pep_database()
        
        matches = []
        
        for pep_entry in pep_database.get('peps', []):
            # Check nationality filter if provided
            if nationality and pep_entry.get('nationality', '').lower() != nationality.lower():
                continue
            
            # Check for name match
            match_result = self._check_pep_match(name, pep_entry, fuzzy_match)
            
            if match_result:
                # Additional verification with date of birth if provided
                if date_of_birth and pep_entry.get('date_of_birth'):
                    if date_of_birth == pep_entry['date_of_birth']:
                        match_result['match_score'] += 0.1  # Boost score for DOB match
                    else:
                        match_result['match_score'] *= 0.8  # Reduce score for DOB mismatch
                
                matches.append(match_result)
        
        # Sort matches by score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Prepare result
        result = {
            'search_parameters': {
                'name': name,
                'date_of_birth': date_of_birth,
                'nationality': nationality,
                'fuzzy_match': fuzzy_match
            },
            'timestamp': datetime.now().isoformat(),
            'pep_status': 'No Match' if not matches else 'Match Found',
            'matches': matches[:5],  # Return top 5 matches
            'total_matches': len(matches),
            'database_version': pep_database.get('version', 'Unknown'),
            'database_last_updated': pep_database.get('last_updated', 'Unknown')
        }
        
        # Determine overall PEP status
        if matches:
            highest_match = matches[0]
            if highest_match['match_score'] > 0.9:
                result['pep_status'] = 'Confirmed PEP' if 'Direct' in highest_match['match_type'] else 'PEP Associate'
            elif highest_match['match_score'] > 0.7:
                result['pep_status'] = 'Potential Match - Verification Required'
        
        return json.dumps(result, indent=2)

    async def _arun(self, name: str, date_of_birth: Optional[str] = None,
                    nationality: Optional[str] = None, fuzzy_match: bool = True) -> str:
        return self._run(name, date_of_birth, nationality, fuzzy_match)