from typing import Dict, Any, Optional, List
from utils.rule_loader import RuleLoader
from engines.lod_client import LODClient
from core.nlp_core import AdvancedNLPCore
from data.knowledge_base import KnowledgeBase
from engines.retrieval_engine import AgentDrivenRetrieval
from agents.expert_agent import ExpertAgent
from engines.ollama_client import OllamaClient


class HybridKnowledgeAgent:
    """
    Refactored NLP Agent replacing the static ontology system.
    Implements a Hybrid Approach: Local Docs (RAG) > Local Ontology > LOD (DBpedia).
    Uses AdvancedNLPCore for mapping user queries to Ontology Concepts (Intents).
    """
    
    def __init__(self):
        print("🚀 Initializing Hybrid Knowledge Agent...")
        # 1. Load Local Ontology
        self.loader = RuleLoader()
        self.local_ontology = self._load_local_ontology()
        
        # 2. Initialize NLP Core (Layer 1)
        self.nlp = AdvancedNLPCore()
        
        # 3. Initialize RAG Components (Layer 4)
        # We initialize components internally to keep the API simple
        print("   Initializing Retrieval Engine (lite mode)...")
        self.expert_agent = ExpertAgent() # Needed for retrieval constraints
        self.kb = KnowledgeBase()
        # No embedder for lightweight operation (keyword-based retrieval only)
        self.retrieval = AgentDrivenRetrieval(self.kb, self.expert_agent, embedder=None)
        
        # 4. Initialize LOD Client (External Knowledge)
        self.lod = LODClient()
        
        # 5. Initialize Generative Layer (LLM)
        self.ollama = OllamaClient()
        
        print(f"✅ Loaded {len(self.local_ontology)} local concepts")
        print("✅ Connected to Linked Open Data (DBpedia)")

    def _load_local_ontology(self) -> Dict[str, Any]:
        """Flatten local ontology for easier lookup"""
        ontology = {}
        # Load from config/ontology.yaml via RuleLoader
        raw_concepts = self.loader.load_ontology()
        for concept in raw_concepts:
            # Map Concepts to Dictionary
            ontology[concept["name"]] = {
                "name": concept["name"],
                "definition": f"Core concept in {concept.get('parent', 'system')}. " 
                              f"Requires: {', '.join(concept.get('requires', []))}. "
                              f"Priority: {concept.get('priority', 5)}",
                "type": "Local Concept",
                "excludes": concept.get("excludes", [])
            }
        return ontology

    def ask(self, query: str, mode: str = "hybrid") -> Dict[str, Any]:
        """
        Main entry point for queries.
        Modes: 'internal', 'external', 'hybrid' (default)
        """
        # 1. NLP Analysis (Identify Intent & Entity)
        analysis = self.nlp.analyze(query)
        
        # Identify Intent (Local Concept)
        intent = None
        if analysis.intent_hypotheses:
            top_hypothesis = analysis.intent_hypotheses[0]
            if top_hypothesis["confidence"] > 0.4: # Only trust confident intents
                intent = top_hypothesis["intent"]
        
        if not intent:
            intent = "General"
                
        # Identify Entity (LOD Subject)
        entity = None
        # Prioritize Technical Terms or Proper Nouns
        technical_terms = [k for k in analysis.keywords if k in self.nlp.technical_terms]
        if technical_terms:
            entity = technical_terms[0] # Take first technical term
        elif analysis.entities:
             entity = list(analysis.entities.values())[0] if analysis.entities else None
        
        # If no entity found via NLP, fallback to keyword extraction
        if not entity:
             entity = self._fallback_entity_extraction(query)

        print(f"\n🔎 Query Analysis (Mode: {mode})")
        print(f"   Intent (Local): {intent}")
        print(f"   Entity (LOD): {entity}")
        
        # 2. Check Local Knowledge (Priority 1)
        local_result = None
        
        # A. Try RAG (Docs) first
        print("   Attempting Retrieval (RAG)...")
        docs, trace, grounding, kg_facts = self.retrieval.retrieve(intent, analysis, max_docs=1)
        
        if docs:
            top_doc = docs[0]
            print(f"   ✅ Found Document: {top_doc['name']} (Score: {top_doc['score']})")
            
            # Format answer from document sections
            content = ""
            if top_doc.get("full_content"):
                # Use FULL content as requested by user
                content = top_doc["full_content"]
            elif top_doc.get("sections"):
                # Use the most relevant section
                section = top_doc["sections"][0]
                content = f"**{section['section']}**: {section['context']}..."
            else:
                # Fallback to description if no sections extracted
                content = top_doc.get("info", {}).get("description", "Refer to documentation.")
                
            local_result = {
                "definition": content,
                "source": f"Local Docs ({top_doc['name']})",
                "documents": docs # precise documents list
            }
        
        # B. Fallback to Ontology Metadata if no docs found
        if not local_result and intent in self.local_ontology:
            print("   ⚠️ No docs found, falling back to Ontology Metadata")
            # Skip "General" as a primary answer if we have an entity for LOD lookup
            if intent == "General" and entity:
                pass # Don't block LOD
            else:
                local_result = self.local_ontology[intent]
        
        # If strict internal mode, return local only
        if mode == "internal":
            if local_result:
                return self._format_response(local_result["definition"], source=local_result.get("source", "Local Ontology"), 
                                             documents=local_result.get("documents", []), intent=intent, entity=entity)
            else:
                return self._format_response(f"No answer found in local ontology for intent '{intent}'.", source="Local Ontology", intent=intent, entity=entity)
        
        # 3. Check LOD (Priority 2 / Enrichment)
        lod_result = None
        if (not local_result) or (mode == "hybrid") or (mode == "external"):
            if entity:
                # Try to fetch from DBpedia
                lod_entity = entity.replace(" ", "_")
                # Normalize common terms for DBpedia
                if lod_entity.lower() == "react": lod_entity = "React_(JavaScript_library)"
                
                lod_abstract = self.lod.get_entity_abstract(lod_entity)
                if lod_abstract:
                    lod_result = {
                        "definition": lod_abstract,
                        "source": "DBpedia (LOD)"
                    }
        
        # 4. Synthesize Answer (Generative or Formatting)
        final_context = ""
        source_label = "System"
        
        # A. Format Knowledge Graph facts if available
        kg_context = ""
        if kg_facts:
            formatted_facts = [f"- {f['subject']} {f['predicate']} {f['object']}" for f in kg_facts]
            kg_context = "**Verified Knowledge Graph Facts**:\n" + "\n".join(formatted_facts) + "\n\n"
            print(f"   📊 Integrated {len(kg_facts)} facts from KG")

        if local_result and lod_result:
            # Hybrid
            local_text = local_result['definition']
            final_context = (
                f"{kg_context}"
                f"**{local_result.get('source', 'Local')}** ({intent}):\n{local_text}\n\n"
                f"**Enriched Context ({entity})**:\n{lod_result['definition'][:500]}... [Source: DBpedia]"
            )
            source_label = "Hybrid (Local + KG + LOD)"
            
        elif local_result:
            # Local + KG
            final_context = f"{kg_context}**{local_result.get('source', 'Local')}** ({intent}):\n{local_result['definition']}"
            source_label = f"{local_result.get('source', 'Local Ontology')} + KG"
            
        elif lod_result and (mode == "external"):
            # LOD Only
            final_context = f"{kg_context}**LOD (DBpedia)**:\n{lod_result['definition']}"
            source_label = "LOD (DBpedia)"
            
        elif lod_result:
            # LOD + KG (Fallback or Hybrid without local)
            final_context = f"{kg_context}**LOD (DBpedia)**:\n{lod_result['definition']}"
            source_label = "LOD (DBpedia) + KG"
            
        else:
            # KG Only or General
            if kg_context:
                final_context = kg_context
                source_label = "Induced Knowledge Graph"
            else:
                final_context = ""
                source_label = "General Knowledge"

        # GENERATIVE STEP (ChatGPT-like)
        if self.ollama.is_available():
            print("   🤖 Generative RAG: Synthesizing answer with Ollama...")
            if not final_context:
                prompt = (
                    f"You are an expert AI assistant. The specific project knowledge does not contain information on this topic.\n"
                    f"Please answer the following question using your general knowledge.\n"
                    f"Be professional, accurate, and direct.\n\n"
                    f"QUESTION: {query}\n\n"
                    f"ANSWER:"
                )
            else:
                prompt = (
                    f"You are an expert AI assistant for a technical project.\n"
                    f"Use the following context to answer the user's question.\n"
                    f"CONTEXT:\n{final_context}\n\n"
                    f"QUESTION: {query}\n\n"
                    f"ANSWER:"
                )
            generated_answer = self.ollama.generate(prompt)
            if generated_answer:
                return self._format_response(
                    generated_answer, 
                    source=f"Generative RAG ({source_label})", 
                    documents=local_result.get("documents", []) if local_result else [], 
                    intent=intent, 
                    entity=entity
                )

        # Fallback to raw text
        return self._format_response(final_context, source=source_label, 
                                     documents=local_result.get("documents", []) if local_result else [], 
                                     intent=intent, entity=entity)

    def _fallback_entity_extraction(self, query: str) -> Optional[str]:
        """Fallback simple keyword extractor"""
        stops = ["what", "is", "a", "an", "the", "explain", "tell", "me", "about", "who", "where", "why", "how", "to"]
        cleaned_query = query.replace("?", "").replace("!", "").replace(".", "")
        terms = [w for w in cleaned_query.split() if w.lower() not in stops]
        return " ".join(terms) if terms else None

    def _format_response(self, answer: str, source: str, documents: List[Dict[str, Any]] = None, 
                         intent: str = None, entity: str = None) -> Dict[str, Any]:
        return {
            "answer": answer,
            "source": source,
            "documents": documents or [],
            "intent": intent,
            "entity": entity,
            "timestamp": "00:00.000" # Mock timestamp
        }

# Example Usage
if __name__ == "__main__":
    agent = HybridKnowledgeAgent()
    
    queries = [
        ("What is Next.js?", "hybrid"),       # Intent: ProjectInitialization -> Should find docs
        ("How to create a project?", "hybrid"), # Intent: ProjectInitialization -> Should find docs
        ("What is React?", "hybrid"),         # Intent: ComponentDevelopment -> Maybe docs, or LOD fallback
        ("Who is Tim Berners-Lee?", "internal") # Intent: General -> No docs -> General fallback
    ]
    
    for q, m in queries:
        print(f"\n{'='*40}")
        print(f"Question: '{q}' (Mode: {m})")
        response = agent.ask(q, mode=m)
        print(f"Source: {response['source']}")
        print(f"Answer: {response['answer'][:100]}...")
        print(f"{'='*40}")
