import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List
from src.agents.request_handler import GPTRequestHandler
from pprint import pprint
logger = logging.getLogger(__name__)



class BusinessIntelligenceAnalyzer:
    """Analyzes SQL query results to generate business insights, visualizations, and recommendations."""

    def __init__(self, request_handler):
        """
        Initializes the BIAnalyzer with an AI request handler.

        Parameters:
        - request_handler: The object responsible for interacting with the AI model.
        """
        self.request_handler = request_handler

    def analyze_results(self, system_prompt: str, sql_query_steps_result: Dict[str, Any], user_question = str) -> Dict[str, Any]:
        """
        Generates business insights, visualization code, and strategic recommendations.

        Parameters:
        - system_prompt (str): The system prompt defining the analysis task.
        - sql_query_steps_result (Dict[str, Any]): SQL query steps including reason, query, and results.

        Returns:
        - Dict[str, Any]: JSON response containing analysis, insights, and Python visualization code.
        """
        from decimal import Decimal

        # Lambda function for recursively converting Decimals to float
        # Lambda function for recursively converting Decimal to float
        convert_decimal_recursive = lambda obj: (
            float(obj) if isinstance(obj, Decimal) else
            [convert_decimal_recursive(i) for i in obj] if isinstance(obj, list) else
            {k: convert_decimal_recursive(v) for k, v in obj.items()} if isinstance(obj, dict) else
            obj
        )
        sql_query_steps = sql_query_steps_result.get("sql_query_steps", [])

        # Convert SQL query results into JSON format for AI processing
        timestamp = time.time()
        current_date = time.strftime("%Y-%m-%d", time.localtime(timestamp))
        try:
           formatted = json.dumps(convert_decimal_recursive(sql_query_steps), indent=4)
        except Exception as e:
            logger.error(f"Error in JSON conversion: {e}")
            formatted = str(sql_query_steps)

        user_prompt = (
            f"User Question:{user_question}\n### SQL QUERY RESULTS ###\n{formatted}"
        )

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'Current Timestamp: {current_date}. {user_prompt}'}
            ],
            "temperature": 0.15,
            "top_p": 0.95,
            "max_tokens": 4000
        }

        response = self.request_handler.send_request(payload)

        if response:
            try:
                parsed_response = json.loads(response['choices'][0]['message']['content'][7:-3])
                if isinstance(parsed_response, dict) and "business_analysis" in parsed_response:
                    return parsed_response  # Ensures valid JSON format
                else:
                    logger.error("BusinessIntelligenceAnalyzer :: Invalid JSON structure received from AI.")
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"BusinessIntelligenceAnalyzer :: Error parsing AI response: {e} :: {response['choices'][0]['message']['content']}")

        return {"sql_query_steps": sql_query_steps, "business_analysis": {"summary": "Error occurred", "recommendations": [], "chart-python-code": ""}}


