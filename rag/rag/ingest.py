import os
import json
import uuid
from typing import List
from .cache import get_cached_embedding, set_cached_embedding
from .vertex import embed_text
from .db import insert_document, init_db

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
QUEUE_DIR = os.path.join(BASE_DIR, "queue")
os.makedirs(QUEUE_DIR, exist_ok=True)

def queue_documents(docs: List[dict]):
    """Write docs to queue as JSON files for offline-safe ingestion."""
    for d in docs:
        fname = f"{uuid.uuid4().hex}.json"
        path = os.path.join(QUEUE_DIR, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f)

def process_queue():
    """Process queued documents: compute embeddings (with local cache) and insert into Postgres."""
    init_db()
    files = [f for f in os.listdir(QUEUE_DIR) if f.endswith('.json')]
    for fn in files:
        path = os.path.join(QUEUE_DIR, fn)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            text = d.get('content') or d.get('text') or ''
            doc_id = d.get('id') or str(uuid.uuid4())
            metadata = d.get('metadata') or {}

            emb = get_cached_embedding(text)
            if not emb:
                emb = embed_text(text)
                set_cached_embedding(text, emb)

            insert_document(doc_id, text, metadata, emb)
            # move/delete queue file
            os.remove(path)
        except Exception as e:
            print(f"Failed to process {path}: {e}")
