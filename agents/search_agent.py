# agents/search_agent.py

import logging, requests, time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import List, Dict
from core.memory import Memory

class SearchAgent:
    """Agent responsible for finding relevant sources"""
    
    def __init__(self, memory: Memory):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.memory = memory
        self.search_engines = [
            "https://duckduckgo.com/html/",
            # Fallback search methods
        ]
    
    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search using DuckDuckGo"""
        try:
            # Check memory first
            if self.memory.has_searched(query):
                self.logger.info(f"Query '{query}' already searched, skipping")
                return []
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            params = {
                'q': query,
                'b': '',  # Start from beginning
                'kl': 'us-en',
                'df': 'm'  # Recent results
            }
            
            response = requests.get(
                "https://duckduckgo.com/html/",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                self.logger.error(f"Search failed with status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Parse DuckDuckGo results
            for result in soup.find_all('div', class_='result')[:max_results]:
                try:
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem and snippet_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href')
                        snippet = snippet_elem.get_text(strip=True)
                        
                        # Filter tech news sources
                        if any(domain in url.lower() for domain in [
                            'techcrunch', 'theverge', 'engadget', 'gsmarena',
                            'androidcentral', 'macrumors', 'phonearena',
                            'notebookcheck', 'tomshardware'
                        ]):
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'source': urlparse(url).netloc
                            })
                
                except Exception as e:
                    self.logger.warning(f"Error parsing result: {e}")
                    continue
            
            self.memory.mark_searched(query)
            self.logger.info(f"Found {len(results)} relevant sources for '{query}'")
            return results
            
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return []
    
    def search(self, topic: str) -> List[Dict]:
        """Main search method"""
        self.logger.info(f"Searching for: {topic}")
        
        # Create search queries
        queries = [
            f"{topic} latest news 2025",
            f"{topic} new release announcement",
            f"{topic} specs features launch"
        ]
        
        all_results = []
        for query in queries:
            results = self.search_duckduckgo(query, max_results=3)
            all_results.extend(results)
            time.sleep(1)  # Rate limiting
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        return unique_results[:5] 