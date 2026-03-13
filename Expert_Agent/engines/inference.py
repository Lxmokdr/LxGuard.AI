import string
import os
import re
import spacy
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from functools import lru_cache
from sklearn.metrics.pairwise import cosine_similarity

from data.knowledge_base import KnowledgeBase
from engines.rule_engine import RuleEngine


class InferenceEngine:
    """
    Agent that uses NLP and semantic search to infer answers from a knowledge base.
    """
    
    def __init__(self, use_embeddings=True):
        self.kb = KnowledgeBase()
        self.re = RuleEngine()
        # Use repo-relative docs folder instead of a hardcoded absolute path
        self.base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'docs')
        )
        
        # Load spaCy for linguistic analysis
        try:
            self.nlp = spacy.load("en_core_web_md")
        except Exception:
            print("⚠️  spaCy model 'en_core_web_md' not found; using blank 'en' model (reduced NLP capabilities).")
            self.nlp = spacy.blank("en")
        
        # Load sentence transformer for semantic search (optional)
        self.use_embeddings = use_embeddings
        self.embedder = None
        self.doc_embeddings = {}
        if use_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                self.doc_embeddings = {}  # Cache for document embeddings
            except Exception as e:
                print("\u26a0\ufe0f  sentence-transformers not available, disabling embeddings:", e)
                self.use_embeddings = False
        
        # Question type patterns
        self.question_patterns = {
            "how_to": r"^(how (do|can|to)|what's the way)",
            "what_is": r"^what (is|are|does)",
            "why": r"^why",
            "troubleshooting": r"(error|issue|problem|not working|fails?|broken)",
            "comparison": r"(vs|versus|difference between|compare)",
            "best_practice": r"(best (way|practice)|should I|recommended)"
        }
        
        # Next.js specific entities
        self.nextjs_terms = {
            "app router", "pages router", "middleware", "api routes",
            "server components", "client components", "next.config",
            "image optimization", "metadata", "incremental static regeneration",
            "isr", "ssg", "ssr", "csr", "next/link", "next/image",
            "next/font", "turbopack", "webpack", "vercel"
        }
        
        # Scoring weights
        self.weights = {
            "priority": 10,
            "specificity": 5,
            "semantic_similarity": 20,
            "keyword_density": 10,
            "question_type_match": 8,
        }
        

    def prepare_facts(self, question: str) -> Dict:
        """
        Extracts details from the question using NLP techniques.
        """
        qst = self.nlp(question.lower()) #spacy processing pipeline
        
        # 1. lemmatization (base forms)
        keywords = []
        for token in qst:
            if not token.is_stop and not token.is_punct and len(token.text) > 1:
                keywords.append(token.lemma_)

        # Normalize and remove empty lemmas; fallback if none remain
        keywords = [k for k in keywords if k and len(k.strip()) > 0]
        if not keywords:
            import re as _re
            stopwords = {"the", "a", "an", "in", "on", "and", "or", "to", "how", "what", "are", "is", "of", "for", "do", "can"}
            tokens = [t for t in _re.findall(r"\w+", question.lower()) if len(t) > 1 and t not in stopwords]
            keywords = tokens
        
        # 2. Extract Next.js specific terms from the question
        tech_entities = []
        question_lower = question.lower()
        for term in self.nextjs_terms:
            if term in question_lower:
                tech_entities.append(term)
        
        # 3. Named Entities (Organizations, Products, GPEs) + Next.js terms
        entities = [
            {"text": ent.text, "label": ent.label_} 
            for ent in qst.ents 
            if ent.label_ in ["ORG", "PRODUCT", "GPE", "TECH"]
        ]
        entities.extend([{"text": term, "label": "NEXTJS_TERM"} for term in tech_entities])
        

        # 5. Question Type Classification
        question_type = self._classify_question_type(question)
        
        # 6. Syntactic Analysis
        subject = [token.text for token in qst if "subj" in token.dep_]
        objects = [token.text for token in qst if "obj" in token.dep_]
        
        # 7. Extract verb-object pairs (action-target relationships)
        action_targets = self._extract_action_targets(qst)
        
        
        # 8. Pre-compute question embedding for reuse
        return {
            "question": question,
            "keywords": list(set(keywords)),
            "entities": entities,
            "tech_entities": tech_entities,
            "subject": subject,
            "objects": objects,
            "action_targets": action_targets,
            "question_type": question_type,
        }
    
    """ Understanding the user's question """

    def _classify_question_type(self, question: str) -> str:
        question_lower = question.lower()
        
        for q_type, pattern in self.question_patterns.items():
            if re.search(pattern, question_lower):
                return q_type
        
        return "general"
    
    #Extract verb-object pairs .
    def _extract_action_targets(self, doc) -> List[Tuple[str, str]]:
        pairs = []
        for token in doc:
            if token.pos_ == "VERB":
                # Find direct objects of this verb
                for child in token.children:
                    if "obj" in child.dep_:
                        pairs.append((token.lemma_, child.text))
        return pairs

    @lru_cache(maxsize=1000) # Cache embeddings for efficiency (ie won't re do all the calculations).
    def _get_embedding(self, text: str) -> np.ndarray:
        if self.use_embeddings:
            return self.embedder.encode(text)
        return np.array([])
    
    """ deciding the relevant document """

    def select_documents(self, facts: Dict) -> List[str]:
        """
        Select documents based on keyword matching between question keywords and KB keywords.
        """
        selected = set()
        
        # Match keywords extracted from question with keywords in KB
        for keyword in facts["keywords"]:
            docs = self.kb.get_docs_by_keyword(keyword)
            selected.update(docs)
        
        return list(selected)

    # Compute semantic similarity between query and document ( used in ranking).
    def _compute_semantic_similarity_with_embedding(self, keywords_list, doc_text):
        """
        Compute semantic similarity between a list of keywords and document text.
        Converts keywords list to string, then computes cosine similarity.
        """
        if not self.use_embeddings:
            return 0.0
        
        # Convert list to string if needed
        if isinstance(keywords_list, list):
            query_str = " ".join(keywords_list)
        else:
            query_str = str(keywords_list)
        
        # Get embeddings
        query_emb = self._get_embedding(query_str).reshape(1, -1)
        doc_emb = self._get_embedding(doc_text).reshape(1, -1)
        
        # Calculate similarity
        similarity = cosine_similarity(query_emb, doc_emb)[0][0]
        return float(similarity)
    
    def rank_documents(self, documents: List[str], facts: Dict) -> Tuple[List[Dict], List[Dict]]:
        
        if not documents:
            return [], []
        
        scored_docs = []
        keywords = facts["keywords"]
        question_type = facts["question_type"]
        
        for doc_name in documents:
            info = self.kb.get_document(doc_name)
            if not info:
                continue
            
            #get document keywords from the kb for semantic analysis
            doc_keywords = info.get("keywords", [])
            doc_keywords_str = " ".join(doc_keywords) if isinstance(doc_keywords, list) else str(doc_keywords)
            
            # 1. Keyword Density Score
            keyword_matches = [k for k in keywords if k in doc_keywords]
            keyword_density = len(keyword_matches) / max(len(keywords), 1)
            
            # 2. Semantic Similarity Score - using keywords list
            semantic_score = 0.0
            if doc_keywords_str and self.use_embeddings:
                semantic_score = self._compute_semantic_similarity_with_embedding(keywords, doc_keywords_str)
            
            # 3. Specificity Score
            specificity_map = {"high": 3, "medium": 2, "low": 1}
            specificity_score = specificity_map.get(info.get("specificity", "low"), 1)
            
            # 4. Question Type Match
            doc_type = info.get("type", "general")
            type_match_score = 1.0 if self._matches_question_type(question_type, doc_type) else 0.5
            
            # Calculate final weighted score
            final_score = (
                self.weights["priority"] * info.get("priority", 1) +
                self.weights["specificity"] * specificity_score +
                self.weights["semantic_similarity"] * semantic_score +
                self.weights["keyword_density"] * keyword_density +
                self.weights["question_type_match"] * type_match_score

            )
            
            scored_docs.append({
                "score": final_score,
                "name": doc_name,
                "matches": keyword_matches,
                "semantic_similarity": semantic_score,
                "info": info
            })
        
        # Sort by score (descending)
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        
        # Split into selected and excluded
        top_docs = scored_docs[:3]  # Top 3 documents
        excluded_docs = scored_docs[3:]
        
        return top_docs, excluded_docs
    
    def _matches_question_type(self, question_type: str, doc_type: str) -> bool: ##we can add more types
        type_mappings = {
            "how_to": ["set-up", "configuration", "rooting"],
            "what_is": ["functions", "componenets"],
            "troubleshooting": ["operations", "functions", "componenets"],
            "comparison": ["functions", "set-up"]
        }
        
        expected_types = type_mappings.get(question_type, [])
        return doc_type.lower() in expected_types
    
    def _read_document_content(self, doc_name: str, info: Dict) -> str:
        """Read document content with strict path validation and logging."""
        # 1. Resolve folder name logic
        raw_folder = info.get('folder', '')
        space_folder = raw_folder.replace('_', ' ')
        
        # Try the path with spaces first
        filepath = os.path.join(self.base_path, space_folder, doc_name)
        
        # 2. Fallback to original folder name if space version fails
        if not os.path.exists(filepath):
            filepath = os.path.join(self.base_path, raw_folder, doc_name)
        
        # 3. Final Verification and Reading
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Debug print to confirm success
                    print(f"SUCCESS: Loaded {len(content)} bytes from {filepath}")
                    return content
            except Exception as e:
                print(f"ERROR reading {filepath}: {e}")
        else:
            # Crucial for troubleshooting: print where it searched
            print(f"FILE NOT FOUND: Checked both space/underscore paths for '{doc_name}'")
            print(f"   Looked in: {os.path.abspath(filepath)}")
            
        return ""
    
    """ section work"""

    def identify_sections(self, ranked_docs: list, facts: dict) -> list:
        """
        Identifies the best 3 sections from each top-scored document by comparing 
        semantic meaning using the pre-computed keywords embedding.
        """
        final_results = []
        keywords = facts.get("keywords", [])
        
        for item in ranked_docs:
            doc_name = item["name"]
            info = item["info"]
            content = self._read_document_content(doc_name, info)
            
            if not content:
                item["sections"] = [{"section": "blah", "context": "", "confidence": 0.0}]
                final_results.append(item)
                continue

            # 1. Parse markdown into sections
            sections = self._parse_markdown_sections(content)
            
            # 2. Score all sections using keywords
            scored_sections = []
            
            for section in sections:
                # Combine title and content for semantic comparison
                section_text = f"{section['title']}\n{section['content']}"
                
                # Use keywords list to compute similarity
                similarity = 0.0
                if self.use_embeddings:
                    similarity = self._compute_semantic_similarity_with_embedding(keywords, section_text)
                
                # Also check tech entities
                tech_entities = facts.get("tech_entities", [])
                if tech_entities and self.use_embeddings:
                    tech_similarity = self._compute_semantic_similarity_with_embedding(tech_entities, section_text)
                    similarity = max(similarity, tech_similarity)

                scored_sections.append({
                    "section": section["title"],
                    "context": section["content"].strip(),
                    "confidence": round(similarity, 2)
                })
            
            # 3. Sort sections by confidence and take top 3
            scored_sections.sort(key=lambda x: x["confidence"], reverse=True)
            top_3_sections = scored_sections[:3]
            
            # 4. Update item with top 3 sections
            item["sections"] = top_3_sections
            
            final_results.append(item)
            
        return final_results

    def _parse_markdown_sections(self, content: str) -> list:
    
        """Parses short markdown files by headers #, ##, ###."""
        sections = []
        # Split by headers but keep the headers in the results
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
    
    def process_question(self, question: str) -> Dict:
        """Main method to process a user question and return inference results."""
        
        # 1. Prepare facts from the question
        facts = self.prepare_facts(question)
        
        # 2. Select relevant documents
        selected_docs = self.select_documents(facts)
        
        # 3. Rank documents
        top_docs, excluded_docs = self.rank_documents(selected_docs, facts)
        
        # 4. Identify best sections in top documents
        detailed_results = self.identify_sections(top_docs, facts)
        
        # Apply expert rules which may augment facts (returns (new_facts, activated_rules))
        new_facts, activated_rules = self.re.apply_rules(facts)

        return {
            "question": question,
            "keywords": facts["keywords"],
            "selected_documents": top_docs,
            "top_sections": detailed_results,
            "excluded_documents": excluded_docs,
            "activated_rules": activated_rules,
            "topic": new_facts.get("topic", "general")
        }