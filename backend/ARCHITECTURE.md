# Cash Horizon Backend - Architecture Documentation

## Overview

Cash Horizon is an AI-powered financial health tracker for startups built with FastAPI, SQLAlchemy, and Google Gemini 2.0 Flash. The backend implements a multi-agent system that analyzes financial data and provides actionable insights.

## Technology Stack

- **Framework:** FastAPI 0.104+ (async web framework)
- **Database:** SQLite (development) with SQLAlchemy 2.0 ORM
- **AI/LLM:** Google Gemini 2.0 Flash via Google ADK
- **Migration:** Alembic for database versioning
- **Testing:** pytest with async support
- **Validation:** Pydantic v2 for data validation

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                  │
│         Routers, Endpoints, Request Validation          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                         │
│         Business Logic, Orchestration                   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Agent Layer                          │
│   Financial Analyst │ Runway Predictor │ Inv. Advisor  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                     Tools Layer                         │
│  Calculator │ Data Processor │ Charts │ Web Search     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Data Layer (SQLAlchemy)               │
│         Models, Relationships, Database Access          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  Database (SQLite/PostgreSQL)           │
│      Companies │ Transactions │ Agent Sessions         │
└─────────────────────────────────────────────────────────┘
```

## Database Schema

### Entity Relationship Diagram

```
┌──────────────────────────┐
│       Companies          │
│──────────────────────────│
│ PK  id                   │
│     name                 │
│     industry             │
│     founded_date         │
│     initial_capital      │
│     created_at           │
│     updated_at           │
└──────────────────────────┘
            │
            │ 1:N
            ├──────────────────────────────┐
            │                              │
            ↓                              ↓
┌──────────────────────────┐  ┌──────────────────────────┐
│     Transactions         │  │     Agent Sessions       │
│──────────────────────────│  │──────────────────────────│
│ PK  id                   │  │ PK  id                   │
│ FK  company_id           │  │ FK  company_id           │
│     date                 │  │     session_id           │
│     amount               │  │     agent_type           │
│     category             │  │     input_data           │
│     type (income/exp)    │  │     output_data          │
│     description          │  │     execution_time_ms    │
│     created_at           │  │     token_count          │
│     updated_at           │  │     status               │
└──────────────────────────┘  │     error_message        │
                              │     created_at           │
                              └──────────────────────────┘
```

## Data Flow

### 1. Financial Analysis Flow

```
User Request
    ↓
API Endpoint (/api/v1/companies/{id}/analyze)
    ↓
Validation (Pydantic Schema)
    ↓
Financial Analyst Agent
    ↓
Tools: Financial Calculator + Data Processor
    ↓
Database Query (Transactions)
    ↓
LLM Processing (Gemini 2.0 Flash)
    ↓
Generate Insights
    ↓
Store Agent Session (observability)
    ↓
Return Response (FinancialAnalysisResponse)
    ↓
User receives insights + metrics
```

### 2. Runway Prediction Flow

```
User Request
    ↓
API Endpoint (/api/v1/companies/{id}/runway)
    ↓
Runway Predictor Agent
    ↓
Tools: Financial Calculator + Chart Generator
    ↓
Calculate Burn Rate
    ↓
LLM Forecasting (Gemini 2.0 Flash)
    ↓
Generate Forecast Data
    ↓
Return Runway Metrics + Charts
```

### 3. Investment Recommendation Flow

```
User Request
    ↓
API Endpoint (/api/v1/companies/{id}/investments)
    ↓
Investment Advisor Agent
    ↓
Tools: Financial Calculator + Web Search
    ↓
Assess Financial Health
    ↓
Search Investment Options (if positive balance)
    ↓
LLM Recommendations (Gemini 2.0 Flash)
    ↓
Return Personalized Advice
```

## Database Models

### Company Model

**Purpose:** Represents a startup or business being tracked

**Fields:**
- `id` (Integer, PK): Unique identifier
- `name` (String): Company name
- `industry` (String): Industry sector
- `founded_date` (Date): When company was founded
- `initial_capital` (Decimal): Starting capital/funding
- `created_at` (DateTime): Record creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- `transactions`: One-to-Many with Transaction
- `agent_sessions`: One-to-Many with AgentSession

**Properties:**
- `transaction_count`: Computed count of transactions

### Transaction Model

**Purpose:** Records all financial transactions (income and expenses)

**Fields:**
- `id` (Integer, PK): Unique identifier
- `company_id` (Integer, FK): Reference to Company
- `date` (Date): Transaction date
- `amount` (Decimal): Transaction amount (always positive)
- `category` (String): Category (Salaries, Rent, Revenue, etc.)
- `type` (Enum): INCOME or EXPENSE
- `description` (String): Optional details
- `created_at` (DateTime): Record creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Properties:**
- `signed_amount`: Returns positive for income, negative for expenses

**Indexes:**
- `company_id` (FK index)
- `date` (for time-series queries)
- `category` (for grouping)
- `type` (for filtering)

### AgentSession Model

**Purpose:** Tracks AI agent executions for observability and memory

**Fields:**
- `id` (Integer, PK): Unique identifier
- `company_id` (Integer, FK): Reference to Company
- `session_id` (String): Session identifier for multi-agent workflows
- `agent_type` (Enum): FINANCIAL_ANALYST | RUNWAY_PREDICTOR | INVESTMENT_ADVISOR | ORCHESTRATOR
- `input_data` (Text/JSON): Agent input parameters
- `output_data` (Text/JSON): Agent output results
- `execution_time_ms` (Integer): Execution time in milliseconds
- `token_count` (Integer): LLM tokens consumed
- `status` (String): success | failed | partial
- `error_message` (Text): Error details if failed
- `created_at` (DateTime): Execution timestamp

**Properties:**
- `execution_time_seconds`: Converts ms to seconds

**Use Cases:**
- Performance monitoring
- Token usage tracking
- Agent conversation history
- Debugging and troubleshooting

## Configuration Management

### Settings Class (`config.py`)

All configuration is managed through Pydantic Settings:

```python
class Settings(BaseSettings):
    # Application
    app_name: str
    app_version: str
    environment: str
    
    # Database
    database_url: str
    
    # Google Gemini
    gemini_api_key: str
    gemini_model: str
    
    # API
    api_v1_prefix: str
    cors_origins: List[str]
    
    # Security
    secret_key: str
    algorithm: str
