"""
Enhanced web search tools for KYC analysis
Works without API keys using web scraping
"""
import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Any
from urllib.parse import quote_plus
import logging


class KYCWebSearcher:
    """Web search tool for KYC investigations"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_duckduckgo(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo HTML interface"""
        results = []
        try:
            # DuckDuckGo HTML search
            url = "https://html.duckduckgo.com/html/"
            params = {'q': query, 's': '0', 'dc': '0', 'v': 'l', 'o': 'json'}
            
            response = self.session.post(url, data=params, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all result divs
            for i, result_div in enumerate(soup.find_all('div', class_=['result', 'results_links_deep'])):
                if i >= num_results:
                    break
                
                # Extract title
                title_elem = result_div.find('a', class_='result__a')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                
                # Extract snippet
                snippet_elem = result_div.find('a', class_='result__snippet')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                
                if title and url:
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet,
                        'source': 'DuckDuckGo'
                    })
            
            self.logger.info(f"DuckDuckGo search for '{query}' returned {len(results)} results")
            
        except Exception as e:
            self.logger.error(f"DuckDuckGo search error: {e}")
        
        return results
    
    def search_bing(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search using Bing"""
        results = []
        try:
            url = f"https://www.bing.com/search"
            params = {'q': query, 'count': num_results}
            
            response = self.session.get(url, params=params, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find search results
            for li in soup.find_all('li', class_='b_algo'):
                h2 = li.find('h2')
                if not h2:
                    continue
                
                a = h2.find('a')
                if not a:
                    continue
                
                title = a.get_text(strip=True)
                url = a.get('href', '')
                
                # Get snippet
                caption_div = li.find('div', class_='b_caption')
                snippet = ''
                if caption_div:
                    p = caption_div.find('p')
                    if p:
                        snippet = p.get_text(strip=True)
                
                if title and url:
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet,
                        'source': 'Bing'
                    })
                
                if len(results) >= num_results:
                    break
            
            self.logger.info(f"Bing search for '{query}' returned {len(results)} results")
            
        except Exception as e:
            self.logger.error(f"Bing search error: {e}")
        
        return results
    
    def search_google_news(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search Google News RSS feed"""
        results = []
        try:
            # Google News RSS URL
            rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
            
            response = self.session.get(rss_url, timeout=15)
            soup = BeautifulSoup(response.text, 'xml')
            
            # Parse RSS items
            for i, item in enumerate(soup.find_all('item')):
                if i >= num_results:
                    break
                
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                pub_date = item.find('pubDate')
                source = item.find('source')
                
                if title and link:
                    results.append({
                        'title': title.get_text(strip=True),
                        'url': link.get_text(strip=True),
                        'snippet': description.get_text(strip=True) if description else '',
                        'source': source.get_text(strip=True) if source else 'Google News',
                        'published': pub_date.get_text(strip=True) if pub_date else ''
                    })
            
            self.logger.info(f"Google News search for '{query}' returned {len(results)} results")
            
        except Exception as e:
            self.logger.error(f"Google News search error: {e}")
        
        return results
    
    def search_multiple(self, query: str, num_results_per_engine: int = 5) -> List[Dict[str, Any]]:
        """Search multiple search engines and combine results"""
        all_results = []
        
        # Search each engine
        engines = [
            ('DuckDuckGo', self.search_duckduckgo),
            ('Bing', self.search_bing),
            ('Google News', self.search_google_news)
        ]
        
        for engine_name, search_func in engines:
            self.logger.info(f"Searching {engine_name}...")
            try:
                results = search_func(query, num_results_per_engine)
                all_results.extend(results)
                # Small delay to avoid rate limiting
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"{engine_name} search failed: {e}")
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    def search_for_pep(self, name: str, additional_terms: List[str] = None) -> List[Dict[str, Any]]:
        """Specialized search for PEP identification"""
        pep_queries = [
            f'"{name}" politician minister ambassador',
            f'"{name}" government official position',
            f'"{name}" "politically exposed person"',
            f'"{name}" election campaign political party'
        ]
        
        if additional_terms:
            for term in additional_terms:
                pep_queries.append(f'"{name}" {term}')
        
        all_results = []
        for query in pep_queries:
            results = self.search_multiple(query, num_results_per_engine=3)
            all_results.extend(results)
            time.sleep(1)  # Rate limiting
        
        return all_results
    
    def search_for_adverse_media(self, name: str, company: str = None) -> List[Dict[str, Any]]:
        """Search for adverse media and negative news"""
        adverse_queries = [
            f'"{name}" scandal fraud corruption',
            f'"{name}" investigation lawsuit legal',
            f'"{name}" arrest charged convicted',
            f'"{name}" sanctions violation fine penalty',
            f'"{name}" money laundering terrorist financing'
        ]
        
        if company:
            adverse_queries.extend([
                f'"{name}" "{company}" scandal',
                f'"{company}" fraud investigation'
            ])
        
        all_results = []
        for query in adverse_queries:
            results = self.search_multiple(query, num_results_per_engine=3)
            all_results.extend(results)
            time.sleep(1)
        
        return all_results
    
    def analyze_search_result(self, result: Dict[str, Any], target_name: str) -> Dict[str, Any]:
        """Analyze a search result for relevance and sentiment"""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        combined_text = f"{title} {snippet}"
        
        # Check if the target name appears in the result
        name_parts = target_name.lower().split()
        name_found = all(part in combined_text for part in name_parts)
        
        # Check for adverse keywords
        adverse_keywords = [
            'scandal', 'fraud', 'corruption', 'investigation', 'lawsuit',
            'arrest', 'charged', 'convicted', 'violation', 'fine', 'penalty',
            'money laundering', 'terrorist', 'criminal', 'illegal'
        ]
        
        adverse_found = any(keyword in combined_text for keyword in adverse_keywords)
        
        # Check for positive keywords
        positive_keywords = [
            'award', 'honor', 'achievement', 'success', 'leader',
            'innovative', 'philanthropist', 'recognized', 'appointed'
        ]
        
        positive_found = any(keyword in combined_text for keyword in positive_keywords)
        
        # Check for political keywords (PEP indicators)
        political_keywords = [
            'minister', 'politician', 'government', 'official', 'ambassador',
            'senator', 'deputy', 'mayor', 'governor', 'president',
            'political', 'election', 'campaign', 'party'
        ]
        
        political_found = any(keyword in combined_text for keyword in political_keywords)
        
        return {
            'is_relevant': name_found,
            'has_adverse_content': adverse_found,
            'has_positive_content': positive_found,
            'has_political_content': political_found,
            'relevance_score': 1.0 if name_found else 0.0,
            'sentiment': 'negative' if adverse_found else 'positive' if positive_found else 'neutral'
        }


