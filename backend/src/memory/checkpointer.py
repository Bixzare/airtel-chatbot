"""
Memory persistence and checkpointing for conversation memory.
"""

from langgraph.checkpoint.memory import MemorySaver

class Checkpointer:
    """Wrapper for LangGraph MemorySaver for persistent conversation memory."""
    def __init__(self):
        self.memory = MemorySaver()

    def get_memory(self):
        return self.memory 