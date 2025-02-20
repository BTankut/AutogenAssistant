import requests
import time
from typing import Dict, Any

class OpenRouterAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def generate_completion(self, 
                          model: str, 
                          messages: list, 
                          temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate completion using OpenRouter API
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        start_time = time.time()
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            completion_time = time.time() - start_time
            
            result = response.json()
            return {
                "success": True,
                "response": result["choices"][0]["message"]["content"],
                "tokens": result["usage"]["total_tokens"],
                "time": completion_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_models(self) -> Dict[str, Any]:
        """
        Get available models from OpenRouter
        """
        url = f"{self.base_url}/models"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return {
                "success": True,
                "models": response.json()["data"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
