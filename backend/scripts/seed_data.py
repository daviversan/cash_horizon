"""Seed database with sample data for testing and demonstration."""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import sync_engine, Base, SessionLocal
from app.models import Company, Transaction, TransactionType, AgentSession, AgentType


def clear_database():
    """Clear all data from database (use with caution!)."""
    print("🗑️  Clearing database...")
    Base.metadata.drop_all(bind=sync_engine)
    Base.metadata.create_all(bind=sync_engine)
    print("✅ Database cleared and recreated")


def seed_companies(db):
    """Seed sample companies."""
    print("🏢 Seeding companies...")
    
    companies = [
        Company(
            name="TechStart AI",
            industry="Artificial Intelligence",
            founded_date=date(2023, 1, 15),
            initial_capital=Decimal("500000.00")
        ),
        Company(
            name="GreenEnergy Solutions",
            industry="Renewable Energy",
            founded_date=date(2022, 6, 1),
            initial_capital=Decimal("1000000.00")
        ),
        Company(
            name="HealthTech Innovations",
            industry="Healthcare Technology",
            founded_date=date(2023, 9, 10),
            initial_capital=Decimal("750000.00")
        ),
    ]
    
    db.add_all(companies)
    db.commit()
    
    for company in companies:
        db.refresh(company)
    
    print(f"✅ Created {len(companies)} companies")
    return companies


def seed_transactions(db, companies):
    """Seed sample transactions for companies."""
    print("💰 Seeding transactions...")
    
    # Get the first company (TechStart AI) for detailed transactions
    company = companies[0]
    
    # Generate transactions for the last 12 months
    base_date = date.today()
    transactions = []
    
    # Initial funding
    transactions.append(Transaction(
        company_id=company.id,
        date=company.founded_date,
        amount=company.initial_capital,
        category="Funding",
        type=TransactionType.INCOME,
        description="Initial seed funding round"
    ))
    
    # Monthly expenses and income for the past 12 months
    for month_offset in range(12):
        month_date = base_date - timedelta(days=30 * month_offset)
        
        # Salaries (major expense)
        transactions.append(Transaction(
            company_id=company.id,
            date=month_date,
            amount=Decimal("45000.00"),
            category="Salaries",
            type=TransactionType.EXPENSE,
            description=f"Monthly salaries for {month_date.strftime('%B %Y')}"
        ))
        
        # Office rent
        transactions.append(Transaction(
            company_id=company.id,
            date=month_date,
            amount=Decimal("5000.00"),
            category="Rent",
            type=TransactionType.EXPENSE,
            description="Office space rent"
        ))
        
        # Cloud infrastructure
        transactions.append(Transaction(
            company_id=company.id,
            date=month_date,
            amount=Decimal("3500.00"),
            category="Infrastructure",
            type=TransactionType.EXPENSE,
            description="AWS and cloud services"
        ))
        
        # Marketing
        transactions.append(Transaction(
            company_id=company.id,
            date=month_date,
            amount=Decimal("8000.00"),
            category="Marketing",
            type=TransactionType.EXPENSE,
            description="Digital marketing and advertising"
        ))
        
        # Software licenses
        transactions.append(Transaction(
            company_id=company.id,
            date=month_date,
            amount=Decimal("2000.00"),
            category="Software",
            type=TransactionType.EXPENSE,
            description="Software licenses and subscriptions"
        ))
        
        # Revenue (growing over time)
        revenue_base = 15000 + (month_offset * 2000)  # Growing revenue
        transactions.append(Transaction(
            company_id=company.id,
            date=month_date,
            amount=Decimal(str(revenue_base)),
            category="Service Revenue",
            type=TransactionType.INCOME,
            description=f"Customer payments for {month_date.strftime('%B %Y')}"
        ))
        
        # Occasional consulting income
        if month_offset % 3 == 0:
            transactions.append(Transaction(
                company_id=company.id,
                date=month_date,
                amount=Decimal("12000.00"),
                category="Consulting",
                type=TransactionType.INCOME,
                description="Consulting project payment"
            ))
    
    # Add some varied expenses
    special_expenses = [
        ("Legal", Decimal("15000.00"), "Legal consultation and incorporation", 90),
        ("Equipment", Decimal("25000.00"), "Laptops and development equipment", 180),
        ("Travel", Decimal("8000.00"), "Conference attendance and travel", 60),
        ("Training", Decimal("5000.00"), "Team training and development", 120),
        ("Insurance", Decimal("3000.00"), "Business insurance premium", 200),
    ]
    
    for category, amount, description, days_ago in special_expenses:
        transactions.append(Transaction(
            company_id=company.id,
            date=base_date - timedelta(days=days_ago),
            amount=amount,
            category=category,
            type=TransactionType.EXPENSE,
            description=description
        ))
    
    # Add transactions for other companies (lighter data)
    for other_company in companies[1:]:
        for month_offset in range(6):
            month_date = base_date - timedelta(days=30 * month_offset)
            
            # Basic expenses
            transactions.append(Transaction(
                company_id=other_company.id,
                date=month_date,
                amount=Decimal("30000.00"),
                category="Salaries",
                type=TransactionType.EXPENSE,
                description="Monthly salaries"
            ))
            
            transactions.append(Transaction(
                company_id=other_company.id,
                date=month_date,
                amount=Decimal("10000.00"),
                category="Service Revenue",
                type=TransactionType.INCOME,
                description="Customer payments"
            ))
    
    db.add_all(transactions)
    db.commit()
    
    print(f"✅ Created {len(transactions)} transactions")
    return transactions


