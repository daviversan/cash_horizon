"""Unit tests for agents."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.financial_analyst_agent import FinancialAnalystAgent
from app.agents.runway_predictor_agent import RunwayPredictorAgent
from app.agents.investment_advisor_agent import InvestmentAdvisorAgent
from app.agents.orchestrator import AgentOrchestrator, WorkflowType
from app.models.agent_session import AgentType


@pytest.fixture
def sample_transactions():
    """Create sample transactions for testing."""
    base_date = datetime.utcnow()
    transactions = []
    
    # 3 months of transactions
    for month in range(3):
        month_date = (base_date - timedelta(days=30 * month)).isoformat()
        
        # Monthly income
        transactions.append({
            "date": month_date,
            "amount": 50000.0,
            "category": "Revenue",
            "type": "income"
        })
        
        # Monthly expenses
        transactions.append({
            "date": month_date,
            "amount": 30000.0,
            "category": "Salaries",
            "type": "expense"
        })
        transactions.append({
            "date": month_date,
            "amount": 10000.0,
            "category": "Marketing",
            "type": "expense"
        })
        transactions.append({
            "date": month_date,
            "amount": 5000.0,
            "category": "Infrastructure",
            "type": "expense"
        })
    
    return transactions


@pytest.fixture
def sample_company_data():
    """Create sample company data for testing."""
    return {
        "id": 1,
        "name": "Test Startup Inc",
        "industry": "Technology",
        "initial_capital": 200000.0,
        "founded_date": "2023-01-01"
    }


class TestFinancialAnalystAgent:
    """Tests for FinancialAnalystAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = FinancialAnalystAgent(company_id=1)
        
        assert agent.company_id == 1
        assert agent.agent_type == AgentType.FINANCIAL_ANALYST
        assert agent.session_id is not None
    
    def test_get_system_prompt(self):
        """Test system prompt retrieval."""
        agent = FinancialAnalystAgent(company_id=1)
        prompt = agent.get_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Financial Analyst" in prompt
    
    def test_get_tools(self):
        """Test tools retrieval."""
        agent = FinancialAnalystAgent(company_id=1)
        tools = agent.get_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Check tool structure
        tool = tools[0]
        assert "name" in tool
        assert "description" in tool
    
    @pytest.mark.asyncio
    async def test_process_tool_call_category_analysis(self, sample_transactions):
        """Test processing category analysis tool call."""
        agent = FinancialAnalystAgent(company_id=1)
        
        result = await agent.process_tool_call(
            "analyze_spending_by_category",
            {
                "transactions": sample_transactions,
                "period_months": 3
            }
        )
        
        assert "categories" in result
        assert "total_expenses" in result
    
    @pytest.mark.asyncio
    async def test_process_tool_call_balance(self, sample_transactions):
        """Test processing balance calculation tool call."""
        agent = FinancialAnalystAgent(company_id=1)
        
        result = await agent.process_tool_call(
            "calculate_balance",
            {
                "transactions": sample_transactions,
                "initial_capital": 200000.0
            }
        )
        
        assert "current_balance" in result
        assert "total_income" in result
        assert "total_expenses" in result
    
    @pytest.mark.asyncio
    @patch("app.agents.base_agent.BaseAgent.execute")
    async def test_analyze(self, mock_execute, sample_transactions, sample_company_data):
        """Test full analysis workflow."""
        # Mock the LLM response
        mock_execute.return_value = {
            "response": "Analysis complete",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        agent = FinancialAnalystAgent(company_id=1)
        result = await agent.analyze(sample_transactions, sample_company_data)
        
        assert "agent_type" in result
        assert result["agent_type"] == "financial_analyst"
        assert "analysis" in result
        assert "insights" in result
        assert "status" in result
        
        # Check analysis components
        analysis = result["analysis"]
        assert "category_breakdown" in analysis
        assert "balance" in analysis
        assert "growth_rates" in analysis
        assert "charts" in analysis


class TestRunwayPredictorAgent:
    """Tests for RunwayPredictorAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = RunwayPredictorAgent(company_id=1)
        
        assert agent.company_id == 1
        assert agent.agent_type == AgentType.RUNWAY_PREDICTOR
        assert agent.session_id is not None
    
    def test_get_system_prompt(self):
        """Test system prompt retrieval."""
        agent = RunwayPredictorAgent(company_id=1)
        prompt = agent.get_system_prompt()
        
        assert isinstance(prompt, str)
        assert "Runway Predictor" in prompt
        assert "burn rate" in prompt.lower()
    
    def test_get_tools(self):
        """Test tools retrieval."""
        agent = RunwayPredictorAgent(company_id=1)
        tools = agent.get_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Check for specific tools
        tool_names = [tool["name"] for tool in tools]
        assert "calculate_burn_rate" in tool_names
        assert "calculate_runway" in tool_names
    
    @pytest.mark.asyncio
    async def test_process_tool_call_burn_rate(self, sample_transactions):
        """Test processing burn rate calculation."""
        agent = RunwayPredictorAgent(company_id=1)
        
        result = await agent.process_tool_call(
            "calculate_burn_rate",
            {
                "transactions": sample_transactions,
                "period_months": 3
            }
        )
        
        assert "burn_rate" in result
        assert "avg_monthly_income" in result
        assert "avg_monthly_expenses" in result
    
    @pytest.mark.asyncio
    async def test_process_tool_call_runway(self):
        """Test processing runway calculation."""
        agent = RunwayPredictorAgent(company_id=1)
        
        result = await agent.process_tool_call(
            "calculate_runway",
            {
                "current_balance": 100000.0,
                "monthly_burn_rate": 10000.0
            }
        )
        
        assert "runway_months" in result
        assert "status" in result
        assert result["runway_months"] == 10.0
    
    @pytest.mark.asyncio
    @patch("app.agents.base_agent.BaseAgent.execute")
    async def test_predict_runway(self, mock_execute, sample_transactions, sample_company_data):
        """Test full runway prediction workflow."""
        # Mock the LLM response
        mock_execute.return_value = {
            "response": "Runway prediction complete",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        agent = RunwayPredictorAgent(company_id=1)
        result = await agent.predict_runway(sample_transactions, sample_company_data)
        
        assert "agent_type" in result
        assert result["agent_type"] == "runway_predictor"
        assert "analysis" in result
        assert "insights" in result
        
        # Check analysis components
        analysis = result["analysis"]
        assert "runway" in analysis
        assert "burn_rate" in analysis
        assert "health_score" in analysis
        assert "charts" in analysis


class TestInvestmentAdvisorAgent:
    """Tests for InvestmentAdvisorAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = InvestmentAdvisorAgent(company_id=1)
        
        assert agent.company_id == 1
        assert agent.agent_type == AgentType.INVESTMENT_ADVISOR
        assert agent.session_id is not None
    
    def test_get_system_prompt(self):
        """Test system prompt retrieval."""
        agent = InvestmentAdvisorAgent(company_id=1)
        prompt = agent.get_system_prompt()
        
        assert isinstance(prompt, str)
        assert "Investment Advisor" in prompt
        assert "investment" in prompt.lower()
    
    def test_get_tools(self):
        """Test tools retrieval."""
        agent = InvestmentAdvisorAgent(company_id=1)
        tools = agent.get_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Check for specific tools
        tool_names = [tool["name"] for tool in tools]
        assert "assess_financial_readiness" in tool_names
        assert "search_investment_options" in tool_names
    
    @pytest.mark.asyncio
    async def test_process_tool_call_readiness(self):
        """Test processing financial readiness assessment."""
        agent = InvestmentAdvisorAgent(company_id=1)
        
        result = await agent.process_tool_call(
            "assess_financial_readiness",
            {
                "current_balance": 100000.0,
                "monthly_burn_rate": 10000.0
            }
        )
        
        assert "readiness" in result
        assert "reason" in result
        assert "runway_months" in result
    
    @pytest.mark.asyncio
    async def test_process_tool_call_investment_capacity(self):
        """Test processing investment capacity calculation."""
        agent = InvestmentAdvisorAgent(company_id=1)
        
        result = await agent.process_tool_call(
            "calculate_investment_capacity",
            {
                "current_balance": 200000.0,
                "monthly_expenses": 30000.0,
                "emergency_fund_months": 6
            }
        )
        
        assert "investable_amount" in result
        assert "emergency_fund_required" in result
        assert "recommended_allocation" in result
    
    @pytest.mark.asyncio
    @patch("app.agents.base_agent.BaseAgent.execute")
    async def test_advise_positive_balance(self, mock_execute, sample_transactions, sample_company_data):
        """Test investment advice for company with positive balance."""
        # Mock the LLM response
        mock_execute.return_value = {
            "response": "Investment advice complete",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        agent = InvestmentAdvisorAgent(company_id=1)
        result = await agent.advise(sample_transactions, sample_company_data)
        
        assert "agent_type" in result
        assert result["agent_type"] == "investment_advisor"
        assert "analysis" in result
        assert "insights" in result
        
        # Check analysis components
        analysis = result["analysis"]
        assert "readiness" in analysis
        assert "capacity" in analysis
    
    def test_infer_company_stage(self):
        """Test company stage inference."""
        agent = InvestmentAdvisorAgent(company_id=1)
        
        # Test seed stage
        data1 = {"initial_capital": 50000.0}
        stage1 = agent._infer_company_stage(data1, [])
        assert stage1 == "seed"
        
        # Test early stage
        data2 = {"initial_capital": 500000.0}
        stage2 = agent._infer_company_stage(data2, [])
        assert stage2 == "early"
        
        # Test growth stage
        data3 = {"initial_capital": 5000000.0}
        stage3 = agent._infer_company_stage(data3, [])
        assert stage3 == "growth"
    
    def test_determine_risk_tolerance(self):
        """Test risk tolerance determination."""
        agent = InvestmentAdvisorAgent(company_id=1)
        
        # Conservative: low runway
        risk1 = agent._determine_risk_tolerance(3.0, 10000.0, 30000.0)
        assert risk1 == "conservative"
        
        # Moderate: healthy runway
        risk2 = agent._determine_risk_tolerance(12.0, 10000.0, 200000.0)
        assert risk2 == "moderate"


class TestAgentOrchestrator:
    """Tests for AgentOrchestrator."""
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = AgentOrchestrator(company_id=1)
        
        assert orchestrator.company_id == 1
        assert orchestrator.session_id is not None
    
    @pytest.mark.asyncio
    @patch("app.agents.financial_analyst_agent.FinancialAnalystAgent.analyze")
    @patch("app.agents.runway_predictor_agent.RunwayPredictorAgent.predict_runway")
    @patch("app.agents.investment_advisor_agent.InvestmentAdvisorAgent.advise")
    async def test_run_sequential_workflow(
        self,
        mock_investment,
        mock_runway,
        mock_analyst,
        sample_transactions,
        sample_company_data
    ):
        """Test sequential workflow execution."""
        # Mock agent responses
        mock_analyst.return_value = {
            "agent_type": "financial_analyst",
            "status": "completed",
            "analysis": {}
        }
        mock_runway.return_value = {
            "agent_type": "runway_predictor",
            "status": "completed",
            "analysis": {}
        }
        mock_investment.return_value = {
            "agent_type": "investment_advisor",
            "status": "completed",
            "analysis": {}
        }
        
        orchestrator = AgentOrchestrator(company_id=1)
        result = await orchestrator.run_full_analysis(
            sample_transactions,
            sample_company_data,
            WorkflowType.SEQUENTIAL
        )
        
        assert "agents" in result
        assert "financial_analyst" in result["agents"]
        assert "runway_predictor" in result["agents"]
        assert "investment_advisor" in result["agents"]
        assert "summary" in result
    
    @pytest.mark.asyncio
    @patch("app.agents.financial_analyst_agent.FinancialAnalystAgent.analyze")
    @patch("app.agents.runway_predictor_agent.RunwayPredictorAgent.predict_runway")
    @patch("app.agents.investment_advisor_agent.InvestmentAdvisorAgent.advise")
    async def test_run_parallel_workflow(
        self,
        mock_investment,
        mock_runway,
        mock_analyst,
        sample_transactions,
        sample_company_data
    ):
        """Test parallel workflow execution."""
        # Mock agent responses
        mock_analyst.return_value = {
            "agent_type": "financial_analyst",
            "status": "completed",
            "analysis": {}
        }
        mock_runway.return_value = {
            "agent_type": "runway_predictor",
            "status": "completed",
            "analysis": {}
        }
        mock_investment.return_value = {
            "agent_type": "investment_advisor",
            "status": "completed",
            "analysis": {}
        }
        
        orchestrator = AgentOrchestrator(company_id=1)
        result = await orchestrator.run_full_analysis(
            sample_transactions,
            sample_company_data,
            WorkflowType.PARALLEL
        )
        
        assert "agents" in result
        assert len(result["agents"]) == 3
    
    @pytest.mark.asyncio
    @patch("app.agents.financial_analyst_agent.FinancialAnalystAgent.analyze")
    async def test_run_single_agent(
        self,
        mock_analyst,
        sample_transactions,
        sample_company_data
    ):
        """Test single agent execution."""
        mock_analyst.return_value = {
            "agent_type": "financial_analyst",
            "status": "completed"
        }
        
        orchestrator = AgentOrchestrator(company_id=1)
        result = await orchestrator.run_single_agent(
            "analyst",
            sample_transactions,
            sample_company_data
        )
        
        assert result["agent_type"] == "financial_analyst"
        assert result["status"] == "completed"
    
    def test_aggregate_results(self):
        """Test result aggregation."""
        orchestrator = AgentOrchestrator(company_id=1)
        
        results = {
            "financial_analyst": {
                "status": "completed",
                "insights": "Analysis complete",
                "analysis": {}
            },
            "runway_predictor": {
                "status": "completed",
                "insights": "Runway predicted",
                "analysis": {
                    "runway": {"runway_months": 12, "status": "healthy"}
                }
            }
        }
        
        aggregated = orchestrator._aggregate_results(results)
        
        assert "company_id" in aggregated
        assert "agents" in aggregated
        assert "summary" in aggregated
        assert len(aggregated["agents"]) == 2
    
    def test_generate_summary(self):
        """Test summary generation."""
        orchestrator = AgentOrchestrator(company_id=1)
        
        results = {
            "financial_analyst": {
                "status": "completed",
                "analysis": {
                    "balance": {"current_balance": 100000}
                }
            },
            "runway_predictor": {
                "status": "completed",
                "analysis": {
                    "runway": {"runway_months": 12, "status": "healthy"}
                }
            }
        }
        
        summary = orchestrator._generate_summary(results)
        
        assert "agents_completed" in summary
        assert "overall_status" in summary
        assert summary["agents_completed"] == 2
        assert summary["overall_status"] == "success"
        assert "runway_months" in summary
        assert "current_balance" in summary

