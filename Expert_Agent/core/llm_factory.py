import os

from engines.gemini_client import GeminiClient
from engines.ollama_client import OllamaClient


def get_llm(model: str = None):
    provider = os.getenv("LLM_PROVIDER", "gemini")

    if provider == "gemini":
        if model:
            return GeminiClient(model=model)
        return GeminiClient()

    elif provider == "ollama":
        if model:
            return OllamaClient(model=model)
        return OllamaClient()

    else:
        raise ValueError(f"Unsupported provider: {provider}")