class PEPDatabaseSearcher:
    """Search public PEP databases"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; KYC-Bot/1.0)'
        })
    
    def search_opensanctions(self, name: str) -> List[Dict[str, Any]]:
        """Search OpenSanctions database"""
        results = []
        try:
            # OpenSanctions search API (if available)
            # This is a placeholder - implement based on actual API
            url = f"https://www.opensanctions.org/search/?q={quote_plus(name)}"
            
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                # Parse results page
                soup = BeautifulSoup(response.text, 'html.parser')
                # Implementation depends on actual page structure
                
                self.logger.info(f"OpenSanctions search for '{name}' completed")
        
        except Exception as e:
            self.logger.error(f"OpenSanctions search error: {e}")
        
        return results
    
    def search_worldbank_debarred(self, name: str) -> List[Dict[str, Any]]:
        """Search World Bank debarred entities"""
        results = []
        try:
            # World Bank API endpoint
            url = "https://apigwext.worldbank.org/dvsvc/v1.0/json/APPLICATION/ADOBE_EXPRNCE_MGR/FIRM"
            params = {
                'format': 'json',
                'frmNm': name
            }
            
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                # Parse response based on actual structure
                
                self.logger.info(f"World Bank search for '{name}' completed")
        
        except Exception as e:
            self.logger.error(f"World Bank search error: {e}")
        
        return results