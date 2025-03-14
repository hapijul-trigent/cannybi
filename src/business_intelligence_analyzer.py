import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List
from src.request_handler import GPTRequestHandler

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

    def analyze_results(self, system_prompt: str, sql_query_steps_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates business insights, visualization code, and strategic recommendations.

        Parameters:
        - system_prompt (str): The system prompt defining the analysis task.
        - sql_query_steps_result (Dict[str, Any]): SQL query steps including reason, query, and results.

        Returns:
        - Dict[str, Any]: JSON response containing analysis, insights, and Python visualization code.
        """
        sql_query_steps = sql_query_steps_result.get("sql_query_steps", [])

        # Convert SQL query results into JSON format for AI processing
        # formatted_queries = json.dumps(sql_query_steps, indent=4)

        user_prompt = (
            f"### SQL QUERY RESULTS ###\n{sql_query_steps}\n\n"
            "Analyze the results as a Business Intelligence (BI) expert.\n"
            "- Provide key business insights.\n"
            "- Summarize findings across all SQL queries.\n"
            "- Suggest strategic recommendations for business improvement.\n"
            "- Generate Python visualization code using seaborn & matplotlib, and save inside chart folder with name chart.png.\n"
            "Return output as structured JSON in the format:\n"
            "{\n"
            '    "sql_query_steps": [...],\n'
            '    "business_analysis": {\n'
            '        "summary": "<Overall BI interpretation>",\n'
            '        "recommendations": ["<Recommendation 1>", "<Recommendation 2>", "<Recommendation 3>"],\n'
            '        "chart-python-code": "<Seaborn & Matplotlib Python Code>"\n'
            "    }\n"
            "}"
        )

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'Current Timestamp: {datetime.now()}. {user_prompt}'}
            ],
            "temperature": 0.3,
            "top_p": 0.95,
            "max_tokens": 4000
        }

        response = self.request_handler.send_request(payload)

        if response:
            try:
                print(response['choices'][0]['message']['content'])

                parsed_response = json.loads(response['choices'][0]['message']['content'][7:-3])
                if isinstance(parsed_response, dict) and "business_analysis" in parsed_response:
                    return parsed_response  # Ensures valid JSON format
                else:
                    logger.error("Invalid JSON structure received from AI.")
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error parsing AI response: {e}")

        return {"sql_query_steps": sql_query_steps, "business_analysis": {"summary": "Error occurred", "recommendations": [], "chart-python-code": ""}}


