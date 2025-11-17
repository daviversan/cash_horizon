"""Unit tests for custom tools."""

import pytest
from datetime import datetime, timedelta
from app.tools.financial_calculator import financial_calculator
from app.tools.data_processor import data_processor
from app.tools.chart_generator import chart_generator


class TestFinancialCalculator:
    """Tests for FinancialCalculator."""
    
    @pytest.fixture
    def sample_transactions(self):
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
    
    def test_calculate_burn_rate(self, sample_transactions):
        """Test burn rate calculation."""
        result = financial_calculator.calculate_burn_rate(
            sample_transactions,
            period_months=3
        )
        
        assert "burn_rate" in result
        assert "avg_monthly_income" in result
        assert "avg_monthly_expenses" in result
        assert result["avg_monthly_income"] == 50000.0
        assert result["avg_monthly_expenses"] == 45000.0
        # Burn rate = expenses - income = -5000 (net positive)
        assert result["burn_rate"] == -5000.0
    
    def test_calculate_runway_positive_burn(self):
        """Test runway calculation with positive burn rate."""
        result = financial_calculator.calculate_runway(
            current_balance=100000.0,
            monthly_burn_rate=10000.0
        )
        
        assert result["runway_months"] == 10.0
        assert result["runway_days"] == 300.0
        assert result["status"] == "healthy"
    
    def test_calculate_runway_critical(self):
        """Test runway calculation with critical status."""
        result = financial_calculator.calculate_runway(
            current_balance=20000.0,
            monthly_burn_rate=10000.0
        )
        
        assert result["runway_months"] == 2.0
        assert result["status"] == "critical"
    
    def test_calculate_runway_negative_burn(self):
        """Test runway calculation with negative burn (profit)."""
        result = financial_calculator.calculate_runway(
            current_balance=100000.0,
            monthly_burn_rate=-5000.0  # Negative = making money
        )
        
        assert result["runway_months"] == float('inf')
        assert result["status"] == "positive_cash_flow"
    
    def test_analyze_spending_by_category(self, sample_transactions):
        """Test spending analysis by category."""
        result = financial_calculator.analyze_spending_by_category(
            sample_transactions,
            period_months=None
        )
        
        assert "categories" in result
        assert "total_expenses" in result
        assert "total_income" in result
        
        categories = result["categories"]
        assert len(categories) == 3  # Salaries, Marketing, Infrastructure
        
        # Check Salaries is the top category
        assert categories[0]["category"] == "Salaries"
        assert categories[0]["total"] == 90000.0  # 30k * 3 months
    
    def test_calculate_balance(self, sample_transactions):
        """Test balance calculation."""
        result = financial_calculator.calculate_balance(
            initial_capital=100000.0,
            transactions=sample_transactions
        )
        
        assert "current_balance" in result
        assert "initial_capital" in result
        assert "total_income" in result
        assert "total_expenses" in result
        
        # 100k initial + 150k income - 135k expenses = 115k
        assert result["current_balance"] == 115000.0
        assert result["balance_status"] == "positive"
    
    def test_calculate_growth_rate(self, sample_transactions):
        """Test growth rate calculation."""
        result = financial_calculator.calculate_growth_rate(
            sample_transactions,
            metric="income",
            period_months=6
        )
        
        assert "growth_rate" in result
        assert "metric" in result
        assert result["metric"] == "income"
    
    def test_calculate_financial_health_score(self):
        """Test financial health score calculation."""
        result = financial_calculator.calculate_financial_health_score(
            current_balance=120000.0,
            monthly_burn_rate=10000.0,
            revenue_growth_rate=15.0,
            expense_growth_rate=5.0
        )
        
        assert "health_score" in result
        assert "rating" in result
        assert "factors" in result
        assert "recommendations" in result
        
        # Score should be good with 12 months runway and positive growth
        assert result["health_score"] >= 60
        assert result["rating"] in ["Good", "Excellent"]


