"""
LLM-Assisted Ontology Refiner
Responsibilities:
- Prune noisy or redundant S-P-O triples.
- Identify missing hierarchical or semantic links.
- Contextual validation of extracted knowledge.
"""

import json
from typing import List, Dict, Any
from core.ontology_induction import InductionTriple
from engines.ollama_client import OllamaClient

class LLMRefiner:
    """
    Refines induced triples using a local LLM (Ollama).
    """

    def __init__(self, model_name: str = "gemma:2b"):
        self.client = OllamaClient(model=model_name)
        
    def refine(self, triples: List[InductionTriple], context: str) -> List[InductionTriple]:
        """
        Send triples to LLM for pruning and refinement.
        """
        if not triples:
            return []

        print(f"🪄  Refining {len(triples)} triples with LLM...")
        
        # Prepare triples for the prompt
        triples_data = [
            {"s": t.subject, "p": t.predicate, "o": t.object}
            for t in triples
        ]

        prompt = f"""You are an Ontology Expert. 
Below are S-P-O triples extracted from a technical document. 
Some might be noisy, redundant, or incomplete.

CONTEXT HIGHLIGHTS:
{context[:2000]}

EXTRACTED TRIPLES:
{json.dumps(triples_data, indent=2)}

TASK:
1. Remove noisy or incorrect triples.
2. Normalize predicates to formal terms (subClassOf, isPartOf, requires, etc).
3. Identify 2-3 missing critical triples that represent core concepts.
4. Return ONLY a JSON list of refined triples in the same format: [{{"s": "...", "p": "...", "o": "..."}}]

Refined JSON:"""

        response = self.client.generate(prompt)
        if not response:
            print("⚠️  LLM Refinement failed (no response). Returning raw triples.")
            return triples

        try:
            # Try to extract JSON from response (sometimes LLMs wrap it in markdown)
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            refined_data = json.loads(json_str)
            
            # Map back to InductionTriple objects
            refined_triples = []
            for item in refined_data:
                refined_triples.append(InductionTriple(
                    subject=item.get("s", ""),
                    predicate=item.get("p", ""),
                    object=item.get("o", ""),
                    confidence=0.95,
                    source_section="LLM Refinement",
                    metadata={"refined": True}
                ))
            
            print(f"✨ LLM Refinement complete: {len(refined_triples)} triples.")
            return refined_triples

        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  LLM Refinement failed to parse JSON: {e}")
            return triples
