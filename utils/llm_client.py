from __future__ import annotations
import os
from typing import Optional
import requests
from pathlib import Path

# Manually read .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

from config.model_config import load_config

class GroqClient:
    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None):
        self.app_config = load_config(config_path)
        self.model_cfg = self.app_config.model

        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Please set it in your .env file.")

    def ask(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model_cfg.name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.model_cfg.temperature,
            "top_p": self.model_cfg.top_p,
            "max_tokens": self.model_cfg.max_output_token
        }
        response = requests.post(self.GROQ_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
