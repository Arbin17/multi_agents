from typing import List, Dict
from transformers import pipeline
from utils.logger import logger

class SummarizeAgent:
    def __init__(self):
        try:
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            logger.info("Summarizer (facebook/bart-large-cnn) loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load summarization model: {e}")
            raise

    def summarize_results(self, results: List[Dict]) -> List[Dict]:
        summarized_results = []
        for item in results:
            update = item.get("update", "")
            try:
                if len(update.split()) > 20:
                    summary = self.summarizer(update, max_length=60, min_length=15, do_sample=False)[0]['summary_text']
                else:
                    summary = update
            except Exception as e:
                logger.warning(f"Summarization failed for item: {e}")
                summary = update
            item["summary"] = summary
            summarized_results.append(item)
        return summarized_results
