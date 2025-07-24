from agents.search_agent import SearchAgent
from typing import List, Dict
from utils.logger import logger

class VerifyAgent:
    def __init__(self, search_agent: SearchAgent):
        self.search_agent = search_agent

    def verify_results(self, results: List[Dict], top_k: int = 3) -> List[Dict]:
        verified_results = []

        for item in results:
            product_name = item.get("product", "").strip()
            if not product_name:
                logger.warning("Missing product name in item, skipping verification.")
                item["verified"] = False
                verified_results.append(item)
                continue

            try:
                # Construct verification query
                verify_query = f"{product_name} release confirmation"
                second_results = self.search_agent.run(query=verify_query, num_results=top_k)

                # Check for confirmation using relaxed keyword match
                confirmed = any(product_name.lower() in r.get("update", "").lower() for r in second_results)

                item["verified"] = confirmed
                verified_results.append(item)
                logger.info(f"Verified '{product_name}': {confirmed}")
            except Exception as e:
                logger.warning(f"Verification failed for '{product_name}': {e}")
                item["verified"] = False
                verified_results.append(item)

        return verified_results
