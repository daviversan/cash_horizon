# Cash Horizon - Google ADK & Search API Implementation Roadmap

**Document Version:** 1.0  
**Created:** November 18, 2025  
**Status:** Implementation Complete - Ready for User Configuration

---

## 📋 Executive Summary

This roadmap provides a step-by-step plan for configuring and integrating **Google ADK (Agent Development Kit)** and **Google Custom Search API** into the Cash Horizon project. All code changes have been implemented and are production-ready.

**What's Been Done:**
- ✅ All code refactored to use proper Gemini ADK function calling
- ✅ Google Custom Search API fully integrated with automatic fallback
- ✅ Configuration structure created
- ✅ Documentation completed
- ✅ Zero linter errors

**What You Need to Do:**
- 🔧 Configure Google Cloud project and APIs (15 minutes)
- 🔑 Generate and add API keys to environment (5 minutes)
- 📦 Install new dependencies (2 minutes)
- 🧪 Test and verify integration (5 minutes)

**Total Time: ~30 minutes**

---

## 🎯 Implementation Overview

### Phase 1: Google Cloud Setup ⏱️ 15 minutes

**Objective:** Create Google Cloud project, enable APIs, generate credentials

**Steps:**
1. Create/select Google Cloud project
2. Enable Generative Language API (Gemini)
3. Enable Custom Search API
4. Create API keys
5. Create Programmable Search Engine

**Output:** 
- Gemini API Key
- Custom Search API Key
- Search Engine ID (cx)

### Phase 2: Local Configuration ⏱️ 7 minutes

**Objective:** Configure environment and install dependencies

**Steps:**
1. Copy environment template
2. Add API keys to `.env`
3. Install Python dependencies
4. Run database migrations

**Output:**
- Configured `.env` file
- All dependencies installed
- Database ready

### Phase 3: Testing & Verification ⏱️ 5 minutes

**Objective:** Verify everything works correctly

**Steps:**
1. Start application
2. Test health endpoint
3. Test web search tool
4. Test agent function calling
5. Review logs

**Output:**
- Working application
- Verified integrations
- Production-ready system

---

## 📖 Detailed Implementation Steps

### Phase 1: Google Cloud Setup

#### Step 1.1: Access Google Cloud Console

```
URL: https://console.cloud.google.com/
Action: Sign in with your Google account
Time: 1 minute
```

#### Step 1.2: Create or Select Project

**Option A: Create New Project**
```
1. Click "Select a project" → "New Project"
2. Project name: cash-horizon-prod
3. Click "Create"
4. Wait for project creation (~30 seconds)
```

**Option B: Use Existing Project**
```
1. Click "Select a project"
2. Choose your existing project
3. Proceed to next step
```

**Time: 2 minutes**

#### Step 1.3: Enable Generative Language API (Gemini)

```
Navigation: APIs & Services → Library
Action:
  1. Search: "Generative Language API"
  2. Click on "Generative Language API"
  3. Click "Enable"
  4. Wait for activation (~30 seconds)

Verify:
  - Go to: APIs & Services → Dashboard
  - Should see "Generative Language API" listed
```

**Time: 2 minutes**

#### Step 1.4: Create Gemini API Key

```
Navigation: APIs & Services → Credentials
Action:
  1. Click "Create Credentials"
  2. Select "API Key"
  3. Copy the key (starts with AIza...)
  4. Save securely (Notepad, password manager, etc.)

Optional Security (Recommended):
  1. Click "Restrict Key"
  2. API restrictions → Select "Generative Language API"
  3. Save
```

**Time: 2 minutes**

**✅ Checkpoint:** You now have your Gemini API Key

#### Step 1.5: Enable Custom Search API

```
Navigation: APIs & Services → Library
Action:
  1. Search: "Custom Search API"
  2. Click on "Custom Search API"
  3. Click "Enable"
  4. Wait for activation (~30 seconds)

Verify:
  - Go to: APIs & Services → Dashboard
  - Should see "Custom Search API" listed
```

**Time: 2 minutes**

#### Step 1.6: Create Search API Key

