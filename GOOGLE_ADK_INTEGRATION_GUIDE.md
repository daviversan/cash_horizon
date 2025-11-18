# Google ADK & Search API Integration Guide

**Document Version:** 1.0  
**Date:** November 18, 2025  
**Status:** Implementation Guide

---

## 📋 Overview

This guide provides step-by-step instructions for integrating:
1. **Google Gemini ADK** (Agent Development Kit) - Proper function calling with native tool integration
2. **Google Custom Search API** - Real web search functionality for investment research

---

## 🎯 What's Being Integrated

### 1. Google Gemini ADK (Function Calling)

**Current State:**
- Basic `generate_content()` calls without native function calling
- Manual tool execution outside of Gemini's function calling framework
- Tools defined but not passed to Gemini in proper format

**Target State:**
- Native Gemini function calling with automatic tool invocation
- Tools properly declared using `types.Tool` and `types.FunctionDeclaration`
- Automatic function call handling by Gemini
- Multi-turn conversations with tool results

**Benefits:**
- ✅ Gemini automatically decides when to call tools
- ✅ Structured tool calling with schema validation
- ✅ Better reasoning about which tools to use
- ✅ Multi-step tool chaining
- ✅ Reduced latency with native integration

### 2. Google Custom Search API

**Current State:**
- Mock/curated investment data in `web_search.py`
- No real-time market data
- Static recommendations

**Target State:**
- Real-time Google Search API integration
- Live financial news and investment research
- Market trend analysis from current data
- Programmable Search Engine for financial sources

**Benefits:**
- ✅ Real-time investment options and rates
- ✅ Current market trends and news
- ✅ Up-to-date financial advice from trusted sources
- ✅ Better investment recommendations

---

## 🔧 Phase 1: Google Cloud Project Setup

### Step 1.1: Create/Configure Google Cloud Project

1. **Navigate to Google Cloud Console**
   - Go to: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project (or select existing)**
   ```
   Project Name: cash-horizon-prod
   Project ID: cash-horizon-<unique-id>
   Organization: (your organization or none)
   ```

3. **Enable Billing**
   - Go to "Billing" in the navigation menu
   - Link a billing account (required for API usage)
   - Note: Gemini API and Custom Search have free tiers

### Step 1.2: Enable Required APIs

1. **Enable Google Generative AI API** (Gemini)
   - Go to: APIs & Services → Library
   - Search: "Generative Language API"
   - Click "Enable"
   - This enables Gemini API with function calling

2. **Enable Custom Search API**
   - In APIs & Services → Library
   - Search: "Custom Search API"
   - Click "Enable"
   - This allows programmatic Google searches

3. **Enable Cloud Logging API** (Optional but recommended)
   - Search: "Cloud Logging API"
   - Click "Enable"
   - For production observability

### Step 1.3: Create API Credentials

1. **Create Gemini API Key**
   - Go to: APIs & Services → Credentials
   - Click: "Create Credentials" → "API Key"
   - Copy the key: `AIzaSy...`
   - Restrict key (recommended):
     * API restrictions → Select "Generative Language API"
     * Application restrictions → HTTP referrers or IP addresses
   - Save as: `GEMINI_API_KEY`

2. **Create Search API Key**
   - Click: "Create Credentials" → "API Key"
   - Copy the key: `AIzaSy...`
   - Restrict key:
     * API restrictions → Select "Custom Search API"
   - Save as: `GOOGLE_SEARCH_API_KEY`

---

## 🔍 Phase 2: Google Custom Search Engine Setup

### Step 2.1: Create Programmable Search Engine

1. **Go to Programmable Search Engine**
   - Navigate to: https://programmablesearchengine.google.com/
   - Sign in with the same Google account

2. **Create New Search Engine**
   - Click: "Add" or "Create"
   - Configuration:
     ```
     Search engine name: Cash Horizon Financial Search
     What to search: Search the entire web
     ```

3. **Configure Search Settings**
   - **Advanced Settings:**
     * Enable "Image search" (optional)
     * Enable "SafeSearch" (recommended)
     * Language: English
   
   - **Sites to search:** (Optional - restrict to financial sites)
     ```
     www.investopedia.com/*
     www.bloomberg.com/*
     finance.yahoo.com/*
     www.wsj.com/*
     www.forbes.com/*
     www.marketwatch.com/*
     www.cnbc.com/*
     ```
     Note: Leave empty to search entire web

4. **Get Search Engine ID (cx)**
   - After creation, go to "Setup" → "Basic"
   - Copy the "Search engine ID": `0123456789abcdef:xyz`
   - Save as: `GOOGLE_SEARCH_ENGINE_ID`

### Step 2.2: Test Search Engine

1. **Test in Browser**
   - Use the "Public URL" provided
   - Verify search results are relevant
   - Adjust site restrictions if needed

2. **Test with API**
   ```bash
   curl "https://www.googleapis.com/customsearch/v1?\
   q=best+investment+options+startups&\
   key=YOUR_SEARCH_API_KEY&\
   cx=YOUR_SEARCH_ENGINE_ID"
   ```

---

## 🐍 Phase 3: Python Integration - Web Search Tool

