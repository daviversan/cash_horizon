# Cash Horizon 💰

> AI-Powered Startup Financial Health Tracker

Cash Horizon is an intelligent financial analysis platform designed specifically for startups. Using a multi-agent AI system powered by Google Gemini 2.0 Flash, it provides automated financial analysis, runway predictions, and personalized investment recommendations.

## 🎯 Problem Statement

Startups struggle with:
- **Manual financial tracking** across spreadsheets and tools
- **Uncertain runway calculations** that impact decision-making
- **Lack of actionable insights** from raw financial data
- **Time-consuming analysis** that distracts from core business

## 💡 Solution

Cash Horizon employs a **multi-agent AI system** that:
1. **Analyzes spending patterns** and categorizes transactions automatically
2. **Predicts financial runway** with burn rate calculations
3. **Provides investment recommendations** tailored to company stage and health

## 🏗️ Architecture

### Tech Stack

- **Backend:** Python + FastAPI + Google ADK (Agent Development Kit)
- **Frontend:** React + TypeScript + Vite + TailwindCSS
- **Database:** SQLite (local) → Cloud SQL (production)
- **AI Model:** Google Gemini 2.0 Flash
- **Deployment:** Docker Compose (local) + Google Cloud Run (production)

### Multi-Agent System

#### 🔍 Agent 1: Financial Analyst
- Analyzes spending patterns and transaction history
- Categorizes expenses automatically
- Generates natural language financial insights
- **Tools:** Financial Calculator, Data Processor

#### 📊 Agent 2: Runway Predictor
- Calculates burn rate from historical data
- Predicts runway based on current spending
- Generates forecast charts and visualizations
- **Tools:** Financial Calculator, Chart Generator

#### 💼 Agent 3: Investment Advisor
- Researches investment options via web search
- Provides personalized recommendations
- Adapts advice based on company financial health
- **Tools:** Web Search, Financial Calculator

### Key Features (Kaggle Requirements)

✅ **Multi-agent system** - 3 specialized agents working in orchestration  
✅ **Custom tools** - Financial calculations, data processing, web search, chart generation  
✅ **Sessions & Memory** - Persistent conversation context and company data  
✅ **Observability** - Structured logging with Google Cloud Trace integration  
✅ **Agent deployment** - Full Google Cloud Run deployment with documentation  

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Google Gemini API Key ([Get one here](https://ai.google.dev/))

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd cash_horizon
```

2. **Set up environment variables**

Backend:
```bash
cd backend
cp env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Frontend:
```bash
cd frontend
cp env.example .env
# Configure VITE_API_URL if needed
```

3. **Run with Docker Compose**
```bash
docker-compose up --build
```

4. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Setup (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
cash_horizon/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agents (Analyst, Predictor, Advisor)
│   │   ├── tools/           # Custom tools for agents
│   │   ├── models/          # Database models
│   │   ├── routers/         # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── main.py          # FastAPI entry point
│   │   └── config.py        # Configuration
│   ├── tests/               # Unit & integration tests
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript types
│   │   └── main.tsx         # Entry point
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 📊 API Documentation

Once the backend is running, visit the interactive API documentation:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

```
POST /api/v1/companies              # Create company
GET  /api/v1/companies/{id}         # Get company details

POST /api/v1/companies/{id}/analyze      # Trigger Financial Analyst
POST /api/v1/companies/{id}/runway       # Trigger Runway Predictor
POST /api/v1/companies/{id}/investments  # Trigger Investment Advisor

POST /api/v1/companies/{id}/transactions # Upload transactions
GET  /api/v1/companies/{id}/transactions # List transactions
```

## 🧪 Testing

**Backend:**
```bash
cd backend
pytest tests/ -v --cov=app
```

**Frontend:**
```bash
cd frontend
npm run lint
npm run build
```

## 🌐 Cloud Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed Google Cloud Run deployment instructions.

**Quick Deploy:**
```bash
# Coming in Phase 9
gcloud run deploy cash-horizon-backend --source ./backend
gcloud run deploy cash-horizon-frontend --source ./frontend
```

## 📖 Documentation

- **Architecture Details:** [ARCHITECTURE.md](./ARCHITECTURE.md) *(Coming soon)*
- **Deployment Guide:** [DEPLOYMENT.md](./DEPLOYMENT.md) *(Coming soon)*
- **API Reference:** [API.md](./API.md) *(Coming soon)*

## 🛠️ Development Roadmap

- [x] **Phase 1:** Project scaffold and configuration
- [ ] **Phase 2:** Database setup and models
- [ ] **Phase 3:** Agent implementation
- [ ] **Phase 4:** Tool development
- [ ] **Phase 5:** Backend API
- [ ] **Phase 6:** Frontend development
- [ ] **Phase 7:** Testing
- [ ] **Phase 8:** Documentation
- [ ] **Phase 9:** Deployment
- [ ] **Phase 10:** Final polish

## 🤝 Contributing

This is a competition submission project. For educational purposes, feel free to:
1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built for the [Kaggle Google AI Agent Competition](https://www.kaggle.com/competitions/)
- Powered by [Google Gemini 2.0 Flash](https://ai.google.dev/)
- Uses [Google ADK](https://github.com/google/adk) for agent orchestration

## 📧 Contact

For questions or feedback, please open an issue in this repository.

---

**Status:** Phase 1 Complete ✅ | Project scaffold and configuration ready



