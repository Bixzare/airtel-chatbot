"""
RAG retrieval tool for vector similarity search.
"""

from .base_tool import BaseTool
from src.rag.document_processor import DocumentProcessor
from src.rag.vector_store import VectorStore
from src.rag.cache import RAGCache
from src.config.settings import Settings
from typing import List, Optional
import os


class RAGTool(BaseTool):
    """RAG tool that retrieves relevant chunks using vector similarity search."""
    name = "rag_search"
    description = "Search the knowledge base for relevant information."

    def __init__(self, document_path_or_content: str, is_file_path: bool = True):
        # Load settings
        self.settings = Settings()
        """
        Initialize the RAG tool with a document.
        
        Args:
            document_path_or_content: Path to document file or raw document content
            is_file_path: Whether the first argument is a file path (True) or raw content (False)
        """
        # OPTIMIZED FOR SPEED - Smaller chunks and overlap for faster processing
        self.processor = DocumentProcessor(chunk_size=400, chunk_overlap=50)
        self.vector_store = VectorStore(
            embedding_dim=768)  # Google embedding dimension

        # Initialize cache if enabled
        self.cache = RAGCache() if self.settings.rag_cache_enabled else None

        # Process the document
        if is_file_path and os.path.exists(document_path_or_content):
            documents = self.processor.load_file(document_path_or_content)
        else:
            # Treat as raw content
            documents = self.processor.load_text(
                document_path_or_content,
                metadata={"source": "static_content"}
            )

        # Add to vector store
        self.vector_store.add_documents(documents)

        # Store the number of chunks for logging
        self.num_chunks = len(documents)
        print(f"RAG Tool initialized with {self.num_chunks} document chunks")

    def __call__(self, query: str) -> List[str]:
        """
        Search for relevant document chunks based on the query.

        Args:
            query: The search query

        Returns:
            List of relevant document texts
        """
        try:
            # Check cache first for faster responses
            if self.cache:
                cached_result = self.cache.get(query)
                if cached_result:
                    return cached_result

            # Get similar documents - OPTIMIZED FOR SPEED (reduced k)
            results = self.vector_store.similarity_search(query, k=2)

            if not results:
                return ["No specific information found in the knowledge base for this query."]

            # Extract texts from results
            texts = [result["text"] for result in results]

            # Cache the result for future requests
            if self.cache:
                self.cache.set(query, texts)

            return texts

        except Exception as e:
            print(f"Error in RAG search: {e}")
            return ["Error retrieving information from the knowledge base."]

    def save(self, directory: str):
        """Save the vector store to disk."""
        self.vector_store.save(directory)

    @classmethod
    def load(cls, directory: str, document_path: Optional[str] = None):
        """
        Load a RAG tool from disk.

        Args:
            directory: Directory containing the saved vector store
            document_path: Optional path to document (for metadata only)

        Returns:
            Loaded RAGTool instance
        """
        # Create a minimal instance
        if document_path:
            instance = cls(document_path, is_file_path=False)
        else:
            instance = cls("", is_file_path=False)

        # Replace the vector store with the loaded one
        instance.vector_store = VectorStore.load(directory)
        instance.num_chunks = len(instance.vector_store.documents)

        return instance