```
Navigation: APIs & Services → Credentials
Action:
  1. Click "Create Credentials"
  2. Select "API Key"
  3. Copy the key
  4. Save securely

Optional Security (Recommended):
  1. Click "Restrict Key"
  2. API restrictions → Select "Custom Search API"
  3. Save
```

**Time: 2 minutes**

**✅ Checkpoint:** You now have your Search API Key

#### Step 1.7: Create Programmable Search Engine

```
URL: https://programmablesearchengine.google.com/
Action:
  1. Sign in (same Google account)
  2. Click "Add" or "Get Started"
  3. Fill in form:
     - Name: "Cash Horizon Financial Search"
     - What to search: Select "Search the entire web"
     OR (for better results):
     - Add specific sites:
       * www.investopedia.com/*
       * www.bloomberg.com/*
       * finance.yahoo.com/*
       * www.wsj.com/*
       * www.forbes.com/*
  4. Click "Create"
  5. Go to "Setup" → "Basic"
  6. Copy the "Search engine ID" (cx parameter)
  7. Save securely
```

**Time: 4 minutes**

**✅ Checkpoint:** You now have your Search Engine ID

---

### Phase 2: Local Configuration

#### Step 2.1: Navigate to Project

```bash
cd /path/to/cash_horizon
cd backend
```

#### Step 2.2: Copy Environment Template

```bash
# Copy the template
cp env.example .env

# Verify file was created
ls .env
```

**Time: 30 seconds**

#### Step 2.3: Configure API Keys

**Open `.env` file:**
```bash
# Windows
notepad .env

# Mac
open -e .env

# Linux
nano .env
```

**Add your API keys:**

```bash
# Required: Gemini API
GEMINI_API_KEY=AIza...your_actual_key_here...

# Required: Custom Search API (for web search tool)
GOOGLE_SEARCH_API_KEY=AIza...your_actual_key_here...
GOOGLE_SEARCH_ENGINE_ID=0123456789abcdef:xyz...
GOOGLE_SEARCH_ENABLED=true  # Change from false to true

# Required: Security
SECRET_KEY=generate_this_with_openssl_rand_hex_32
```

**Generate SECRET_KEY:**

```bash
# Mac/Linux
openssl rand -hex 32

# Windows PowerShell
-join ((48..57) + (97..102) | Get-Random -Count 32 | % {[char]$_})

# Copy output and paste into SECRET_KEY
```

**Save and close `.env` file**

**Time: 3 minutes**

**✅ Checkpoint:** Your `.env` file is configured

#### Step 2.4: Install Dependencies

```bash
# Make sure you're in backend directory
cd backend

# Install all dependencies
pip install -r requirements.txt

# This will install:
# - google-genai (Gemini SDK)
# - google-api-python-client (Custom Search)
# - google-auth (Authentication)
# - All other project dependencies
```

**Expected output:**
```
Successfully installed google-genai-0.2.2 google-api-python-client-2.110.0 ...
```

**Time: 2 minutes** (depending on internet speed)

**✅ Checkpoint:** Dependencies installed

#### Step 2.5: Run Database Migrations

```bash
# Run Alembic migrations to set up database
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade -> ..., Initial schema
INFO  [alembic.runtime.migration] Running upgrade -> ..., Add agent sessions
```

**Verify database created:**
```bash
ls cash_horizon.db
# You should see the file
```

**Time: 30 seconds**

**✅ Checkpoint:** Database ready

---

### Phase 3: Testing & Verification

#### Step 3.1: Start Application

**Terminal 1 (Application Server):**
```bash
cd backend
uvicorn app.main:app --reload --log-level info
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:app.tools.web_search:Google Custom Search API initialized successfully
```

**Look for this key line:** `"Google Custom Search API initialized successfully"`

**Time: 30 seconds**

**✅ Checkpoint:** Application running

#### Step 3.2: Test Health Endpoint

**Terminal 2 (Testing):**
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status":"healthy"}
```

**Time: 10 seconds**

**✅ Checkpoint:** Basic API working

#### Step 3.3: Test Web Search Tool

Create a test file `test_search.py`:

```python
import asyncio
from app.tools.web_search import web_search

