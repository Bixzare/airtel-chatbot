"""
In-memory vector store using FAISS.
"""

import faiss
import numpy as np
from typing import List, Dict, Any, Optional
import pickle
import os
from .embeddings import Embeddings

class VectorStore:
    """FAISS-based vector store for document embeddings and similarity search."""
    
    def __init__(self, embedding_dim: int = 768):
        """
        Initialize a new FAISS vector store.
        
        Args:
            embedding_dim: Dimension of the embedding vectors
        """
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)  # L2 distance for similarity
        self.documents = []  # Store document texts and metadata
        self.embeddings_model = Embeddings()
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of dictionaries with 'text' and 'metadata' keys
        """
        if not documents:
            return
        
        # Extract texts for embedding
        texts = [doc["text"] for doc in documents]
        
        # Generate embeddings
        embeddings = self.embeddings_model.embed_documents(texts)
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Add to FAISS index
        self.index.add(embeddings_array)
        
        # Store documents
        self.documents.extend(documents)
    
    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Search for similar documents based on query.
        
        Args:
            query: The search query
            k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        # Embed the query
        query_embedding = self.embeddings_model.embed_query(query)
        query_array = np.array([query_embedding]).astype('float32')
        
        # Ensure k is not larger than the number of documents
        k = min(k, len(self.documents))
        
        if k == 0:
            return []
        
        # Search the index
        distances, indices = self.index.search(query_array, k)
        
        # Prepare results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):  # Ensure index is valid
                doc = self.documents[idx]
                results.append({
                    "text": doc["text"],
                    "metadata": doc["metadata"],
                    "score": float(distances[0][i])
                })
        
        return results
    
    def save(self, directory: str):
        """
        Save the vector store to disk.
        
        Args:
            directory: Directory to save the vector store
        """
        os.makedirs(directory, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, os.path.join(directory, "index.faiss"))
        
        # Save documents
        with open(os.path.join(directory, "documents.pkl"), "wb") as f:
            pickle.dump(self.documents, f)
    
    @classmethod
    def load(cls, directory: str):
        """
        Load a vector store from disk.
        
        Args:
            directory: Directory containing the vector store
            
        Returns:
            Loaded VectorStore instance
        """
        # Create a new instance
        vector_store = cls()
        
        # Load FAISS index
        vector_store.index = faiss.read_index(os.path.join(directory, "index.faiss"))
        
        # Load documents
        with open(os.path.join(directory, "documents.pkl"), "rb") as f:
            vector_store.documents = pickle.load(f)
        
        return vector_store 