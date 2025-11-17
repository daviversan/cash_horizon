"""Session management service for agent conversations."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from app.config import settings

logger = logging.getLogger(__name__)


class InMemorySessionService:
    """
    In-memory session service for managing agent conversation state.
    
    This service maintains conversation history and context across multiple
    agent interactions. In production, this could be backed by Redis or
    a similar cache.
    
    Features:
    - Session creation and retrieval
    - Message history tracking
    - Context management
    - Automatic cleanup of expired sessions
    """
    
    def __init__(self):
        """Initialize the session service with empty storage."""
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._session_timeout = settings.session_timeout
        
    def create_session(
        self,
        session_id: str,
        company_id: int,
        agent_type: str,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new session.
        
        Args:
            session_id: Unique session identifier
            company_id: ID of the company
            agent_type: Type of agent (analyst, runway, investment)
            initial_context: Optional initial context data
            
        Returns:
            Created session dictionary
        """
        session = {
            "session_id": session_id,
            "company_id": company_id,
            "agent_type": agent_type,
            "created_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow(),
            "messages": [],
            "context": initial_context or {},
            "metadata": {}
        }
        
        self._sessions[session_id] = session
        
        logger.info(
            f"Created session {session_id}",
            extra={
                "session_id": session_id,
                "company_id": company_id,
                "agent_type": agent_type
            }
        )
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session dictionary or None if not found
        """
        session = self._sessions.get(session_id)
        
        if session:
            # Update last accessed time
            session["last_accessed"] = datetime.utcnow()
            
            # Check if session has expired
            if self._is_expired(session):
                logger.info(f"Session {session_id} has expired, removing")
                self.delete_session(session_id)
                return None
        
        return session
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a message to the session history.
        
        Args:
            session_id: Session identifier
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            True if message was added, False if session not found
        """
        session = self.get_session(session_id)
        
        if not session:
            logger.warning(f"Session {session_id} not found for adding message")
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        session["messages"].append(message)
        
        logger.debug(
            f"Added message to session {session_id}",
            extra={
                "session_id": session_id,
                "role": role,
                "message_count": len(session["messages"])
            }
        )
        
        return True
    
    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get message history for a session.
        
        Args:
            session_id: Session identifier
            limit: Optional limit on number of messages (most recent)
            
        Returns:
            List of messages (empty if session not found)
        """
        session = self.get_session(session_id)
        
        if not session:
            return []
        
        messages = session["messages"]
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def update_context(
        self,
        session_id: str,
        context_updates: Dict[str, Any]
    ) -> bool:
        """
        Update the session context.
        
        Args:
            session_id: Session identifier
            context_updates: Dictionary of context updates to merge
            
        Returns:
            True if context was updated, False if session not found
        """
        session = self.get_session(session_id)
        
        if not session:
            logger.warning(f"Session {session_id} not found for context update")
            return False
        
        session["context"].update(context_updates)
        
        logger.debug(
            f"Updated context for session {session_id}",
            extra={
                "session_id": session_id,
                "context_keys": list(context_updates.keys())
            }
        )
        
        return True
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get the session context.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Context dictionary (empty if session not found)
        """
        session = self.get_session(session_id)
        
        if not session:
            return {}
        
        return session["context"]
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session {session_id}")
            return True
        
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions.
        
        Returns:
            Number of sessions removed
        """
        expired_sessions = [
            session_id
            for session_id, session in self._sessions.items()
            if self._is_expired(session)
        ]
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_active_sessions(self, company_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all active sessions, optionally filtered by company.
        
        Args:
            company_id: Optional company ID to filter by
            
        Returns:
            List of active session summaries
        """
        sessions = []
        
        for session_id, session in self._sessions.items():
            if self._is_expired(session):
                continue
            
            if company_id is not None and session["company_id"] != company_id:
                continue
            
            sessions.append({
                "session_id": session_id,
                "company_id": session["company_id"],
                "agent_type": session["agent_type"],
                "created_at": session["created_at"].isoformat(),
                "last_accessed": session["last_accessed"].isoformat(),
                "message_count": len(session["messages"])
            })
        
        return sessions
    
    def _is_expired(self, session: Dict[str, Any]) -> bool:
        """
        Check if a session has expired.
        
        Args:
            session: Session dictionary
            
        Returns:
            True if expired, False otherwise
        """
        last_accessed = session["last_accessed"]
        expiry_time = last_accessed + timedelta(seconds=self._session_timeout)
        
        return datetime.utcnow() > expiry_time
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current sessions.
        
        Returns:
            Dictionary of session statistics
        """
        total_sessions = len(self._sessions)
        expired_count = sum(
            1 for session in self._sessions.values()
            if self._is_expired(session)
        )
        active_count = total_sessions - expired_count
        
        total_messages = sum(
            len(session["messages"])
            for session in self._sessions.values()
        )
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_count,
            "expired_sessions": expired_count,
            "total_messages": total_messages,
            "avg_messages_per_session": (
                total_messages / total_sessions if total_sessions > 0 else 0
            )
        }


# Global session service instance
session_service = InMemorySessionService()

