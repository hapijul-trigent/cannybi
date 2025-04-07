from  src.agents.request_handler import GPTRequestHandler
import json
import logging
from typing import Dict, Any
logger = logging.getLogger(__name__)


class QueryIntentClassifier:
    """Classifies user intent based on system prompt, chat memory, and current user input."""

    def __init__(self, request_handler: GPTRequestHandler):
        self.request_handler = request_handler

    def classify(self, system_prompt: str, context: str, user_input: str, chat_memory: str) -> Dict[str, Any]:
        """
        Classifies user input using prior memory and structured prompt.
        Injects memory into the prompt to allow rephrasing and accurate intent detection.
        """
        user_prompt = (
            f"### MEMORY ###\n{chat_memory.strip()}\n\n"
            f"### DATABASE SCHEMA ###\n{context.strip()}\n\n"
            f"### USER QUESTION ###\n{user_input.strip()}"
        )

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "top_p": 0.95,
            "max_tokens": 1000
        }
        response = self.request_handler.send_request(payload)

        if response:
            try:
                return json.loads(response['choices'][0]['message']['content'][7:-3])
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"IntentClassifier :: Error parsing GPT response: {e}")

        return {"rephrased_question": None, "reasoning": "Error occurred", "results": "MISLEADING_QUERY"}