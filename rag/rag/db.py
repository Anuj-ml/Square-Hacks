import os
import json
import psycopg2
from psycopg2.extras import Json
from typing import List, Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(DATABASE_URL)

def init_db():
    """Create documents table if it doesn't exist."""
    sql = """
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        metadata JSONB,
        embedding JSONB
    );
    """
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql)
    finally:
        conn.close()

def insert_document(doc_id: str, content: str, metadata: Dict[str, Any], embedding: List[float]):
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO documents (id, content, metadata, embedding) VALUES (%s,%s,%s,%s) ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content, metadata = EXCLUDED.metadata, embedding = EXCLUDED.embedding",
                    (doc_id, content, Json(metadata), Json(embedding) if embedding is not None else None)
                )
    finally:
        conn.close()

def get_all_documents():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, content, metadata, embedding FROM documents")
            rows = cur.fetchall()
            return [ {"id": r[0], "content": r[1], "metadata": r[2], "embedding": r[3]} for r in rows ]
    finally:
        conn.close()

def search_candidates_by_keyword(keyword: str, limit: int = 50):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            pattern = f"%{keyword}%"
            cur.execute("SELECT id, content, metadata, embedding FROM documents WHERE content ILIKE %s LIMIT %s", (pattern, limit))
            rows = cur.fetchall()
            return [ {"id": r[0], "content": r[1], "metadata": r[2], "embedding": r[3]} for r in rows ]
    finally:
        conn.close()
