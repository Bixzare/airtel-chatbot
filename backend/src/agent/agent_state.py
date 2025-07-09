"""
Agent state management for LangGraph RAG agent.
"""

from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]
    retrieved_docs: List[str]
    current_query: str
    tool_calls: List[Dict[str, Any]] 