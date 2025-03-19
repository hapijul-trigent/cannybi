import requests
import json
import logging
import pandas as pd
from time import sleep
import time
from typing import Dict, Any, Optional, List
from pprint import pprint
logger = logging.getLogger(__name__)


class GPTRequestHandler:
    """Handles interactions with the GPT API, ensuring retry mechanisms and error handling."""
    
    def __init__(self, api_key: str, endpoint: str, max_retries: int = 2):
        self.api_key = api_key
        self.endpoint = endpoint
        self.max_retries = max_retries

    def send_request(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sends a request to the GPT API and handles retries."""
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries + 1} to get response")
                response = requests.post(self.endpoint, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()
            except (json.JSONDecodeError, KeyError) as e:
                if attempt < self.max_retries:
                    sleep_time = 1.5
                    logger.warning(f"JSONDecodeError: {e}. Retrying in {sleep_time} seconds...")
                    sleep(sleep_time)
                else:
                    logger.error(f"Failed to decode JSON response after {self.max_retries} attempts. Error: {e}")
            except requests.RequestException as e:
                logger.error(f"Request failed. Error: {e}")
                
        logger.error("Unable to get a valid response.")
        return None
