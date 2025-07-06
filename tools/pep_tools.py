import json
import os
import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Tuple
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import re
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import hashlib
from playwright.async_api import async_playwright
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PEPCheckInput(BaseModel):
    name: str = Field(..., description="Full name of the person to check")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    nationality: Optional[str] = Field(None, description="Nationality or country")
    fuzzy_match: bool = Field(True, description="Enable fuzzy matching for name variations")
    online_search: bool = Field(True, description="Enable online search for PEP information")


class PEPDatabaseUpdater:
    """Handles dynamic updating of PEP databases from public sources"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.cache_dir = os.path.join(data_dir, "pep_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Public PEP data sources
        self.pep_sources = {
            "opensanctions": {
                "url": "https://api.opensanctions.org/search/{name}",
                "type": "api",
                "requires_key": False
            },
            "world_bank": {
                "url": "https://apigwext.worldbank.org/dvsvc/v1.0/json/APPLICATION/ADOBE_EXPRNCE_MGR/FIRM/SANCTIONED_FIRM",
                "type": "api",
                "requires_key": False
            },
            "everypolitician": {
                "url": "http://everypolitician.org/api/v0.1/countries.json",
                "type": "api",
                "requires_key": False
            }
        }
        
        # News sources for PEP identification
        self.news_sources = [
            "https://www.reuters.com/search/news?blob={query}",
            "https://www.bbc.com/search?q={query}+politician",
            "https://apnews.com/search?q={query}+political",
            "https://www.bloomberg.com/search?query={query}+minister+senator"
        ]

    async def fetch_opensanctions_data(self, name: str) -> List[Dict]:
        """Fetch PEP data from OpenSanctions API"""
        try:
            url = f"https://api.opensanctions.org/search/{quote_plus(name)}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        for result in data.get('results', []):
                            if 'properties' in result:
                                props = result['properties']
                                results.append({
                                    'source': 'opensanctions',
                                    'name': props.get('name', [''])[0],
                                    'aliases': props.get('alias', []),
                                    'nationality': props.get('nationality', [''])[0],
                                    'positions': props.get('position', []),
                                    'birth_date': props.get('birthDate', [''])[0],
                                    'topics': result.get('topics', []),
                                    'score': result.get('score', 0)
                                })
                        return results
        except Exception as e:
            logger.error(f"Error fetching OpenSanctions data: {e}")
        return []

    async def search_news_for_pep(self, name: str) -> List[Dict]:
        """Search news sources for PEP information"""
        results = []
        political_keywords = [
            'minister', 'senator', 'parliament', 'congress', 'president',
            'governor', 'mayor', 'politician', 'ambassador', 'secretary',
            'commissioner', 'councillor', 'deputy', 'chairman', 'director general'
        ]
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Search major news sites
                for source_url in self.news_sources[:2]:  # Limit to avoid rate limiting
                    try:
                        search_url = source_url.format(query=quote_plus(name))
                        await page.goto(search_url, wait_until='networkidle', timeout=30000)
                        content = await page.content()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Extract text content
                        text_content = soup.get_text().lower()
                        
                        # Check for political keywords
                        found_keywords = []
                        for keyword in political_keywords:
                            if keyword in text_content:
                                found_keywords.append(keyword)
                        
                        if found_keywords:
                            results.append({
                                'source': source_url.split('/')[2],
                                'name': name,
                                'political_indicators': found_keywords,
                                'search_url': search_url,
                                'timestamp': datetime.now().isoformat()
                            })
                        
                    except Exception as e:
                        logger.error(f"Error searching {source_url}: {e}")
                        continue
                
                await browser.close()
                
        except Exception as e:
            logger.error(f"Error in news search: {e}")
        
        return results

    async def update_pep_database(self):
        """Update the local PEP database with data from public sources"""
        logger.info("Updating PEP database from public sources...")
        
        # This would be run periodically to update the database
        # For now, we'll just ensure the structure is in place
        database_file = os.path.join(self.data_dir, "pep_database.json")
        
        if not os.path.exists(database_file):
            initial_database = {
                "peps": [],
                "sources": [],
                "version": "2.0",
                "last_updated": datetime.now().isoformat()
            }
            with open(database_file, 'w') as f:
                json.dump(initial_database, f, indent=2)
        
        return database_file


class PEPCheckTool(BaseTool):
    name: str = "Enhanced PEP Check"
    description: str = """
    Advanced PEP checking tool that:
    1. Searches local and dynamically updated PEP databases
    2. Queries public APIs for PEP information
    3. Searches news articles and public records
    4. Identifies political connections through web research
    """
    args_schema: type[BaseModel] = PEPCheckInput

    def __init__(self):
        super().__init__()
        self.data_dir = os.getenv("PEP_DATA_DIR", "./data")
        self.pep_database_path = os.path.join(self.data_dir, "pep_database.json")
        self.updater = PEPDatabaseUpdater(self.data_dir)
        self._load_pep_database()
        
    def _load_pep_database(self):
        """Load PEP database from file"""
        if os.path.exists(self.pep_database_path):
            with open(self.pep_database_path, 'r') as f:
                self.pep_database = json.load(f)
        else:
            # Initialize empty database
            self.pep_database = {
                "peps": [],
                "sources": [],
                "version": "2.0",
                "last_updated": datetime.now().isoformat()
            }
            os.makedirs(os.path.dirname(self.pep_database_path), exist_ok=True)
            with open(self.pep_database_path, 'w') as f:
                json.dump(self.pep_database, f, indent=2)

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

    def _check_local_database(self, name: str, fuzzy_match: bool) -> List[Dict]:
        """Check the local PEP database"""
        matches = []
        
        for pep_entry in self.pep_database.get('peps', []):
            # Check main name
            name_score = self._calculate_name_similarity(name, pep_entry.get('name', ''))
            if name_score > 0.8 or (fuzzy_match and name_score > 0.7):
                matches.append({
                    'source': 'local_database',
                    'match_score': name_score,
                    'match_type': 'Direct PEP',
                    'pep_details': pep_entry
                })
            
            # Check aliases
            for alias in pep_entry.get('aliases', []):
                alias_score = self._calculate_name_similarity(name, alias)
                if alias_score > 0.8 or (fuzzy_match and alias_score > 0.7):
                    matches.append({
                        'source': 'local_database',
                        'match_score': alias_score,
                        'match_type': 'Direct PEP (Alias)',
                        'pep_details': pep_entry
                    })
            
            # Check family members
            for family_member in pep_entry.get('family_members', []):
                family_score = self._calculate_name_similarity(name, family_member.get('name', ''))
                if family_score > 0.8 or (fuzzy_match and family_score > 0.7):
                    matches.append({
                        'source': 'local_database',
                        'match_score': family_score,
                        'match_type': f"PEP Relative ({family_member.get('relationship', 'Unknown')})",
                        'pep_details': pep_entry
                    })
        
        return matches

    async def _check_online_sources(self, name: str) -> Tuple[List[Dict], List[Dict]]:
        """Check online sources for PEP information"""
        # Fetch from OpenSanctions
        opensanctions_results = await self.updater.fetch_opensanctions_data(name)
        
        # Search news for political connections
        news_results = await self.updater.search_news_for_pep(name)
        
        return opensanctions_results, news_results

    def _consolidate_results(self, local_matches: List[Dict], 
                           opensanctions_results: List[Dict],
                           news_results: List[Dict]) -> Dict:
        """Consolidate results from all sources"""
        all_matches = []
        
        # Add local matches
        all_matches.extend(local_matches)
        
        # Add OpenSanctions results
        for result in opensanctions_results:
            if result.get('topics') and any('role.pep' in topic for topic in result['topics']):
                all_matches.append({
                    'source': 'opensanctions',
                    'match_score': result.get('score', 0.7),
                    'match_type': 'Direct PEP',
                    'pep_details': result
                })
        
        # Analyze news results
        political_evidence = []
        for news_result in news_results:
            if news_result.get('political_indicators'):
                political_evidence.append({
                    'source': news_result['source'],
                    'indicators': news_result['political_indicators'],
                    'url': news_result.get('search_url', '')
                })
        
        # Sort matches by score
        all_matches.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        # Determine overall PEP status
        pep_status = 'No Match'
        if all_matches:
            highest_match = all_matches[0]
            if highest_match['match_score'] > 0.9:
                pep_status = 'Confirmed PEP' if 'Direct' in highest_match['match_type'] else 'PEP Associate'
            elif highest_match['match_score'] > 0.7:
                pep_status = 'Potential Match - Verification Required'
        elif political_evidence:
            pep_status = 'Political Indicators Found - Further Investigation Required'
        
        return {
            'pep_status': pep_status,
            'matches': all_matches[:5],  # Top 5 matches
            'political_evidence': political_evidence,
            'total_matches': len(all_matches)
        }

    def _run(self, name: str, date_of_birth: Optional[str] = None,
             nationality: Optional[str] = None, fuzzy_match: bool = True,
             online_search: bool = True) -> str:
        
        # Check local database
        local_matches = self._check_local_database(name, fuzzy_match)
        
        # Filter by nationality if provided
        if nationality:
            local_matches = [m for m in local_matches 
                           if m['pep_details'].get('nationality', '').lower() == nationality.lower()]
        
        # Filter by date of birth if provided
        if date_of_birth:
            for match in local_matches:
                if match['pep_details'].get('date_of_birth') == date_of_birth:
                    match['match_score'] = min(match['match_score'] + 0.1, 1.0)
                else:
                    match['match_score'] *= 0.8
        
        # Online search if enabled
        opensanctions_results = []
        news_results = []
        
        if online_search:
            try:
                # Run async operations
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                opensanctions_results, news_results = loop.run_until_complete(
                    self._check_online_sources(name)
                )
            except Exception as e:
                logger.error(f"Error in online search: {e}")
            finally:
                loop.close()
        
        # Consolidate all results
        consolidated = self._consolidate_results(
            local_matches, opensanctions_results, news_results
        )
        
        # Prepare final result
        result = {
            'search_parameters': {
                'name': name,
                'date_of_birth': date_of_birth,
                'nationality': nationality,
                'fuzzy_match': fuzzy_match,
                'online_search': online_search
            },
            'timestamp': datetime.now().isoformat(),
            'pep_status': consolidated['pep_status'],
            'matches': consolidated['matches'],
            'political_evidence': consolidated.get('political_evidence', []),
            'total_matches': consolidated['total_matches'],
            'data_sources': {
                'local_database': {
                    'version': self.pep_database.get('version', 'Unknown'),
                    'last_updated': self.pep_database.get('last_updated', 'Unknown')
                },
                'online_sources': ['opensanctions', 'news_search'] if online_search else []
            }
        }
        
        return json.dumps(result, indent=2)

    async def _arun(self, name: str, date_of_birth: Optional[str] = None,
                    nationality: Optional[str] = None, fuzzy_match: bool = True,
                    online_search: bool = True) -> str:
        return self._run(name, date_of_birth, nationality, fuzzy_match, online_search)