from typing import Dict, Any
from core.llm_factory import get_llm

class LLMEngine:
    """
    MODE B: General LLM Engine.
    Uses the configured LLM provider (Gemini or Ollama) based on LLM_PROVIDER env var.
    """
    
    def __init__(self):
        print("🤖 Initializing LLM Engine (Mode B)...")
        self.client = get_llm()
        
    def query(self, user_query: str, context: str = "") -> Dict[str, Any]:
        """
        Ask the LLM.
        """
        if not self.client.is_available():
            return {
                "answer": "⚠️ Local LLM is not available. Please ensure Ollama is running.",
                "source": "System Error"
            }
            
        system_prompt = (
            "You are a helpful AI assistant. "
            "Answer the user's question clearly and concisely. "
            "If the question is about specific internal domain rules, advise the user to use Expert Mode."
        )
        
        full_prompt = user_query
        if context:
            full_prompt = f"Context:\n{context}\n\nQuestion: {user_query}"
            
        response = self.client.generate(full_prompt, system_prompt=system_prompt)
        
        return {
            "answer": response,
            "source": "Local LLM"
        }

if __name__ == "__main__":
    engine = LLMEngine()
    print(engine.query("Why is the sky blue?"))