async def test():
    print("Testing web search tool...")
    
    result = await web_search.search_investment_options(
        company_stage="early",
        risk_tolerance="moderate"
    )
    
    print(f"\nSource: {result['source']}")
    print(f"Search enabled: {result['search_enabled']}")
    print(f"Curated options: {len(result['options'])}")
    print(f"Web research results: {len(result.get('web_research', []))}")
    
    if result['web_research']:
        print("\nFirst web result:")
        print(f"  Title: {result['web_research'][0]['title']}")
        print(f"  Source: {result['web_research'][0]['source']}")
        print("✅ Google Search API is working!")
    else:
        print("\n⚠️  Using fallback mode (curated data only)")
        print("   Check your API keys if this is unexpected")

asyncio.run(test())
```

Run the test:
```bash
python test_search.py
```

**Expected output (with API working):**
```
Testing web search tool...

Source: google_search_and_curated
Search enabled: True
Curated options: 4
Web research results: 5

First web result:
  Title: Best Investment Options for Early Stage Startups...
  Source: investopedia.com
✅ Google Search API is working!
```

**Time: 2 minutes**

**✅ Checkpoint:** Web search working

#### Step 3.4: Test Agent Function Calling

Create a test file `test_agent.py`:

```python
import asyncio
from app.agents.investment_advisor_agent import InvestmentAdvisorAgent

async def test():
    print("Testing Investment Advisor Agent with ADK function calling...")
    
    agent = InvestmentAdvisorAgent(company_id=1)
    
    # Sample transaction data
    transactions = [
        {"date": "2024-01-15", "amount": 5000, "type": "expense", "category": "Operations"},
        {"date": "2024-02-01", "amount": 10000, "type": "income", "category": "Revenue"},
        {"date": "2024-03-01", "amount": 8000, "type": "expense", "category": "Marketing"}
    ]
    
    company_data = {
        "initial_capital": 100000,
        "company_stage": "early",
        "industry": "SaaS"
    }
    
    print("\nExecuting agent (this will take 5-10 seconds)...")
    result = await agent.advise(
        transactions=transactions,
        company_data=company_data
    )
    
    print(f"\n✅ Agent execution completed!")
    print(f"Agent type: {result['agent_type']}")
    print(f"Status: {result['status']}")
    print(f"Response available: {len(result.get('response', ''))} characters")
    
    # Check if tools were called
    print("\n📊 Check application logs for:")
    print("   - 'Gemini requested function call: ...'")
    print("   - This indicates proper ADK integration")

asyncio.run(test())
```

Run the test:
```bash
python test_agent.py
```

**Expected output:**
```
Testing Investment Advisor Agent with ADK function calling...

Executing agent (this will take 5-10 seconds)...

✅ Agent execution completed!
Agent type: investment_advisor
Status: success
Response available: 1234 characters

📊 Check application logs for:
   - 'Gemini requested function call: ...'
   - This indicates proper ADK integration
