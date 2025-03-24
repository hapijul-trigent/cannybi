import json
import logging
import time
from typing import Dict, Any, List
from src.agents.request_handler import GPTRequestHandler

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

        # Get current date in YYYY-MM-DD format
        timestamp = time.time()
        current_date = time.strftime("%Y-%m-%d", time.localtime(timestamp))  

        # Generate reasoning text from reasoning steps
        reasoning_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(reasoning_steps)])

        user_prompt = (
            f"### DATABASE SCHEMA ###\n{schema}\n\n"
            f"### QUESTION ###\nUser's Question: {query}\n"
            f"Current Date: {current_date}\nLanguage: {language}\n\n"
            "### REASONING STEPS ###\n"
            "1. Analyze the user’s question and identify relevant database fields.\n"
            "2. Determine if the query requires filtering by time.\n"
            "3. If time-based, extract the current date and calculate the last quarter’s date range:\n"
            "   - Q1 (Jan-Mar) → Last quarter: Q4 (Oct-Dec, previous year)\n"
            "   - Q2 (Apr-Jun) → Last quarter: Q1 (Jan-Mar, same year)\n"
            "   - Q3 (Jul-Sep) → Last quarter: Q2 (Apr-Jun, same year)\n"
            "   - Q4 (Oct-Dec) → Last quarter: Q3 (Jul-Sep, same year)\n"
            "4. Construct the SQL query with the appropriate conditions for filtering, aggregation, and ordering.\n"
            "5. Ensure the query is optimized for performance (e.g., using indexed fields, avoiding unnecessary joins).\n\n"
            f"{reasoning_text}\n"
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
                parsed_response = json.loads(response['choices'][0]['message']['content'][7:-3])
                if isinstance(parsed_response, dict) and "sql_query_steps" in parsed_response:
                    return parsed_response  # Ensures valid JSON format
                else:
                    logger.error("SQLQueryGenerator :: Invalid JSON structure received from GPT.")
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"SQLQueryGenerator :: Error parsing GPT response: {e}")

        return {"stepwise_sql": []}