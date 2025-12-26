"""
RAG (Retrieval-Augmented Generation) Service
Provides medical document search and question answering capabilities
"""
import sys
import os
import re
import math
from typing import List, Dict, Any, Optional

# Load environment variables from parent directories
try:
    from dotenv import load_dotenv
    # Load from backend/.env
    backend_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(backend_env):
        load_dotenv(backend_env, override=True)
    
    # Load from rag/.env if it exists
    rag_env = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "rag", ".env")
    if os.path.exists(rag_env):
        load_dotenv(rag_env, override=True)
except ImportError:
    print("Warning: python-dotenv not installed")

# Ensure API keys are in environment before importing RAG modules
if "VITE_GEMINI_API_KEY" not in os.environ and "VERTEX_API_KEY" not in os.environ:
    # Try to get from current environment or config
    if os.environ.get("GOOGLE_API_KEY"):
        os.environ["VITE_GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

# Add rag directory to Python path
RAG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "rag")
if RAG_DIR not in sys.path:
    sys.path.insert(0, RAG_DIR)

try:
    from rag.vertex import embed_text, generate_text
    from rag.db import init_db, get_all_documents, search_candidates_by_keyword, insert_document
    from rag.cache import get_cached_embedding, set_cached_embedding
except ImportError as e:
    print(f"Warning: RAG modules not available: {e}")
    # Define stub functions for when RAG is not available
    def embed_text(text): raise NotImplementedError("RAG not available")
    def generate_text(prompt): raise NotImplementedError("RAG not available")
    def init_db(): pass
    def get_all_documents(): return []
    def search_candidates_by_keyword(kw, limit): return []
    def insert_document(*args): pass
    def get_cached_embedding(text): return None
    def set_cached_embedding(text, emb): pass


