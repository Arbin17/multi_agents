import logging, re, time, requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import List, Optional,Dict
from core.model import ProductUpdate
from core.memory import Memory
class SummarizerAgent:
    """Agent responsible for extracting key information"""
    
    def __init__(self, memory: Memory):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.memory = memory
    
    def fetch_content(self, url: str) -> str:
        """Fetch and clean content from URL"""
        try:
            if self.memory.has_processed_url(url):
                self.logger.info(f"URL already processed: {url}")
                return ""
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return ""
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Extract main content
            content_selectors = [
                'article', '.article-content', '.post-content',
                '.entry-content', 'main', '.content'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text(strip=True)
                    break
            
            if not content:
                content = soup.get_text(strip=True)
            
            # Clean and truncate content
            content = re.sub(r'\s+', ' ', content)[:2000]  # Limit to 2000 chars
            
            self.memory.mark_processed_url(url)
            return content
            
        except Exception as e:
            self.logger.error(f"Error fetching content from {url}: {e}")
            return ""
    
    def extract_product_info(self, content: str, url: str) -> Optional[ProductUpdate]:
        """Extract product information using rule-based approach"""
        try:
            # Product name extraction patterns
            product_patterns = [
                r'(iPhone \d+[^,.\s]*)',
                r'(Galaxy S\d+[^,.\s]*)',
                r'(Pixel \d+[^,.\s]*)',
                r'(MacBook [^,.\s]+)',
                r'(iPad [^,.\s]+)',
                r'(Surface [^,.\s]+)',
                r'(ThinkPad [^,.\s]+)',
                r'(Dell [^,.\s]+)',
                r'(OnePlus [^,.\s]+)',
                r'(Xiaomi [^,.\s]+)'
            ]
            
            product_name = "Unknown Product"
            for pattern in product_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    product_name = match.group(1)
                    break
            
            # Update/feature extraction
            update_keywords = [
                'new feature', 'update', 'released', 'launched', 'announced',
                'specs', 'price', 'availability', 'camera', 'battery',
                'processor', 'display', 'storage'
            ]
            
            sentences = content.split('.')
            relevant_sentences = []
            
            for sentence in sentences[:10]:  # Check first 10 sentences
                if any(keyword in sentence.lower() for keyword in update_keywords):
                    relevant_sentences.append(sentence.strip())
            
            update_summary = '. '.join(relevant_sentences[:3])  # Top 3 relevant sentences
            if not update_summary:
                update_summary = content[:200] + "..." if len(content) > 200 else content
            
            # Date extraction (simple approach)
            date_patterns = [
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{4}-\d{1,2}-\d{1,2})',
                r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
            ]
            
            date_found = "2025-07-23"  # Default to current date
            for pattern in date_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    date_found = match.group(1)
                    break
            
            return ProductUpdate(
                product=product_name,
                update=update_summary,
                source=url,
                date=date_found,
                confidence_score=0.7  # Base confidence
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting product info: {e}")
            return None
    
    def summarize(self, search_results: List[Dict]) -> List[ProductUpdate]:
        """Main summarization method"""
        self.logger.info(f"Summarizing {len(search_results)} sources")
        
        updates = []
        for result in search_results:
            content = self.fetch_content(result['url'])
            if content:
                update = self.extract_product_info(content, result['url'])
                if update:
                    updates.append(update)
                    self.logger.info(f"Extracted update for {update.product}")
            
            time.sleep(1)  # Rate limiting
        
        return updates