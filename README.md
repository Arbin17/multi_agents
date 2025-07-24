# AI-Powered News Intelligence Agents

This project is an agentic system designed to extract **reliable product and news** from the web for any given topic. It consists of three modular AI agents that work in sequence to search, summarize, and verify information.
---

# Overview
### 1. **SearchAgent**
- Uses a search API (e.g., SerpAPI),duckduckgo to fetch **top 5 relevant web pages** based on a user-provided topic.
- Supports keyword-based topic queries like:
  - `"iPhone 16 Pro Max release"`
  - `"MacBook Pro M4 benchmark"`

### ✂️ 2. **SummarizeAgent**
- Applies a transformer-based summarization model (`facebook/bart-large-cnn`) to **condense long-form articles**.
- Automatically skips summarizing very short or irrelevant text blocks.

### ✅ 3. **VerifierAgent**
- Filters out **unreliable, outdated, or irrelevant content** using basic fact-checking logic or criteria (e.g., source reputation, date checks).
- Ensures only high-confidence summaries are passed to the final report.

---

## 🛠️ Tech Stack

- Python 
- Hugging Face Transformers (`facebook/bart-large-cnn`)
- Requests / SerpAPI / 
- Logging & Error Handling

```
├── agents/
│   ├── search_agent.py
│   ├── summarize_agent.py
│   └── verifier_agent.py
├── requirements.txt
├── utils/
│   └── logger.py
├── .env
├── .gitignore
└── README.md
```
---
# Steps to Run the Project

### 1. **Clone the repository**
```bash
git clone https://github.com/Arbin17/multi_agents.git
```
### 2. **Set up a Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate
```
### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```
### 4. **Set up Environment Variables**
```bash
cp .env.example .env
```
### 5. **Run the Project**
```bash
python main.py or
python app.py for Gradio
```
### 6. **View Output**
The output will be logged in the `output.log` file in the project directory.
