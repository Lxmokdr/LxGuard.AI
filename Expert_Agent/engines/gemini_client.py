import os
import asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:

    def __init__(self, model: str = "gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found in environment")
            
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def is_available(self) -> bool:
        return os.getenv("GEMINI_API_KEY") is not None

    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.2) -> str:
        # Construct full prompt if system prompt exists
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                    )
                )
                return response.text
            except Exception as e:
                if attempt == 2:
                    raise e
                # Wait before retrying (synchronous sleep since generate is sync)
                import time
                time.sleep(2)
        return ""

    def stream_generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.2):
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            
        for attempt in range(3):
            try:
                response = self.client.models.generate_content_stream(
                    model=self.model,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                    )
                )

                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                return # Exit on success
            except Exception as e:
                if attempt == 2:
                    raise e
                import time
                time.sleep(2)
