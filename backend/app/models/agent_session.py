"""Agent Session model for tracking agent interactions and memory."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from ..database import Base

if TYPE_CHECKING:
    from .company import Company


class AgentType(str, enum.Enum):
    """Agent type enum."""
    FINANCIAL_ANALYST = "financial_analyst"
    RUNWAY_PREDICTOR = "runway_predictor"
    INVESTMENT_ADVISOR = "investment_advisor"
    ORCHESTRATOR = "orchestrator"


class AgentSession(Base):
    """Agent Session model for tracking agent executions and maintaining memory."""
    
    __tablename__ = "agent_sessions"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session Information
    session_id = Column(String(255), nullable=False, index=True)
    agent_type = Column(SQLEnum(AgentType), nullable=False, index=True)
    
    # Agent I/O Data (stored as JSON strings)
    input_data = Column(Text, nullable=True)
    output_data = Column(Text, nullable=True)
    
    # Execution Metadata
    execution_time_ms = Column(Integer, nullable=True)  # Execution time in milliseconds
    token_count = Column(Integer, nullable=True)  # Tokens used by LLM
    status = Column(String(50), nullable=True, default="success")  # success, failed, partial
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    company: "Company" = relationship("Company", back_populates="agent_sessions")
    
    def __repr__(self) -> str:
        return (
            f"<AgentSession(id={self.id}, company_id={self.company_id}, "
            f"agent_type={self.agent_type.value}, session_id='{self.session_id}', "
            f"status='{self.status}')>"
        )
    
    @property
    def execution_time_seconds(self) -> Optional[float]:
        """Get execution time in seconds."""
        return self.execution_time_ms / 1000.0 if self.execution_time_ms else None