class TestDataProcessor:
    """Tests for DataProcessor."""
    
    def test_parse_csv_valid(self):
        """Test parsing valid CSV data."""
        csv_content = """date,amount,category,type,description
2024-01-15,1500.00,Salaries,expense,Employee payroll
2024-01-20,5000.00,Revenue,income,Customer payment"""
        
        result = data_processor.parse_csv(csv_content, company_id=1)
        
        assert result["success"] is True
        assert result["valid_rows"] == 2
        assert result["invalid_rows"] == 0
        assert len(result["transactions"]) == 2
    
    def test_parse_csv_missing_columns(self):
        """Test parsing CSV with missing required columns."""
        csv_content = """date,amount
2024-01-15,1500.00"""
        
        result = data_processor.parse_csv(csv_content, company_id=1)
        
        assert result["success"] is False
        assert "Missing required columns" in result["error"]
    
    def test_parse_csv_invalid_date(self):
        """Test parsing CSV with invalid date."""
        csv_content = """date,amount,category,type,description
invalid-date,1500.00,Salaries,expense,Test"""
        
        result = data_processor.parse_csv(csv_content, company_id=1)
        
        assert result["success"] is False
        assert result["invalid_rows"] == 1
    
    def test_parse_date_formats(self):
        """Test parsing different date formats."""
        # YYYY-MM-DD format
        result1 = data_processor.parse_date("2024-01-15")
        assert result1["valid"] is True
        
        # MM/DD/YYYY format
        result2 = data_processor.parse_date("01/15/2024")
        assert result2["valid"] is True
        
        # Invalid format
        result3 = data_processor.parse_date("invalid")
        assert result3["valid"] is False
    
    def test_validate_amount(self):
        """Test amount validation."""
        # Valid amount
        result1 = data_processor.validate_amount("1500.00")
        assert result1["valid"] is True
        assert result1["amount"] == 1500.0
        
        # Amount with currency symbol
        result2 = data_processor.validate_amount("$1,500.00")
        assert result2["valid"] is True
        assert result2["amount"] == 1500.0
        
        # Negative amount
        result3 = data_processor.validate_amount("-100")
        assert result3["valid"] is False
        
        # Invalid amount
        result4 = data_processor.validate_amount("invalid")
        assert result4["valid"] is False
    
    def test_clean_transactions(self):
        """Test transaction cleaning."""
        transactions = [
            {
                "company_id": 1,
                "date": "2024-01-15",
                "amount": 1500.555,
                "category": "  salaries  ",
                "type": "EXPENSE",
                "description": "  test  "
            }
        ]
        
        cleaned = data_processor.clean_transactions(transactions)
        
        assert len(cleaned) == 1
        assert cleaned[0]["amount"] == 1500.56  # Rounded
        assert cleaned[0]["category"] == "Salaries"  # Title case, trimmed
        assert cleaned[0]["type"] == "expense"  # Lowercase
        assert cleaned[0]["description"] == "test"  # Trimmed
    
    def test_validate_batch(self):
        """Test batch validation."""
        transactions = [
            {
                "company_id": 1,
                "date": "2024-01-15",
                "amount": 1500.0,
                "category": "Salaries",
                "type": "expense"
            },
            {
                "company_id": 1,
                "date": "2024-01-20",
                "amount": 5000.0,
                "category": "Revenue",
                "type": "income"
            }
        ]
        
        result = data_processor.validate_batch(transactions)
        
        assert result["valid"] is True
        assert result["transaction_count"] == 2
        assert len(result["issues"]) == 0
    
    def test_generate_summary_statistics(self):
        """Test summary statistics generation."""
        transactions = [
            {
                "date": "2024-01-15",
                "amount": 1000.0,
                "category": "Salaries",
                "type": "expense"
            },
            {
                "date": "2024-01-20",
                "amount": 5000.0,
                "category": "Revenue",
                "type": "income"
            }
        ]
        
        result = data_processor.generate_summary_statistics(transactions)
        
        assert result["count"] == 2
        assert result["total_income"] == 5000.0
        assert result["total_expenses"] == 1000.0
        assert result["net"] == 4000.0


