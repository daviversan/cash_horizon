# Cash Horizon - Quick Setup Instructions

**Version:** 1.0  
**Date:** November 18, 2025  
**Setup Time:** ~15-20 minutes

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Install dependencies
cd backend && pip install -r requirements.txt

# 2. Configure environment
cp env.example .env
nano .env  # Add your API keys

# 3. Run the application
uvicorn app.main:app --reload
```

---

## 📋 Prerequisites

- Python 3.10 or higher
- Google Account (for API keys)
- Internet connection
- Terminal/Command Line access

---

## 🔑 Step 1: Get Google API Keys (10 minutes)

### A. Gemini API Key (Required)

1. **Go to Google AI Studio:**
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with your Google account

2. **Create API Key:**
   - Click "Create API Key"
   - Select or create a Google Cloud project
   - Copy the API key (starts with `AIza...`)
   - Save it securely

3. **Verify Key:**
   ```bash
   # Test your key works
   curl -H "Content-Type: application/json" \
        -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=YOUR_KEY"
   ```

### B. Custom Search API Key (Optional but Recommended)

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/
   - Select your project (same as Gemini API)

2. **Enable Custom Search API:**
   - Go to: APIs & Services → Library
   - Search: "Custom Search API"
   - Click "Enable"

3. **Create API Key:**
   - Go to: APIs & Services → Credentials
   - Click "Create Credentials" → "API Key"
   - Copy the key
   - (Optional) Restrict key to Custom Search API only

4. **Create Programmable Search Engine:**
   - Visit: https://programmablesearchengine.google.com/
   - Click "Add" or "Get Started"
   - Name: "Cash Horizon Financial Search"
   - Search: "Search the entire web" OR specific financial sites
   - Create and copy the Search Engine ID (cx)

---

## ⚙️ Step 2: Configure Environment (5 minutes)

### Copy Environment Template

```bash
cd backend
cp env.example .env
```

### Edit Configuration

```bash
# On Windows
notepad .env

# On Mac/Linux
nano .env
# or
vim .env
```

### Required Configuration

**Minimum (just Gemini):**
```bash
GEMINI_API_KEY=your_actual_gemini_api_key_here
SECRET_KEY=your_secret_key_here  # Generate with: openssl rand -hex 32
```

**Recommended (with Search):**
```bash
GEMINI_API_KEY=your_actual_gemini_api_key_here
GOOGLE_SEARCH_API_KEY=your_actual_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
GOOGLE_SEARCH_ENABLED=true
SECRET_KEY=your_secret_key_here
```

### Generate Secret Key

```bash
# On Mac/Linux
openssl rand -hex 32

# On Windows (PowerShell)
-join ((48..57) + (97..102) | Get-Random -Count 32 | % {[char]$_})

# Copy the output and paste into SECRET_KEY
```

---

## 📦 Step 3: Install Dependencies (2-3 minutes)

### Using pip

```bash
cd backend
pip install -r requirements.txt
```

### Using virtual environment (Recommended)

```bash
# Create virtual environment
cd backend
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
# Check that key packages are installed
python -c "import google.genai; print('✅ google-genai installed')"
python -c "from googleapiclient.discovery import build; print('✅ google-api-python-client installed')"
python -c "import fastapi; print('✅ FastAPI installed')"
```

---

## 🗄️ Step 4: Setup Database (1 minute)

### Run Migrations

```bash
cd backend

# Run Alembic migrations
alembic upgrade head
```

### Verify Database

```bash
# Check that database file was created
ls cash_horizon.db
# You should see: cash_horizon.db
```

---

## 🚀 Step 5: Run the Application

### Development Mode

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Production Mode

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify Application is Running

```bash
# In a new terminal, test the health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}
```

---

## 🧪 Step 6: Test the Integration

### Test 1: Basic Health Check

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"healthy"}`

### Test 2: Test Web Search Tool (if configured)

```python
# In Python shell or Jupyter notebook
import asyncio
from app.tools.web_search import web_search

async def test_search():
    result = await web_search.search_investment_options(
        company_stage="early",
        risk_tolerance="moderate"
    )
    print("Source:", result["source"])
    print("Options count:", len(result["options"]))
    print("Web results:", len(result.get("web_research", [])))

# Run test
asyncio.run(test_search())
```

Expected output (with API enabled):
```
Source: google_search_and_curated
Options count: 4-7
Web results: 5
```

Expected output (without API):
```
Source: curated_recommendations
Options count: 4-7
Web results: 0
```

### Test 3: Test Agent Function Calling

