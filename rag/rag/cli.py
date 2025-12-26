try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Diagnostic: print env values for debugging
import os
gemini_key = os.environ.get("VITE_GEMINI_API_KEY") or os.environ.get("VERTEX_API_KEY")
print("[DEBUG] GEMINI_API_KEY:", gemini_key[:20] + "..." if gemini_key else None)
import argparse
import os
import json
import sys
import math
import re
from typing import List

from .ingest import queue_documents, process_queue
from .cache import get_cached_embedding, set_cached_embedding
from .vertex import embed_text, generate_text
from .db import get_all_documents, search_candidates_by_keyword, init_db


def cosine_sim(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return -1.0
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    if na == 0 or nb == 0:
        return -1.0
    return dot/(na*nb)


def build_rag_prompt(question: str, docs: List[dict]) -> str:
    s = "Use the following documents to answer the question. If answer not found, say you don't know.\n\n"
    for i, d in enumerate(docs, 1):
        s += f"Document {i}:\n{d['content']}\n\n"
    s += f"Question: {question}\nAnswer concisely with references to the documents when applicable."
    return s


def cmd_ingest(args):
    path = args.file
    if not os.path.exists(path):
        print("File not found:", path); sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        docs = json.load(f)
    if not isinstance(docs, list):
        print("Input file must contain a JSON array of documents."); sys.exit(1)
    queue_documents(docs)
    print(f"Queued {len(docs)} documents for ingestion.")


def cmd_process_queue(args):
    process_queue()
    print("Queue processed (processed files removed on success).")


def generate_offline_response(question: str, docs: List[dict]) -> str:
    """Generate a simple response when API is unavailable."""
    if not docs:
        return "I don't have relevant information to answer this question in offline mode."
    
    response = f"Based on the available documents, here's what I found related to '{question}':\n\n"
    for i, doc in enumerate(docs, 1):
        content = doc.get('content', '')[:200]  # First 200 chars
        if len(doc.get('content', '')) > 200:
            content += "..."
        response += f"{i}. {content}\n\n"
    
    response += "Note: This is a simplified response due to API rate limiting. For better answers, please try again later."
    return response


def retrieve_relevant(query: str, top_k: int = 3):
    def load_local_documents():
        # Try a couple of fallback locations for local documents
        candidates = []
        possible = [
            os.path.join(os.path.dirname(__file__), '..', 'local_documents.json'),
            os.path.join(os.path.dirname(__file__), '..', 'data', 'test_docs.json')
        ]
        for p in possible:
            p = os.path.abspath(p)
            if os.path.exists(p):
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        docs = json.load(f)
                    for d in docs:
                        # normalize to expected schema
                        candidates.append({
                            'id': d.get('id'),
                            'content': d.get('content') or d.get('text') or '',
                            'metadata': d.get('metadata') or {},
                            'embedding': d.get('embedding') if 'embedding' in d else None
                        })
                    return candidates
                except Exception:
                    continue
        return []

    # try database-backed keyword search; if DB is unavailable, fall back to local files
    words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 3]
    candidates = []
    db_error = None
    try:
        print(f"[DEBUG] Searching PostgreSQL for keywords: {words[:3]}")
        for w in words[:3]:
            candidates.extend(search_candidates_by_keyword(w, limit=50))
        if not candidates:
            print("[DEBUG] No keyword matches, fetching all documents from PostgreSQL")
            candidates = get_all_documents()
        print(f"[DEBUG] Found {len(candidates)} documents from PostgreSQL")
    except Exception as e:
        db_error = str(e)
        print(f"[DEBUG] PostgreSQL error: {db_error}")
        print("[DEBUG] Falling back to local documents")
        candidates = load_local_documents()
        print(f"[DEBUG] Found {len(candidates)} local documents")

    # try to obtain a query embedding (use cache first). If Vertex is not available,
    # fall back to token-overlap scoring below.
    q_emb = get_cached_embedding(query)
    got_embedding = True
    if not q_emb:
        try:
            q_emb = embed_text(query)
            set_cached_embedding(query, q_emb)
        except Exception:
            q_emb = None
            got_embedding = False

    # compute similarity (embedding cosine when possible, else token overlap heuristic)
    q_tokens = set(re.findall(r"\w+", query.lower()))
    scored = []
    for c in candidates:
        emb = c.get('embedding')
        sim = 0.0
        if emb and q_emb:
            try:
                sim = cosine_sim(q_emb, emb)
            except Exception:
                sim = 0.0
        elif not got_embedding:
            # token overlap heuristic
            d_tokens = set(re.findall(r"\w+", c.get('content', '').lower()))
            if not d_tokens:
                sim = 0.0
            else:
                sim = len(q_tokens & d_tokens) / max(1, len(q_tokens | d_tokens))
        else:
            sim = 0.0
        scored.append((sim, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [s[1] for s in scored[:top_k]]
    return top


def cmd_chat(args):
    print("RAG CLI Chat — type a question, empty line to exit.")
    print("Note: If API is rate limited, system will use offline fallback mode.")
    
    # Test database connection and initialize if needed
    try:
        from .db import init_db, get_all_documents
        print("\n[DEBUG] Testing PostgreSQL connection...")
        init_db()  # Ensure tables exist
        docs = get_all_documents()
        print(f"[DEBUG] PostgreSQL connected successfully. Found {len(docs)} documents in database.")
        if len(docs) == 0:
            print("[WARNING] No documents found in PostgreSQL. You may need to ingest documents first.")
            print("Run: python -m rag.cli ingest --file data/test_docs.json")
            print("Then: python -m rag.cli process-queue")
    except Exception as e:
        print(f"[ERROR] PostgreSQL connection failed: {e}")
        print("[INFO] System will fall back to local documents if available.")
    while True:
        q = input('\n> ').strip()
        if not q:
            print("Goodbye.")
            break
        docs = retrieve_relevant(q, top_k=3)
        prompt = build_rag_prompt(q, docs)
        try:
            resp = generate_text(prompt)
        except Exception as e:
            error_msg = str(e)
            if "rate limit" in error_msg.lower() or "429" in error_msg:
                print("\n--- Offline Mode (API Rate Limited) ---\n")
                resp = generate_offline_response(q, docs)
            else:
                print("Generation error:", e)
                continue
        print('\n--- Response ---\n')
        print(resp)


def main():
    p = argparse.ArgumentParser(prog='rag')
    sub = p.add_subparsers(dest='cmd')

    ing = sub.add_parser('ingest')
    ing.add_argument('--file', required=True, help='JSON file with array of documents (each should have id/content/metadata)')
    ing.set_defaults(func=cmd_ingest)

    proc = sub.add_parser('process-queue')
    proc.set_defaults(func=cmd_process_queue)

    chat = sub.add_parser('chat')
    chat.set_defaults(func=cmd_chat)

    args = p.parse_args()
    if not hasattr(args, 'func'):
        p.print_help(); sys.exit(1)
    args.func(args)


if __name__ == '__main__':
    main()
