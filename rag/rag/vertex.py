import os
import requests
from typing import List
import time

# Use Google AI Studio API key (Gemini API)
API_KEY = os.environ.get("VITE_GEMINI_API_KEY") or os.environ.get("VERTEX_API_KEY")  # Support both env var names

if not API_KEY:
    # don't raise here; allow code to provide clearer error later
    pass

def _post(url, json_body, max_retries=3):
    headers = {"Content-Type": "application/json"}
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, json=json_body, headers=headers, timeout=60)
            if resp.status_code == 429:  # Rate limited
                if attempt < max_retries:
                    wait_time = (2 ** attempt) + 1  # Exponential backoff: 2, 5, 9 seconds
                    print(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                wait_time = (2 ** attempt) + 1
                print(f"Request failed, retrying in {wait_time}s... ({e})")
                time.sleep(wait_time)
            else:
                raise

def embed_text(text: str, model: str = "text-embedding-004") -> List[float]:
    """Call Google AI Studio embedding endpoint. Returns list of floats."""
    if not API_KEY:
        raise RuntimeError("VITE_GEMINI_API_KEY or VERTEX_API_KEY must be set in environment (Google AI Studio API key)")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent?key={API_KEY}"
    body = {
        "model": f"models/{model}",
        "content": {
            "parts": [{"text": text}]
        }
    }
    data = _post(url, body)
    # expected shape: { "embedding": {"values": [...]} }
    emb = data.get("embedding", {}).get("values")
    if not emb:
        raise RuntimeError(f"No embedding in response: {data}")
    return emb

def generate_text(prompt: str, model: str = "gemini-2.0-flash-exp", temperature: float = 0.2, max_output_tokens: int = 512) -> str:
    """Call Google AI Studio generation endpoint. Returns generated text."""
    if not API_KEY:
        raise RuntimeError("VITE_GEMINI_API_KEY or VERTEX_API_KEY must be set in environment (Google AI Studio API key)")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    body = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens
        }
    }
    data = _post(url, body)
    # expected shape: { "candidates": [{"content": {"parts": [{"text": "..."}]}}] }
    candidates = data.get("candidates")
    if not candidates:
        raise RuntimeError(f"No generation in response: {data}")
    
    # Extract text from the first candidate
    first_candidate = candidates[0]
    content = first_candidate.get("content", {})
    parts = content.get("parts", [])
    if parts and "text" in parts[0]:
        return parts[0]["text"]
    
    raise RuntimeError(f"Could not extract text from response: {data}")
