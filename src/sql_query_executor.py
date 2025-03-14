import os
import pymysql
import json
from dotenv import load_dotenv
from typing import Dict, Any, List
load_dotenv()


class SQLQueryExecutor:
    """Executes generated SQL queries and manages database connections."""

    def __init__(self):
        """
        Initializes the SQLQueryExecutor and establishes a database connection.
        """
        self.db_connection = self._connect_to_database()

    def _connect_to_database(self):
        """
        Establishes a database connection using credentials from environment variables.

        Returns:
        - pymysql.connections.Connection: Active database connection.
        """
        # Database configuration
        db_config = {
            "host": "sql12.freesqldatabase.com",
            "user": "sql12766815",
            "password": "ZvPV8XPsBs",
            "database": "sql12766815",
            "port": int(os.getenv("DB_PORT", 3306)),
            "cursorclass": pymysql.cursors.DictCursor
        }

        # Ensure all required environment variables are set
        required_keys = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME", "DB_PORT"]
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        if missing_keys:
            raise ValueError(f"Missing environment variables: {', '.join(missing_keys)}")

        try:
            return pymysql.connect(**db_config)
        except pymysql.MySQLError as db_err:
            raise ConnectionError(f"Database connection failed: {db_err}")

    def execute_queries(self, sql_query_steps: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Executes SQL queries and returns results along with their reasoning.

        Parameters:
        - sql_query_steps (List[Dict[str, str]]): List of reasoning steps and corresponding SQL queries.

        Returns:
        - Dict[str, Any]: JSON response containing executed query results.
        """
        executed_steps = []

        for step in sql_query_steps:
            reason = step.get("reason", "No reason provided")
            query = step.get("query")

            if not query or query.lower() == "null":
                executed_steps.append({"reason": reason, "query": query, "result": None})
                continue

            try:
                with self.db_connection.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchall()  # Fetch all results
                self.db_connection.commit()

                executed_steps.append({"reason": reason, "query": query, "result": result})

            except Exception as e:
                executed_steps.append({"reason": reason, "query": query, "result": f"Error: {str(e)}"})

        return {"sql_query_steps": executed_steps}

    def close_connection(self):
        """Closes the database connection."""
        if self.db_connection:
            self.db_connection.close()

# Example Usage
if __name__ == "__main__":
    queries = {'sql_query_steps': [{'reason': 'Identify the number of sales orders per city.',
   'query': 'SELECT c.City, COUNT(s.SaleID) AS NumberOfSales FROM Sales s JOIN Customers c ON s.CustomerID = c.CustomerID GROUP BY c.City'},
  {'reason': 'Retrieve the top 3 cities with the highest number of sales orders.',
   'query': 'SELECT City, NumberOfSales FROM (SELECT c.City, COUNT(s.SaleID) AS NumberOfSales FROM Sales s JOIN Customers c ON s.CustomerID = c.CustomerID GROUP BY c.City) AS CitySales ORDER BY NumberOfSales DESC LIMIT 3'}]}

    executor = SQLQueryExecutor()
    result = executor.execute_queries(queries["sql_query_steps"])
    executor.close_connection()

    print(json.dumps(result, indent=4))
