from typing import Any, Dict
import requests

class OllamaClient:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    def generate_skript_code(self, prompt: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt,
            "model": "skript-model"  # Specify the model to use
        }
        
        response = requests.post(self.api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Failed to generate code: {response.status_code}",
                "message": response.text
            }