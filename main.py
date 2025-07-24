# main.py (SearchAgent only)

from datetime import datetime
import os
import json

from agents.search_agent import SearchAgent
from core.memory import Memory

def main():
    memory = Memory()
    search_agent = SearchAgent(memory)

    topics = [
        "iPhone",
        "Samsung Galaxy",
        "MacBook "
    ]

    for topic in topics:
        print(f"\n🔍 Searching: {topic}")
        results = search_agent.search(topic)

        if results:
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = topic.replace(" ", "_").lower()
            os.makedirs("reports", exist_ok=True)

            json_path = f"reports/search_{safe_topic}_{timestamp}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print(f"✅ {len(results)} results saved to {json_path}")
        else:
            print("⚠️  No results found.")

if __name__ == "__main__":
    main()
