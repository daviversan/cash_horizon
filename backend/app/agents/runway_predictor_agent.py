"""Runway Predictor Agent for burn rate calculation and runway forecasting."""

import logging
from typing import Any, Dict, List, Optional

from app.agents.base_agent import BaseAgent
from app.models.agent_session import AgentType
from app.tools.financial_calculator import financial_calculator
from app.tools.chart_generator import chart_generator

logger = logging.getLogger(__name__)


class RunwayPredictorAgent(BaseAgent):
    """
    Runway Predictor Agent - Calculates burn rate and predicts runway.
    
    Capabilities:
    - Calculate monthly burn rate
    - Predict runway (months until cash depletion)
    - Generate forecast projections
    - Assess financial health status
    - Provide runway extension strategies
    - Create time-series visualizations
    
    Tools:
    - financial_calculator: Burn rate and runway calculations
    - chart_generator: Runway forecast and burn rate charts
    """
    
    def __init__(self, company_id: int, session_id: Optional[str] = None):
        """
        Initialize Runway Predictor Agent.
        
        Args:
            company_id: ID of the company to analyze
            session_id: Optional session ID for continuity
        """
        super().__init__(
            agent_type=AgentType.RUNWAY_PREDICTOR,
            company_id=company_id,
            session_id=session_id
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Runway Predictor Agent."""
        return """You are a Runway Predictor Agent for Cash Horizon, a startup financial health tracking platform.

Your role is to calculate burn rate, predict runway, and help startups extend their runway.

CAPABILITIES:
- Calculate monthly burn rate (expenses - income)
- Predict runway in months
- Assess runway health status (critical/warning/healthy/excellent)
- Generate forecast projections
- Recommend runway extension strategies

RUNWAY HEALTH CRITERIA:
- CRITICAL: < 3 months (immediate action required)
- WARNING: 3-6 months (start planning now)
- HEALTHY: 6-12 months (monitor closely)
- EXCELLENT: > 12 months (optimal position)

BURN RATE ANALYSIS:
- Calculate average monthly expenses
- Calculate average monthly income
- Compute net burn rate
- Identify trends (increasing/decreasing burn)
- Compare to industry benchmarks

TONE AND STYLE:
- Clear and direct about runway status
- Urgent when runway is critical
- Supportive with actionable recommendations
- Data-driven with specific numbers
- Balance realism with encouragement

RECOMMENDATIONS FRAMEWORK:
For startups with limited runway:
1. Immediate cost reduction opportunities
2. Revenue acceleration strategies
3. Fundraising timeline guidance
4. Operational efficiency improvements

For startups with healthy runway:
1. Maintain current trajectory
2. Strategic growth investments
3. Proactive fundraising planning
4. Long-term sustainability focus

OUTPUT FORMAT:
Provide a structured runway analysis with:
- Runway Status (with urgency indicator)
- Key Metrics (burn rate, runway months, depletion date)
- Burn Rate Analysis
- Forecast Projection
- Action Items and Recommendations

Always include specific numbers, dates, and timeframes. Be clear about assumptions."""
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get available tools for Runway Predictor Agent.
        
        Returns:
            List of tool definitions
        """
        return [
            {
                "name": "calculate_burn_rate",
                "description": "Calculate monthly burn rate from transactions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "period_months": {
                            "type": "integer",
                            "description": "Number of months to analyze (default: 3)"
                        }
                    }
                }
            },
            {
                "name": "calculate_runway",
                "description": "Calculate runway months from balance and burn rate",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "current_balance": {
                            "type": "number",
                            "description": "Current cash balance"
                        },
                        "monthly_burn_rate": {
                            "type": "number",
                            "description": "Monthly burn rate"
                        }
                    },
                    "required": ["current_balance", "monthly_burn_rate"]
                }
            },
            {
                "name": "generate_runway_forecast",
                "description": "Generate runway forecast chart data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "current_balance": {
                            "type": "number",
                            "description": "Current cash balance"
                        },
                        "monthly_burn_rate": {
                            "type": "number",
                            "description": "Monthly burn rate"
                        },
                        "forecast_months": {
                            "type": "integer",
                            "description": "Number of months to forecast"
                        }
                    },
                    "required": ["current_balance", "monthly_burn_rate"]
                }
            },
            {
                "name": "generate_burn_rate_chart",
                "description": "Generate historical burn rate chart",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "months": {
                            "type": "integer",
                            "description": "Number of months to include"
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
        
        transactions = tool_args.get("transactions", [])
        
        if tool_name == "calculate_burn_rate":
            period_months = tool_args.get("period_months", 3)
            return financial_calculator.calculate_burn_rate(
                transactions,
                period_months
            )
        
        elif tool_name == "calculate_runway":
            current_balance = tool_args["current_balance"]
            monthly_burn_rate = tool_args["monthly_burn_rate"]
            return financial_calculator.calculate_runway(
                current_balance,
                monthly_burn_rate
            )
        
        elif tool_name == "generate_runway_forecast":
            current_balance = tool_args["current_balance"]
            monthly_burn_rate = tool_args["monthly_burn_rate"]
            forecast_months = tool_args.get("forecast_months", 12)
            return chart_generator.generate_runway_forecast_chart(
                current_balance,
                monthly_burn_rate,
                forecast_months
            )
        
        elif tool_name == "generate_burn_rate_chart":
            months = tool_args.get("months", 12)
            return chart_generator.generate_burn_rate_chart(
                transactions,
                months
            )
        
        else:
            return {
                "error": f"Unknown tool: {tool_name}"
            }
    
    async def predict_runway(
        self,
        transactions: List[Dict[str, Any]],
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive runway prediction and analysis.
        
        Args:
            transactions: List of transaction dictionaries
            company_data: Company information including initial_capital
            
        Returns:
            Complete runway analysis results
        """
        try:
            logger.info(
                f"Starting runway prediction",
                extra={
                    "company_id": self.company_id,
                    "transaction_count": len(transactions)
                }
            )
            
            initial_capital = company_data.get("initial_capital", 0.0)
            
            # 1. Calculate burn rate
            burn_rate_analysis = financial_calculator.calculate_burn_rate(
                transactions,
                period_months=3
            )
            
            monthly_burn_rate = burn_rate_analysis.get("burn_rate", 0.0)
            
            # 2. Calculate current balance
            balance_info = financial_calculator.calculate_balance(
                initial_capital,
                transactions
            )
            
            current_balance = balance_info.get("current_balance", 0.0)
            
            # 3. Calculate runway
            runway_info = financial_calculator.calculate_runway(
                current_balance,
                monthly_burn_rate
            )
            
            # 4. Generate forecast chart
            forecast_chart = chart_generator.generate_runway_forecast_chart(
                current_balance,
                monthly_burn_rate,
                forecast_months=12
            )
            
            # 5. Generate burn rate chart
            burn_rate_chart = chart_generator.generate_burn_rate_chart(
                transactions,
                months=12
            )
            
            # 6. Calculate financial health score
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
            
            health_score = financial_calculator.calculate_financial_health_score(
                current_balance,
                monthly_burn_rate,
                income_growth.get("growth_rate", 0.0),
                expense_growth.get("growth_rate", 0.0)
            )
            
            # 7. Build context for LLM
            context = {
                "company_name": company_data.get("name", "Your Company"),
                "current_balance": current_balance,
                "monthly_burn_rate": monthly_burn_rate,
                "runway_months": runway_info.get("runway_months", 0),
                "runway_status": runway_info.get("status", "unknown"),
                "depletion_date": runway_info.get("estimated_depletion_date"),
                "burn_rate_analysis": burn_rate_analysis,
                "health_score": health_score
            }
            
            # 8. Generate insights using LLM
            user_message = f"""Analyze the runway and burn rate for {context['company_name']} based on this data:

RUNWAY STATUS: {runway_info.get('status', 'unknown').upper()}

KEY METRICS:
- Current Balance: ${current_balance:,.2f}
- Monthly Burn Rate: ${monthly_burn_rate:,.2f}
- Runway: {runway_info.get('runway_months', 0):.1f} months
- Estimated Depletion: {runway_info.get('estimated_depletion_date', 'N/A')}

BURN RATE DETAILS:
- Avg Monthly Income: ${burn_rate_analysis.get('avg_monthly_income', 0):,.2f}
- Avg Monthly Expenses: ${burn_rate_analysis.get('avg_monthly_expenses', 0):,.2f}
- Net Monthly Burn: ${monthly_burn_rate:,.2f}
- Period Analyzed: {burn_rate_analysis.get('period_months', 0)} months

FINANCIAL HEALTH:
- Overall Score: {health_score.get('health_score', 0)}/100 ({health_score.get('rating', 'Unknown')})
- Runway Component: {health_score.get('factors', {}).get('runway_score', 0)}/40
- Revenue Growth Component: {health_score.get('factors', {}).get('revenue_growth_score', 0)}/30
- Expense Control Component: {health_score.get('factors', {}).get('expense_control_score', 0)}/30

RECOMMENDED ACTIONS:
{self._format_recommendations(health_score.get('recommendations', []))}

Provide a comprehensive runway analysis with:
1. Runway Status Assessment (with urgency level)
2. Burn Rate Analysis
3. Key Concerns and Risks
4. Detailed Action Plan
5. Timeline for Critical Actions

Be specific about dates, amounts, and action items. If runway is critical, emphasize urgency."""
            
            # Call the base execute method to get LLM insights
            llm_response = await self.execute(user_message, context)
            
            # 9. Combine all results
            result = {
                "agent_type": "runway_predictor",
                "company_id": self.company_id,
                "session_id": self.session_id,
                "analysis": {
                    "runway": runway_info,
                    "burn_rate": burn_rate_analysis,
                    "balance": {
                        "current_balance": current_balance,
                        "initial_capital": initial_capital
                    },
                    "health_score": health_score,
                    "charts": {
                        "runway_forecast": forecast_chart,
                        "burn_rate_history": burn_rate_chart
                    }
                },
                "insights": llm_response.get("response", ""),
                "status": "completed",
                "timestamp": llm_response.get("timestamp")
            }
            
            logger.info(
                f"Completed runway prediction",
                extra={
                    "company_id": self.company_id,
                    "runway_months": runway_info.get("runway_months", 0),
                    "status": runway_info.get("status", "unknown")
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error in runway prediction",
                extra={"company_id": self.company_id, "error": str(e)},
                exc_info=True
            )
            raise
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations list for prompt."""
        if not recommendations:
            return "No specific recommendations"
        
        return "\n".join(f"  - {rec}" for rec in recommendations)

