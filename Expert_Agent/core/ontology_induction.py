"""
Ontology Induction Engine
Responsibilities:
- Named Entity Recognition (NER)
- Knowledge Extraction (S-P-O triples)
- Concept mapping and normalization
- LLM-assisted semantic refinement
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import spacy

@dataclass
class InductionTriple:
    subject: str
    predicate: str
    object: str
    confidence: float
    source_section: str
    metadata: Dict[str, Any]

class OntologyInductionEngine:
    """
    Inductive NLP module that discovers concepts and relationships from text.
    """
    
    def __init__(self, nlp_model: str = "en_core_web_sm"):
        print(f"🧠 Initializing Ontology Induction Engine ({nlp_model})...")
        try:
            self.nlp = spacy.load(nlp_model)
        except OSError:
            print(f"⚠️  NLP model {nlp_model} not found, using basic extraction.")
            self.nlp = None
            
        # Common domain-specific predicates to normalize to
        self.predicate_normalization = {
            "is a": "subClassOf",
            "type of": "subClassOf",
            "part of": "isPartOf",
            "uses": "requires",
            "needs": "requires",
            "depends on": "dependsOn",
            "implements": "implements",
            "extends": "subClassOf"
        }
        
    def induce(self, document_data: Dict[str, Any]) -> List[InductionTriple]:
        """
        Perform induction on a processed document structure.
        """
        all_triples = []
        
        for section in document_data.get("sections", []):
            title = section.get("title", "Unknown")
            content = section.get("content", "")
            
            if not content.strip():
                continue
                
            # 1. NLP Extraction (S-P-O)
            section_triples = self._extract_from_text(content, title)
            all_triples.extend(section_triples)
            
        # 2. Refinement & Normalization
        refined_triples = self._refine_triples(all_triples)
        
        print(f"✅ Induction complete: {len(refined_triples)} triples induced.")
        return refined_triples

    def _extract_from_text(self, text: str, section_name: str) -> List[InductionTriple]:
        """
        Heuristic-based extraction using dependency parsing.
        """
        if not self.nlp:
            return []
            
        doc = self.nlp(text)
        triples = []
        
        for sent in doc.sents:
            # Look for S-V-O patterns
            subj = ""
            pred = ""
            obj = ""
            
            for token in sent:
                # Subject discovery
                if token.dep_ in ("nsubj", "nsubjpass") and not subj:
                    subj = self._expand_node(token)
                
                # Predicate discovery (ROOT verb or ADP links)
                if token.dep_ == "ROOT" and token.pos_ in ("VERB", "AUX"):
                    pred = token.lemma_
                
                # Object discovery
                if token.dep_ in ("dobj", "pobj", "attr") and not obj:
                    obj = self._expand_node(token)
                    
            if subj and pred and obj:
                triples.append(InductionTriple(
                    subject=subj,
                    predicate=pred,
                    object=obj,
                    confidence=0.7,
                    source_section=section_name,
                    metadata={"sent": sent.text}
                ))
                
        return triples

    def _expand_node(self, token) -> str:
        """
        Expand a token to its full noun phrase/compound.
        """
        parts = [t.text for t in token.subtree if t.dep_ in ("compound", "amod", "flat")]
        parts.append(token.text)
        return " ".join(parts).strip()

    def _refine_triples(self, triples: List[InductionTriple]) -> List[InductionTriple]:
        """
        Normalize predicates and remove duplicates.
        """
        refined = []
        seen = set()
        
        for t in triples:
            # Normalize predicate
            norm_pred = self.predicate_normalization.get(t.predicate.lower(), t.predicate)
            
            # Key for deduplication
            key = (t.subject.lower(), norm_pred.lower(), t.object.lower())
            if key not in seen and t.subject.lower() != t.object.lower():
                t.predicate = norm_pred
                refined.append(t)
                seen.add(key)
                
        return refined

if __name__ == "__main__":
    # Test induction
    engine = OntologyInductionEngine()
    test_text = {
        "sections": [
            {
                "title": "Architecture",
                "content": "Next.js is a React framework. It requires Node.js to run. The frontend depends on the API layer."
            }
        ]
    }
    triples = engine.induce(test_text)
    for t in triples:
        print(f"Triple: {t.subject} --({t.predicate})--> {t.object}")