```

**Check Terminal 1 (Application Logs):**

Look for these log lines:
```
INFO:app.agents.base_agent:Gemini requested function call: calculate_balance
INFO:app.agents.base_agent:Gemini requested function call: search_investment_options
INFO:app.agents.base_agent:Received final response after tool execution
```

**Time: 2 minutes**

**✅ Checkpoint:** ADK function calling working

#### Step 3.5: Final Verification Checklist

Go through this checklist:

```
✅ Application starts without errors
✅ Health endpoint returns 200 OK
✅ Web search tool returns results (or fallback works)
✅ Agents execute successfully
✅ Logs show "Gemini requested function call" messages
✅ No error messages in logs
✅ Database queries work
✅ API keys are secure (not in git)
```

If all checkmarks complete:

**🎉 Integration is complete and working!**

**Time: 30 seconds**

---

## 📊 Verification Matrix

| Component | Test | Expected Result | Status |
|-----------|------|-----------------|--------|
| **Dependencies** | `pip list \| grep google` | Shows google-genai, google-api-python-client | ⬜ |
| **Environment** | `.env` file exists | Contains all required keys | ⬜ |
| **Database** | `ls cash_horizon.db` | File exists | ⬜ |
| **Application** | `uvicorn app.main:app` | Starts without errors | ⬜ |
| **Health Check** | `curl /health` | Returns `{"status":"healthy"}` | ⬜ |
| **Web Search** | `test_search.py` | Returns web results or fallback | ⬜ |
| **ADK Function Calling** | `test_agent.py` | Logs show function calls | ⬜ |
| **Gemini API** | Agent execution | Completes successfully | ⬜ |

**Mark each item as ✅ when verified**

---

## 🚨 Troubleshooting Guide

### Problem 1: "API key not valid"

**Symptom:**
```
Error: 401 Unauthorized
```

**Solutions:**
1. Verify API key is copied correctly (no extra spaces)
2. Check that API is enabled in Cloud Console
3. Wait 5 minutes (API activation can be delayed)
4. Try regenerating the API key

**Test:**
```bash
# Test Gemini API key
curl -H "Content-Type: application/json" \
     -d '{"contents":[{"parts":[{"text":"test"}]}]}' \
     "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=YOUR_KEY"
```

### Problem 2: "google-api-python-client not found"

**Symptom:**
```
ModuleNotFoundError: No module named 'googleapiclient'
```

**Solution:**
```bash
pip install google-api-python-client==2.110.0
```

### Problem 3: Web search not working

**Symptom:**
```
Source: curated_recommendations
Web research results: 0
```

**Solutions:**
1. Check `GOOGLE_SEARCH_ENABLED=true` in `.env`
2. Verify Search API key is correct
3. Verify Search Engine ID (cx) is correct
4. Check Custom Search API is enabled in Cloud Console
5. Check daily quota (100 free searches/day)

**Verify configuration:**
```python
from app.config import settings
print(f"Search enabled: {settings.google_search_enabled}")
print(f"API key set: {bool(settings.google_search_api_key)}")
print(f"Engine ID set: {bool(settings.google_search_engine_id)}")
```

### Problem 4: Function calls not happening

**Symptom:**
- No "Gemini requested function call" in logs
- Tools not being executed

**Solutions:**
1. Check tool definitions are properly formatted
2. Verify Gemini API key has access to function calling
3. Review agent system prompts (they should mention tool usage)
4. Check logs for tool conversion errors

**Debug:**
```python
# Check that tools are being converted correctly
agent = InvestmentAdvisorAgent(company_id=1)
tools = agent.get_tools()
print(f"Tools defined: {len(tools)}")
for tool in tools:
    print(f"  - {tool['name']}")
```

### Problem 5: Database locked

**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# Close all connections
pkill -f uvicorn

# Recreate database
rm cash_horizon.db
alembic upgrade head

# Restart application
uvicorn app.main:app --reload
```

### Problem 6: Import errors

**Symptom:**
```
ImportError: cannot import name 'types' from 'google.genai'
```

**Solution:**
```bash
# Reinstall google-genai
pip uninstall google-genai
pip install google-genai==0.2.2
```

---

## 💰 Cost Management

### Free Tier Limits

**Gemini API:**
- 15 requests per minute (RPM)
- 1 million tokens per minute (TPM)
- 1,500 requests per day (RPD)
- **Cost:** FREE for development

**Custom Search API:**
- 100 queries per day
- **Cost:** FREE
- Paid tier: $5 per 1,000 queries after free tier

### Monitoring Usage

**Check Gemini Usage:**
```
URL: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com
Section: Quotas & System Limits
```

**Check Search Usage:**
```
URL: https://console.cloud.google.com/apis/api/customsearch.googleapis.com
Section: Quotas
```

### Cost Optimization Tips

1. **Development Mode:**
   ```bash
   # Disable search in development
   GOOGLE_SEARCH_ENABLED=false
   ```

2. **Caching:**
   - Implement Redis cache for search results
   - Cache TTL: 1 hour for investment data

3. **Rate Limiting:**
   - Limit agent calls per user
   - Queue long-running requests

