import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Try to import optional dependencies
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    print("Warning: duckduckgo_search not available.")

try:
    # Try different serpapi import methods
    try:
        from serpapi import GoogleSearch
        SERPAPI_AVAILABLE = True
        SERPAPI_METHOD = "serpapi"
    except ImportError:
        try:
            import serpapi
            SERPAPI_AVAILABLE = True
            SERPAPI_METHOD = "serpapi_direct"
        except ImportError:
            SERPAPI_AVAILABLE = False
except ImportError:
    SERPAPI_AVAILABLE = False

load_dotenv()

# Configure logging
from utils.logger import logger
class SearchAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.serpapi_key = api_key or os.getenv("SERPAPI_KEY")
        
        # Check available search methods
        self.available_methods = []
        
        if SERPAPI_AVAILABLE and self.serpapi_key:
            self.available_methods.append("serpapi")
            logger.info("SerpAPI available")
        elif self.serpapi_key:
            logger.warning("SerpAPI key provided but package not properly installed")
        
        if DDGS_AVAILABLE:
            self.available_methods.append("duckduckgo")
            logger.info("DuckDuckGo search available")
        
        # Always available - direct web scraping fallback
        self.available_methods.append("direct_search")
        
        if not self.available_methods:
            raise RuntimeError("No search methods available")
        
        # Enhanced product keywords
        self.product_keywords = {
            # Smartphones
            "iPhone": ["iphone", "apple phone"],
            "Samsung Galaxy": ["samsung", "galaxy"],
            "Google Pixel": ["pixel", "google phone"],
            "OnePlus": ["oneplus", "one plus"],
            "Xiaomi": ["xiaomi", "redmi", "mi phone"],
            "Realme": ["realme"],
            "Oppo": ["oppo"],
            "Vivo": ["vivo"],
            "Nothing": ["nothing phone"],
            
            # Laptops
            "MacBook": ["macbook", "mac book"],
            "Dell": ["dell laptop", "dell xps", "dell inspiron"],
            "HP": ["hp laptop", "hp pavilion", "hp spectre"],
            "Lenovo": ["lenovo", "thinkpad", "ideapad"],
            "Asus": ["asus", "zenbook", "vivobook"],
            "Acer": ["acer", "aspire", "predator"],
            "Surface": ["surface laptop", "surface pro"],
            "Framework": ["framework laptop"],
            
            # Other tech
            "iPad": ["ipad"],
            "Apple Watch": ["apple watch"],
            "AirPods": ["airpods"],
            "Galaxy Buds": ["galaxy buds"],
            "Steam Deck": ["steam deck"],
        }

    def search_serpapi(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search using SerpAPI - handles different import methods"""
        try:
            if SERPAPI_METHOD == "serpapi":
                # Standard serpapi import
                params = {
                    "engine": "google",
                    "q": query,
                    "num": num_results,
                    "api_key": self.serpapi_key,
                    "gl": "us",
                    "hl": "en"
                }
                search = GoogleSearch(params)
                results = search.get_dict()
                
            elif SERPAPI_METHOD == "serpapi_direct":
                # Direct serpapi module usage
                params = {
                    "engine": "google",
                    "q": query,
                    "num": num_results,
                    "api_key": self.serpapi_key,
                    "gl": "us",
                    "hl": "en"
                }
                results = serpapi.search(params)
            
            else:
                raise ImportError("SerpAPI not properly configured")
            
            # Extract results
            links = []
            for res in results.get("organic_results", [])[:num_results]:
                links.append({
                    "title": res.get("title", ""),
                    "link": res.get("link", ""),
                    "snippet": res.get("snippet", ""),
                    "date": res.get("date", "")
                })
            
            return links
            
        except Exception as e:
            logger.error(f"SerpAPI search failed: {e}")
            raise

    def search_duckduckgo(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search using DuckDuckGo"""
        if not DDGS_AVAILABLE:
            raise ImportError("DuckDuckGo search not available")
        
        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=num_results):
                    results.append({
                        "title": r.get("title", ""),
                        "link": r.get("href", ""),
                        "snippet": r.get("body", ""),
                        "date": ""
                    })
            return results
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            raise

    def search_direct_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """Direct web search using requests - basic fallback"""
        try:
            # This is a simplified example - in practice you'd want to use
            # proper web scraping with BeautifulSoup or similar
            
            # For now, return some mock tech news results
            # In a real implementation, you'd scrape tech news sites
            mock_results = [
                {
                    "title": f"Latest Tech Updates: {query}",
                    "link": "https://example.com/tech-news",
                    "snippet": "Recent technology releases and updates in the industry.",
                    "date": datetime.now().strftime("%Y-%m-%d")
                },
                {
                    "title": "Technology Release Schedule 2025",
                    "link": "https://example.com/releases",
                    "snippet": "Upcoming product launches and announcements from major tech companies.",
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
            ]
            
            logger.warning("Using mock results - implement proper web scraping for production")
            return mock_results[:num_results]
            
        except Exception as e:
            logger.error(f"Direct web search failed: {e}")
            return []

    def extract_product_name(self, title: str, snippet: str) -> str:
        """Extract primary product name from title """
        title_lower = title.lower()
        snippet_lower = snippet.lower()
        combined_text = f"{title_lower} {snippet_lower}"
        
        # Check for products in order of specificity
        for product, keywords in self.product_keywords.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return product
        
        return "Unknown"

    def run(self, query: str = "latest phone and laptop releases", 
            num_results: int = 5) -> List[Dict]:
        """Main search execution with fallback chain"""
        logger.info(f"Starting search for: {query}")
        logger.info(f"Available methods: {self.available_methods}")
        
        raw_results = []
        last_error = None
        
        # Try each available method in order
        for method in self.available_methods:
            try:
                if method == "serpapi":
                    logger.info("Trying SerpAPI...")
                    raw_results = self.search_serpapi(query, num_results)
                elif method == "duckduckgo":
                    logger.info("Trying DuckDuckGo...")
                    raw_results = self.search_duckduckgo(query, num_results)
                elif method == "direct_search":
                    logger.info("Trying direct search...")
                    raw_results = self.search_direct_web(query, num_results)
                
                if raw_results:
                    logger.info(f"Successfully retrieved {len(raw_results)} results using {method}")
                    break
                    
            except Exception as e:
                last_error = e
                logger.warning(f"{method} failed: {e}")
                continue
        
        if not raw_results:
            logger.error(f"All search methods failed. Last error: {last_error}")
            return []
        
        # Process results in the requested format
        structured_results = []
        for res in raw_results:
            product = self.extract_product_name(res["title"], res["snippet"])
            
            structured_results.append({
                "product": product,
                "update": res["snippet"] or "No summary available.",
                "source": res["link"],
                "date": res.get("date", "") or datetime.now().strftime("%Y-%m-%d")
            })
        
        return structured_results

    def save_results(self, results: List[Dict], filename: str = None) -> str:
        """Save results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_results_{timestamp}.json"
        
        os.makedirs("output", exist_ok=True)
        filepath = os.path.join("output", filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {filepath}")
        return filepath

    def print_results(self, results: List[Dict]):
        """Print results to console in the specified format"""
        print(f"\n{'='*60}")
        print(f"SEARCH RESULTS ({len(results)} items)")
        print(f"{'='*60}")
        
        for i, item in enumerate(results, 1):
            print(f"\n{i}. Product: {item['product']}")
            print(f"   Update: {item['update'][:100]}...")
            print(f"   Source: {item['source']}")
            print(f"   Date: {item['date']}")
            print("-" * 60)