class RagService:
    """Service for RAG-based medical document search and QA"""
    
    def __init__(self):
        self.initialized = False
        self.document_count = 0
        
    def initialize(self) -> Dict[str, Any]:
        """Initialize RAG system - create tables and check status"""
        try:
            init_db()
            docs = get_all_documents()
            self.document_count = len(docs)
            self.initialized = True
            return {
                "status": "success",
                "document_count": self.document_count,
                "message": f"RAG system initialized with {self.document_count} documents"
            }
        except Exception as e:
            return {
                "status": "error",
                "document_count": 0,
                "message": f"Failed to initialize RAG: {str(e)}"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get RAG system health status"""
        try:
            docs = get_all_documents()
            return {
                "status": "healthy",
                "initialized": self.initialized,
                "document_count": len(docs),
                "database_connected": True
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "initialized": False,
                "document_count": 0,
                "database_connected": False,
                "error": str(e)
            }
    
    def query(
        self, 
        question: str, 
        context: Optional[Dict[str, Any]] = None,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Query the RAG system with a question
        
        Args:
            question: User's question
            context: Optional context from dashboard (AQI, bed availability, etc.)
            top_k: Number of documents to retrieve
            
        Returns:
            Dict with answer, sources, confidence, and metadata
        """
        try:
            # Enhance question with dashboard context if available
            enhanced_question = self._enhance_question_with_context(question, context)
            
            # Retrieve relevant documents
            relevant_docs = self._retrieve_relevant(enhanced_question, top_k)
            
            if not relevant_docs:
                return {
                    "answer": "I don't have enough information in my knowledge base to answer this question. Please try rephrasing or ask about hospital operations, medical procedures, or health emergencies.",
                    "sources": [],
                    "confidence": 0.0,
                    "mode": "no_documents"
                }
            
            # Build RAG prompt
            prompt = self._build_rag_prompt(question, relevant_docs, context)
            
            # Generate answer
            try:
                answer = generate_text(prompt, temperature=0.2, max_output_tokens=512)
                mode = "rag"
            except Exception as e:
                # Fallback to offline mode if API fails (rate limiting, SSL errors, network issues)
                error_msg = str(e).lower()
                if any(x in error_msg for x in ["rate limit", "429", "ssl", "connection", "timeout", "max retries"]):
                    answer = self._generate_offline_response(question, relevant_docs)
                    mode = "offline"
                else:
                    raise
            
            # Extract source information
            sources = [
                {
                    "id": doc.get("id", "unknown"),
                    "content": doc.get("content", "")[:200] + "...",
                    "metadata": doc.get("metadata", {})
                }
                for doc in relevant_docs
            ]
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": self._calculate_confidence(relevant_docs, enhanced_question),
                "mode": mode,
                "context_used": context is not None
            }
            
        except Exception as e:
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "mode": "error",
                "error": str(e)
            }
    
    def ingest_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ingest new documents into RAG system
        
        Args:
            documents: List of documents with 'id', 'content', 'metadata'
            
        Returns:
            Dict with status and count of ingested documents
        """
        try:
            ingested = 0
            failed = []
            
            for doc in documents:
                try:
                    doc_id = doc.get("id", str(hash(doc.get("content", ""))))
                    content = doc.get("content", "")
                    metadata = doc.get("metadata", {})
                    
                    # Get or create embedding
                    embedding = get_cached_embedding(content)
                    if not embedding:
                        embedding = embed_text(content)
                        set_cached_embedding(content, embedding)
                    
                    # Insert into database
                    insert_document(doc_id, content, metadata, embedding)
                    ingested += 1
                    
                except Exception as e:
                    failed.append({"id": doc.get("id", "unknown"), "error": str(e)})
            
            self.document_count = len(get_all_documents())
            
            return {
                "status": "success",
                "ingested": ingested,
                "failed": len(failed),
                "total_documents": self.document_count,
                "errors": failed
            }
            
        except Exception as e:
            return {
                "status": "error",
                "ingested": 0,
                "failed": len(documents),
                "error": str(e)
            }
    
    # Private helper methods
    
    def _enhance_question_with_context(
        self, 
        question: str, 
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Add dashboard context to question for better retrieval"""
        if not context:
            return question
        
        context_parts = []
        if "aqi" in context:
            context_parts.append(f"Current AQI: {context['aqi']}")
        if "bed_capacity" in context:
            context_parts.append(f"Bed capacity: {context['bed_capacity']}%")
        if "active_alerts" in context:
            context_parts.append(f"Active alerts: {context['active_alerts']}")
        
        if context_parts:
            return f"{question} [Context: {', '.join(context_parts)}]"
        return question
    
    def _retrieve_relevant(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Retrieve relevant documents using embeddings or keyword search"""
        # Extract keywords for fallback search
        words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 3]
        candidates = []
        
        try:
            # Try keyword search first
            for word in words[:3]:
                candidates.extend(search_candidates_by_keyword(word, limit=50))
            
            # If no results, get all documents
            if not candidates:
                candidates = get_all_documents()
                
        except Exception as e:
            print(f"Database error during retrieval: {e}")
            return []
        
        if not candidates:
            return []
        
        # Get query embedding for similarity scoring
        query_embedding = get_cached_embedding(query)
        if not query_embedding:
            try:
                query_embedding = embed_text(query)
                set_cached_embedding(query, query_embedding)
            except Exception:
                query_embedding = None
        
        # Score documents
        scored = []
        query_tokens = set(re.findall(r"\w+", query.lower()))
        
        for candidate in candidates:
            doc_embedding = candidate.get("embedding")
            
            if doc_embedding and query_embedding:
                # Use cosine similarity
                sim = self._cosine_similarity(query_embedding, doc_embedding)
            else:
                # Fallback to token overlap
                doc_tokens = set(re.findall(r"\w+", candidate.get("content", "").lower()))
                if not doc_tokens:
                    sim = 0.0
                else:
                    sim = len(query_tokens & doc_tokens) / max(1, len(query_tokens | doc_tokens))
            
            scored.append((sim, candidate))
        
        # Sort by similarity and return top-k
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not a or not b or len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def _build_rag_prompt(
        self, 
        question: str, 
        docs: List[Dict[str, Any]], 
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for RAG generation"""
        prompt = "You are a medical AI assistant for Arogya-Swarm hospital management system. "
        prompt += "Use the following documents to answer the question. "
        prompt += "If the answer is not in the documents, say you don't know.\n\n"
        
        # Add dashboard context if available
        if context:
            prompt += "Current System Status:\n"
            if "aqi" in context:
                prompt += f"- Air Quality Index: {context['aqi']}\n"
            if "bed_capacity" in context:
                prompt += f"- Bed Capacity: {context['bed_capacity']}%\n"
            if "active_alerts" in context:
                prompt += f"- Active Alerts: {context['active_alerts']}\n"
            prompt += "\n"
        
        # Add retrieved documents
        for i, doc in enumerate(docs, 1):
            content = doc.get("content", "")
            prompt += f"Document {i}:\n{content}\n\n"
        
        prompt += f"Question: {question}\n\n"
        prompt += "Answer concisely and mention which document(s) you're referencing. "
        prompt += "If discussing medical procedures, include safety considerations."
        
        return prompt
    
    def _generate_offline_response(
        self, 
        question: str, 
        docs: List[Dict[str, Any]]
    ) -> str:
        """Generate simple response when API is unavailable"""
        if not docs:
            return "I searched the medical knowledge base but couldn't find relevant documents for your question. Try asking about: hospital surge protocols, bed management, staff coordination, infection control, or emergency procedures."
        
        # Extract the most relevant excerpts
        response = "Based on the medical knowledge base, here's the relevant information:\n\n"
        
        for i, doc in enumerate(docs, 1):
            doc_id = doc.get("id", "").replace("_", " ").title()
            content = doc.get("content", "")
            
            # Show full content for most relevant document, excerpts for others
            if i == 1:
                response += f"📄 **{doc_id}**\n{content}\n\n"
            else:
                excerpt = content[:400] if len(content) > 400 else content
                if len(content) > 400:
                    excerpt += "..."
                response += f"📄 **{doc_id}**\n{excerpt}\n\n"
        
        response += "💡 *Tip: These are direct excerpts from our medical protocols database.*"
        return response
    
    def _calculate_confidence(
        self, 
        docs: List[Dict[str, Any]], 
        query: str
    ) -> float:
        """Calculate confidence score based on retrieval quality"""
        if not docs:
            return 0.0
        
        # Simple heuristic: average similarity of top documents
        # In production, could use more sophisticated methods
        query_tokens = set(re.findall(r"\w+", query.lower()))
        
        similarities = []
        for doc in docs:
            doc_tokens = set(re.findall(r"\w+", doc.get("content", "").lower()))
            if doc_tokens:
                sim = len(query_tokens & doc_tokens) / max(1, len(query_tokens | doc_tokens))
                similarities.append(sim)
        
        if not similarities:
            return 0.0
        
        avg_sim = sum(similarities) / len(similarities)
        return round(min(avg_sim * 100, 95.0), 1)


# Global RAG service instance
_rag_service = None

def get_rag_service() -> RagService:
    """Get or create global RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RagService()
    return _rag_service
