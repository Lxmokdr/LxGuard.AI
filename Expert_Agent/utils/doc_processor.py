"""
Layout-Aware Document Processor
Responsibilities:
- Advanced PDF extraction using PyMuPDF (fitz)
- Section detection and logical structure analysis
- Multi-column and table handling
- Metadata extraction (title, author, dates)
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

class DocumentProcessor:
    """
    Advanced Document Processor for Ontology Induction.
    Supports layout-aware extraction for PDF and Markdown.
    """
    
    def __init__(self):
        if not fitz:
            print("⚠️  PyMuPDF (fitz) not installed. Falling back to basic extraction.")
            
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document and return structural data.
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        
        result = {
            "file_name": path.name,
            "file_path": str(path),
            "sections": [],
            "metadata": {},
            "raw_text": ""
        }
        
        if ext == ".pdf":
            result.update(self._process_pdf(file_path))
        elif ext == ".md":
            result.update(self._process_markdown(file_path))
        else:
            # Basic text fallback
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                result["raw_text"] = text
                result["sections"] = [{"title": "Content", "content": text}]
                
        return result

    def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extract structural text from PDF using PyMuPDF.
        """
        if not fitz:
            return {"error": "PyMuPDF not available"}
            
        doc = fitz.open(file_path)
        sections = []
        current_section = {"title": "Introduction", "content": ""}
        full_text = ""
        
        # Try to extract metadata
        metadata = doc.metadata
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Layout-aware extraction (blocks preserve structure better than raw text)
            blocks = page.get_text("blocks")
            
            for block in blocks:
                # block[4] is the text content
                text = block[4].strip()
                if not text:
                    continue
                
                # Simple heuristic for section detection: 
                # Bold/Large text or CAPS usually indicates a header
                # (In PyMuPDF blocks, we'd ideally check font size/weight from 'dict' or 'rawdict')
                if self._is_likely_header(text):
                    if current_section["content"].strip():
                        sections.append(current_section)
                    current_section = {"title": text, "content": ""}
                else:
                    current_section["content"] += text + "\n"
                    full_text += text + "\n"
                    
        if current_section["content"].strip():
            sections.append(current_section)
            
        return {
            "sections": sections,
            "metadata": metadata,
            "raw_text": full_text
        }

    def _process_markdown(self, file_path: str) -> Dict[str, Any]:
        """
        Extract structural text from Markdown.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        sections = []
        current_section = {"title": "Preamble", "content": ""}
        full_text = "".join(lines)
        
        for line in lines:
            header_match = re.match(r'^(#+)\s+(.+)$', line)
            if header_match:
                if current_section["content"].strip():
                    sections.append(current_section)
                current_section = {"title": header_match.group(2).strip(), "content": ""}
            else:
                current_section["content"] += line
                
        if current_section["content"].strip():
            sections.append(current_section)
            
        return {
            "sections": sections,
            "raw_text": full_text
        }

    def _is_likely_header(self, text: str) -> bool:
        """
        Simple heuristic to detect if a text block is a section header in a PDF.
        """
        # Headers are usually short and don't end with periods
        if len(text) > 80:
            return False
        
        # Often all caps or Title Case
        if text.isupper():
            return True
            
        # Common section titles
        headers = ["ABSTRACT", "INTRODUCTION", "REFERENCES", "CONCLUSION", "METHODS", "RESULTS"]
        if any(h in text.upper() for h in headers):
            return True
            
        # Numbered sections like "1. Overview"
        if re.match(r'^\d+(\.\d+)*\s+[A-Z]', text):
            return True
            
        return False

if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 1:
        proc = DocumentProcessor()
        data = proc.process(sys.argv[1])
        print(f"Processed: {data['file_name']}")
        print(f"Sections found: {len(data['sections'])}")
        for s in data['sections']:
            print(f"- {s['title']} ({len(s['content'])} chars)")
