-- Migration to fix document_chunks schema
DROP TABLE IF EXISTS document_chunks CASCADE;

CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    domain_id TEXT REFERENCES domains(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    embedding VECTOR(384),
    chunk_index INTEGER
);