```python
# Test that agents use proper ADK function calling
import asyncio
from app.agents.investment_advisor_agent import InvestmentAdvisorAgent

async def test_agent():
    agent = InvestmentAdvisorAgent(company_id=1)
    
    # This should trigger automatic tool calls via Gemini ADK
    result = await agent.advise(
        transactions=[
            {"date": "2024-01-15", "amount": 5000, "type": "expense", "category": "Operations"},
            {"date": "2024-02-01", "amount": 10000, "type": "income", "category": "Revenue"}
        ],
        company_data={
            "initial_capital": 100000,
            "company_stage": "early",
            "industry": "SaaS"
        }
    )
    
    print("Agent type:", result["agent_type"])
    print("Status:", result["status"])

asyncio.run(test_agent())
```

Check logs for: `"Gemini requested function call: ..."`

---

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'google.genai'"

**Solution:**
```bash
pip install google-genai==0.2.2
```

### Issue: "401 Unauthorized" when calling Gemini API

**Solution:**
- Verify API key is correct in `.env`
- Check that Generative Language API is enabled
- Try creating a new API key

### Issue: "Custom Search API error"

**Solution:**
- Verify Custom Search API is enabled in Google Cloud Console
- Check that API key has permission for Custom Search API
- Verify Search Engine ID is correct
- Set `GOOGLE_SEARCH_ENABLED=false` to use fallback mode

### Issue: "Database locked" error

**Solution:**
```bash
# Close all connections and recreate database
rm cash_horizon.db
alembic upgrade head
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001

# Or kill the process using port 8000
# On Mac/Linux:
lsof -ti:8000 | xargs kill -9
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 📊 Verify Everything Works

### Checklist

Run through this checklist to ensure everything is set up correctly:

- [ ] Dependencies installed (`pip list | grep google`)
- [ ] `.env` file configured with API keys
- [ ] Database created (`ls cash_horizon.db`)
- [ ] Application starts without errors
- [ ] Health check returns `{"status":"healthy"}`
- [ ] Web search works (or fallback enabled)
- [ ] Agents can be imported without errors
- [ ] Logs show function calling activity

### Expected Log Output

When running the application, you should see logs like:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:app.tools.web_search:Google Custom Search API initialized successfully
INFO:app.agents.base_agent:Initialized investment_advisor agent
```

---

## 🎯 Next Steps

### 1. Explore the Codebase

- Read `PHASE_3_COMPLETION.md` for architecture overview
- Read `GOOGLE_ADK_INTEGRATION_GUIDE.md` for integration details
- Read `PHASE_3_ADK_INTEGRATION_SUMMARY.md` for what changed

### 2. Test the Agents

- Financial Analyst Agent
- Runway Predictor Agent
- Investment Advisor Agent
- Orchestrator (all agents together)

### 3. Build the API (Phase 4)

- Create FastAPI routers for agent endpoints
- Add authentication and authorization
- Implement background task processing
- Add API documentation (Swagger/OpenAPI)

### 4. Deploy to Production

- Choose hosting platform (Google Cloud Run, AWS, etc.)
- Configure production environment variables
- Set up monitoring and logging
- Configure domain and SSL

---

## 📚 Additional Resources

### Documentation

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Custom Search API Docs](https://developers.google.com/custom-search/v1/overview)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Project Documentation

- `PHASE_3_COMPLETION.md` - Phase 3 overview
- `GOOGLE_ADK_INTEGRATION_GUIDE.md` - Complete integration guide
- `PHASE_3_ADK_INTEGRATION_SUMMARY.md` - What changed in ADK integration
- `backend/env.example` - Environment configuration reference

### Support

For issues:
1. Check troubleshooting section above
2. Review application logs for errors
3. Check Google Cloud Console for API errors
4. Verify environment configuration

---

## ✅ Success Criteria

You're ready to proceed when:

- ✅ Application starts without errors
- ✅ All tests pass
- ✅ Agents can execute and call tools
- ✅ Web search returns results (or fallback works)
- ✅ Database queries work
- ✅ Logs show proper function calling

**Congratulations! Your Cash Horizon agent system is ready!** 🎉

---

## 🔐 Security Reminders

**Before committing code:**

```bash
# Make sure .env is in .gitignore
echo ".env" >> .gitignore

# Never commit API keys
git status  # Verify .env is not tracked
```

**Production checklist:**

- [ ] Use strong SECRET_KEY (32+ characters)
- [ ] Restrict API keys to specific APIs
- [ ] Enable application restrictions (IP/domain)
- [ ] Set up billing alerts
- [ ] Enable Cloud Logging
- [ ] Use HTTPS in production
- [ ] Set up rate limiting

---

*Cash Horizon - AI-Powered Startup Financial Health Tracking*  
*Setup completed successfully!*

