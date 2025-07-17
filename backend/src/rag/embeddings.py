"""
Google embeddings wrapper for text-embedding-004.
"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

class Embeddings:
    """Wrapper for Google text-embedding-004 model."""
    
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",  # Correct model name format with no tabs
            google_api_key=os.environ.get("GOOGLE_API_KEY"),
            task_type="retrieval_query" # Optimized for retrieval tasks
        )
    
    def embed_query(self, text: str):
        """Embed a query text."""
        return self.embeddings.embed_query(text)
    
    def embed_documents(self, texts: list[str]):
        """Embed a list of document texts."""
        return self.embeddings.embed_documents(texts) 