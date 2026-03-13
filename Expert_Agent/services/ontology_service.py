from typing import Any

from data.ontology_builder import OntologyBuilder
from engines.ontology_engine import OntologyEngine


def build_ontology(source_dir: str, app_state: Any) -> None:
    """
    Build or refresh the ontology from a source directory and
    update the application's ontology engine and knowledge base.
    """
    builder = OntologyBuilder(ontology_path="knowledge_base/ontology.ttl")
    
    # 1. Clear existing induced knowledge for a fresh build from source directory
    if hasattr(builder.kg_manager, 'clear_graph'):
        builder.kg_manager.clear_graph()
        
    # 2. Build ontology from the source directory
    builder.build_from_directory(source_dir)

    # Replace or initialize the ontology-backed expert engine
    app_state.dual_expert = OntologyEngine(ontology_path="knowledge_base/ontology.ttl")

    # Optionally refresh the in-memory knowledge base if present
    kb = getattr(app_state, "knowledge_base", None)
    if kb and hasattr(kb, "_refresh_documents"):
        kb._refresh_documents()

