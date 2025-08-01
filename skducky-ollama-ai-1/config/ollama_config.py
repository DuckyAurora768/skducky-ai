from pydantic import BaseModel

class OllamaConfig(BaseModel):
    api_key: str
    api_url: str = "https://api.ollama.com/v1/generate"
    timeout: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"