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
    
    # Document processing settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_results: int = 5
    similarity_threshold: float = 0.7
    
    # Memory settings
    checkpoint_db_path: str = None  # Path to database for future long-term memory (not used with MemorySaver)
    session_timeout_minutes: int = int(os.environ.get("SESSION_TIMEOUT_MINUTES", 30))
    max_history_tokens: int = 4000 