import json
import logging
import time
from typing import Dict, Any, List
from src.request_handler import GPTRequestHandler

logger = logging.getLogger(__name__)


class SQLQueryGenerator:
    """Generates SQL queries in a single GPT request based on user input, database schema, and reasoning steps."""

    def __init__(self, request_handler):
        """
        Initializes the SQLQueryGenerator with a request handler.

        Parameters:
        - request_handler (GPTRequestHandler): The object responsible for interacting with the GPT API.
        """
        self.request_handler = request_handler

    def generate_queries(
        self, system_prompt: str, schema: str, query: str, reasoning_steps: List[str], current_time: str, language: str
    ) -> Dict[str, Any]:
        """
        Generates SQL queries for all reasoning steps in one GPT request and ensures a valid JSON response.

        Parameters:
        - system_prompt (str): The system prompt defining the SQL generation task.
        - schema (str): The database schema defining available tables and columns.
        - query (str): The user's question.
        - reasoning_steps (List[str]): Step-by-step reasoning steps.
        - current_time (str): The current timestamp for handling time-based queries.
        - language (str): The language of the query.

        Returns:
        - Dict[str, Any]: JSON response containing all SQL queries mapped to reasoning steps.
        """
        reasoning_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(reasoning_steps)])

        user_prompt = (
            f"### DATABASE SCHEMA ###\n{schema}\n\n"
            f"### QUESTION ###\nUser's Question: {query}\n"
            f"Current Time: {current_time}\nLanguage: {language}\n\n"
            f"### REASONING STEPS ###\n{reasoning_text}\n\n"
        )

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "top_p": 0.95,
            "max_tokens": 2000
        }

        response = self.request_handler.send_request(payload)

        if response:
            try:
                parsed_response = json.loads(response['choices'][0]['message']['content'][7:-3])
                if isinstance(parsed_response, dict) and "sql_query_steps" in parsed_response:
                    return parsed_response  # Ensures valid JSON format
                else:
                    logger.error("SQLQueryGenerator :: Invalid JSON structure received from GPT.")
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"SQLQueryGenerator :: Error parsing GPT response: {e}")

        return {"stepwise_sql": []}