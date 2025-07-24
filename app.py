import gradio as gr
from agents.search_agent import SearchAgent
from agents.summarizer_agent import SummarizeAgent
from agents.verifier_agent import VerifyAgent

# Initialize agents
search_agent = SearchAgent()
summarize_agent = SummarizeAgent()
verify_agent = VerifyAgent(search_agent)

def run_all(query, num_results, do_summary, do_verify):
    # Step 1: Search
    results = search_agent.run(query=query, num_results=num_results)

    # Step 2: Summarize 
    if do_summary:
        results = summarize_agent.summarize_results(results)

    # Step 3: Verify 
    if do_verify:
        results = verify_agent.verify_results(results)

    # Step 4: Format results
    output_md = ""
    for i, item in enumerate(results, 1):
        output_md += f"### {i}. {item['product']}\n"
        output_md += f"**Update**: {item['update'][:300]}...\n\n"
        if do_summary:
            output_md += f"**Summary**: {item['summary']}\n\n"
        if do_verify:
            output_md += f"**Verified**: {'✅' if item.get('verified') else '❌'}\n\n"
        output_md += f"**Source**: [Link]({item['source']})  \n"
        output_md += f"**Date**: {item['date']}\n"
        output_md += "---\n"
    return output_md if results else "No results found."

iface = gr.Interface(
    fn=run_all,
    inputs=[
        gr.Textbox(label="Search Query", value="latest smartphone and laptop releases"),
        gr.Slider(1, 10, step=1, value=5, label="Number of Results"),
        gr.Checkbox(label="Enable Summarization", value=True),
        gr.Checkbox(label="Enable Verification", value=True)
    ],
    outputs=gr.Markdown(label="Search Results"),
    title="🔍 AI-Powered Product Update Search",
    description="Fetch, summarize, and verify the latest tech product releases.",
)

if __name__ == "__main__":
    iface.launch()
