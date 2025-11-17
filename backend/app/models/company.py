"""Company model for database."""

from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric
from sqlalchemy.orm import relationship
from ..database import Base

if TYPE_CHECKING:
    from .transaction import Transaction
    from .agent_session import AgentSession


class Company(Base):
    """Company model representing a startup or business."""
    
    __tablename__ = "companies"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Company Information
    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(100), nullable=True)
    founded_date = Column(Date, nullable=True)
    initial_capital = Column(Numeric(15, 2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    transactions: List["Transaction"] = relationship(
        "Transaction",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    agent_sessions: List["AgentSession"] = relationship(
        "AgentSession",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.name}', industry='{self.industry}')>"
    
    @property
    def transaction_count(self) -> int:
        """Get count of transactions for this company."""
        return len(self.transactions) if self.transactions else 0

