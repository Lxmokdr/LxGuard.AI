"""
Auto-Discovery Module
Automatically discovers and analyzes new documentation files in the docs/ folder.
Generates metadata (keywords, topics, priority) using NLP.

This makes the system REACTIVE to new files being added.
"""

import os
import re
from typing import Dict, List, Any
from pathlib import Path
import hashlib
import pypdf
import docx


class AutoDiscovery:
    """
    Automatically discovers and analyzes documentation files.
    Generates metadata without manual configuration.
    """
    
    def __init__(self, nlp_core=None, base_path=None):
        # Priority: /app/docs (Docker), then relative project root, then current dir
        path_variants = [
            '/app/docs',
            os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')),
            os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'docs'))
        ]
        
        selected_path = path_variants[1] # Default
        for p in path_variants:
            if os.path.exists(p) and os.path.isdir(p):
                selected_path = p
                break
                
        self.base_path = base_path or selected_path
        
        # Import NLP core for analysis
        if nlp_core:
            self.nlp = nlp_core
        else:
            try:
                from core.nlp_core import AdvancedNLPCore
                self.nlp = AdvancedNLPCore()
            except:
                self.nlp = None
                print("⚠️  NLP Core not available, using basic keyword extraction")
        
        # Topic classification patterns
        self.topic_patterns = {
            "setup": ["install", "create", "new", "start", "initialize", "setup", "prerequisite"],
            "components": ["component", "image", "link", "font", "button", "ui", "element"],
            "routing": ["route", "routing", "page", "navigation", "path", "url", "dynamic"],
            "functions": ["function", "fetch", "api", "data", "server", "action", "async"],
            "configuration": ["config", "configuration", "setting", "option", "environment"],
            "operations": ["deploy", "deployment", "build", "production", "docker", "vercel"],
        }
        
        # Cache for discovered documents
        self.cache_file = os.path.join(os.path.dirname(__file__), '.discovery_cache.json')
        self.discovered_docs = {}
        
        print(f"🔍 Auto-Discovery initialized (base: {self.base_path})")
    
    def discover_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all markdown files in the docs folder.
        Returns a dictionary of document metadata.
        """
        print("\n🔍 Scanning for documentation files...")
        
        discovered = {}
        
        # Walk through docs directory
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.lower().endswith(('.md', '.pdf', '.docx', '.txt')):
                    filepath = os.path.join(root, file)
                    
                    # Get relative folder
                    rel_path = os.path.relpath(root, self.base_path)
                    folder = rel_path if rel_path != '.' else 'root'
                    
                    # Analyze document
                    metadata = self._analyze_document(filepath, file, folder)
                    
                    if metadata:
                        # Use the relative path including folder as the key
                        rel_key = os.path.join(metadata['folder'], file) if metadata['folder'] != 'root' else file
                        metadata['source'] = rel_key
                        discovered[rel_key] = metadata
                        print(f"  ✅ {rel_key} → topic: {metadata['topic']}, priority: {metadata['priority']}")
        
        print(f"\n✅ Discovered {len(discovered)} documents")
        
        self.discovered_docs = discovered
        return discovered
    
    def _analyze_document(self, filepath: str, filename: str, folder: str) -> Dict[str, Any]:
        """
        Analyze a document and generate metadata.
        """
        try:
            # Extract content based on file type
            content = ""
            if filename.lower().endswith('.md') or filename.lower().endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif filename.lower().endswith('.pdf'):
                content = self._extract_text_from_pdf(filepath)
            elif filename.lower().endswith('.docx'):
                content = self._extract_text_from_docx(filepath)
            
            if not content.strip():
                return None
            
            # Extract title
            title = self._extract_title(content, filename)
            
            # Extract keywords
            keywords = self._extract_keywords(content)
            
            # Classify topic
            topic = self._classify_topic(content, keywords, folder)
            
            # Calculate priority
            priority = self._calculate_priority(content, topic, folder)
            
            # Determine specificity
            specificity = self._determine_specificity(content, keywords)
            
            return {
                "name": title,
                "folder": folder,
                "keywords": keywords,
                "topic": topic,
                "priority": priority,
                "specificity": specificity,
                "auto_discovered": True,
                "file_hash": self._get_file_hash(filepath)
            }
        
        except Exception as e:
            print(f"  ⚠️  Error analyzing {filename}: {e}")
            return None
            
    def _extract_text_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            reader = pypdf.PdfReader(filepath)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            print(f"  ⚠️  PDF extraction error {filepath}: {e}")
        return text
        
    def _extract_text_from_docx(self, filepath: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"  ⚠️  DOCX extraction error {filepath}: {e}")
        return text
    
    def _extract_title(self, content: str, filename: str) -> str:
        """Extract document title from first heading or filename"""
        # Try to find first # heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # Fallback to filename
        return filename.replace('.md', '').replace('_', ' ').title()
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from document content"""
        keywords = set()
        
        # Extract from headings (high value)
        headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        for heading in headings:
            words = re.findall(r'\b\w+\b', heading.lower())
            keywords.update([w for w in words if len(w) > 3])
        
        # Extract from code blocks (technical terms)
        code_blocks = re.findall(r'`([^`]+)`', content)
        for code in code_blocks:
            if len(code) < 30:  # Avoid long code snippets
                keywords.add(code.lower())
        
        # Use NLP if available
        if self.nlp:
            # Sample first 1000 chars for efficiency
            sample = content[:1000]
            analysis = self.nlp.analyze(sample)
            keywords.update(analysis.keywords[:10])
        else:
            # Basic extraction: common technical terms
            words = re.findall(r'\b\w+\b', content.lower())
            # Filter for meaningful words
            meaningful = [w for w in words if len(w) > 4 and w not in ['about', 'would', 'could', 'should']]
            # Get most common
            from collections import Counter
            common = Counter(meaningful).most_common(15)
            keywords.update([word for word, count in common if count > 2])
        
        return list(keywords)[:20]  # Limit to top 20
    
    def _classify_topic(self, content: str, keywords: List[str], folder: str) -> str:
        """Classify document topic based on content and keywords"""
        content_lower = content.lower()
        
        # Score each topic
        topic_scores = {}
        for topic, patterns in self.topic_patterns.items():
            score = 0
            for pattern in patterns:
                # Check in keywords
                if pattern in keywords:
                    score += 2
                # Check in content
                score += content_lower.count(pattern)
            
            topic_scores[topic] = score
        
        # Folder hints
        folder_lower = folder.lower()
        if 'cli' in folder_lower or 'getting' in folder_lower:
            topic_scores['setup'] = topic_scores.get('setup', 0) + 5
        elif 'guide' in folder_lower:
            # Guides can be any topic, don't bias
            pass
        elif 'config' in folder_lower:
            topic_scores['configuration'] = topic_scores.get('configuration', 0) + 5
        
        # Get highest scoring topic
        if topic_scores:
            best_topic = max(topic_scores.items(), key=lambda x: x[1])
            if best_topic[1] > 0:
                return best_topic[0]
        
        return "general"
    
    def _calculate_priority(self, content: str, topic: str, folder: str) -> int:
        """Calculate document priority (1-10)"""
        priority = 5  # Default
        
        # Topic-based priority
        topic_priorities = {
            "setup": 8,
            "operations": 7,
            "functions": 6,
            "routing": 6,
            "components": 5,
            "configuration": 5,
            "general": 3
        }
        priority = topic_priorities.get(topic, 5)
        
        # Folder-based adjustments
        if 'getting' in folder.lower() or 'cli' in folder.lower():
            priority += 2
        
        # Content-based adjustments
        if 'quick start' in content.lower() or 'getting started' in content.lower():
            priority += 1
        
        if 'advanced' in content.lower() or 'deep dive' in content.lower():
            priority -= 1
        
        return max(1, min(10, priority))  # Clamp to 1-10
    
    def _determine_specificity(self, content: str, keywords: List[str]) -> str:
        """Determine document specificity (high, medium, low)"""
        # Count technical terms and code examples
        code_blocks = len(re.findall(r'```', content))
        technical_terms = len([k for k in keywords if len(k) > 6])
        
        if code_blocks > 3 or technical_terms > 10:
            return "high"
        elif code_blocks > 1 or technical_terms > 5:
            return "medium"
        else:
            return "low"
    
    def _get_file_hash(self, filepath: str) -> str:
        """Get hash of file content for change detection"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def has_changes(self) -> bool:
        """Check if any files have changed since last discovery"""
        if not self.discovered_docs:
            return True
        
        for filename, metadata in self.discovered_docs.items():
            folder = metadata.get('folder', '')
            filepath = os.path.join(self.base_path, folder, filename)
            
            if os.path.exists(filepath):
                current_hash = self._get_file_hash(filepath)
                if current_hash != metadata.get('file_hash', ''):
                    return True
        
        return False
    
    def get_new_files(self, known_files: List[str]) -> List[str]:
        """Get list of files that aren't in the known list"""
        all_files = set()
        
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.lower().endswith(('.md', '.pdf', '.docx', '.txt')):
                    all_files.add(file)
        
        return list(all_files - set(known_files))


# Example usage
if __name__ == "__main__":
    discovery = AutoDiscovery()
    docs = discovery.discover_all()
    
    print(f"\n{'='*60}")
    print("DISCOVERED DOCUMENTS:")
    print(f"{'='*60}\n")
    
    for filename, metadata in docs.items():
        print(f"📄 {filename}")
        print(f"   Topic: {metadata['topic']}")
        print(f"   Priority: {metadata['priority']}")
        print(f"   Keywords: {', '.join(metadata['keywords'][:5])}...")
        print()
