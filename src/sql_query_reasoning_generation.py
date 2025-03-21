import json, time
import logging
import time
from typing import Dict, Any
from src.request_handler import GPTRequestHandler

logger = logging.getLogger(__name__)


class SQLQueryReasoningGenerator:
    """Generates step-by-step reasoning for SQL query formulation based on user input and database schema."""

    def __init__(self, request_handler: GPTRequestHandler):
        self.request_handler = request_handler

    def generate_reasoning(self, system_prompt: str, schema: str, query: str, language: str) -> Dict[str, Any]:
        """Generates structured reasoning for answering SQL-related questions."""
        user_prompt = (
            f"### DATABASE SCHEMA ###\n{schema}\n\n"
            f"### QUESTION ###\nUser's Question: {query}\n"
            f"Current Time: {time.time()}\nLanguage: {language}\n\n"
            "Think step by step and provide a structured reasoning plan."
        )
        timestamp = time.time()
        print(timestamp) 
        current_time = f"Current Timestamp: {timestamp}"
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": current_time + user_prompt}
            ],
            "temperature": 0.3,
            "top_p": 0.95,
            "max_tokens": 1000
        }

        response = self.request_handler.send_request(payload)

        if response:
            try:
                return json.loads(response['choices'][0]['message']['content'][7:-3])
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error parsing GPT response: {e}")

        return {"reasoning_plan": "Error occurred"}