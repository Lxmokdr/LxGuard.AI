"""
Agent-Driven Retrieval Engine - Layer 4 of Hybrid Architecture
Responsibilities:
- Two-tier retrieval: Symbolic filtering + Semantic ranking
- Agent-controlled document eligibility
- Retrieval explainability

TIER 1: Symbolic Filter (Expert Agent decides what CAN be retrieved)
TIER 2: Semantic Retrieval (NLP ranks within allowed set)

This guarantees: Precision, Determinism, Explainability
"""

import os
import re
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from functools import lru_cache
from sklearn.metrics.pairwise import cosine_similarity
from data.database import SessionLocal
from api.models import Document, DocumentChunk
from sqlalchemy import text
from utils.evidence_scorer import EvidenceScorer, GroundingReport


class AgentDrivenRetrieval:
    """
    Two-Tier Retrieval System:
    - Expert Agent controls WHAT documents are eligible
    - NLP/Embeddings control HOW to rank them
    """
    
    def __init__(self, knowledge_base, expert_agent, embedder=None, min_coverage_threshold=0.6, domain_id: str = None, tenant_id: str = None):
        self.kb = knowledge_base
        self.expert = expert_agent
        self.embedder = embedder
        self.domain_id = domain_id
        self.tenant_id = tenant_id
        
        # Get base path for document reading from KB auto-discovery
        self.base_path = self.kb.auto_discovery.base_path if (hasattr(self.kb, 'auto_discovery') and self.kb.auto_discovery) else ""
        
        # Initialize evidence scorer
        self.evidence_scorer = EvidenceScorer(
            min_coverage_threshold=min_coverage_threshold
        )
        
        print(f"🔍 Agent-Driven Retrieval Engine (Domain: {domain_id}) initialized with pgvector support")
    
    def retrieve(self, intent: str, nlp_analysis, max_docs: int = 3, user=None) -> Tuple[List[Dict], Dict, Optional[GroundingReport], List[Dict]]:
        """
        Main retrieval method with two tiers + evidence grounding + KG facts.
        Returns: (ranked_documents, retrieval_trace, grounding_report, kg_facts)
        """
        # Get defaults from expert
        doc_constraints = self.expert.get_eligible_documents(intent, user)
        return self.retrieve_with_constraints(intent, nlp_analysis, doc_constraints, max_docs)

    def retrieve_with_constraints(self, intent: str, nlp_analysis, doc_constraints: Dict, max_docs: int = 3) -> Tuple[List[Dict], Dict, Optional[GroundingReport], List[Dict]]:
        """
        Retrieval with pre-calculated constraints (e.g. from RBAC).
        Enhanced with evidence scoring, grounding enforcement, and KG facts.
        """
        trace = {
            "tier1_symbolic": {},
            "tier2_semantic": {},
            "tier3_evidence_scoring": {},
            "tier4_graph": {},
            "grounding_assessment": {},
            "final_selection": []
        }
        
        # TIER 1: Symbolic Filtering
        eligible_docs, tier1_trace = self._tier1_symbolic_filter(intent, nlp_analysis, doc_constraints)
        trace["tier1_symbolic"] = tier1_trace
        
        # TIER 4: Graph Retrieval (Induced Knowledge)
        kg_facts = self.expert.query_knowledge_graph(nlp_analysis.keywords)
        trace["tier4_graph"] = {"fact_count": len(kg_facts) if kg_facts else 0, "facts": kg_facts}

        print(f"DEBUG: [Layer 4] Intent: {intent} | Eligible after Tier 1: {len(eligible_docs)}")

        if not eligible_docs:
            grounding = self.evidence_scorer.assess_grounding([], nlp_analysis.query, min_documents=1)
            trace["grounding_assessment"] = {"sufficient": False, "reason": "No eligible documents"}
            return [], trace, grounding, kg_facts
        
        # TIER 2: Semantic Ranking
        ranked_docs, tier2_trace = self._tier2_semantic_ranking(
            eligible_docs, 
            nlp_analysis, 
            max_docs,
            required_docs=trace["tier1_symbolic"]["required_docs"]
        )
        trace["tier2_semantic"] = tier2_trace
        
        # TIER 3: Evidence Scoring (NEW)
        scored_docs, evidence_trace = self._tier3_evidence_scoring(
            ranked_docs,
            nlp_analysis,
            doc_constraints
        )
        trace["tier3_evidence_scoring"] = evidence_trace
        
        # Grounding Assessment
        grounding_report = self.evidence_scorer.assess_grounding(
            scored_docs,
            nlp_analysis.query,
            min_documents=1
        )
        trace["grounding_assessment"] = {
            "sufficient": grounding_report.sufficient,
            "coverage": grounding_report.total_coverage,
            "threshold": grounding_report.min_threshold,
            "gaps": grounding_report.gaps,
            "recommendation": grounding_report.recommendation
        }
        
        # Extract sections from top documents
        final_docs = self._extract_sections(ranked_docs, nlp_analysis)
        trace["final_selection"] = [doc["name"] for doc in final_docs]
        
        return final_docs, trace, grounding_report, kg_facts
    
    def _tier1_symbolic_filter(self, intent: str, nlp_analysis, doc_constraints: Dict) -> Tuple[List[str], Dict]:
        """
        TIER 1: Symbolic filtering based on expert agent rules.
        This is deterministic and rule-based.
        """
        trace = {
            "intent": intent,
            "required_docs": [],
            "forbidden_docs": [],
            "topic_filter": None,
            "eligible_count": 0
        }
        
        trace["required_docs"] = doc_constraints.get("required", [])
        trace["forbidden_docs"] = doc_constraints.get("forbidden", [])
        trace["topic_filter"] = doc_constraints.get("topic", None)
        
        # Start with all documents
        all_docs = self.kb.get_all_docs()
        eligible = set()
        
        # Apply topic filter
        topic = doc_constraints.get("topic")
        if topic:
            topic_docs = self.kb.get_docs_by_topic(topic)
            eligible.update(topic_docs)
        elif intent == "General" or not doc_constraints.get("topic"):
            # FALLBACK: For general queries without a specific topic constraint,
            # we allow the full document pool to be passed to Tier 2 (Semantic Ranking).
            # This prevents the "not in context" error for broad queries.
            print(f"DEBUG: [Layer 4] General intent detected. Allowing full document pool for semantic search.")
            eligible.update(all_docs)
        
        # Add required documents
        eligible.update(trace["required_docs"])
        
        # Remove forbidden documents
        for forbidden in trace["forbidden_docs"]:
            eligible.discard(forbidden)
        
        if len(eligible) < 2 and topic != "restricted":
            print(f"DEBUG: Supplementing low topic results ({len(eligible)}) with keyword search...")
            for keyword in nlp_analysis.keywords[:5]:
                docs = self.kb.get_docs_by_keyword(keyword.lower())
                eligible.update(docs)
        
        # Final forbidden check
        eligible = [doc for doc in eligible if doc not in trace["forbidden_docs"]]
        
        trace["eligible_count"] = len(eligible)
        print(f"DEBUG: [Layer 4] Symbolic Filter Result: {len(eligible)} docs")
        
        return list(eligible), trace
    
    def _tier3_evidence_scoring(self, ranked_docs: List[Dict], nlp_analysis, doc_constraints: Dict) -> Tuple[List[Any], Dict]:
        """
        TIER 3: Multi-dimensional evidence scoring.
        Scores documents on relevance, compatibility, recency, coverage.
        """
        from utils.evidence_scorer import EvidenceScore
        
        trace = {
            "scored_count": 0,
            "top_scores": []
        }
        
        scored_evidence = []
        query = nlp_analysis.query
        keywords = nlp_analysis.keywords
        required_docs = doc_constraints.get("required", [])
        forbidden_docs = doc_constraints.get("forbidden", [])
        
        for doc in ranked_docs:
            doc_name = doc["name"]
            doc_info = doc["info"]
            
            # Prepare document for scoring
            document = {
                "name": doc_name,
                "keywords": doc_info.get("keywords", []),
                "content": doc_info.get("description", ""),
                "metadata": {
                    "version": doc_info.get("version", "1.0.0"),
                    "last_modified": doc_info.get("last_modified", "2024-01-01")
                }
            }
            
            # Score document
            score = self.evidence_scorer.score_document(
                document=document,
                query=query,
                query_keywords=keywords,
                required_docs=required_docs,
                forbidden_docs=forbidden_docs
            )
            
            scored_evidence.append(score)
        
        # Sort by combined score
        scored_evidence.sort(key=lambda x: x.combined_score, reverse=True)
        
        trace["scored_count"] = len(scored_evidence)
        trace["top_scores"] = [
            {"doc": s.document_id, "score": round(s.combined_score, 3)}
            for s in scored_evidence[:5]
        ]
        
        return scored_evidence, trace
    
    def _tier2_semantic_ranking(self, eligible_docs: List[str], nlp_analysis, max_docs: int, required_docs: List[str] = None) -> Tuple[List[Dict], Dict]:
        """
        TIER 2: Semantic ranking via pgvector in the database.
        This replaces the hardcoded sklearn cosine_similarity.
        """
        trace = {
            "input_count": len(eligible_docs),
            "ranking_method": "pgvector",
            "top_scores": []
        }
        
        if not self.embedder or not self.domain_id:
            print("⚠️  No embedder or domain_id: falling back to empty retrieval")
            return [], trace

        # 1. Generate query embedding
        query_text = nlp_analysis.query
        query_embedding = self.embedder.encode(query_text).tolist()
        
        # 2. Perform pgvector search in DB
        db = SessionLocal()
        try:
            # Construct the query with pgvector cosine similarity (<=>)
            # We filter by domain_id and only include eligible documents
            # If eligible_docs is too long, we might need a different strategy, 
            # but for now we'll use an IN clause if it's manageable.
            
            # Map doc names to IDs for more efficient querying if possible
            doc_ids = [self.kb.get_document(name).get("id") for name in eligible_docs if self.kb.get_document(name)]
            doc_ids = [d for d in doc_ids if d is not None]
            
            if not doc_ids:
                return [], trace

            # Using raw SQL for pgvector operator until SQLAlchemy natively supports it better in some versions
            # <=> is cosine distance (smaller is better). 1 - <=> is similarity.
            stmt = text("""
                SELECT dc.id, dc.document_id, dc.content, dc.chunk_index, 
                       (1 - (dc.embedding <=> :emb)) as similarity,
                       d.source as doc_source, d.title as doc_title
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE d.domain_id = :domain_id
                AND d.id IN :doc_ids
                ORDER BY dc.embedding <=> :emb
                LIMIT :limit
            """)
            
            results = db.execute(stmt, {
                "emb": str(query_embedding),
                "domain_id": self.domain_id,
                "doc_ids": tuple(doc_ids),
                "limit": max_docs * 5 # Get more chunks to allow for better doc coverage
            }).fetchall()
            
            scored_docs = []
            seen_docs = set()
            
            for row in results:
                doc_name = row.doc_source
                info = self.kb.get_document(doc_name)
                
                # Check if it was already in scored_docs to boost/update
                existing = next((d for d in scored_docs if d["name"] == doc_name), None)
                if existing:
                    # Update with best chunk if needed
                    if row.similarity > existing["score"]:
                        existing["score"] = row.similarity
                    # Add to chunks if not already present
                    if row.content not in existing["chunks"]:
                        existing["chunks"].append(row.content)
                    continue

                scored_docs.append({
                    "name": doc_name,
                    "score": row.similarity,
                    "info": info,
                    "best_chunk": row.content, # Legacy field for compatibility
                    "chunks": [row.content],
                    "chunk_index": row.chunk_index
                })
                seen_docs.add(doc_name)
                
            # BOOST required documents (still applied in Python for policy enforcement)
            required_set = set(required_docs or [])
            for doc in scored_docs:
                if doc["name"] in required_set:
                    doc["score"] += 10.0
            
            # Re-sort after boost
            scored_docs.sort(key=lambda x: x["score"], reverse=True)
            top_docs = scored_docs[:max_docs]
            
            trace["top_scores"] = [(doc["name"], round(doc["score"], 2)) for doc in top_docs]
            return top_docs, trace
            
        except Exception as e:
            print(f"❌ pgvector search failed: {e}")
            import traceback
            traceback.print_exc()
            return [], trace
        finally:
            db.close()
    
    def _calculate_keyword_score(self, query_keywords: List[str], doc_keywords: List[str]) -> float:
        """Calculate keyword overlap score (case-insensitive)"""
        if not query_keywords or not doc_keywords:
            return 0.0
        
        q_low = {k.lower() for k in query_keywords}
        d_low = {k.lower() for k in doc_keywords}
        matches = q_low & d_low
        return len(matches) / len(q_low) if q_low else 0.0
    
    @lru_cache(maxsize=1000)
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text (cached)"""
        if self.embedder:
            return self.embedder.encode(text)
        return np.array([])
    
    def _calculate_semantic_score(self, query_keywords: List[str], doc_keywords: List[str]) -> float:
        """Calculate semantic similarity using embeddings"""
        if not self.embedder or not query_keywords or not doc_keywords:
            return 0.0
        
        query_text = " ".join(query_keywords)
        doc_text = " ".join(doc_keywords)
        
        query_emb = self._get_embedding(query_text).reshape(1, -1)
        doc_emb = self._get_embedding(doc_text).reshape(1, -1)
        
        if query_emb.size == 0 or doc_emb.size == 0:
            return 0.0
        
        similarity = cosine_similarity(query_emb, doc_emb)[0][0]
        return float(similarity)
    
    def _extract_sections(self, ranked_docs: List[Dict], nlp_analysis) -> List[Dict]:
        """Extract relevant sections from top documents"""
        results = []
        
        for doc in ranked_docs:
            doc_name = doc["name"]
            info = doc["info"]
            
            # Read document content
            content = self._read_document(doc_name, info)
            
            scored_sections = []
            if content:
                # Parse sections
                sections = self._parse_markdown_sections(content)
                
                # Store full content for maximize length mode
                doc["full_content"] = content
                
                # Score sections
                for section in sections:
                    section_text = f"{section['title']}\n{section['content']}"
                    score = self._calculate_semantic_score(nlp_analysis.keywords, section_text.split())
                    
                    scored_sections.append({
                        "section": section["title"],
                        "context": section["content"],
                        "score": round(score, 2)
                    })
                
                # Sort sections
                scored_sections.sort(key=lambda x: x["score"], reverse=True)
            
            # FALLBACK: If no sections were identified (common for non-markdown PDFs)
            # or reading failed, use the chunks found by pgvector.
            if not scored_sections:
                print(f"DEBUG: [Layer 4] Using chunks fallback for {doc_name} ({len(doc.get('chunks', []))} chunks)")
                for i, chunk in enumerate(doc.get("chunks", [])):
                    scored_sections.append({
                        "section": f"Excerpt {i+1}",
                        "context": chunk,
                        "score": doc.get("score", 0.0)
                    })
            
            doc["sections"] = scored_sections[:3]
            results.append(doc)
        
        return results
    
    def _read_document(self, doc_name: str, info: Dict) -> str:
        """Read document content from filesystem"""
        folder = info.get('folder', '').lower()
        if folder in ['root', '.', './', 'none', '']:
            folder = ""
        else:
            folder = folder.replace('_', ' ')
            
        current_base_path = self.kb.auto_discovery.base_path if (hasattr(self.kb, 'auto_discovery') and self.kb.auto_discovery) else self.base_path
            
        filepath = os.path.join(current_base_path, folder, doc_name)
        
        # Try with original folder name if space replacement fails
        if not os.path.exists(filepath):
            folder = info.get('folder', '')
            filepath = os.path.join(current_base_path, folder, doc_name)
        
        # FINAL FALLBACK: try looking directly in base_path if not found
        if not os.path.exists(filepath):
            filepath = os.path.join(current_base_path, doc_name)
        
        if os.path.exists(filepath):
            try:
                # Handle different file types
                ext = doc_name.lower()
                if ext.endswith('.pdf'):
                    if hasattr(self.kb, 'auto_discovery') and self.kb.auto_discovery:
                        content = self.kb.auto_discovery._extract_text_from_pdf(filepath)
                    else:
                        print(f"⚠️  Cannot extract PDF without AutoDiscovery: {filepath}")
                        content = ""
                elif ext.endswith('.docx'):
                    if hasattr(self.kb, 'auto_discovery') and self.kb.auto_discovery:
                        content = self.kb.auto_discovery._extract_text_from_docx(filepath)
                    else:
                        print(f"⚠️  Cannot extract DOCX without AutoDiscovery: {filepath}")
                        content = ""
                else:
                    # Default text/markdown reading
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                
                if content:
                    print(f"DEBUG: [Layer 4] Successfully read {len(content)} chars from {filepath}")
                return content
            except Exception as e:
                print(f"ERROR: [Layer 4] Failed to read {filepath}: {e}")
        else:
            print(f"ERROR: [Layer 4] Document not found: {filepath}")
        
        return ""
    
    def _parse_markdown_sections(self, content: str) -> List[Dict]:
        """Parse markdown into sections"""
        sections = []
        raw_parts = re.split(r'\n(?=#+ )', f"\n{content}")
        
        for part in raw_parts:
            if not part.strip():
                continue
            
            lines = part.strip().split('\n')
            header_match = re.match(r'^#+\s+(.+)', lines[0])
            
            title = header_match.group(1) if header_match else "Introduction"
            body = "\n".join(lines[1:]) if header_match else "\n".join(lines)
            
            sections.append({
                "title": title,
                "content": body
            })
        
        return sections


# Example usage
if __name__ == "__main__":
    from data.knowledge_base import KnowledgeBase
    from agents.expert_agent import ExpertAgent
    from core.nlp_core import AdvancedNLPCore
    
    # Initialize components
    kb = KnowledgeBase()
    expert = ExpertAgent()
    nlp = AdvancedNLPCore()
    
    # Try to load embedder
    try:
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
    except:
        embedder = None
    
    retrieval = AgentDrivenRetrieval(kb, expert, embedder)
    
    # Test query
    query = "How do I create a new Next.js project?"
    analysis = nlp.analyze(query)
    
    print(f"Query: {query}")
    print(f"Top intent: {analysis.intent_hypotheses[0]['intent']}")
    
    # Retrieve
    docs, trace = retrieval.retrieve(analysis.intent_hypotheses[0]['intent'], analysis)
    
    print(f"\nTier 1 (Symbolic Filter):")
    print(f"  Topic: {trace['tier1_symbolic']['topic_filter']}")
    print(f"  Forbidden: {trace['tier1_symbolic']['forbidden_docs']}")
    print(f"  Eligible: {trace['tier1_symbolic']['eligible_count']} documents")
    
    print(f"\nTier 2 (Semantic Ranking):")
    print(f"  Top scores: {trace['tier2_semantic']['top_scores']}")
    
    print(f"\nFinal Selection:")
    for doc in docs:
        print(f"  - {doc['name']} (score: {doc['score']:.2f})")
