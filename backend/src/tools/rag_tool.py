"""
RAG retrieval tool for vector similarity search.
"""

from .base_tool import BaseTool
from typing import List

class RAGTool(BaseTool):
    """RAG tool that retrieves relevant chunks from a static document."""
    name = "rag_search"
    description = "Search the knowledge base for relevant information."

    def __init__(self, document: str):
        self.document = document
        self.chunks = self.document.split(". ")  # Simple sentence split

    def __call__(self, query: str) -> List[str]:
        # Simple keyword search for demo
        relevant_chunks = [chunk for chunk in self.chunks if query.lower() in chunk.lower()]
        if not relevant_chunks:
            # Return a fallback message instead of empty list
            return ["No specific information found in the knowledge base for this query."]
        return relevant_chunks

# Example usage:
# doc = open('static_document.txt').read()
# rag_tool = RAGTool(doc)
# rag_tool('remote work') 