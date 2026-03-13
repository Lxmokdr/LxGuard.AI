import os
import argparse
from typing import List, Dict, Any
from utils.doc_processor import DocumentProcessor
from core.ontology_induction import OntologyInductionEngine
from core.llm_refiner import LLMRefiner
from data.kg_manager import KGManager

class OntologyBuilder:
    """
    Orchestrator for the Research-Oriented Ontology Induction Pipeline.
    Flow: Document -> Processor -> Induction -> LLM Refinement -> KG Manager.
    """
    
    def __init__(self, ontology_path: str = "knowledge_base/ontology.ttl", hitl_enabled: bool = False, use_llm_refinement: bool = True):
        print("🏗️  Initializing Advanced Ontology Induction Pipeline...")
        self.processor = DocumentProcessor()
        self.induction_engine = OntologyInductionEngine()
        self.llm_refiner = LLMRefiner() if use_llm_refinement else None
        self.kg_manager = KGManager(output_path=ontology_path)
        self.hitl_enabled = hitl_enabled
        self.use_llm_refinement = use_llm_refinement
        
    def build_from_directory(self, directory_path: str):
        """
        Process all documents in a directory and induce an ontology.
        """
        if not os.path.exists(directory_path):
            print(f"❌ Directory not found: {directory_path}")
            return
            
        print(f"📂 Recursively scanning for knowledge in: {directory_path}")
        
        found_files = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith(('.pdf', '.md', '.txt')):
                    found_files.append(os.path.join(root, file))
        
        if not found_files:
            print("⚠️  No supported files found.")
            return

        for file in found_files:
            self.build_from_file(file)
            
        self.kg_manager.save()
        print("\n✅ Global Knowledge Graph Induction complete.")

    def build_from_file(self, file_path: str):
        """
        Single file induction pipeline with optional LLM refinement and HITL validation.
        """
        print(f"\n📄 Inducing from: {os.path.basename(file_path)}")
        
        # 1. Extraction
        try:
            doc_data = self.processor.process(file_path)
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return
        
        # 2. Induction (NLP-based)
        triples = self.induction_engine.induce(doc_data)
        
        # 3. LLM Refinement
        if self.use_llm_refinement and self.llm_refiner:
            triples = self.llm_refiner.refine(triples, doc_data.get("raw_text", ""))
        
        # 4. Human-in-the-loop (Optional)
        if self.hitl_enabled:
            triples = self._validate_triples_hitl(triples)
            
        # 5. Persistence
        self.kg_manager.add_triples(triples)

    def _validate_triples_hitl(self, triples: List[Any]) -> List[Any]:
        """
        Basic CLI interface for validating extracted triples.
        """
        print("\n📝 --- Human-in-the-loop Validation ---")
        validated = []
        for t in triples:
            print(f"  Proposed: {t.subject} --({t.predicate})--> {t.object}")
            choice = input("  Accept? ([y]/n/skip): ").lower().strip()
            if choice in ('', 'y', 'yes'):
                validated.append(t)
            elif choice == 'skip':
                continue
        return validated

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Induce Ontology from Documents")
    parser.add_argument("input_dir", help="Directory containing documents")
    parser.add_argument("--output", default="knowledge_base/ontology.ttl", help="Output Turtle file")
    parser.add_argument("--hitl", action="store_true", help="Enable Human-in-the-loop validation")
    args = parser.parse_args()
    
    builder = OntologyBuilder(ontology_path=args.output, hitl_enabled=args.hitl)
    builder.build_from_directory(args.input_dir)
