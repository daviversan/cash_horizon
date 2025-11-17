"""Financial Analyst Agent for spending analysis and insights."""

import logging
from typing import Any, Dict, List, Optional

from app.agents.base_agent import BaseAgent
from app.models.agent_session import AgentType
from app.tools.financial_calculator import financial_calculator
from app.tools.data_processor import data_processor
from app.tools.chart_generator import chart_generator

logger = logging.getLogger(__name__)


class FinancialAnalystAgent(BaseAgent):
    """
    Financial Analyst Agent - Analyzes spending patterns and generates insights.
    
    Capabilities:
    - Analyze spending by category
    - Identify trends and anomalies
    - Generate financial summaries
    - Provide natural language insights
    - Create visualization data
    
    Tools:
    - financial_calculator: Compute financial metrics
    - data_processor: Parse and validate transaction data
    - chart_generator: Create chart data for visualizations
    """
    
    def __init__(self, company_id: int, session_id: Optional[str] = None):
        """
        Initialize Financial Analyst Agent.
        
        Args:
            company_id: ID of the company to analyze
            session_id: Optional session ID for continuity
        """
        super().__init__(
            agent_type=AgentType.FINANCIAL_ANALYST,
            company_id=company_id,
            session_id=session_id
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Financial Analyst Agent."""
        return """You are a Financial Analyst Agent for Cash Horizon, a startup financial health tracking platform.

Your role is to analyze company spending patterns and provide actionable insights.

CAPABILITIES:
- Analyze transactions by category and time period
- Identify spending trends and anomalies
- Calculate key financial metrics (total spend, category breakdown, growth rates)
- Generate clear, actionable recommendations
- Create data for financial visualizations

TONE AND STYLE:
- Professional but accessible
- Data-driven with clear explanations
- Focus on actionable insights
- Highlight both concerns and opportunities
- Use specific numbers and percentages

ANALYSIS FRAMEWORK:
1. Overall Financial Summary
   - Total income vs expenses
   - Net position
   - Transaction volume

2. Category Breakdown
   - Top spending categories
   - Category percentages
   - Notable patterns

3. Trends and Insights
   - Month-over-month changes
   - Growth rates
   - Seasonal patterns
   - Anomalies or concerns

4. Recommendations
   - Cost optimization opportunities
   - Areas for monitoring
   - Action items

OUTPUT FORMAT:
Provide a structured analysis with:
- Executive Summary (2-3 sentences)
- Key Metrics (bullet points)
- Category Analysis
- Insights and Trends
- Recommendations

Always base your analysis on the actual transaction data provided. Be specific with numbers and percentages."""
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get available tools for Financial Analyst Agent.
        
        Returns:
            List of tool definitions (Google ADK format)
        """
        # For now, tools are called directly in process_tool_call
        # In production with full Google ADK integration, these would be
        # properly formatted tool definitions
        return [
            {
                "name": "analyze_spending_by_category",
                "description": "Analyze spending breakdown by category",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "period_months": {
                            "type": "integer",
                            "description": "Number of months to analyze (default: all time)"
                        }
                    }
                }
            },
            {
                "name": "calculate_balance",
                "description": "Calculate current balance and financial position",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "calculate_growth_rate",
                "description": "Calculate growth rate for income or expenses",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "metric": {
                            "type": "string",
                            "enum": ["income", "expenses"],
                            "description": "Metric to analyze"
                        },
                        "period_months": {
                            "type": "integer",
                            "description": "Number of months to analyze"
                        }
                    }
                }
            },
            {
                "name": "generate_category_charts",
                "description": "Generate chart data for category breakdown",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transaction_type": {
                            "type": "string",
                            "enum": ["income", "expense"],
                            "description": "Type of transactions to visualize"
                        }
                    }
                }
            }
        ]
    
    async def process_tool_call(
        self,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool call.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            
        Returns:
            Tool execution results
        """
        logger.info(
            f"Executing tool: {tool_name}",
            extra={"tool": tool_name, "args": tool_args}
        )
        
        # Tools expect transactions to be in context
        transactions = tool_args.get("transactions", [])
        initial_capital = tool_args.get("initial_capital", 0.0)
        
        if tool_name == "analyze_spending_by_category":
            period_months = tool_args.get("period_months")
            return financial_calculator.analyze_spending_by_category(
                transactions,
                period_months
            )
        
        elif tool_name == "calculate_balance":
            return financial_calculator.calculate_balance(
                initial_capital,
                transactions
            )
        
        elif tool_name == "calculate_growth_rate":
            metric = tool_args.get("metric", "income")
            period_months = tool_args.get("period_months", 6)
            return financial_calculator.calculate_growth_rate(
                transactions,
                metric,
                period_months
            )
        
        elif tool_name == "generate_category_charts":
            transaction_type = tool_args.get("transaction_type", "expense")
            return chart_generator.generate_category_breakdown_chart(
                transactions,
                transaction_type,
                top_n=10
            )
        
        else:
            return {
                "error": f"Unknown tool: {tool_name}"
            }
    
    async def analyze(
        self,
        transactions: List[Dict[str, Any]],
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive financial analysis.
        
        This is a convenience method that orchestrates the full analysis workflow.
        
        Args:
            transactions: List of transaction dictionaries
            company_data: Company information including initial_capital
            
        Returns:
            Complete analysis results
        """
        try:
            logger.info(
                f"Starting financial analysis",
                extra={
                    "company_id": self.company_id,
                    "transaction_count": len(transactions)
                }
            )
            
            # Calculate key metrics using tools
            initial_capital = company_data.get("initial_capital", 0.0)
            
            # 1. Category analysis
            category_analysis = financial_calculator.analyze_spending_by_category(
                transactions,
                period_months=None  # All time
            )
            
            # 2. Balance calculation
            balance_info = financial_calculator.calculate_balance(
                initial_capital,
                transactions
            )
            
            # 3. Growth rates
            income_growth = financial_calculator.calculate_growth_rate(
                transactions,
                metric="income",
                period_months=6
            )
            
            expense_growth = financial_calculator.calculate_growth_rate(
                transactions,
                metric="expense",
                period_months=6
            )
            
            # 4. Generate chart data
            expense_chart = chart_generator.generate_category_breakdown_chart(
                transactions,
                "expense",
                top_n=10
            )
            
            income_chart = chart_generator.generate_category_breakdown_chart(
                transactions,
                "income",
                top_n=10
            )
            
            # 5. Build context for LLM
            context = {
                "company_name": company_data.get("name", "Your Company"),
                "initial_capital": initial_capital,
                "transaction_count": len(transactions),
                "category_analysis": category_analysis,
                "balance_info": balance_info,
                "income_growth": income_growth,
                "expense_growth": expense_growth
            }
            
            # 6. Generate insights using LLM
            user_message = f"""Analyze the financial health of {context['company_name']} based on the following data:

FINANCIAL POSITION:
- Initial Capital: ${initial_capital:,.2f}
- Current Balance: ${balance_info['current_balance']:,.2f}
- Total Income: ${balance_info['total_income']:,.2f}
- Total Expenses: ${balance_info['total_expenses']:,.2f}
- Net Change: ${balance_info['net_change']:,.2f}

SPENDING BY CATEGORY:
{self._format_category_data(category_analysis)}

GROWTH TRENDS:
- Income Growth (6mo): {income_growth.get('growth_rate', 0)}%
- Expense Growth (6mo): {expense_growth.get('growth_rate', 0)}%

Provide a comprehensive analysis with:
1. Executive Summary
2. Key Financial Metrics
3. Category Breakdown Insights
4. Trend Analysis
5. Recommendations for improvement"""
            
            # Call the base execute method to get LLM insights
            llm_response = await self.execute(user_message, context)
            
            # 7. Combine all results
            result = {
                "agent_type": "financial_analyst",
                "company_id": self.company_id,
                "session_id": self.session_id,
                "analysis": {
                    "category_breakdown": category_analysis,
                    "balance": balance_info,
                    "growth_rates": {
                        "income": income_growth,
                        "expenses": expense_growth
                    },
                    "charts": {
                        "expense_breakdown": expense_chart,
                        "income_breakdown": income_chart
                    }
                },
                "insights": llm_response.get("response", ""),
                "status": "completed",
                "timestamp": llm_response.get("timestamp")
            }
            
            logger.info(
                f"Completed financial analysis",
                extra={"company_id": self.company_id}
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error in financial analysis",
                extra={"company_id": self.company_id, "error": str(e)},
                exc_info=True
            )
            raise
    
    def _format_category_data(self, category_analysis: Dict[str, Any]) -> str:
        """Format category data for LLM prompt."""
        if "error" in category_analysis:
            return "No category data available"
        
        categories = category_analysis.get("categories", [])
        if not categories:
            return "No spending data available"
        
        lines = []
        for cat in categories[:10]:  # Top 10
            lines.append(
                f"  - {cat['category']}: ${cat['total']:,.2f} ({cat['percentage']:.1f}%) - {cat['count']} transactions"
            )
        
        return "\n".join(lines)

