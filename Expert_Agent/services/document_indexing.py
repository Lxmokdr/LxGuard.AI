import os
import re
from typing import List

import docx
import pypdf
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from api.models import Document as DBDocument, DocumentChunk as DBDocumentChunk


class DocumentIndexingError(Exception):
    """Base error for document indexing failures."""


class DocumentFileNotFound(DocumentIndexingError):
    """Raised when the physical document file cannot be located."""


class DocumentExtractionError(DocumentIndexingError):
    """Raised when text cannot be extracted from the document."""


class DocumentChunkingError(DocumentIndexingError):
    """Raised when the extracted text cannot be chunked."""


_embedder_model: SentenceTransformer | None = None


def get_embedder() -> SentenceTransformer:
    """
    Return a process-wide cached embedding model.

    Using a singleton here avoids re-loading the SentenceTransformer
    model on every request, which is expensive and unnecessary.
    """
    global _embedder_model
    if _embedder_model is None:
        _embedder_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder_model


def extract_text(filepath: str) -> str:
    """
    Extract text from PDF, DOCX, MD, or TXT files.
    """
    filename = os.path.basename(filepath).lower()
    print(f"📄 [Indexing] Extracting text from {filepath}...")
    try:
        if filename.endswith(".pdf"):
            reader = pypdf.PdfReader(filepath)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if not text.strip():
                print(f"⚠️ [Indexing] PDF extraction returned empty text for {filename}. Possibly scanned or encrypted.")
            return text
        if filename.endswith(".docx"):
            doc = docx.Document(filepath)
            return "\n".join(para.text for para in doc.paragraphs)
        if filename.endswith((".md", ".txt")):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as exc:
        print(f"❌ [Indexing] Error extracting {filepath}: {exc}")
    return ""


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
    """
    Paragraph-aware chunking with overlap.

    Strategy:
    1. Split on blank lines to preserve paragraph/list structure.
    2. Within each paragraph, further split on sentence endings and newlines.
    3. Group segments into chunks up to `chunk_size` chars.
    4. Carry the last `overlap` chars of each chunk into the next for context.

    Edge cases:
    - Empty / whitespace-only text  → returns []
    - Text shorter than chunk_size  → returns as a single chunk (no overlap needed)
    - Very long paragraphs          → split by sentence boundaries inside them
    """
    if not text or not text.strip():
        return []

    # --- Step 1: paragraph split (preserves bullet lists, numbered lists, etc.) ---
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        return []

    # --- Step 2: segment each paragraph into lines / sentences ---
    segments: List[str] = []
    for para in paragraphs:
        # Normalise only horizontal whitespace inside the paragraph
        para_clean = re.sub(r"[ \t]+", " ", para)
        # Split on sentence endings OR embedded newlines (bullets, list items)
        parts = re.split(r"(?<=[.!?]) +|\n", para_clean)
        segments.extend(p.strip() for p in parts if p.strip())

    # Short-document fast path: everything fits in one chunk
    full_text = " ".join(segments)
    if len(full_text) <= chunk_size:
        return [full_text]

    # --- Step 3: group segments into chunks with overlap ---
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    for seg in segments:
        if current_len + len(seg) > chunk_size and current:
            chunk_str = " ".join(current)
            chunks.append(chunk_str)
            # Carry the tail of the last chunk for context continuity
            carry = chunk_str[-overlap:] if len(chunk_str) > overlap else chunk_str
            current = [carry, seg]
            current_len = len(carry) + len(seg)
        else:
            current.append(seg)
            current_len += len(seg)

    if current:
        chunks.append(" ".join(current))

    return chunks


def _find_document_path(db_doc: DBDocument, source_dir: str) -> str:
    """
    Locate the physical file for a document.
    """
    # Use the absolute path of the source_dir if provided, otherwise assume 'docs'
    base_search = os.path.abspath(source_dir)
    
    possible_dirs = [
        base_search,
        os.path.join(os.getcwd(), source_dir),
        "/app/docs", # Docker standard
        "/home/lxmix/Downloads/projetiia/projet/docs", # Host standard
    ]

    print(f"🔍 [Indexing] Searching for {db_doc.source} in {len(possible_dirs)} base paths...")
    
    for attempt_dir in possible_dirs:
        if not os.path.exists(attempt_dir):
            continue
        for root, _, files in os.walk(attempt_dir):
            if db_doc.source in files:
                found_path = os.path.join(root, db_doc.source)
                print(f"✅ [Indexing] Found physical file: {found_path}")
                return found_path

    print(f"❌ [Indexing] Physical file for '{db_doc.source}' NOT FOUND.")
    raise DocumentFileNotFound(
        f"Physical file for '{db_doc.source}' not found. Looked in: {possible_dirs}"
    )


def reindex_document(db: Session, db_doc: DBDocument, source_dir: str) -> int:
    """
    Re-index a single document:
      - find the physical file
      - extract text
      - chunk
      - generate embeddings
      - replace existing chunks in the database

    Returns the number of chunks created.
    """
    filepath = _find_document_path(db_doc, source_dir)

    content = extract_text(filepath)
    if not content:
        raise DocumentExtractionError("Could not extract text from document")

    chunks = chunk_text(content)
    if not chunks:
        raise DocumentChunkingError("Document resulted in 0 chunks")

    model = get_embedder()

    # Replace existing chunks for this document.
    db.query(DBDocumentChunk).filter(DBDocumentChunk.document_id == db_doc.id).delete()

    # Determine domain_id fallback
    from api.models import Domain
    domain_id = db_doc.domain_id
    if not domain_id:
        first_domain = db.query(Domain).first()
        domain_id = first_domain.id if first_domain else None

    for index, chunk_text_content in enumerate(chunks):
        embedding = model.encode(chunk_text_content).tolist()
        new_chunk = DBDocumentChunk(
            document_id=db_doc.id,
            # Use determined domain_id; if still None, table constraint might fail if not nullable
            domain_id=domain_id,
            content=chunk_text_content,
            chunk_index=index,
            embedding=embedding,
        )
        db.add(new_chunk)

    db.commit()
    return len(chunks)


def remove_document(db: Session, doc_source: str) -> bool:
    """
    Remove a document and its associated chunks from the database
    based on its source filename.
    """
    db_doc = db.query(DBDocument).filter(DBDocument.source == doc_source).first()
    if not db_doc:
        return False

    # Chunks will be deleted via cascade if configured, 
    # but we'll do it explicitly here for safety if not.
    db.query(DBDocumentChunk).filter(DBDocumentChunk.document_id == db_doc.id).delete()
    db.delete(db_doc)
    db.commit()
    print(f"🗑 Removed document '{doc_source}' from database.")
    return True
