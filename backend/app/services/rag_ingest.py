"""Ingest Markdown docs into pgvector. Run: python -m app.services.rag_ingest"""
import os
import glob
import re
from sqlalchemy import create_engine, text
from app.services.llm_service import embed

DOCS_DIR = os.getenv("RAG_DOCS_DIR", "rag_docs")
SYNC_DB_URL = os.getenv("SYNC_DATABASE_URL", "postgresql://wellnexa:wellnexa_secure_password@localhost:5432/wellnexa_db")


def parse_frontmatter(raw: str):
    title = ""
    url = ""
    body = raw
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
    if m:
        fm, body = m.group(1), m.group(2)
        for line in fm.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip().lower()
                v = v.strip().strip('"').strip("'")
                if k == "title":
                    title = v
                elif k == "url":
                    url = v
    return title, url, body


def chunk(text: str, size: int = 500):
    words = text.split()
    for i in range(0, len(words), size):
        yield " ".join(words[i:i+size])


def main():
    engine = create_engine(SYNC_DB_URL)
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rag_chunks (
                id SERIAL PRIMARY KEY,
                doc_title TEXT,
                source_url TEXT,
                chunk TEXT,
                embedding vector(1536)
            )
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS rag_chunks_embedding_idx ON rag_chunks USING hnsw (embedding vector_cosine_ops)"))
    files = glob.glob(os.path.join(DOCS_DIR, "*.md"))
    for f in files:
        raw = open(f, encoding="utf-8").read()
        title, url, body = parse_frontmatter(raw)
        if not title:
            title = os.path.basename(f)
        for c in chunk(body):
            vec = embed(c)
            with engine.begin() as conn:
                conn.execute(text("INSERT INTO rag_chunks (doc_title, source_url, chunk, embedding) VALUES (:t,:u,:c,:e)"),
                             {"t": title, "u": url, "c": c, "e": vec})
    print(f"Ingested {len(files)} docs")


if __name__ == "__main__":
    main()
