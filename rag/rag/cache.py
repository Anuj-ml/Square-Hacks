import os
import json
import hashlib
from threading import Lock

_lock = Lock()

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
EMBED_FILE = os.path.join(CACHE_DIR, "embeddings.json")

def _load_cache():
    if not os.path.exists(EMBED_FILE):
        return {}
    with open(EMBED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_cache(d):
    with open(EMBED_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f)

def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_cached_embedding(text: str):
    key = _hash_text(text)
    with _lock:
        d = _load_cache()
        return d.get(key)

def set_cached_embedding(text: str, embedding):
    key = _hash_text(text)
    with _lock:
        d = _load_cache()
        d[key] = embedding
        _save_cache(d)
