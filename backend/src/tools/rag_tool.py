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

    def __init__(self, document_path_or_content: str, is_file_path: bool = True, additional_documents: Optional[List[str]] = None):
        # Load settings
        self.settings = Settings()
        """
        Initialize the RAG tool with a document.
        
        Args:
            document_path_or_content: Path to document file or raw document content
            is_file_path: Whether the first argument is a file path (True) or raw content (False)
            additional_documents: List of additional document paths to load
        """
        # OPTIMIZED FOR SPEED - Smaller chunks and overlap for faster processing
        self.processor = DocumentProcessor(chunk_size=400, chunk_overlap=50)
        self.vector_store = VectorStore(
            embedding_dim=768)  # Google embedding dimension

        # Initialize cache if enabled
        self.cache = RAGCache() if self.settings.rag_cache_enabled else None

        # Process the main document
        if is_file_path and os.path.exists(document_path_or_content):
            documents = self.processor.load_file(document_path_or_content)
        else:
            # Treat as raw content
            documents = self.processor.load_text(
                document_path_or_content,
                metadata={"source": "static_content"}
            )

        # Add main document to vector store
        self.vector_store.add_documents(documents)
        total_chunks = len(documents)

        # Process additional documents if provided (optional)
        if additional_documents and len(additional_documents) > 0:
            for doc_path in additional_documents:
                if os.path.exists(doc_path):
                    try:
                        additional_docs = self.processor.load_file(doc_path)
                        self.vector_store.add_documents(additional_docs)
                        total_chunks += len(additional_docs)
                        print(
                            f"Loaded additional document: {doc_path} ({len(additional_docs)} chunks)")
                    except Exception as e:
                        print(
                            f"Error loading additional document {doc_path}: {e}")
                else:
                    print(f"Additional document not found: {doc_path}")

        # Store the number of chunks for logging
        self.num_chunks = total_chunks
        print(
            f"RAG Tool initialized with {self.num_chunks} total document chunks")

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
            document_path: Optional document path for fallback

        Returns:
            Loaded RAGTool instance
        """
        try:
            # Try to load from disk
            vector_store = VectorStore.load(directory)
            rag_tool = cls.__new__(cls)
            rag_tool.settings = Settings()
            rag_tool.processor = DocumentProcessor(
                chunk_size=400, chunk_overlap=50)
            rag_tool.vector_store = vector_store
            rag_tool.cache = RAGCache() if rag_tool.settings.rag_cache_enabled else None
            rag_tool.num_chunks = len(vector_store.documents)
            return rag_tool
        except Exception as e:
            print(f"Error loading RAG tool from disk: {e}")
            # Fallback to loading from document
            if document_path:
                return cls(document_path)
            else:
                raise e
