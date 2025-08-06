"""
Configuration settings for the RAG agent.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    # Embedding settings
    embedding_model: str = "text-embedding-004"

    # Document processing settings - OPTIMIZED FOR SPEED
    chunk_size: int = 800  # Reduced from 1000 for faster processing
    chunk_overlap: int = 100  # Reduced from 200
    max_results: int = 3  # Reduced from 5 for faster retrieval
    similarity_threshold: float = 0.6  # Reduced from 0.7 for more results

    # Memory settings
    # Path to database for future long-term memory (not used with MemorySaver)
    checkpoint_db_path: str = None
    session_timeout_minutes: int = int(
        os.environ.get("SESSION_TIMEOUT_MINUTES", 30))
    max_history_tokens: int = 3000  # Reduced from 4000 for faster processing

    # Performance optimization settings
    # Reduced from 30 seconds
    llm_timeout: int = int(os.environ.get("LLM_TIMEOUT", 20))
    rag_cache_enabled: bool = os.environ.get(
        "RAG_CACHE_ENABLED", "true").lower() == "true"
    max_concurrent_requests: int = int(
        os.environ.get("MAX_CONCURRENT_REQUESTS", 10))
