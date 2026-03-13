from typing import Dict, Any, Tuple
from core.nlp_core import AdvancedNLPCore

class IntentRouter:
    """
    Traffic Cop for User Queries.
    Decides whether to use:
    - Mode A: Expert Ontology Engine (Domain Specific)
    - Mode B: General LLM Engine (General Knowledge)
    """
    
    def __init__(self):
        print("🚦 Initializing Intent Router...")
        self.nlp = AdvancedNLPCore()
        
    def route(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze query and return (mode, metadata).
        Modes: 'expert', 'llm', 'ambiguous'
        """
        analysis = self.nlp.analyze(query)
        
        # 1. Check for Domain Technical Terms
        technical_term_count = len([k for k in analysis.keywords if k in self.nlp.technical_terms])
        
        # 2. Check Intent Confidence
        top_intent = analysis.intent_hypotheses[0] if analysis.intent_hypotheses else None
        confidence = top_intent['confidence'] if top_intent else 0.0
        intent_name = top_intent['intent'] if top_intent else "General"
        
        # Routing Logic
        
        # STRONG DOMAIN SIGNAL
        if technical_term_count > 0 or (confidence > 0.6 and intent_name != "General"):
            print(f"   -> Routing to EXPERT (Confidence: {confidence}, Tech Terms: {technical_term_count})")
            return "expert", {
                "intent": intent_name,
                "entities": analysis.entities,
                "confidence": confidence
            }
            
        # GENERAL CONVERSATION
        if intent_name == "General" or confidence < 0.4:
            print(f"   -> Routing to LLM (Confidence: {confidence}, Intent: {intent_name})")
            return "llm", {
                "intent": "General",
                "entities": analysis.entities,
                "confidence": confidence
            }
            
        # AMBIGUOUS
        print(f"   -> Routing to AMBIGUOUS (Confidence: {confidence})")
        return "ambiguous", {
            "intent": intent_name,
            "entities": analysis.entities,
            "confidence": confidence
        }

if __name__ == "__main__":
    router = IntentRouter()
    print(router.route("What is Next.js?")) # Expect Expert
    print(router.route("Write a poem."))    # Expect LLM
