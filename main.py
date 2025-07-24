# main.py (SearchAgent only)

from datetime import datetime
import os
import json

from agents.search_agent import SearchAgent
from core.memory import Memory

def main():
    memory = Memory()
    search_agent = SearchAgent(memory)
    
    # Test searches
    test_topics = [
        "iPhone 16 Pro Max",
        "Samsung Galaxy S25 Ultra",
        "MacBook Pro M4 2025",
        "Google Pixel 9 Pro"
    ]
    
    for topic in test_topics:
        print(f"\n{'='*60}")
        print(f"Searching for: {topic}")
        print(f"{'='*60}")
        
        results = search_agent.search(topic, max_results=10)
        
        print(f"Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   Domain: {result['domain']} (Score: {result['priority_score']})")
            print(f"   URL: {result['url']}")
            print(f"   Snippet: {result['snippet'][:100]}...")
            print()
        
        # Show search stats
        stats = search_agent.get_search_stats()
        print(f"Search Stats: {stats}")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
