"""
Memory persistence and checkpointing for conversation memory.
"""

from langgraph.checkpoint.memory import MemorySaver
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Checkpointer:
    """
    Wrapper for LangGraph memory systems with support for both short-term and long-term memory.
    
    Currently uses MemorySaver for short-term memory with a backup dictionary.
    Designed to be extended for database-backed long-term memory in the future.
    """
    def __init__(self, db_path: str = None):
        """
        Initialize the checkpointer.
        
        Args:
            db_path: Path to database for future long-term storage (not used currently)
        """
        # Initialize MemorySaver for short-term memory
        self.memory = MemorySaver()
        
        # Backup in-memory storage for states
        self.states: Dict[str, Any] = {}
        
        # Store db_path for future database integration
        self.db_path = db_path
        
        logger.info("Initialized in-memory checkpointer for short-term memory")
        if db_path:
            logger.info(f"Database path {db_path} stored for future long-term memory integration")
    
    def get_memory(self):
        """Get the MemorySaver memory object for LangGraph integration."""
        return self.memory
    
    def save_state(self, state: Dict[str, Any], thread_id: str = "default") -> None:
        """
        Save state manually for a specific thread.
        
        Args:
            state: The state to save
            thread_id: The thread ID to save the state for
        """
        logger.info(f"Manually saving state for thread: {thread_id}")
        
        # Save to our backup dictionary
        self.states[thread_id] = state
        
        # Try to save to LangGraph memory if possible
        try:
            config = {"configurable": {"thread_id": thread_id}}
            # MemorySaver doesn't have a direct save method, but we can
            # save the state by simulating a workflow run
            self.memory.put(config, state, {}, {})
            logger.debug(f"State saved to LangGraph memory for thread: {thread_id}")
        except Exception as e:
            logger.debug(f"Could not save to LangGraph memory (expected behavior): {str(e)}")
    
    def get_state(self, thread_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        Get state manually for a specific thread.
        
        Args:
            thread_id: The thread ID to get the state for
            
        Returns:
            The state for the thread, or None if not found
        """
        # Try to get from LangGraph memory first
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = self.memory.get(config)
            if state:
                logger.debug(f"Retrieved state from LangGraph memory for thread: {thread_id}")
                # Update our backup store for consistency
                self.states[thread_id] = state
                return state
        except Exception as e:
            logger.debug(f"Could not get state from LangGraph memory (expected behavior): {str(e)}")
        
        # Fall back to our backup in-memory state
        state = self.states.get(thread_id)
        if state:
            logger.debug(f"Retrieved state from backup memory for thread: {thread_id}")
        return state
    
    def clear_state(self, thread_id: str = "default") -> bool:
        """
        Clear the state for a specific thread.
        
        Args:
            thread_id: The thread ID to clear
            
        Returns:
            True if state was found and cleared, False otherwise
        """
        found = False
        
        # Clear from our backup dictionary
        if thread_id in self.states:
            del self.states[thread_id]
            found = True
            logger.info(f"Cleared state from backup memory for thread: {thread_id}")
        
        # Try to clear from LangGraph memory
        try:
            config = {"configurable": {"thread_id": thread_id}}
            if self.memory.delete(config):
                found = True
                logger.debug(f"Cleared state from LangGraph memory for thread: {thread_id}")
        except Exception as e:
            logger.debug(f"Could not clear state from LangGraph memory: {str(e)}")
        
        return found
    
    def list_threads(self) -> list[str]:
        """
        List all thread IDs with saved states.
        
        Returns:
            List of thread IDs
        """
        return list(self.states.keys()) 