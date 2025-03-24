import json, time
import logging
import time
from typing import Dict, Any
from src.agents.request_handler import GPTRequestHandler

logger = logging.getLogger(__name__)


class SQLQueryReasoningGenerator:
    """Generates step-by-step reasoning for SQL query formulation based on user input and database schema."""

    def __init__(self, request_handler: GPTRequestHandler):
        self.request_handler = request_handler

    def generate_reasoning(self, system_prompt: str, schema: str, query: str, language: str) -> Dict[str, Any]:
        """Generates structured reasoning for answering SQL-related questions."""

        timestamp = time.time()
        current_date = time.strftime("%Y-%m-%d", time.localtime(timestamp))  # Format as YYYY-MM-DD

        user_prompt = (
            f"### DATABASE SCHEMA ###\n{schema}\n\n"
            f"### QUESTION ###\nUser's Question: {query}\n"
            f"Current Date: {current_date}\nLanguage: {language}\n\n"
        )

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.15,
            "top_p": 0.95,
            "max_tokens": 2000
        }


        response = self.request_handler.send_request(payload)

        if response:
            try:
                return json.loads(response['choices'][0]['message']['content'][7:-3])
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"SQLQueryReasoningGenerator :: Error parsing GPT response: {e}")

        return {"reasoning_plan": "Error occurred"}