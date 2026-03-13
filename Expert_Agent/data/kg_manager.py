"""
Knowledge Graph Manager
Responsibilities:
- RDFLib graph construction
- OWL Class and Property induction
- Turtle/RDF serialization
- URI normalization and namespace management
"""

import re
import os
from typing import List, Dict, Any, Optional
from rdflib import Graph, Literal, RDF, RDFS, OWL, URIRef, Namespace
from core.ontology_induction import InductionTriple

# Default Namespace
EX = Namespace("http://expert-agent.ai/ontology/")

class KGManager:
    """
    Manages the formal Knowledge Graph and its ontological structure.
    """
    
    def __init__(self, output_path: str = "knowledge_base/ontology.ttl"):
        self.output_path = output_path
        self.graph = Graph()
        self.graph.bind("ex", EX)
        self.graph.bind("owl", OWL)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # Load existing graph if it exists
        if os.path.exists(self.output_path):
            try:
                self.graph.parse(self.output_path, format="turtle")
                print(f"📖 Loaded existing ontology from {self.output_path}")
            except Exception as e:
                print(f"⚠️  Failed to load existing ontology: {e}")

    def add_triples(self, triples: List[InductionTriple]):
        """
        Convert InductionTriples into RDF and add to the graph.
        """
        for t in triples:
            subj_uri = self._get_uri(t.subject)
            obj_uri = self._get_uri(t.object)
            pred_uri = self._get_predicate_uri(t.predicate)
            
            # 1. Add class assertions (Schema Induction)
            self._induce_classes(t)
            
            # 2. Add the relationship
            self.graph.add((subj_uri, pred_uri, obj_uri))
            
            # 3. Add labels and provenance
            self.graph.add((subj_uri, RDFS.label, Literal(t.subject)))
            self.graph.add((obj_uri, RDFS.label, Literal(t.object)))
            
            if "sent" in t.metadata:
                self.graph.add((subj_uri, EX.derivedFrom, Literal(t.metadata["sent"])))

    def clear_graph(self):
        """
        Wipe all triples from the current graph.
        Useful for fresh rebuilds.
        """
        print("🧹 Clearing all triples from Knowledge Graph...")
        self.graph = Graph()
        self.graph.bind("ex", EX)
        self.graph.bind("owl", OWL)

    def save(self):
        """
        Serialize graph to Turtle.
        """
        self.graph.serialize(destination=self.output_path, format="turtle")
        print(f"💾 Knowledge Graph saved to {self.output_path} ({len(self.graph)} triples)")

    def _get_uri(self, name: str) -> URIRef:
        """Helper to create slug-friendly URIs"""
        slug = re.sub(r'\W+', '_', name.strip()).strip('_')
        return EX[slug]

    def _get_predicate_uri(self, name: str) -> URIRef:
        """Map common predicates to standard OWL/RDF properties or custom ones"""
        name_lower = name.lower()
        if name_lower in ("subclassof", "isa", "type"):
            return RDFS.subClassOf
        if name_lower in ("partof", "haspart"):
            return EX.isPartOf
        
        # Custom predicate
        slug = re.sub(r'\W+', '_', name).strip('_')
        return EX[slug]

    def _induce_classes(self, triple: InductionTriple):
        """
        Identify if subjects/objects should be formal OWL classes or instances.
        Heuristic: Capitalized words are likely Classes.
        """
        subj_uri = self._get_uri(triple.subject)
        obj_uri = self._get_uri(triple.object)
        
        # Assert as Class if it looks like a concept (starts with Uppercase)
        if triple.subject[0].isupper():
            self.graph.add((subj_uri, RDF.type, OWL.Class))
        
        if triple.object[0].isupper():
            self.graph.add((obj_uri, RDF.type, OWL.Class))
            
        # Handle subClassOf hierarchy
        if triple.predicate.lower() in ("subclassof", "isa", "type of"):
            self.graph.add((subj_uri, RDFS.subClassOf, obj_uri))

if __name__ == "__main__":
    # Test
    manager = KGManager("test_ontology.ttl")
    test_triples = [
        InductionTriple("Next.js", "subClassOf", "WebFramework", 0.9, "Arch", {"sent": "Next.js is a framework."}),
        InductionTriple("React", "uses", "VirtualDOM", 0.8, "Arch", {"sent": "React uses the Virtual DOM."})
    ]
    manager.add_triples(test_triples)
    manager.save()
