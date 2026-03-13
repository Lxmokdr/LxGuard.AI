import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data.ontology_builder import OntologyBuilder

def run_induction():
    print("🚀 Starting Ontology Induction Build...")
    
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs'))
    if not os.path.exists(docs_dir):
        docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs'))
        
    print(f"📂 Scanning directory: {docs_dir}")
    
    # We output to the correct path where the ontology engine expects it
    ontology_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base', 'ontology.ttl')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(ontology_path), exist_ok=True)
    
    builder = OntologyBuilder(ontology_path=ontology_path)
    builder.build_from_directory(docs_dir)
    
    print(f"🎉 Induction Build Complete! Ontology saved at {ontology_path}")

if __name__ == "__main__":
    run_induction()
