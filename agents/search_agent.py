import requests
import logging
import time
from typing import List, Dict, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json
from core.memory import Memory
class SearchAgent:
    """Enhanced agent responsible for finding relevant tech sources"""
    def __init__(self, memory: Optional[Memory] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.memory = memory or Memory()
        
        # Ensure memory has all required attributes
        if not hasattr(self.memory, 'cached_results'):
            self.memory.cached_results = {}
        if not hasattr(self.memory, 'searched_queries'):
            self.memory.searched_queries = set()
        if not hasattr(self.memory, 'processed_urls'):
            self.memory.processed_urls = set()
        
        # Trusted tech news domains with priority scores
        self.trusted_domains = {
            'techcrunch.com': 9,
            'theverge.com': 9,
            'engadget.com': 8,
            'arstechnica.com': 9,
            'wired.com': 8,
            'gsmarena.com': 8,
            'androidcentral.com': 7,
            'macrumors.com': 8,
            'phonearena.com': 7,
            'notebookcheck.net': 8,
            'tomshardware.com': 8,
            '9to5mac.com': 7,
            'androidpolice.com': 7,
            'xda-developers.com': 7
        }
        
        # Common headers to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def generate_search_queries(self, topic: str) -> List[str]:
        """Generate multiple search query variations for better coverage"""
        base_topic = topic.lower()
        
        # Product-specific query patterns
        queries = [
            f"{topic} latest news 2025",
            f"{topic} announcement release date",
            f"{topic} specs features price",
            f"{topic} review hands-on",
            f"{topic} launch event"
        ]
        
        # Add brand-specific queries if detected
        brands = ['iphone', 'samsung', 'google pixel', 'macbook', 'ipad', 'surface', 'thinkpad']
        for brand in brands:
            if brand in base_topic:
                queries.extend([
                    f"{brand} new model 2025",
                    f"{brand} latest update announcement"
                ])
                break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for query in queries:
            if query not in seen:
                seen.add(query)
                unique_queries.append(query)
        
        return unique_queries[:5]  # Limit to top 5 queries
    
    def search_duckduckgo(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search using DuckDuckGo with improved parsing"""
        try:
            # Check cache first
            if hasattr(self.memory, 'get_cached_result'):
                cached = self.memory.get_cached_result(query)
                if cached:
                    self.logger.info(f"Using cached results for '{query}'")
                    return cached
            
            self.logger.info(f"Searching DuckDuckGo for: '{query}'")
            
            params = {
                'q': query,
                'kl': 'us-en',
                'df': 'm',  # Recent results (past month)
                'ia': 'web'
            }
            
            response = requests.get(
                "https://duckduckgo.com/html/",
                params=params,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code != 200:
                self.logger.error(f"Search failed with status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Parse search results with multiple selectors
            result_selectors = [
                'div.result',
                'div.web-result',
                'div[class*="result"]'
            ]
            
            for selector in result_selectors:
                elements = soup.select(selector)
                if elements:
                    break
            else:
                self.logger.warning("No results found with any selector")
                return []
            
            for result in elements[:max_results]:
                try:
                    # Try multiple title selectors
                    title_elem = (
                        result.find('a', class_='result__a') or
                        result.find('h3') or
                        result.find('a', {'data-testid': 'result-title-a'}) or
                        result.find('a')
                    )
                    
                    # Try multiple snippet selectors
                    snippet_elem = (
                        result.find('a', class_='result__snippet') or
                        result.find('span', class_='result__snippet') or
                        result.find('div', {'data-testid': 'result-snippet'}) or
                        result.find('span')
                    )
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    # Clean URL (remove DuckDuckGo redirect)
                    if url.startswith('/l/?uddg='):
                        # Extract actual URL from DuckDuckGo redirect
                        import urllib.parse
                        url = urllib.parse.unquote(url.split('uddg=')[1].split('&')[0])
                    
                    if not url or not title:
                        continue
                    
                    # Parse domain and check if it's a trusted tech source
                    try:
                        domain = urlparse(url).netloc.lower()
                        domain = domain.replace('www.', '')
                    except:
                        continue
                    
                    # Filter for tech-related domains or content
                    is_tech_domain = any(trusted in domain for trusted in self.trusted_domains.keys())
                    is_tech_content = any(keyword in (title + snippet).lower() for keyword in [
                        'tech', 'smartphone', 'laptop', 'tablet', 'processor', 'camera',
                        'display', 'battery', 'storage', 'release', 'announcement', 'review'
                    ])
                    
                    if is_tech_domain or is_tech_content:
                        # Calculate priority score
                        priority_score = self.trusted_domains.get(domain, 5)
                        
                        # Boost score for recent content indicators
                        if any(keyword in (title + snippet).lower() for keyword in ['2025', 'new', 'latest', 'announced']):
                            priority_score += 2
                        
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'domain': domain,
                            'priority_score': priority_score
                        })
                
                except Exception as e:
                    self.logger.debug(f"Error parsing individual result: {e}")
                    continue
            
            # Sort by priority score (highest first)
            results.sort(key=lambda x: x['priority_score'], reverse=True)
            
            # Cache results
            self.memory.cache_result(query, results)
            self.memory.mark_searched(query)
            
            self.logger.info(f"Found {len(results)} relevant sources for '{query}'")
            return results
            
        except Exception as e:
            self.logger.error(f"Search error for '{query}': {e}")
            return []
    
    def search_bing(self, query: str, max_results: int = 10) -> List[Dict]:
        """Alternative search using Bing (fallback method)"""
        try:
            self.logger.info(f"Searching Bing for: '{query}'")
            
            params = {
                'q': query,
                'count': max_results,
                'freshness': 'Month'  # Recent results
            }
            
            response = requests.get(
                "https://www.bing.com/search",
                params=params,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Parse Bing results
            for result in soup.find_all('li', class_='b_algo')[:max_results]:
                try:
                    title_elem = result.find('h2')
                    if not title_elem:
                        continue
                    
                    link_elem = title_elem.find('a')
                    if not link_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = link_elem.get('href', '')
                    
                    snippet_elem = result.find('p')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    domain = urlparse(url).netloc.lower().replace('www.', '')
                    
                    # Filter for tech domains
                    if any(trusted in domain for trusted in self.trusted_domains.keys()):
                        priority_score = self.trusted_domains.get(domain, 5)
                        
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'domain': domain,
                            'priority_score': priority_score
                        })
                
                except Exception as e:
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Bing search error: {e}")
            return []
    
    def search(self, topic: str, max_results: int = 15) -> List[Dict]:
        """Main search method with multiple query strategies"""
        self.logger.info(f"Starting comprehensive search for: {topic}")
        
        # Generate query variations
        queries = self.generate_search_queries(topic)
        
        all_results = []
        search_methods = [self.search_duckduckgo, self.search_bing]
        
        for query in queries:
            for search_method in search_methods:
                try:
                    results = search_method(query, max_results=8)
                    all_results.extend(results)
                    
                    # Rate limiting
                    time.sleep(2)
                    
                    # Break if we have enough results
                    if len(all_results) >= max_results * 2:
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Search method failed: {e}")
                    continue
            
            # Break outer loop if we have enough results
            if len(all_results) >= max_results * 2:
                break
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            url = result['url']
            if url not in seen_urls and len(url) > 10:  # Basic URL validation
                seen_urls.add(url)
                unique_results.append(result)
        
        # Sort by priority score and limit results
        unique_results.sort(key=lambda x: x['priority_score'], reverse=True)
        final_results = unique_results[:max_results]
        
        self.logger.info(f"Completed search: {len(final_results)} unique results from {len(queries)} queries")
        
        return final_results
    
    def get_search_stats(self) -> Dict:
        """Get statistics about search operations"""
        return {
            'queries_searched': len(self.memory.searched_queries),
            'cached_results': len(self.memory.cached_results),
            'trusted_domains': len(self.trusted_domains)
        }