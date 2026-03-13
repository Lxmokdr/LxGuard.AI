import requests
import json
import os
from typing import Optional, Dict, Any

class OllamaClient:
    """
    Client for local LLM generation via Ollama.
    Layer 5 (Generative Layer) of the Hybrid Architecture.
    """
    
    def __init__(self, base_url: str = None, model: str = "gemma:2b"):
        # Use env var or default to docker service name
        self.base_url = base_url or os.getenv("OLLAMA_HOST", "http://expert-agent-ollama:11434")
        self.model = model
        print(f"🤖 Ollama Client initialized (Model: {self.model}, URL: {self.base_url})")

    def generate(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """
        Generate text from prompt (Synchronous, non-streaming).
        """
        url = f"{self.base_url}/api/generate"
        
        full_prompt = prompt
        if system_prompt:
             full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_ctx": 4096
            }
        }
        
        try:
            print(f"DEBUG: Ollama Request -> URL: {url}, Model: {self.model}")
            response = requests.post(url, json=payload, timeout=60)
            print(f"DEBUG: Ollama Response -> Status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except Exception as e:
            print(f"⚠️  Ollama Generation Failed: {e}")
            return None

    def stream_generate(self, prompt: str, system_prompt: str = None):
        """
        Generator that yields chunks from Ollama.
        """
        url = f"{self.base_url}/api/generate"
        
        full_prompt = prompt
        if system_prompt:
             full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": 0.3,
                "num_ctx": 4096
            }
        }
        
        try:
            with requests.post(url, json=payload, stream=True, timeout=120) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                        if chunk.get("done"):
                            break
        except Exception as e:
            print(f"⚠️  Ollama Stream Failed: {e}")
            yield f"Error: {str(e)}"

    def is_available(self) -> bool:
        """Check if Ollama is reachable"""
        try:
            requests.get(self.base_url, timeout=2)
            return True
        except:
            return False
