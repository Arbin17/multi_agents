import hashlib
from typing import List, Dict, Optional
class Memory:
    def __init__(self):
        self.searched_queries = set()
        self.cached_results = {}
        self.processed_urls = set()
        
    def has_searched(self, query: str) -> bool:
        try:
            query_hash = hashlib.md5(query.lower().encode()).hexdigest()
            return query_hash in self.searched_queries
        except Exception:
            return False
    
    def mark_searched(self, query: str):
        try:
            query_hash = hashlib.md5(query.lower().encode()).hexdigest()
            self.searched_queries.add(query_hash)
        except Exception:
            pass
    
    def cache_result(self, query: str, results: List[Dict]):
        try:
            query_hash = hashlib.md5(query.lower().encode()).hexdigest()
            self.cached_results[query_hash] = results
        except Exception:
            pass
    
    def get_cached_result(self, query: str) -> Optional[List[Dict]]:
        try:
            query_hash = hashlib.md5(query.lower().encode()).hexdigest()
            return self.cached_results.get(query_hash)
        except Exception:
            return None