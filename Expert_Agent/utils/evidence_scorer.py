"""
Evidence Scoring Module - Multi-Dimensional Document Grounding Assessment
Responsibilities:
- Score documents by semantic relevance
- Assess rule compatibility
- Factor in recency/versioning
- Calculate coverage metrics
- Enforce minimum evidence thresholds

This ensures GROUNDED GENERATION - no hallucinations.
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class EvidenceScore:
    """Comprehensive evidence score for a document"""
    document_id: str
    semantic_relevance: float  # 0-1: How relevant to query
    rule_compatibility: float  # 0-1: Alignment with expert rules
    recency_score: float       # 0-1: Document freshness
    coverage_score: float      # 0-1: How much of query is addressed
    combined_score: float      # Weighted combination
    metadata: Dict[str, Any]


@dataclass
class GroundingReport:
    """Report on evidence grounding sufficiency"""
    sufficient: bool
    total_coverage: float
    min_threshold: float
    top_documents: List[EvidenceScore]
    gaps: List[str]
    recommendation: str


class EvidenceScorer:
    """
    Multi-dimensional evidence scorer.
    Ensures answers are grounded in sufficient, relevant evidence.
    """
    
    def __init__(self, 
                 semantic_weight: float = 0.4,
                 compatibility_weight: float = 0.3,
                 recency_weight: float = 0.1,
                 coverage_weight: float = 0.2,
                 min_coverage_threshold: float = 0.6):
        """
        Initialize scorer with configurable weights.
        Weights should sum to 1.0.
        """
        self.semantic_weight = semantic_weight
        self.compatibility_weight = compatibility_weight
        self.recency_weight = recency_weight
        self.coverage_weight = coverage_weight
        self.min_coverage_threshold = min_coverage_threshold
        
        # Validate weights
        total_weight = sum([semantic_weight, compatibility_weight, recency_weight, coverage_weight])
        if not 0.99 <= total_weight <= 1.01:
            print(f"⚠️  Warning: Weights sum to {total_weight}, expected 1.0")
        
        print(f"📊 Evidence Scorer initialized (min coverage: {min_coverage_threshold})")
    
    def score_document(self,
                      document: Dict[str, Any],
                      query: str,
                      query_keywords: List[str],
                      required_docs: List[str],
                      forbidden_docs: List[str],
                      query_embedding: Optional[np.ndarray] = None,
                      doc_embedding: Optional[np.ndarray] = None) -> EvidenceScore:
        """
        Score a single document across all dimensions.
        
        Args:
            document: Document metadata and content
            query: Original query string
            query_keywords: Extracted keywords from query
            required_docs: Documents required by expert rules
            forbidden_docs: Documents forbidden by expert rules
            query_embedding: Optional embedding vector for query
            doc_embedding: Optional embedding vector for document
        
        Returns:
            EvidenceScore with all dimensions
        """
        doc_id = document.get("name", "unknown")
        doc_keywords = document.get("keywords", [])
        doc_content = document.get("content", "")
        doc_metadata = document.get("metadata", {})
        
        # 1. Semantic Relevance
        semantic_score = self._calculate_semantic_relevance(
            query_keywords, doc_keywords, query_embedding, doc_embedding
        )
        
        # 2. Rule Compatibility
        compatibility_score = self._calculate_rule_compatibility(
            doc_id, required_docs, forbidden_docs
        )
        
        # 3. Recency Score
        recency_score = self._calculate_recency(doc_metadata)
        
        # 4. Coverage Score
        coverage_score = self._calculate_coverage(
            query, query_keywords, doc_content, doc_keywords
        )
        
        # 5. Combined Score (weighted)
        combined = (
            self.semantic_weight * semantic_score +
            self.compatibility_weight * compatibility_score +
            self.recency_weight * recency_score +
            self.coverage_weight * coverage_score
        )
        
        return EvidenceScore(
            document_id=doc_id,
            semantic_relevance=semantic_score,
            rule_compatibility=compatibility_score,
            recency_score=recency_score,
            coverage_score=coverage_score,
            combined_score=combined,
            metadata={
                "required": doc_id in required_docs,
                "forbidden": doc_id in forbidden_docs,
                "version": doc_metadata.get("version", "unknown"),
                "last_modified": doc_metadata.get("last_modified", "unknown")
            }
        )
    
    def _calculate_semantic_relevance(self,
                                     query_keywords: List[str],
                                     doc_keywords: List[str],
                                     query_embedding: Optional[np.ndarray],
                                     doc_embedding: Optional[np.ndarray]) -> float:
        """
        Calculate semantic relevance using embeddings or keyword overlap.
        """
        # Prefer embedding-based similarity if available
        if query_embedding is not None and doc_embedding is not None:
            try:
                # Cosine similarity
                similarity = np.dot(query_embedding, doc_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                )
                # Normalize to 0-1
                return float((similarity + 1) / 2)
            except Exception as e:
                print(f"⚠️  Embedding similarity failed: {e}")
        
        # Fallback to keyword overlap
        if not query_keywords or not doc_keywords:
            return 0.0
        
        query_set = set(k.lower() for k in query_keywords)
        doc_set = set(k.lower() for k in doc_keywords)
        
        intersection = query_set & doc_set
        union = query_set | doc_set
        
        if not union:
            return 0.0
        
        # Jaccard similarity
        return len(intersection) / len(union)
    
    def _calculate_rule_compatibility(self,
                                     doc_id: str,
                                     required_docs: List[str],
                                     forbidden_docs: List[str]) -> float:
        """
        Calculate compatibility with expert rules.
        """
        # Forbidden documents get 0 score
        if doc_id in forbidden_docs:
            return 0.0
        
        # Required documents get maximum score
        if doc_id in required_docs:
            return 1.0
        
        # Partial match on filename
        doc_name_lower = doc_id.lower()
        for required in required_docs:
            if required.lower() in doc_name_lower or doc_name_lower in required.lower():
                return 0.8
        
        # Not explicitly required or forbidden - neutral
        return 0.5
    
    def _calculate_recency(self, metadata: Dict[str, Any]) -> float:
        """
        Calculate recency score based on version or last modified date.
        """
        # Check for version number
        version = metadata.get("version", "")
        if version:
            # Parse semantic version (e.g., "2.1.0")
            match = re.match(r'(\d+)\.(\d+)\.(\d+)', str(version))
            if match:
                major, minor, patch = map(int, match.groups())
                # Higher versions get higher scores
                # Normalize assuming max version is 10.0.0
                score = min(1.0, (major * 100 + minor * 10 + patch) / 1000)
                return score
        
        # Check for last modified date
        last_modified = metadata.get("last_modified", "")
        if last_modified:
            try:
                # Parse ISO date
                mod_date = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
                now = datetime.now(mod_date.tzinfo)
                days_old = (now - mod_date).days
                
                # Exponential decay: score = e^(-days/365)
                # Documents older than 2 years get very low scores
                score = np.exp(-days_old / 365)
                return float(score)
            except Exception:
                pass
        
        # No recency information - neutral score
        return 0.5
    
    def _calculate_coverage(self,
                           query: str,
                           query_keywords: List[str],
                           doc_content: str,
                           doc_keywords: List[str]) -> float:
        """
        Calculate how much of the query is covered by the document.
        """
        if not query_keywords:
            return 0.0
        
        query_lower = query.lower()
        content_lower = doc_content.lower()
        
        # Count how many query keywords appear in document
        covered_keywords = 0
        for keyword in query_keywords:
            if keyword.lower() in content_lower:
                covered_keywords += 1
        
        keyword_coverage = covered_keywords / len(query_keywords)
        
        # Check for phrase coverage (bigrams)
        query_words = query_lower.split()
        if len(query_words) >= 2:
            bigrams = [f"{query_words[i]} {query_words[i+1]}" for i in range(len(query_words)-1)]
            covered_bigrams = sum(1 for bg in bigrams if bg in content_lower)
            phrase_coverage = covered_bigrams / len(bigrams) if bigrams else 0
        else:
            phrase_coverage = keyword_coverage
        
        # Combine keyword and phrase coverage
        return 0.6 * keyword_coverage + 0.4 * phrase_coverage
    
    def assess_grounding(self,
                        scored_documents: List[EvidenceScore],
                        query: str,
                        min_documents: int = 1) -> GroundingReport:
        """
        Assess whether evidence is sufficient for grounded generation.
        
        Args:
            scored_documents: List of scored documents
            query: Original query
            min_documents: Minimum number of documents required
        
        Returns:
            GroundingReport with sufficiency assessment
        """
        if not scored_documents:
            return GroundingReport(
                sufficient=False,
                total_coverage=0.0,
                min_threshold=self.min_coverage_threshold,
                top_documents=[],
                gaps=["No documents retrieved"],
                recommendation="Unable to answer - no relevant documentation found"
            )
        
        # Sort by combined score
        sorted_docs = sorted(scored_documents, key=lambda x: x.combined_score, reverse=True)
        top_docs = sorted_docs[:min_documents]
        
        # Calculate total coverage (max of individual coverages)
        total_coverage = max(doc.coverage_score for doc in top_docs)
        
        # Check if any required documents are missing
        gaps = []
        
        # Check minimum document count
        if len(top_docs) < min_documents:
            gaps.append(f"Only {len(top_docs)} documents found, need {min_documents}")
        
        # Check coverage threshold
        if total_coverage < self.min_coverage_threshold:
            gaps.append(f"Coverage {total_coverage:.2f} below threshold {self.min_coverage_threshold}")
        
        # Check for forbidden documents in top results
        forbidden_in_top = [doc for doc in top_docs if doc.metadata.get("forbidden", False)]
        if forbidden_in_top:
            gaps.append(f"Forbidden documents in top results: {[d.document_id for d in forbidden_in_top]}")
        
        # Determine sufficiency
        sufficient = (
            len(top_docs) >= min_documents and
            total_coverage >= self.min_coverage_threshold and
            not forbidden_in_top
        )
        
        # Generate recommendation
        if sufficient:
            recommendation = f"Sufficient evidence from {len(top_docs)} documents (coverage: {total_coverage:.2f})"
        else:
            recommendation = f"Insufficient evidence: {', '.join(gaps)}"
        
        return GroundingReport(
            sufficient=sufficient,
            total_coverage=total_coverage,
            min_threshold=self.min_coverage_threshold,
            top_documents=top_docs,
            gaps=gaps,
            recommendation=recommendation
        )
    
    def get_scoring_explanation(self, score: EvidenceScore) -> str:
        """Generate human-readable explanation of score"""
        lines = [
            f"📄 Document: {score.document_id}",
            f"   Combined Score: {score.combined_score:.3f}",
            f"   ├─ Semantic Relevance: {score.semantic_relevance:.3f} (weight: {self.semantic_weight})",
            f"   ├─ Rule Compatibility: {score.rule_compatibility:.3f} (weight: {self.compatibility_weight})",
            f"   ├─ Recency: {score.recency_score:.3f} (weight: {self.recency_weight})",
            f"   └─ Coverage: {score.coverage_score:.3f} (weight: {self.coverage_weight})",
        ]
        
        if score.metadata.get("required"):
            lines.append("   ✅ Required by expert rules")
        if score.metadata.get("forbidden"):
            lines.append("   ⛔ Forbidden by expert rules")
        
        return "\n".join(lines)


# Example usage and testing
if __name__ == "__main__":
    scorer = EvidenceScorer(min_coverage_threshold=0.6)
    
    # Mock documents
    mock_docs = [
        {
            "name": "installation.md",
            "keywords": ["install", "setup", "npm", "create", "next", "app"],
            "content": "To install Next.js, run: npx create-next-app@latest my-app. This will create a new Next.js project with all dependencies.",
            "metadata": {"version": "14.0.0", "last_modified": "2024-01-15"}
        },
        {
            "name": "deployment.md",
            "keywords": ["deploy", "vercel", "production", "build"],
            "content": "Deploy your Next.js app to Vercel with zero configuration. Run: vercel deploy",
            "metadata": {"version": "13.5.0", "last_modified": "2023-11-20"}
        },
        {
            "name": "routing.md",
            "keywords": ["routing", "pages", "app", "router", "navigation"],
            "content": "Next.js uses file-system based routing. Create pages in the app directory.",
            "metadata": {"version": "14.1.0", "last_modified": "2024-02-01"}
        }
    ]
    
    # Mock query
    query = "How do I install and create a new Next.js project?"
    query_keywords = ["install", "create", "next", "project"]
    required_docs = ["installation.md", "create_next_app.md"]
    forbidden_docs = ["deployment.md"]
    
    print("="*60)
    print("EVIDENCE SCORING DEMONSTRATION")
    print("="*60)
    print(f"\nQuery: {query}")
    print(f"Required docs: {required_docs}")
    print(f"Forbidden docs: {forbidden_docs}")
    
    # Score all documents
    scored_docs = []
    for doc in mock_docs:
        score = scorer.score_document(
            document=doc,
            query=query,
            query_keywords=query_keywords,
            required_docs=required_docs,
            forbidden_docs=forbidden_docs
        )
        scored_docs.append(score)
        print(f"\n{scorer.get_scoring_explanation(score)}")
    
    # Assess grounding
    print("\n" + "="*60)
    print("GROUNDING ASSESSMENT")
    print("="*60)
    
    grounding = scorer.assess_grounding(scored_docs, query, min_documents=2)
    
    print(f"\nSufficient: {grounding.sufficient}")
    print(f"Total Coverage: {grounding.total_coverage:.2f}")
    print(f"Threshold: {grounding.min_threshold}")
    print(f"Recommendation: {grounding.recommendation}")
    
    if grounding.gaps:
        print(f"\nGaps:")
        for gap in grounding.gaps:
            print(f"  - {gap}")
    
    print(f"\nTop Documents:")
    for doc in grounding.top_documents:
        print(f"  - {doc.document_id} (score: {doc.combined_score:.3f})")