class TestChartGenerator:
    """Tests for ChartGenerator."""
    
    @pytest.fixture
    def sample_transactions(self):
        """Create sample transactions for testing."""
        base_date = datetime.utcnow()
        transactions = []
        
        for month in range(6):
            month_date = (base_date - timedelta(days=30 * month)).isoformat()
            
            transactions.append({
                "date": month_date,
                "amount": 50000.0,
                "category": "Revenue",
                "type": "income"
            })
            
            transactions.append({
                "date": month_date,
                "amount": 30000.0,
                "category": "Salaries",
                "type": "expense"
            })
        
        return transactions
    
    def test_generate_burn_rate_chart(self, sample_transactions):
        """Test burn rate chart generation."""
        result = chart_generator.generate_burn_rate_chart(
            sample_transactions,
            months=6
        )
        
        assert result["type"] == "burn_rate_chart"
        assert "data" in result
        assert len(result["data"]) > 0
        
        # Check data structure
        data_point = result["data"][0]
        assert "month" in data_point
        assert "income" in data_point
        assert "expenses" in data_point
        assert "burn_rate" in data_point
    
    def test_generate_category_breakdown_chart(self, sample_transactions):
        """Test category breakdown chart generation."""
        result = chart_generator.generate_category_breakdown_chart(
            sample_transactions,
            transaction_type="expense",
            top_n=10
        )
        
        assert result["type"] == "category_breakdown_chart"
        assert result["transaction_type"] == "expense"
        assert "data" in result
        assert len(result["data"]) > 0
        
        # Check data structure
        data_point = result["data"][0]
        assert "category" in data_point
        assert "amount" in data_point
        assert "percentage" in data_point
    
    def test_generate_runway_forecast_chart(self):
        """Test runway forecast chart generation."""
        result = chart_generator.generate_runway_forecast_chart(
            current_balance=100000.0,
            monthly_burn_rate=10000.0,
            forecast_months=12
        )
        
        assert result["type"] == "runway_forecast_chart"
        assert "data" in result
        assert len(result["data"]) == 13  # 12 forecast + current month
        
        # Check data structure
        data_point = result["data"][0]
        assert "month" in data_point
        assert "balance" in data_point
        assert "is_projected" in data_point
    
    def test_generate_balance_history_chart(self, sample_transactions):
        """Test balance history chart generation."""
        result = chart_generator.generate_balance_history_chart(
            initial_capital=100000.0,
            transactions=sample_transactions,
            months=6
        )
        
        assert result["type"] == "balance_history_chart"
        assert "data" in result
        assert result["initial_capital"] == 100000.0
        
        # Check data structure
        if len(result["data"]) > 0:
            data_point = result["data"][0]
            assert "month" in data_point
            assert "balance" in data_point
    
    def test_generate_trend_chart(self, sample_transactions):
        """Test trend chart generation."""
        result = chart_generator.generate_trend_chart(
            sample_transactions,
            metric="income",
            months=6
        )
        
        assert result["type"] == "trend_chart"
        assert result["metric"] == "income"
        assert "data" in result
        assert "overall_growth_rate" in result
    
    def test_generate_combined_dashboard_data(self, sample_transactions):
        """Test combined dashboard data generation."""
        result = chart_generator.generate_combined_dashboard_data(
            initial_capital=100000.0,
            transactions=sample_transactions,
            months=6
        )
        
        # Check all chart types are present
        assert "burn_rate_chart" in result
        assert "expense_breakdown" in result
        assert "income_breakdown" in result
        assert "balance_history" in result
        assert "income_trend" in result
        assert "expense_trend" in result


@pytest.mark.asyncio
class TestWebSearch:
    """Tests for WebSearch."""
    
    async def test_search_investment_options(self):
        """Test investment options search."""
        from app.tools.web_search import web_search
        
        result = await web_search.search_investment_options(
            company_stage="early",
            risk_tolerance="moderate"
        )
        
        assert "options" in result
        assert len(result["options"]) > 0
        
        # Check option structure
        option = result["options"][0]
        assert "name" in option
        assert "type" in option
        assert "risk_level" in option
        assert "expected_return" in option
    
    async def test_search_market_trends(self):
        """Test market trends search."""
        from app.tools.web_search import web_search
        
        result = await web_search.search_market_trends(
            industry="technology",
            region="global"
        )
        
        assert "trends" in result
        assert len(result["trends"]) > 0
    
    async def test_search_financial_advice(self):
        """Test financial advice search."""
        from app.tools.web_search import web_search
        
        result = await web_search.search_financial_advice(
            topic="runway extension",
            context="early stage startup"
        )
        
        assert "advice" in result
        assert len(result["advice"]) > 0

