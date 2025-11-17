"""Initialize database and create tables."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import sync_engine, Base
from app.models import Company, Transaction, AgentSession  # noqa: F401

def main():
    """Create all database tables."""
    print("🔨 Creating database tables...")
    
    try:
        Base.metadata.create_all(bind=sync_engine)
        print("✅ Database tables created successfully!")
        print("\nTables created:")
        print("  - companies")
        print("  - transactions")
        print("  - agent_sessions")
        print("\n💡 Tip: Run 'python scripts/seed_data.py' to populate with sample data")
        
    except Exception as e:
        print(f"❌ Error creating database: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

