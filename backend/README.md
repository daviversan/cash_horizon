# Cash Horizon - Backend

AI-powered financial health tracker for startups using a multi-agent system powered by Google Gemini 2.0 Flash.

## Architecture

- **Framework:** FastAPI + Python 3.11+
- **Database:** SQLite (development) with SQLAlchemy ORM
- **AI/LLM:** Google Gemini 2.0 Flash via Google ADK
- **Agents:** 3 specialized agents (Financial Analyst, Runway Predictor, Investment Advisor)
- **API Docs:** Auto-generated Swagger/OpenAPI at `/api/docs`

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models & Pydantic schemas
│   │   ├── company.py
│   │   ├── transaction.py
│   │   ├── agent_session.py
│   │   └── schemas.py
│   ├── agents/              # AI agent implementations
│   ├── tools/               # Custom tools for agents
│   ├── routers/             # API route handlers
│   └── services/            # Business logic services
├── scripts/
│   └── seed_data.py         # Database seeding script
├── alembic/                 # Database migrations
├── tests/                   # Unit and integration tests
└── requirements.txt         # Python dependencies
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file (or copy from `.env.example`):

```bash
cp .env.example .env
```

Update the following in `.env`:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `SECRET_KEY`: Generate a secure key for production

### 3. Initialize Database

The database will be automatically created when you run the application. To seed with sample data:

```bash
python scripts/seed_data.py
```

### 4. Run the Application

**Development mode with auto-reload:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Or using Python:**
```bash
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/health

## Database Management

### Create Migration

```bash
alembic revision --autogenerate -m "description"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### View Migration History

```bash
alembic history
```

## Database Models

### Company
Represents a startup or business being tracked.
- `id`, `name`, `industry`, `founded_date`, `initial_capital`
- Relationships: `transactions`, `agent_sessions`

### Transaction
Financial transactions (income/expenses).
- `id`, `company_id`, `date`, `amount`, `category`, `type`, `description`
- Types: `income` or `expense`

### AgentSession
Tracks agent executions for observability and memory.
- `id`, `company_id`, `session_id`, `agent_type`, `input_data`, `output_data`
- Metrics: `execution_time_ms`, `token_count`, `status`

## API Endpoints

### Health & Info
- `GET /` - Health check
- `GET /api/health` - Detailed health status
- `GET /api/docs` - Swagger UI documentation

### Companies (Phase 5)
- `POST /api/v1/companies` - Create company
- `GET /api/v1/companies` - List companies
- `GET /api/v1/companies/{id}` - Get company details

### Transactions (Phase 5)
- `POST /api/v1/companies/{id}/transactions` - Add transactions
- `GET /api/v1/companies/{id}/transactions` - List transactions

### Agent Endpoints (Phase 5)
- `POST /api/v1/companies/{id}/analyze` - Financial analysis
- `POST /api/v1/companies/{id}/runway` - Runway prediction
- `POST /api/v1/companies/{id}/investments` - Investment recommendations

## Development

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
```

### Type Checking

```bash
mypy app/
```

### Linting

```bash
flake8 app/
```

## Docker

Build and run with Docker:

```bash
docker build -t cash-horizon-backend .
docker run -p 8000:8000 --env-file .env cash-horizon-backend
```

## Next Steps

- **Phase 3:** Implement custom tools (financial calculator, data processor, chart generator)
- **Phase 4:** Build AI agents with Google ADK
- **Phase 5:** Complete API routers and integrate agents

## License

Copyright © 2024 Cash Horizon Team

