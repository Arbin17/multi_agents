import hashlib

class Memory:
    def __init__(self):
        self.searched_queries = set()
        self.processed_urls = set()
    
    def has_searched(self, query: str) -> bool:
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        return query_hash in self.searched_queries
    
    def mark_searched(self, query: str):
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        self.searched_queries.add(query_hash)