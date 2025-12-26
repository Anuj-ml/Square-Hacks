"""
Script to ingest medical documents into RAG system
Run this after starting the backend server to populate the knowledge base
"""
import sys
import os

# Add rag directory to Python path
RAG_DIR = os.path.join(os.path.dirname(__file__), "..", "rag")
sys.path.insert(0, RAG_DIR)

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    # Also load from rag/.env if it exists
    rag_env = os.path.join(RAG_DIR, ".env")
    if os.path.exists(rag_env):
        load_dotenv(rag_env)
except ImportError:
    print("Warning: python-dotenv not installed")

import json
from rag.ingest import queue_documents, process_queue

def main():
    print("=" * 60)
    print("RAG Medical Documents Ingestion Script")
    print("=" * 60)
    print()
    
    # Path to medical documents
    docs_path = os.path.join(RAG_DIR, "data", "medical_documents.json")
    
    if not os.path.exists(docs_path):
        print(f"❌ Error: Medical documents not found at {docs_path}")
        return 1
    
    print(f"📄 Loading documents from: {docs_path}")
    
    try:
        with open(docs_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        print(f"✓ Loaded {len(documents)} documents")
        print()
        
        # Queue documents
        print("📝 Queueing documents for ingestion...")
        queue_documents(documents)
        print("✓ Documents queued successfully")
        print()
        
        # Process queue (create embeddings and insert into database)
        print("🔄 Processing queue (creating embeddings and inserting into database)...")
        print("   This may take a few minutes...")
        process_queue()
        print()
        print("✓ All documents processed successfully!")
        print()
        print("=" * 60)
        print("RAG system is now ready with medical knowledge base!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
