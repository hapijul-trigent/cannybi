import json
import logging
from typing import Dict, Any
from textwrap import dedent
from src.agents.request_handler import GPTRequestHandler
from src.agents.prompts import SYTEM_PROMPT_MISLEADING_QUERY_SUGGESTION

logger = logging.getLogger(__name__)

class MisleadingQueryHandler:
    """Handles MISLEADING_QUERY cases and suggests rephrased questions based on the database schema."""

    def __init__(self, request_handler, system_prompt: str):
        """
        Initializes the MisleadingQueryHandler.

        Parameters:
        - request_handler: AI request handler for generating rephrased questions.
        - database_schema (str): The database schema to suggest insightful questions.
        """
        self.request_handler = request_handler
        self.system_prompt = system_prompt

    def suggest_better_questions(self, reasoning: str, user_question: str) -> str:
        """
        Suggests 3 schema-aligned questions formatted in markdown for chat response.

        Parameters:
        - reasoning (str): Explanation of why the original question is misleading.
        - user_question (str): The user's original question.

        Returns:
        - str: Markdown-formatted response with improved questions.
        """

        user_prompt = dedent(f"""
            **❌ Original Question:** _{user_question}_

            **🔍 Why It’s Misleading:**  
            {reasoning}

            Suggest 3 schema-aligned questions that can be answered with the available database.
        """)

        payload = {
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.5,
            "top_p": 0.9,
            "max_tokens": 500
        }

        response = self.request_handler.send_request(payload)
        print(response['choices'][0]['message']['content'])
        if response:
            try:
                return response['choices'][0]['message']['content']  # Markdown-formatted response
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error parsing AI response: {e}")

        return "**❌ Error:** Failed to generate better questions."

# Example Usage
if __name__ == "__main__":
    API_KEY = "your-api-key"
    ENDPOINT = "https://genai-trigent-openai.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview"

    request_handler = GPTRequestHandler(api_key=API_KEY, endpoint=ENDPOINT)  # Assume this exists
    database_schema = "Tables: Customers, Sales, Transactions. Fields: CustomerID, TotalSales, Date."

    handler = MisleadingQueryHandler(request_handler, database_schema)

    misleading_input = {
        "reasoning": "The question requires external data (CAC), making it not directly answerable from the database.",
        "rephrased_question": "Calculate the customer lifetime value (CLV) for the top 5 cities by total sales amount. "
                              "How does it correlate with customer acquisition costs (CAC)?",
        "results": "MISLEADING_QUERY"
    }

    result = handler.suggest_better_questions(misleading_input["reasoning"], misleading_input["rephrased_question"])
    print(result)