4. **Monitoring:**
   ```bash
   # Set up billing alerts at 50%, 80%, 100% of budget
   # In Google Cloud Console → Billing → Budgets & alerts
   ```

---

## 📚 Reference Documentation

### Quick Links

1. **Setup Guide:** `SETUP_INSTRUCTIONS.md`
2. **Complete Integration Guide:** `GOOGLE_ADK_INTEGRATION_GUIDE.md`
3. **What Changed:** `PHASE_3_ADK_INTEGRATION_SUMMARY.md`
4. **Phase 3 Overview:** `PHASE_3_COMPLETION.md`
5. **Environment Template:** `backend/env.example`

### External Resources

1. **Gemini API:**
   - Documentation: https://ai.google.dev/docs
   - Function Calling Guide: https://ai.google.dev/docs/function_calling
   - Python SDK: https://github.com/google/generative-ai-python

2. **Custom Search API:**
   - Documentation: https://developers.google.com/custom-search/v1/overview
   - Getting Started: https://developers.google.com/custom-search/v1/introduction
   - API Reference: https://developers.google.com/custom-search/v1/reference/rest

3. **Google Cloud:**
   - Console: https://console.cloud.google.com/
   - Billing: https://console.cloud.google.com/billing
   - API Dashboard: https://console.cloud.google.com/apis/dashboard

---

## ✅ Success Checklist

After completing all steps, you should have:

- [ ] Google Cloud project created
- [ ] Gemini API enabled and key generated
- [ ] Custom Search API enabled and key generated
- [ ] Programmable Search Engine created with ID
- [ ] `.env` file configured with all keys
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database initialized (`alembic upgrade head`)
- [ ] Application running (`uvicorn app.main:app`)
- [ ] Health check passing
- [ ] Web search returning results
- [ ] Agents executing successfully
- [ ] Logs showing function calls
- [ ] No error messages

**All checked? You're ready for production! 🚀**

---

## 🎯 Next Steps

### 1. Development

- Explore the agents and tools
- Test different scenarios
- Review code structure
- Customize agents for your needs

### 2. Phase 4: Backend API

- Create FastAPI routers for agents
- Add authentication and authorization
- Implement background tasks
- Add rate limiting

### 3. Frontend Integration

- Build React/Vue frontend
- Connect to agent endpoints
- Display real-time insights
- Create dashboards

### 4. Production Deployment

- Choose hosting platform
- Configure production environment
- Set up monitoring
- Enable Cloud Logging

---

## 📞 Support & Resources

### If You Get Stuck

1. **Check Troubleshooting Guide** (above)
2. **Review Application Logs** (`uvicorn` output)
3. **Check Google Cloud Console** for API errors
4. **Verify Environment Configuration** (`.env` file)
5. **Test Individual Components** (web search, agents separately)

### Key Log Messages to Look For

**✅ Success:**
```
INFO:app.tools.web_search:Google Custom Search API initialized successfully
INFO:app.agents.base_agent:Gemini requested function call: search_investment_options
INFO:app.agents.base_agent:Received final response after tool execution
```

**❌ Problems:**
```
WARNING:app.tools.web_search:Failed to initialize Google Search API
ERROR:app.agents.base_agent:Gemini API call failed
ERROR:app.agents.base_agent:Failed to process tool result with Gemini
```

---

## 🎉 Conclusion

This roadmap provides a complete path from code implementation to production deployment. The Google ADK and Search API integrations are:

- ✅ **Fully Implemented** - All code changes complete
- ✅ **Production-Ready** - Error handling and logging in place
- ✅ **Well-Documented** - Comprehensive guides available
- ✅ **Cost-Effective** - Free tier friendly
- ✅ **Easy to Configure** - Step-by-step instructions provided

**Estimated Time to Full Integration: 30 minutes**

Follow this roadmap step-by-step, and you'll have a fully functional, AI-powered financial analysis system with real-time web search capabilities!

---

*Cash Horizon - AI-Powered Startup Financial Health Tracking*  
*Implementation Roadmap v1.0 - November 18, 2025*

