import os
from rdflib import Graph, Namespace, RDF, RDFS
from typing import Dict, Any, List, Optional
import re

EX = Namespace("http://example.org/ontology/")

class OntologyEngine:
    """
    MODE A: Secure Expert Engine.
    Queries the local RDF Graph to answer questions.
    No LLM hallucinations permitted here.
    """
    
    def __init__(self, ontology_path: str = "knowledge_base/ontology.ttl"):
        print("🧠 Initializing Ontology Engine (Mode A)...")
        self.ontology_path = ontology_path
        self.graph = Graph()
        self.graph.bind("ex", EX)
        
        if os.path.exists(self.ontology_path):
            try:
                self.graph.parse(self.ontology_path, format="turtle")
                print(f"✅ Loaded {len(self.graph)} triples from {self.ontology_path}")
            except Exception as e:
                print(f"❌ Failed to load ontology: {e}")
        else:
            print(f"⚠️  Ontology file not found at {self.ontology_path}")

    def query(self, user_query: str, entities: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Execute SPARQL query based on input.
        If entities are provided, we use them to anchor the search.
        """
        if not entities:
            return {"answer": "I need to know what entity you are asking about.", "source": "Local Ontology (Empty)"}
            
        # 1. Identify Subject in Ontology (fuzzy match)
        target_subject = None
        target_uri = None
        
        # Try to match extracted entities to graph subjects
        for entity_text in entities.values():
            # Normalized search in graph
            query = """
                SELECT ?s ?label WHERE {
                    ?s rdfs:label ?label .
                }
            """
            results = self.graph.query(query)
            for row in results:
                label = str(row.label).lower()
                if entity_text.lower() in label or label in entity_text.lower():
                    target_subject = str(row.label)
                    target_uri = row.s
                    break
            if target_subject:
                break
                
        if not target_uri:
             return {
                "answer": f"I couldn't find information about '{list(entities.values())[0]}' in the local ontology.",
                "source": "Local Ontology"
            }
            
        # 2. Query for Relations (Facts)
        facts = []
        
        # Outgoing relations
        q_out = f"""
            SELECT ?p ?o ?label WHERE {{
                <{target_uri}> ?p ?o .
                OPTIONAL {{ ?o rdfs:label ?label }}
            }}
        """
        for row in self.graph.query(q_out):
            pred = self._clean_uri(row.p)
            obj = row.label if row.label else self._clean_uri(row.o)
            if pred != "type" and pred != "label" and pred != "mentionedIn":
                facts.append(f"{target_subject} {pred} {obj}.")
                
        # Incoming relations
        q_in = f"""
            SELECT ?s ?p ?label WHERE {{
                ?s ?p <{target_uri}> .
                OPTIONAL {{ ?s rdfs:label ?label }}
            }}
        """
        for row in self.graph.query(q_in):
            subj = row.label if row.label else self._clean_uri(row.s)
            pred = self._clean_uri(row.p)
            if pred != "mentionedIn":
                facts.append(f"{subj} {pred} {target_subject}.")
        
        if not facts:
             return {
                "answer": f"I know '{target_subject}' exists, but I have no specific facts about it yet.",
                "source": "Local Ontology"
            }
            
        return {
            "answer": " ".join(facts),
            "source": "Local Ontology",
            "debug_triples": facts
        }

    def _clean_uri(self, uri) -> str:
        """Extract local name from URI"""
        if isinstance(uri, str) and "#" in uri:
            return uri.split("#")[-1]
        elif isinstance(uri, str):
             # Handle slash namespaces
             return uri.split("/")[-1].replace("_", " ")
        return str(uri)

if __name__ == "__main__":
    # Test
    engine = OntologyEngine("test_kb/ontology.ttl") # Use test KB if available
    if len(engine.graph) == 0:
        print("Empty graph, cannot test.")
    else:
        print(engine.query("What does Next.js use?", {"entity": "Next.js"}))
