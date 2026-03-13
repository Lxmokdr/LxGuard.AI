
import os
import sys
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import numpy as np

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import SessionLocal, engine
from api.models import DocumentChunk

def generate_embeddings():
    """
    Generate embeddings for all document chunks that don't have them yet.
    """
    print("🧬 Starting embedding generation...")
    
    # 1. Initialize Model
    print("📥 Loading Embedding Model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 2. Connect to DB
    db: Session = SessionLocal()
    
    try:
        # 3. Fetch chunks without embeddings
        chunks = db.query(DocumentChunk).filter(DocumentChunk.embedding == None).all()
        print(f"📄 Found {len(chunks)} chunks requiring embeddings")
        
        if not chunks:
            print("✅ All chunks already have embeddings.")
            return

        # 4. Process in batches
        batch_size = 32
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            texts = [c.content for c in batch]
            
            # Generate embeddings
            print(f"  ⚡ Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}...")
            embeddings = model.encode(texts)
            
            # Update DB
            for chunk, emb in zip(batch, embeddings):
                # Convert to list for pgvector
                chunk.embedding = emb.tolist()
            
            db.commit()
            print(f"  ✅ Batch {i//batch_size + 1} committed")
            
        print("🎉 Embedding generation complete!")
        
    except Exception as e:
        print(f"❌ Error during embedding generation: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_embeddings()
