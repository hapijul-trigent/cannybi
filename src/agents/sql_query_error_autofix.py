from openai import AsyncAzureOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel, Field
import asyncio
from typing import ClassVar, Optional

# Azure OpenAI Configuration
GPT_ENDPOINT = "https://genai-trigent-openai.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview"
GPT4V_KEY = "51ba5d46601c477b844d3883af93463c"

# Initialize Azure OpenAI client
client = AsyncAzureOpenAI(
    azure_endpoint=GPT_ENDPOINT,
    api_version="2024-02-15-preview",
    api_key=GPT4V_KEY,
)

# Set up OpenAI model for pydantic-ai
model = OpenAIModel(
    "gpt-4o",
    provider=OpenAIProvider(openai_client=client),
)
agent = Agent(model)


# Define AI model for fixing SQL queries
class SQLFixer(BaseModel):
    """AI-powered SQL fixer."""

    query: str = Field(..., description="The original incorrect SQL query")
    error_message: str = Field(..., description="The error message from database execution")
    fixed_query: Optional[str] = Field(None, description="A corrected version of the SQL query")

    system_message: ClassVar[str] = """
    You are an SQL expert. Given an incorrect SQL query and its error message, fix the query while preserving its intent.
    Ensure the fixed query follows proper SQL syntax and structure.
    """

    model_config = {
        "description": system_message
    }


async def fix_sql_query(query, error_message):
    """
    Uses Azure OpenAI GPT-4o to correct an erroneous SQL query based on the error message.
    
    :param query: The incorrect SQL query.
    :param error_message: The SQL error message.
    :return: The corrected SQL query.
    """
    sql_fixer = await agent.run(SQLFixer(query=query, error_message=error_message))
    
    # Ensure the AI returns a valid fixed_query
    return sql_fixer.fixed_query if sql_fixer.fixed_query else None



# Example Usage
if __name__ == "__main__":
    # Example erroneous SQL query and error message
    erroneous_query = "SELECT * FROM users WHERE id = 1"
    error_message = "ORA-00911: invalid character"

    # Fix the SQL query using Azure OpenAI GPT-4o
    fixed_query = asyncio.run(fix_sql_query(erroneous_query, error_message))
    print(fixed_query)