```

**Environment Variables:**
- Loaded from `.env` file
- Type-safe with Pydantic validation
- Default values for development
- Override-able for production

## API Design Principles

### RESTful Endpoints

- Resource-based URLs
- HTTP methods for CRUD operations
- Consistent response formats
- Proper status codes

### Request/Response Flow

```
Request → Validation (Pydantic) → Business Logic → Database → Response
         ↓ (400 Bad Request if invalid)
```

### Error Handling

- Global exception handler
- Structured error responses
- Detailed errors in development
- Generic errors in production

### Documentation

- Auto-generated with OpenAPI
- Swagger UI at `/api/docs`
- ReDoc at `/api/redoc`

## Database Session Management

### Async Sessions

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Usage in Endpoints

```python
@app.get("/companies/{id}")
async def get_company(id: int, db: AsyncSession = Depends(get_db)):
    company = await db.get(Company, id)
    return company
```

## Migration Strategy

### Alembic Configuration

- Auto-generate migrations from model changes
- Version-controlled schema evolution
- Upgrade and downgrade paths

### Workflow

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Testing Strategy

### Unit Tests

- Test individual models
- Test relationships
- Test computed properties
- In-memory SQLite for speed

### Integration Tests (Future)

- Test API endpoints
- Test agent workflows
- Test database operations

### Test Database

- Separate from development database
- Fresh schema for each test run
- Isolated test data

## Security Considerations

### API Security

- CORS configuration
- API key authentication (future)
- Rate limiting (future)
- Input validation (Pydantic)

### Database Security

- Parameterized queries (SQLAlchemy)
- No raw SQL injection points
- Connection pooling
- Secure credential storage

### Environment Variables

- Sensitive data in `.env`
- Never commit `.env` to git
- Different keys per environment

## Performance Optimization

### Database

- Indexed foreign keys
- Indexed date and category fields
- Lazy loading with `selectin` for relationships
- Connection pooling

### Async Operations

- Non-blocking database queries
- Async engine for concurrent requests
- FastAPI async endpoints

### Caching (Future)

- Cache agent results with TTL
- Redis for distributed caching
- In-memory cache for frequent queries

## Observability

### Logging

- Structured logging with Python `logging`
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging
- Agent execution logging

### Metrics (via AgentSession)

- Execution time tracking
- Token usage monitoring
- Success/failure rates
- Agent performance analytics

### Tracing (Future)

- Google Cloud Trace integration
- Request ID propagation
- Distributed tracing

## Deployment Architecture

### Development

```
Docker Compose
├── Backend (FastAPI)
│   └── SQLite Database
└── Frontend (React)
```

### Production (Google Cloud Run)

```
Cloud Load Balancer
├── Backend Service (Container)
│   └── Cloud SQL (PostgreSQL)
├── Frontend Service (Container)
└── Cloud Logging & Monitoring
```

## Future Enhancements

### Phase 3-10

1. **Tools Implementation**
   - Financial calculator
   - Data processor
   - Chart generator
   - Web search

2. **Agent Implementation**
   - Financial Analyst Agent
   - Runway Predictor Agent
   - Investment Advisor Agent
   - Orchestrator

3. **API Completion**
   - Company CRUD endpoints
   - Transaction management
   - Agent trigger endpoints

4. **Frontend Integration**
   - React dashboard
   - Real-time agent feedback
   - Interactive charts

5. **Testing & Documentation**
   - Comprehensive test suite
   - Architecture diagrams
   - Deployment guides

6. **Cloud Deployment**
   - Google Cloud Run
   - CI/CD pipeline
   - Production monitoring

## Development Guidelines

### Code Style

- Follow PEP 8
- Type hints everywhere
- Docstrings for functions
- Descriptive variable names

### Git Workflow

- Feature branches
- Descriptive commits
- Pull request reviews
- Squash and merge

### Testing

- Write tests for new features
- Maintain test coverage
- Run tests before commits

---

**Last Updated:** November 17, 2025  
**Phase:** 2 (Database Setup) - COMPLETE  
**Next Phase:** 3 (Tool Development)

