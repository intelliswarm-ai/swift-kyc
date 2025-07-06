import os
import asyncio
from typing import Dict, List, Optional
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
import json
from datetime import datetime
from fake_useragent import UserAgent


class BrowserSearchInput(BaseModel):
    query: str = Field(..., description="Search query for the person or company")
    max_results: int = Field(5, description="Maximum number of results to return")
    search_engines: List[str] = Field(
        ["duckduckgo", "bing"], 
        description="Search engines to use"
    )


class HeadlessBrowserTool(BaseTool):
    name: str = "Headless Browser Search"
    description: str = """
    Performs confidential web searches using a headless browser.
    Searches multiple search engines and extracts relevant information
    while maintaining privacy and avoiding tracking.
    """
    args_schema: type[BaseModel] = BrowserSearchInput

    def __init__(self):
        super().__init__()
        self.ua = UserAgent()
        self.search_urls = {
            "duckduckgo": "https://duckduckgo.com/?q={query}",
            "bing": "https://www.bing.com/search?q={query}",
            "startpage": "https://www.startpage.com/search?q={query}"
        }

    async def _search_with_browser(self, query: str, max_results: int, search_engines: List[str]) -> List[Dict]:
        results = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=os.getenv("BROWSER_HEADLESS", "true").lower() == "true",
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            context = await browser.new_context(
                user_agent=self.ua.random,
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                permissions=[],
                geolocation=None,
                color_scheme='light',
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            page = await context.new_page()
            
            for engine in search_engines:
                if engine not in self.search_urls:
                    continue
                    
                try:
                    search_url = self.search_urls[engine].format(query=query.replace(" ", "+"))
                    await page.goto(search_url, wait_until='networkidle', timeout=30000)
                    await page.wait_for_timeout(2000)  # Wait for dynamic content
                    
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract search results based on search engine
                    if engine == "duckduckgo":
                        search_results = soup.find_all('article', {'data-testid': 'result'})[:max_results]
                        for result in search_results:
                            title_elem = result.find('h2')
                            link_elem = result.find('a', href=True)
                            snippet_elem = result.find('span')
                            
                            if title_elem and link_elem:
                                results.append({
                                    'title': title_elem.get_text(strip=True),
                                    'url': link_elem['href'],
                                    'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                                    'source': engine,
                                    'timestamp': datetime.now().isoformat()
                                })
                    
                    elif engine == "bing":
                        search_results = soup.select('.b_algo')[:max_results]
                        for result in search_results:
                            title_elem = result.find('h2')
                            link_elem = title_elem.find('a') if title_elem else None
                            snippet_elem = result.find('p')
                            
                            if title_elem and link_elem:
                                results.append({
                                    'title': title_elem.get_text(strip=True),
                                    'url': link_elem.get('href', ''),
                                    'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                                    'source': engine,
                                    'timestamp': datetime.now().isoformat()
                                })
                    
                except Exception as e:
                    print(f"Error searching {engine}: {str(e)}")
                    continue
            
            await browser.close()
        
        return results

    def _run(self, query: str, max_results: int = 5, search_engines: List[str] = None) -> str:
        if search_engines is None:
            search_engines = ["duckduckgo", "bing"]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                self._search_with_browser(query, max_results, search_engines)
            )
            
            return json.dumps({
                'query': query,
                'total_results': len(results),
                'results': results
            }, indent=2)
            
        finally:
            loop.close()

    async def _arun(self, query: str, max_results: int = 5, search_engines: List[str] = None) -> str:
        if search_engines is None:
            search_engines = ["duckduckgo", "bing"]
            
        results = await self._search_with_browser(query, max_results, search_engines)
        
        return json.dumps({
            'query': query,
            'total_results': len(results),
            'results': results
        }, indent=2)