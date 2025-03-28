from  src.agents.request_handler import GPTRequestHandler
import json
import logging
from typing import Dict, Any
logger = logging.getLogger(__name__)



class QueryIntentClassifier:
    """Classifies user intent based on a system prompt, context, and user input."""

    def __init__(self, request_handler: GPTRequestHandler):
        self.request_handler = request_handler

    def classify(self, system_prompt: str, context: str, user_input: str) -> Dict[str, Any]:
        """Classifies the user input and returns structured intent information."""
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {context}\nQuestion: {user_input}"}
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