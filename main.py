from agents.search_agent import SearchAgent
from agents.summarizer_agent import SummarizeAgent
from agents.verifier_agent import VerifyAgent
from utils.logger import logger

def main():
    try:
        # Initialize agents
        agent = SearchAgent()
        summarize_agent = SummarizeAgent()
        verify_agent = VerifyAgent(agent)

        # Run search
        query = "latest AI and Tech"
        results = agent.run(query=query, num_results=5)

        if results:
            # Step 1: Summarize
            summarized = summarize_agent.summarize_results(results)

            # Step 2: Verify
            verified = verify_agent.verify_results(summarized)

            # Step 3: Print
            agent.print_results(verified)

            # Step 4: Save
            filepath = agent.save_results(verified)
            print(f"\nResults saved to: {filepath}")
        else:
            print("No results found")

    except Exception as e:
        logger.error(f"Search failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 