"""
Session management for conversation history with timeout functionality.
"""

import time
import threading
import logging
from typing import Dict, List, Any, Optional
from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manages chat sessions with automatic timeout functionality.
    Sessions inactive for longer than the timeout period will be automatically cleared.
    """
    
    def __init__(self, timeout_minutes: int = 30):
        """
        Initialize the session manager.
        
        Args:
            timeout_minutes: Number of minutes of inactivity before a session is cleared
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.timeout_minutes = timeout_minutes
        self.lock = threading.RLock()
        
        # Start the cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions, daemon=True)
        self.cleanup_thread.start()
        
        logger.info(f"Session manager initialized with {timeout_minutes} minute timeout")
    
    def get_session(self, session_id: str) -> List[BaseMessage]:
        """
        Get the message history for a session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            List of messages in the session
        """
        with self.lock:
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "messages": [],
                    "last_activity": time.time()
                }
            else:
                # Update last activity time
                self.sessions[session_id]["last_activity"] = time.time()
                
            return self.sessions[session_id]["messages"]
    
    def update_session(self, session_id: str, messages: List[BaseMessage]) -> None:
        """
        Update the message history for a session.
        
        Args:
            session_id: The session identifier
            messages: The updated list of messages
        """
        with self.lock:
            self.sessions[session_id] = {
                "messages": messages,
                "last_activity": time.time()
            }
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear a session's message history.
        
        Args:
            session_id: The session identifier
            
        Returns:
            True if session was found and cleared, False otherwise
        """
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"Cleared session {session_id}")
                return True
            return False
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active sessions.
        
        Returns:
            Dictionary of session data
        """
        with self.lock:
            return self.sessions.copy()
    
    def _cleanup_expired_sessions(self) -> None:
        """
        Periodically clean up expired sessions.
        This runs in a background thread.
        """
        while True:
            try:
                # Sleep for 5 minutes between cleanup checks
                time.sleep(300)
                
                current_time = time.time()
                timeout_seconds = self.timeout_minutes * 60
                
                with self.lock:
                    # Find expired sessions
                    expired_sessions = [
                        session_id for session_id, data in self.sessions.items()
                        if current_time - data["last_activity"] > timeout_seconds
                    ]
                    
                    # Remove expired sessions
                    for session_id in expired_sessions:
                        del self.sessions[session_id]
                        logger.info(f"Session {session_id} expired after {self.timeout_minutes} minutes of inactivity")
                
                logger.debug(f"Cleaned up {len(expired_sessions)} expired sessions")
                
            except Exception as e:
                logger.error(f"Error in session cleanup: {str(e)}") 