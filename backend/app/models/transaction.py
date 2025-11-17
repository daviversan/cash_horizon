"""Transaction model for database."""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from ..database import Base

if TYPE_CHECKING:
    from .company import Company


class TransactionType(str, enum.Enum):
    """Transaction type enum."""
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(Base):
    """Transaction model representing financial transactions."""
    
    __tablename__ = "transactions"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transaction Details
    date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    company: "Company" = relationship("Company", back_populates="transactions")
    
    def __repr__(self) -> str:
        return (
            f"<Transaction(id={self.id}, company_id={self.company_id}, "
            f"date={self.date}, amount={self.amount}, type={self.type.value})>"
        )
    
    @property
    def signed_amount(self) -> float:
        """Get amount with sign based on transaction type."""
        amount_float = float(self.amount)
        return amount_float if self.type == TransactionType.INCOME else -amount_float