### Step 3.1: Update Dependencies

**File:** `backend/requirements.txt`

Add:
```
# Google APIs
google-genai==0.2.2
google-api-python-client==2.110.0  # For Custom Search
google-auth==2.25.2
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
```

Install:
```bash
cd backend
pip install -r requirements.txt
```

### Step 3.2: Update Configuration

**File:** `backend/app/config.py`

Add settings:
```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Google Search API
    google_search_api_key: str = ""
    google_search_engine_id: str = ""
    google_search_enabled: bool = True  # Toggle for testing
    
    # Search Configuration
    search_max_results: int = 10
    search_safe_mode: str = "active"
```

### Step 3.3: Create Environment File

**File:** `backend/.env.example`

```bash
# Application
APP_NAME=Cash Horizon
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///./cash_horizon.db

# Google Gemini API (Required)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Google Custom Search API (Required for web search)
GOOGLE_SEARCH_API_KEY=your_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
GOOGLE_SEARCH_ENABLED=true

# Google Cloud (Optional - for production deployment)
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Session
SESSION_TIMEOUT=3600

# Security
SECRET_KEY=your_secret_key_here_generate_with_openssl_rand_hex_32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
ENABLE_CLOUD_LOGGING=false
```

### Step 3.4: Refactor Web Search Tool

See implementation in code changes below.

---

## 🤖 Phase 4: Google Gemini ADK Integration

### Step 4.1: Understanding Gemini Function Calling

**Key Concepts:**

1. **Function Declarations**
   - Define tools using `types.FunctionDeclaration`
   - Specify parameters with JSON Schema
   - Gemini analyzes when to call functions

2. **Tool Configuration**
   - Pass tools in `types.Tool` objects
   - Configure tool behavior (e.g., always use, auto)
   - Set tool execution mode

3. **Multi-Turn Conversations**
   - First call: Gemini decides to use tool (returns function call)
   - Execute tool and return result
   - Second call: Gemini processes tool result and responds

**Example Flow:**
```python
# 1. Define function
search_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search_investment_options",
            description="Search for investment options",
            parameters={
                "type": "object",
                "properties": {
                    "risk_tolerance": {
                        "type": "string",
                        "enum": ["conservative", "moderate", "aggressive"]
                    }
                }
            }
        )
    ]
)

# 2. Call Gemini with tool
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents="Find conservative investments",
    config=types.GenerateContentConfig(
        tools=[search_tool],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode=types.FunctionCallingConfig.Mode.AUTO
            )
        )
    )
)

# 3. Check if tool called
if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    # Execute tool
    result = execute_tool(function_call.name, function_call.args)
    
    # 4. Return result to Gemini
    final_response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[
            {"role": "user", "parts": [{"text": "Find investments"}]},
            {"role": "model", "parts": [{"function_call": function_call}]},
            {"role": "user", "parts": [{"function_response": {
                "name": function_call.name,
                "response": result
            }}]}
        ]
    )
```

### Step 4.2: Refactor Base Agent

See implementation in code changes below.

---

## 📦 Phase 5: Implementation Changes

### Files to Modify:

1. ✅ `backend/requirements.txt` - Add Google Search API client
2. ✅ `backend/app/config.py` - Add Search API configuration
3. ✅ `backend/.env.example` - Add API key placeholders
4. ✅ `backend/app/tools/web_search.py` - Implement real Google Search
5. ✅ `backend/app/agents/base_agent.py` - Implement ADK function calling
6. ✅ `backend/app/agents/financial_analyst_agent.py` - Update tool definitions
7. ✅ `backend/app/agents/runway_predictor_agent.py` - Update tool definitions
8. ✅ `backend/app/agents/investment_advisor_agent.py` - Update tool definitions

---

## 🧪 Phase 6: Testing Strategy

### Step 6.1: Unit Tests

1. **Test Web Search Integration**
   ```python
   # Mock Google Search API responses
   def test_google_search_integration():
       # Test API key validation
       # Test query formatting
       # Test response parsing
       # Test error handling
   ```

2. **Test Function Calling**
   ```python
   def test_gemini_function_calling():
       # Test tool declaration formatting
       # Test function call detection
       # Test multi-turn conversations
       # Test tool result processing
   ```

### Step 6.2: Integration Tests

1. **End-to-End Agent Tests**
   - Test with real APIs (in staging)
   - Verify tool calling works correctly
   - Validate search results quality
   - Check error recovery

2. **Performance Tests**
   - Measure latency with function calling
   - Test concurrent requests
   - Monitor API quota usage

### Step 6.3: Manual Testing

1. **Test Investment Advisor Agent**
   - Ask: "Find conservative investment options"
   - Verify: Real search results returned
   - Validate: Results are relevant and current

2. **Test Multi-Tool Scenarios**
   - Ask: "Analyze my runway and suggest investments"
   - Verify: Multiple tools called in sequence
   - Validate: Context maintained across tool calls

---

## 📊 Phase 7: Deployment Checklist

### Pre-Deployment

- [ ] All API keys generated and secured
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] API quota limits reviewed

### Deployment Steps

