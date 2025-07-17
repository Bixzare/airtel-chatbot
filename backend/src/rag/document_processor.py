"""
Document processor for loading, chunking, and metadata extraction.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any, Optional

class DocumentProcessor:
    """Processes documents for RAG by loading, chunking, and extracting metadata."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
    
    def load_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Load text content and split into chunks with metadata.
        
        Args:
            text: The text content to process
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of dictionaries with 'text' and 'metadata' keys
        """
        chunks = self.text_splitter.split_text(text)
        
        # Create document chunks with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy() if metadata else {}
            # Add chunk index to metadata
            chunk_metadata["chunk_index"] = i
            documents.append({
                "text": chunk,
                "metadata": chunk_metadata
            })
        
        return documents
    
    def load_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load text from file and process into chunks.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            List of dictionaries with 'text' and 'metadata' keys
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            metadata = {
                "source": file_path,
                "file_type": "text"
            }
            
            return self.load_text(text, metadata)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return [] 