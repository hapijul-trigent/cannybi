import json
import logging
from typing import Dict, Any, List
from textwrap import dedent
from src.agents.request_handler import GPTRequestHandler

logger = logging.getLogger(__name__)

class SQLQueryAutoFixer:
    """Automatically fixes SQL query errors by analyzing the database schema, user question, and error messages."""

    def __init__(self, request_handler, database_schema: str):
        """
        Initializes the SQLQueryAutoFixer.

        Parameters:
        - request_handler: AI request handler for generating corrected queries.
        - database_schema (str): The database schema used to correct queries.
        """
        self.request_handler = request_handler
        self.database_schema = database_schema

    def fix_sql_errors(self, user_question: str, failed_queries: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Fixes SQL query errors and returns corrected SQL queries with optimized fixes.

        Parameters:
        - user_question (str): The user's original question.
        - failed_queries (List[Dict[str, str]]): List of failed queries, including errors.

        Returns:
        - List[Dict[str, Any]]: Updated queries with optimized fixed queries.
        """
        system_prompt = dedent(f"""
            ### TASK ###
            Given a **database schema**, **user's question**, and **failed SQL queries with error messages**, 
            generate **optimized MySQL-compatible SQL queries**.

            ### INSTRUCTIONS ###
            1. **Analyze the user question and schema** to understand the intended query purpose.
            2. **Fix SQL syntax and logical errors** while maintaining query intent.
            3. **Use `JOIN` instead of `IN` with subqueries whenever possible** for efficiency.
            4. **Avoid `LIMIT` inside `IN/ALL/ANY/SOME` subqueries**, replacing it with derived tables or `JOIN`.
            5. **Ensure optimized performance using indexes in `JOIN` and `WHERE` clauses.**
            6. **Return the corrected queries in structured JSON format.**

            ### DATABASE SCHEMA ###
            {self.database_schema}

            ### OUTPUT FORMAT (Valid JSON) ###
            ```json
            [
                {{"reason": "<What the query is trying to answer>", "query": "<Fixed and Optimized SQL Query>"}},
                ...
            ]
            ```
        """)

        user_prompt = dedent(f"""
            **❓ User Question:** _{user_question}_

            **🚨 Failed Queries & Errors:**
            {json.dumps(failed_queries, indent=4)}

            Fix and optimize the queries while ensuring the "reason" field explains the query's intent.
        """)

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "top_p": 0.9,
            "max_tokens": 1500
        }

        response = self.request_handler.send_request(payload)

        if response:
            try:
                fixed_queries = json.loads(response['choices'][0]['message']['content'][7:-3])
                if isinstance(fixed_queries, list):
                    return fixed_queries  # Ensure valid JSON structure
                else:
                    logger.error("Invalid JSON structure received from AI.")
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error parsing AI response: {e}")

        # Return original queries with empty fixed_query if AI fails
        return [{**query, "fixed_query": None} for query in failed_queries]

# Example Usage
if __name__ == "__main__":
    API_KEY = ""
    ENDPOINT = ""

    request_handler = GPTRequestHandler(api_key=API_KEY, endpoint=ENDPOINT)  # Assume this exists
    database_schema = "Tables: Customers, Sales, Transactions. Fields: CustomerID, TotalSales, Date."

    fixer = SQLQueryAutoFixer(request_handler, database_schema)

    failed_queries = [
        {
            "reason": "Retrieve all customer details for the top 5 customers based on total sales.",
            "query": "SELECT * FROM Customers WHERE CustomerID IN (SELECT CustomerID FROM Sales ORDER BY TotalSales LIMIT 5);",
            "result": "Error: This version of MySQL doesn't support 'LIMIT & IN/ALL/ANY/SOME subquery'."
        }
    ]

    result = fixer.fix_sql_errors("Get the top 5 customers by total sales.", failed_queries)
    print(json.dumps(result, indent=4))