def seed_agent_sessions(db, companies):
    """Seed sample agent sessions for demonstration."""
    print("🤖 Seeding agent sessions...")
    
    company = companies[0]
    sessions = []
    
    # Financial Analyst session
    sessions.append(AgentSession(
        company_id=company.id,
        session_id="session_financial_001",
        agent_type=AgentType.FINANCIAL_ANALYST,
        input_data='{"start_date": "2024-01-01", "end_date": "2024-12-31"}',
        output_data='{"total_income": 250000, "total_expenses": 780000, "insights": "Company is currently in growth phase with negative cash flow"}',
        execution_time_ms=1250,
        token_count=450,
        status="success"
    ))
    
    # Runway Predictor session
    sessions.append(AgentSession(
        company_id=company.id,
        session_id="session_runway_001",
        agent_type=AgentType.RUNWAY_PREDICTOR,
        input_data='{"forecast_months": 12}',
        output_data='{"burn_rate": 63500, "runway_months": 7.8, "insights": "At current burn rate, runway is approximately 8 months"}',
        execution_time_ms=980,
        token_count=380,
        status="success"
    ))
    
    # Investment Advisor session
    sessions.append(AgentSession(
        company_id=company.id,
        session_id="session_investment_001",
        agent_type=AgentType.INVESTMENT_ADVISOR,
        input_data='{"risk_tolerance": "medium"}',
        output_data='{"can_invest": false, "insights": "Focus on achieving positive cash flow before considering investments"}',
        execution_time_ms=1100,
        token_count=520,
        status="success"
    ))
    
    db.add_all(sessions)
    db.commit()
    
    print(f"✅ Created {len(sessions)} agent sessions")
    return sessions


def main():
    """Main function to seed database."""
    print("\n" + "="*60)
    print("💾 Cash Horizon - Database Seeding Script")
    print("="*60 + "\n")
    
    try:
        # Create database session
        db = SessionLocal()
        
        # Clear existing data (optional - comment out to preserve data)
        clear_database()
        
        # Seed data
        companies = seed_companies(db)
        transactions = seed_transactions(db, companies)
        sessions = seed_agent_sessions(db, companies)
        
        print("\n" + "="*60)
        print("✅ Database seeding completed successfully!")
        print(f"   - Companies: {len(companies)}")
        print(f"   - Transactions: {len(transactions)}")
        print(f"   - Agent Sessions: {len(sessions)}")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()

