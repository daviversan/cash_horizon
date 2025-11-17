"""Investment Advisor Agent for personalized investment recommendations."""

import logging
from typing import Any, Dict, List, Optional

from app.agents.base_agent import BaseAgent
from app.models.agent_session import AgentType
from app.tools.financial_calculator import financial_calculator
from app.tools.web_search import web_search

logger = logging.getLogger(__name__)


class InvestmentAdvisorAgent(BaseAgent):
    """
    Investment Advisor Agent - Provides personalized investment recommendations.
    
    Capabilities:
    - Assess company financial readiness for investing
    - Research current investment options
    - Provide tailored recommendations based on:
      * Company stage (seed, early, growth, mature)
      * Risk tolerance
      * Financial health
      * Time horizon
    - Adaptive logic:
      * Negative balance → Focus on profitability first
      * Positive balance → Investment recommendations
    
    Tools:
    - financial_calculator: Assess financial health and capacity
    - web_search: Research investment options and market trends
    """
    
    def __init__(self, company_id: int, session_id: Optional[str] = None):
        """
        Initialize Investment Advisor Agent.
        
        Args:
            company_id: ID of the company
            session_id: Optional session ID for continuity
        """
        super().__init__(
            agent_type=AgentType.INVESTMENT_ADVISOR,
            company_id=company_id,
            session_id=session_id
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Investment Advisor Agent."""
        return """You are an Investment Advisor Agent for Cash Horizon, a startup financial health tracking platform.

Your role is to provide personalized investment recommendations for startups based on their financial health.

ADAPTIVE APPROACH:
You must first assess if the company is ready to invest:

IF NEGATIVE BALANCE or CRITICAL RUNWAY (< 3 months):
  - DO NOT recommend investments
  - Focus on achieving profitability first
  - Provide guidance on:
    * Cost reduction strategies
    * Revenue acceleration
    * Path to positive cash flow
    * Fundraising considerations

IF POSITIVE BALANCE and HEALTHY RUNWAY:
  - Assess investment readiness
  - Consider:
    * Company stage (seed/early/growth/mature)
    * Emergency fund adequacy (3-6 months expenses)
    * Risk tolerance
    * Time horizon
  - Provide tailored investment recommendations

INVESTMENT RECOMMENDATION FRAMEWORK:

1. Assess Financial Readiness
   - Current balance and runway
   - Emergency fund coverage
   - Cash flow stability
   - Growth trajectory

2. Determine Risk Profile
   - Conservative: Early stage, unstable cash flow
   - Moderate: Growing stage, stable cash flow
   - Aggressive: Mature stage, strong cash flow

3. Recommend Asset Allocation
   - Emergency Fund (always first priority)
   - Low-risk options (savings, money market, treasuries)
   - Moderate-risk options (bonds, bond funds)
   - Growth options (index funds, ETFs)

4. Investment Vehicles by Stage
   - Seed/Early: High-yield savings, money market (liquidity critical)
   - Growth: Mix of savings + conservative investments
   - Mature: Diversified portfolio with growth potential

TONE AND STYLE:
- Responsible and prudent
- Clear about risks and benefits
- Personalized to company situation
- Educational and empowering
- Conservative bias (startup preservation > returns)

IMPORTANT PRINCIPLES:
- Never compromise runway for investment returns
- Emergency fund is non-negotiable
- Liquidity is critical for startups
- Risk-appropriate recommendations only
- Diversification when appropriate

OUTPUT FORMAT:
- Investment Readiness Assessment
- Risk Profile Analysis
- Recommended Allocations
- Specific Investment Options (with details)
- Action Steps
- Warnings and Considerations

Always prioritize the company's financial stability and survival."""
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get available tools for Investment Advisor Agent.
        
        Returns:
            List of tool definitions
        """
        return [
            {
                "name": "assess_financial_readiness",
                "description": "Assess if company is ready to invest",
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
                "name": "search_investment_options",
                "description": "Research investment options for company stage and risk profile",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company_stage": {
                            "type": "string",
                            "enum": ["seed", "early", "growth", "mature"],
                            "description": "Stage of company"
                        },
                        "risk_tolerance": {
                            "type": "string",
                            "enum": ["conservative", "moderate", "aggressive"],
                            "description": "Risk tolerance level"
                        }
                    },
                    "required": ["company_stage", "risk_tolerance"]
                }
            },
            {
                "name": "calculate_investment_capacity",
                "description": "Calculate how much can be safely invested",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "current_balance": {
                            "type": "number",
                            "description": "Current cash balance"
                        },
                        "monthly_expenses": {
                            "type": "number",
                            "description": "Average monthly expenses"
                        },
                        "emergency_fund_months": {
                            "type": "integer",
                            "description": "Months of emergency fund to maintain (default: 6)"
                        }
                    },
                    "required": ["current_balance", "monthly_expenses"]
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
        
        if tool_name == "assess_financial_readiness":
            current_balance = tool_args["current_balance"]
            monthly_burn_rate = tool_args["monthly_burn_rate"]
            
            runway = financial_calculator.calculate_runway(
                current_balance,
                monthly_burn_rate
            )
            
            runway_months = runway.get("runway_months", 0)
            
            # Determine readiness
            if current_balance <= 0:
                readiness = "not_ready"
                reason = "Negative balance - focus on profitability"
            elif runway_months < 3:
                readiness = "not_ready"
                reason = "Critical runway - preserve cash"
            elif runway_months < 6:
                readiness = "cautious"
                reason = "Limited runway - minimal investment only"
            elif runway_months < 12:
                readiness = "ready"
                reason = "Healthy runway - can invest conservatively"
            else:
                readiness = "ready"
                reason = "Strong runway - can invest moderately"
            
            return {
                "readiness": readiness,
                "reason": reason,
                "runway_months": runway_months,
                "current_balance": current_balance,
                "runway_status": runway.get("status", "unknown")
            }
        
        elif tool_name == "search_investment_options":
            company_stage = tool_args["company_stage"]
            risk_tolerance = tool_args["risk_tolerance"]
            
            # Use web search tool to get investment options
            investment_options = await web_search.search_investment_options(
                company_stage,
                risk_tolerance
            )
            
            return investment_options
        
        elif tool_name == "calculate_investment_capacity":
            current_balance = tool_args["current_balance"]
            monthly_expenses = tool_args["monthly_expenses"]
            emergency_fund_months = tool_args.get("emergency_fund_months", 6)
            
            # Calculate required emergency fund
            emergency_fund_required = monthly_expenses * emergency_fund_months
            
            # Calculate investable amount
            investable_amount = max(0, current_balance - emergency_fund_required)
            
            # Determine allocation percentages
            if investable_amount == 0:
                allocation = {
                    "emergency_fund": 100,
                    "low_risk": 0,
                    "moderate_risk": 0,
                    "growth": 0
                }
            elif current_balance < emergency_fund_required * 1.5:
                # Conservative: mostly build emergency fund
                allocation = {
                    "emergency_fund": 70,
                    "low_risk": 30,
                    "moderate_risk": 0,
                    "growth": 0
                }
            elif current_balance < emergency_fund_required * 2:
                # Moderate: balanced approach
                allocation = {
                    "emergency_fund": 50,
                    "low_risk": 40,
                    "moderate_risk": 10,
                    "growth": 0
                }
            else:
                # Can take more risk
                allocation = {
                    "emergency_fund": 40,
                    "low_risk": 30,
                    "moderate_risk": 20,
                    "growth": 10
                }
            
            return {
                "current_balance": current_balance,
                "emergency_fund_required": emergency_fund_required,
                "emergency_fund_months": emergency_fund_months,
                "investable_amount": investable_amount,
                "recommended_allocation": allocation,
                "allocation_amounts": {
                    "emergency_fund": current_balance * allocation["emergency_fund"] / 100,
                    "low_risk": current_balance * allocation["low_risk"] / 100,
                    "moderate_risk": current_balance * allocation["moderate_risk"] / 100,
                    "growth": current_balance * allocation["growth"] / 100
                }
            }
        
        else:
            return {
                "error": f"Unknown tool: {tool_name}"
            }
    
    async def advise(
        self,
        transactions: List[Dict[str, Any]],
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Provide comprehensive investment advice.
        
        Args:
            transactions: List of transaction dictionaries
            company_data: Company information
            
        Returns:
            Complete investment advisory results
        """
        try:
            logger.info(
                f"Starting investment advisory",
                extra={
                    "company_id": self.company_id,
                    "transaction_count": len(transactions)
                }
            )
            
            initial_capital = company_data.get("initial_capital", 0.0)
            company_stage = self._infer_company_stage(company_data, transactions)
            
            # 1. Calculate current financial position
            balance_info = financial_calculator.calculate_balance(
                initial_capital,
                transactions
            )
            
            current_balance = balance_info.get("current_balance", 0.0)
            
            # 2. Calculate burn rate
            burn_rate_analysis = financial_calculator.calculate_burn_rate(
                transactions,
                period_months=3
            )
            
            monthly_burn_rate = burn_rate_analysis.get("burn_rate", 0.0)
            monthly_expenses = burn_rate_analysis.get("avg_monthly_expenses", 0.0)
            
            # 3. Assess financial readiness
            readiness = await self.process_tool_call(
                "assess_financial_readiness",
                {
                    "current_balance": current_balance,
                    "monthly_burn_rate": monthly_burn_rate
                }
            )
            
            # 4. Calculate investment capacity
            investment_capacity = await self.process_tool_call(
                "calculate_investment_capacity",
                {
                    "current_balance": current_balance,
                    "monthly_expenses": monthly_expenses,
                    "emergency_fund_months": 6
                }
            )
            
            # 5. If ready, search for investment options
            investment_options = None
            if readiness["readiness"] in ["ready", "cautious"]:
                risk_tolerance = self._determine_risk_tolerance(
                    readiness["runway_months"],
                    monthly_burn_rate,
                    current_balance
                )
                
                investment_options = await self.process_tool_call(
                    "search_investment_options",
                    {
                        "company_stage": company_stage,
                        "risk_tolerance": risk_tolerance
                    }
                )
            
            # 6. Build context for LLM
            context = {
                "company_name": company_data.get("name", "Your Company"),
                "company_stage": company_stage,
                "readiness": readiness,
                "current_balance": current_balance,
                "runway_months": readiness.get("runway_months", 0),
                "investment_capacity": investment_capacity,
                "investment_options": investment_options
            }
            
            # 7. Generate advice using LLM
            if readiness["readiness"] == "not_ready":
                user_message = f"""Provide guidance for {context['company_name']} which is NOT READY to invest:

FINANCIAL SITUATION:
- Current Balance: ${current_balance:,.2f}
- Runway: {readiness.get('runway_months', 0):.1f} months
- Status: {readiness.get('runway_status', 'unknown').upper()}
- Reason: {readiness['reason']}

DO NOT recommend investments. Instead, provide:
1. Assessment of why investing is not appropriate now
2. Guidance on achieving positive cash flow
3. Cost reduction strategies
4. Revenue acceleration tactics
5. Fundraising considerations
6. Path to investment readiness

Be supportive but clear that financial stability must come first."""
            
            else:
                user_message = f"""Provide investment recommendations for {context['company_name']}:

FINANCIAL POSITION:
- Current Balance: ${current_balance:,.2f}
- Runway: {readiness.get('runway_months', 0):.1f} months
- Company Stage: {company_stage}
- Investment Readiness: {readiness['readiness'].upper()}

INVESTMENT CAPACITY:
- Emergency Fund Needed: ${investment_capacity['emergency_fund_required']:,.2f} (6 months)
- Investable Amount: ${investment_capacity['investable_amount']:,.2f}

RECOMMENDED ALLOCATION:
- Emergency Fund: {investment_capacity['recommended_allocation']['emergency_fund']}% (${investment_capacity['allocation_amounts']['emergency_fund']:,.2f})
- Low Risk: {investment_capacity['recommended_allocation']['low_risk']}% (${investment_capacity['allocation_amounts']['low_risk']:,.2f})
- Moderate Risk: {investment_capacity['recommended_allocation']['moderate_risk']}% (${investment_capacity['allocation_amounts']['moderate_risk']:,.2f})
- Growth: {investment_capacity['recommended_allocation']['growth']}% (${investment_capacity['allocation_amounts']['growth']:,.2f})

AVAILABLE INVESTMENT OPTIONS:
{self._format_investment_options(investment_options)}

Provide comprehensive investment advice with:
1. Investment Readiness Assessment
2. Risk Profile and Rationale
3. Recommended Allocation Strategy
4. Specific Investment Products (from options above)
5. Implementation Steps
6. Warnings and Considerations
7. Timeline and Review Schedule

Prioritize liquidity and safety appropriate for a startup."""
            
            # Call the base execute method to get LLM insights
            llm_response = await self.execute(user_message, context)
            
            # 8. Combine all results
            result = {
                "agent_type": "investment_advisor",
                "company_id": self.company_id,
                "session_id": self.session_id,
                "analysis": {
                    "readiness": readiness,
                    "capacity": investment_capacity,
                    "balance": balance_info,
                    "burn_rate": burn_rate_analysis,
                    "company_stage": company_stage,
                    "investment_options": investment_options if investment_options else []
                },
                "insights": llm_response.get("response", ""),
                "status": "completed",
                "timestamp": llm_response.get("timestamp")
            }
            
            logger.info(
                f"Completed investment advisory",
                extra={
                    "company_id": self.company_id,
                    "readiness": readiness["readiness"]
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error in investment advisory",
                extra={"company_id": self.company_id, "error": str(e)},
                exc_info=True
            )
            raise
    
    def _infer_company_stage(
        self,
        company_data: Dict[str, Any],
        transactions: List[Dict[str, Any]]
    ) -> str:
        """Infer company stage from data."""
        # Simple heuristic based on initial capital and transaction volume
        initial_capital = company_data.get("initial_capital", 0.0)
        
        if initial_capital < 100000:
            return "seed"
        elif initial_capital < 1000000:
            return "early"
        elif initial_capital < 10000000:
            return "growth"
        else:
            return "mature"
    
    def _determine_risk_tolerance(
        self,
        runway_months: float,
        monthly_burn_rate: float,
        current_balance: float
    ) -> str:
        """Determine appropriate risk tolerance."""
        if runway_months < 6 or monthly_burn_rate > current_balance / 12:
            return "conservative"
        elif runway_months < 12:
            return "moderate"
        else:
            return "moderate"  # Startups should generally be moderate at most
    
    def _format_investment_options(self, investment_options: Optional[Dict[str, Any]]) -> str:
        """Format investment options for prompt."""
        if not investment_options or "options" not in investment_options:
            return "No specific options available"
        
        options = investment_options.get("options", [])
        if not options:
            return "No specific options available"
        
        lines = []
        for option in options:
            lines.append(f"\n{option['name']} ({option['type']}):")
            lines.append(f"  - Risk: {option['risk_level']}")
            lines.append(f"  - Expected Return: {option['expected_return']}")
            lines.append(f"  - Liquidity: {option['liquidity']}")
            lines.append(f"  - Description: {option['description']}")
        
        return "\n".join(lines)

