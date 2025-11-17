"""Tests for database models."""

import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Company, Transaction, TransactionType, AgentSession, AgentType


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_company(db_session):
    """Test creating a company."""
    company = Company(
        name="Test Startup",
        industry="Technology",
        founded_date=date(2023, 1, 1),
        initial_capital=Decimal("100000.00")
    )
    db_session.add(company)
    db_session.commit()
    
    assert company.id is not None
    assert company.name == "Test Startup"
    assert company.industry == "Technology"
    assert company.transaction_count == 0


def test_create_transaction(db_session):
    """Test creating a transaction."""
    company = Company(name="Test Company")
    db_session.add(company)
    db_session.commit()
    
    transaction = Transaction(
        company_id=company.id,
        date=date(2024, 1, 15),
        amount=Decimal("5000.00"),
        category="Revenue",
        type=TransactionType.INCOME,
        description="Test income"
    )
    db_session.add(transaction)
    db_session.commit()
    
    assert transaction.id is not None
    assert transaction.signed_amount == 5000.00
    assert transaction.type == TransactionType.INCOME


def test_transaction_signed_amount(db_session):
    """Test signed amount calculation."""
    company = Company(name="Test Company")
    db_session.add(company)
    db_session.commit()
    
    income = Transaction(
        company_id=company.id,
        date=date.today(),
        amount=Decimal("1000.00"),
        category="Revenue",
        type=TransactionType.INCOME
    )
    expense = Transaction(
        company_id=company.id,
        date=date.today(),
        amount=Decimal("500.00"),
        category="Expense",
        type=TransactionType.EXPENSE
    )
    
    assert income.signed_amount == 1000.00
    assert expense.signed_amount == -500.00


def test_company_transactions_relationship(db_session):
    """Test relationship between company and transactions."""
    company = Company(name="Test Company")
    db_session.add(company)
    db_session.commit()
    
    for i in range(3):
        transaction = Transaction(
            company_id=company.id,
            date=date.today(),
            amount=Decimal("100.00"),
            category="Test",
            type=TransactionType.INCOME
        )
        db_session.add(transaction)
    
    db_session.commit()
    db_session.refresh(company)
    
    assert len(company.transactions) == 3
    assert company.transaction_count == 3


def test_create_agent_session(db_session):
    """Test creating an agent session."""
    company = Company(name="Test Company")
    db_session.add(company)
    db_session.commit()
    
    session = AgentSession(
        company_id=company.id,
        session_id="test_session_001",
        agent_type=AgentType.FINANCIAL_ANALYST,
        input_data='{"test": "data"}',
        output_data='{"result": "success"}',
        execution_time_ms=1000,
        token_count=250,
        status="success"
    )
    db_session.add(session)
    db_session.commit()
    
    assert session.id is not None
    assert session.execution_time_seconds == 1.0
    assert session.agent_type == AgentType.FINANCIAL_ANALYST


def test_agent_session_relationship(db_session):
    """Test relationship between company and agent sessions."""
    company = Company(name="Test Company")
    db_session.add(company)
    db_session.commit()
    
    for agent_type in [AgentType.FINANCIAL_ANALYST, AgentType.RUNWAY_PREDICTOR]:
        session = AgentSession(
            company_id=company.id,
            session_id=f"session_{agent_type.value}",
            agent_type=agent_type,
            status="success"
        )
        db_session.add(session)
    
    db_session.commit()
    db_session.refresh(company)
    
    assert len(company.agent_sessions) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