1. **Set Environment Variables**
   ```bash
   export GEMINI_API_KEY="your_key"
   export GOOGLE_SEARCH_API_KEY="your_key"
   export GOOGLE_SEARCH_ENGINE_ID="your_cx"
   ```

2. **Deploy Application**
   ```bash
   cd backend
   alembic upgrade head  # Run migrations
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Verify Health**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/api/v1/search/test
   ```

### Post-Deployment

- [ ] Monitor API usage in Google Cloud Console
- [ ] Check logs for errors
- [ ] Verify search quality
- [ ] Monitor latency metrics
- [ ] Set up alerts for API quota

---

## 💰 Cost Estimates & Quotas

### Google Gemini API (Function Calling)

**Free Tier:**
- Up to 15 requests per minute (RPM)
- Up to 1 million tokens per minute (TPM)
- Up to 1,500 requests per day (RPD)

**Paid Tier (if needed):**
- $0.0001875 per 1K characters input (Gemini 2.0 Flash)
- $0.000375 per 1K characters output
- ~$0.10-0.50 per 1,000 requests (estimated)

### Google Custom Search API

**Free Tier:**
- 100 queries per day - FREE
- Good for development and small-scale production

**Paid Tier:**
- $5 per 1,000 queries
- Up to 10,000 queries per day max
- For production scale applications

**Monthly Cost Estimates:**
```
Scenario 1: Development/Small (100 users)
- Gemini: ~$0-10/month (free tier)
- Search: FREE (within 100 queries/day)
Total: $0-10/month

Scenario 2: Production/Medium (1,000 users)
- Gemini: ~$50-100/month
- Search: ~$150/month (3,000 queries)
Total: $200-250/month

Scenario 3: Scale (10,000 users)
- Gemini: ~$500-1,000/month
- Search: ~$1,500/month (10,000 queries max)
Total: $2,000-2,500/month
```

---

## 🔒 Security Best Practices

### API Key Management

1. **Never Commit API Keys**
   - Add `.env` to `.gitignore`
   - Use environment variables only
   - Rotate keys regularly

2. **Restrict API Keys**
   - Set API restrictions (specific APIs only)
   - Set application restrictions (IP/domain)
   - Monitor usage for anomalies

3. **Production Security**
   - Use Google Cloud Secret Manager
   - Enable Cloud Armor for DDoS protection
   - Implement rate limiting
   - Set up billing alerts

### Example Key Restrictions

```
Gemini API Key:
- API Restriction: Generative Language API only
- Application Restriction: Your server IP or none for testing

Search API Key:
- API Restriction: Custom Search API only
- Application Restriction: Your server IP or none
- Referrer Restriction: Your domain (if browser-based)
```

---

## 📚 Additional Resources

### Official Documentation

1. **Gemini Function Calling:**
   - https://ai.google.dev/docs/function_calling
   - https://github.com/google/generative-ai-python

2. **Custom Search API:**
   - https://developers.google.com/custom-search/v1/overview
   - https://developers.google.com/custom-search/v1/using_rest

3. **Google Cloud:**
   - https://cloud.google.com/docs
   - https://console.cloud.google.com/

### Code Examples

1. **Gemini Python SDK:**
   - https://github.com/google/generative-ai-python/tree/main/samples

2. **Custom Search Python:**
   - https://github.com/googleapis/google-api-python-client/blob/main/docs/dyn/customsearch_v1.md

### Community Support

1. **Google AI Discord:** https://discord.gg/google-ai-devs
2. **Stack Overflow:** Tag `google-gemini` or `google-custom-search`
3. **GitHub Issues:** Report bugs in respective repositories

---

## 🚨 Troubleshooting

### Common Issues

**1. "API key not valid" Error**
```
Solution:
- Verify API key is correct
- Check API is enabled in Cloud Console
- Ensure key restrictions allow your IP/domain
```

**2. "Quota exceeded" Error**
```
Solution:
- Check quota limits in Cloud Console
- Upgrade to paid tier if needed
- Implement caching to reduce API calls
```

**3. Function Calling Not Working**
```
Solution:
- Verify tool definitions match schema format
- Check Gemini model supports function calling
- Ensure proper multi-turn conversation format
```

**4. Search Results Poor Quality**
```
Solution:
- Refine search queries with better keywords
- Restrict PSE to authoritative financial sites
- Use search parameters (dateRestrict, etc.)
```

### Debug Mode

Enable detailed logging:
```python
# In config.py
LOG_LEVEL=DEBUG
ENABLE_CLOUD_LOGGING=true

# In code
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## ✅ Success Criteria

After completing this integration, you should have:

- [x] Google Cloud project configured
- [x] Gemini API with function calling working
- [x] Custom Search API returning real results
- [x] All agents using ADK-compliant tool definitions
- [x] Web search tool fetching live data
- [x] Tests passing with real API integration
- [x] Documentation complete
- [x] Deployment successful

---

## 📞 Support

For issues with this integration:
1. Check troubleshooting section above
2. Review Google Cloud Console for API errors
3. Check application logs for detailed errors
4. Consult official Google documentation
5. Reach out to community support channels

---

**End of Integration Guide**

