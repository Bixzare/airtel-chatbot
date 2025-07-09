"""
Configuration settings for the RAG agent.
"""

class Settings:
    embedding_model: str = "text-embedding-004"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_results: int = 5
    similarity_threshold: float = 0.7 