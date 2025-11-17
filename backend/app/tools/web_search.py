"""Web search tool for investment research and market data."""

import logging
from typing import Any, Dict, List, Optional
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSearch:
    """
    Web search tool for researching investment options and market data.
    
    In production, this would integrate with Google Search API or similar.
    For demo purposes, provides curated investment recommendations.
    
    Features:
    - Investment option research
    - Market trends
    - Financial advice aggregation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize web search tool.
        
        Args:
            api_key: Optional API key for search service
        """
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_investment_options(
        self,
        company_stage: str = "early",
        risk_tolerance: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Search for suitable investment options.
        
        Args:
            company_stage: Stage of company (seed, early, growth, mature)
            risk_tolerance: Risk tolerance (conservative, moderate, aggressive)
            
        Returns:
            Dictionary with investment options
        """
        try:
            logger.info(
                f"Searching investment options",
                extra={"stage": company_stage, "risk": risk_tolerance}
            )
            
            # For demo: Provide curated investment recommendations
            # In production: Call Google Search API or financial data API
            
            investment_options = self._get_curated_investment_options(
                company_stage,
                risk_tolerance
            )
            
            result = {
                "query": f"Investment options for {company_stage} stage {risk_tolerance} risk",
                "timestamp": datetime.utcnow().isoformat(),
                "options": investment_options,
                "source": "curated_recommendations"
            }
            
            logger.info(f"Found {len(investment_options)} investment options")
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching investment options: {e}", exc_info=True)
            return {
                "error": str(e),
                "options": []
            }
    
    async def search_market_trends(
        self,
        industry: str,
        region: str = "global"
    ) -> Dict[str, Any]:
        """
        Search for market trends in specific industry.
        
        Args:
            industry: Industry to research
            region: Geographic region
            
        Returns:
            Dictionary with market trends
        """
        try:
            logger.info(
                f"Searching market trends",
                extra={"industry": industry, "region": region}
            )
            
            # For demo: Provide general market insights
            # In production: Call news/trends API
            
            trends = self._get_market_trends(industry, region)
            
            result = {
                "query": f"{industry} market trends in {region}",
                "timestamp": datetime.utcnow().isoformat(),
                "trends": trends,
                "source": "market_analysis"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching market trends: {e}", exc_info=True)
            return {
                "error": str(e),
                "trends": []
            }
    
    async def search_financial_advice(
        self,
        topic: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for financial advice on specific topic.
        
        Args:
            topic: Topic to research (e.g., "startup runway", "burn rate")
            context: Optional additional context
            
        Returns:
            Dictionary with advice and recommendations
        """
        try:
            logger.info(
                f"Searching financial advice",
                extra={"topic": topic, "context": context}
            )
            
            # For demo: Provide curated financial advice
            # In production: Aggregate from financial advisory sources
            
            advice = self._get_financial_advice(topic, context)
            
            result = {
                "query": topic,
                "context": context,
                "timestamp": datetime.utcnow().isoformat(),
                "advice": advice,
                "source": "financial_advisory"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching financial advice: {e}", exc_info=True)
            return {
                "error": str(e),
                "advice": []
            }
    
    def _get_curated_investment_options(
        self,
        company_stage: str,
        risk_tolerance: str
    ) -> List[Dict[str, Any]]:
        """Get curated investment recommendations based on stage and risk."""
        
        # Base options available to all
        options = []
        
        # High-yield savings accounts (conservative)
        if risk_tolerance in ["conservative", "moderate"]:
            options.append({
                "name": "High-Yield Savings Account",
                "type": "savings",
                "risk_level": "very_low",
                "expected_return": "4.5-5.0% APY",
                "liquidity": "high",
                "minimum": "$0",
                "description": "FDIC-insured savings with competitive rates. Ideal for emergency funds and short-term reserves.",
                "pros": ["No risk", "High liquidity", "FDIC insured"],
                "cons": ["Lower returns", "Inflation risk"]
            })
        
        # Money Market Funds
        if risk_tolerance in ["conservative", "moderate"]:
            options.append({
                "name": "Money Market Funds",
                "type": "money_market",
                "risk_level": "low",
                "expected_return": "5.0-5.5% APY",
                "liquidity": "high",
                "minimum": "$1,000",
                "description": "Low-risk investment in short-term debt securities. Better returns than savings.",
                "pros": ["Low risk", "Better than savings", "High liquidity"],
                "cons": ["Not FDIC insured", "Market dependent"]
            })
        
        # Treasury Bills (conservative to moderate)
        options.append({
            "name": "U.S. Treasury Bills",
            "type": "treasury",
            "risk_level": "very_low",
            "expected_return": "4.5-5.5%",
            "liquidity": "moderate",
            "minimum": "$100",
            "description": "Government-backed securities with guaranteed returns. Maturities from 4 weeks to 1 year.",
            "pros": ["Government backed", "Predictable", "Tax advantages"],
            "cons": ["Lower returns", "Time commitment"]
        })
        
        # Corporate Bonds (moderate risk)
        if risk_tolerance in ["moderate", "aggressive"]:
            options.append({
                "name": "Investment-Grade Corporate Bonds",
                "type": "bonds",
                "risk_level": "low_moderate",
                "expected_return": "5.5-7.0%",
                "liquidity": "moderate",
                "minimum": "$1,000",
                "description": "Bonds from stable corporations with strong credit ratings.",
                "pros": ["Higher yields", "Regular income", "Diversification"],
                "cons": ["Credit risk", "Interest rate risk", "Less liquid"]
            })
        
        # Index Funds (moderate to aggressive)
        if risk_tolerance in ["moderate", "aggressive"] and company_stage in ["growth", "mature"]:
            options.append({
                "name": "S&P 500 Index Funds",
                "type": "equity_index",
                "risk_level": "moderate",
                "expected_return": "8-12% (historical avg)",
                "liquidity": "high",
                "minimum": "$0-$1,000",
                "description": "Diversified exposure to 500 largest US companies. Long-term growth potential.",
                "pros": ["High returns potential", "Diversified", "Low fees"],
                "cons": ["Market volatility", "Not guaranteed", "Long-term horizon"]
            })
        
        # Growth ETFs (aggressive)
        if risk_tolerance == "aggressive" and company_stage in ["growth", "mature"]:
            options.append({
                "name": "Technology/Growth ETFs",
                "type": "equity_etf",
                "risk_level": "moderate_high",
                "expected_return": "10-15%",
                "liquidity": "high",
                "minimum": "$0",
                "description": "ETFs focused on high-growth sectors like technology and innovation.",
                "pros": ["High growth potential", "Sector exposure", "Liquid"],
                "cons": ["High volatility", "Sector concentration", "Market dependent"]
            })
        
        # CDs (conservative, for mature companies)
        if risk_tolerance == "conservative" and company_stage == "mature":
            options.append({
                "name": "Certificates of Deposit (CDs)",
                "type": "cd",
                "risk_level": "very_low",
                "expected_return": "4.5-5.5%",
                "liquidity": "low",
                "minimum": "$500",
                "description": "Fixed-term deposits with guaranteed returns. Terms from 3 months to 5 years.",
                "pros": ["FDIC insured", "Guaranteed returns", "Predictable"],
                "cons": ["Low liquidity", "Early withdrawal penalties", "Rate lock"]
            })
        
        return options
    
    def _get_market_trends(
        self,
        industry: str,
        region: str
    ) -> List[Dict[str, Any]]:
        """Get market trends for industry."""
        
        # Provide general market insights
        trends = [
            {
                "trend": "Rising interest rates",
                "impact": "Higher returns on fixed-income investments",
                "relevance": "high",
                "timeframe": "2024-2025"
            },
            {
                "trend": "Digital transformation acceleration",
                "impact": "Increased focus on technology investments",
                "relevance": "high" if industry.lower() in ["technology", "software", "saas"] else "moderate",
                "timeframe": "ongoing"
            },
            {
                "trend": "ESG investing growth",
                "impact": "More focus on sustainable and responsible investments",
                "relevance": "moderate",
                "timeframe": "long-term"
            }
        ]
        
        return trends
    
    def _get_financial_advice(
        self,
        topic: str,
        context: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get financial advice on topic."""
        
        advice_database = {
            "runway": [
                {
                    "advice": "Maintain 12-18 months of runway",
                    "rationale": "Provides buffer for unexpected challenges and fundraising cycles",
                    "source": "VC best practices"
                },
                {
                    "advice": "Start fundraising at 6-9 months runway",
                    "rationale": "Fundraising takes 3-6 months on average; don't wait until critical",
                    "source": "Y Combinator guidance"
                },
                {
                    "advice": "Track runway weekly",
                    "rationale": "Early detection of problems allows for corrective action",
                    "source": "CFO best practices"
                }
            ],
            "burn_rate": [
                {
                    "advice": "Reduce burn rate when approaching critical runway",
                    "rationale": "Preserve cash to extend runway and maintain operations",
                    "source": "Financial management"
                },
                {
                    "advice": "Focus on revenue growth to improve burn multiple",
                    "rationale": "Revenue growth reduces net burn and improves unit economics",
                    "source": "Growth metrics"
                },
                {
                    "advice": "Benchmark burn against revenue milestones",
                    "rationale": "Efficient capital usage demonstrates to investors",
                    "source": "VC expectations"
                }
            ],
            "default": [
                {
                    "advice": "Diversify investments across asset classes",
                    "rationale": "Reduces risk through diversification",
                    "source": "Modern portfolio theory"
                },
                {
                    "advice": "Maintain emergency fund of 3-6 months expenses",
                    "rationale": "Provides financial cushion for unexpected events",
                    "source": "Personal finance basics"
                },
                {
                    "advice": "Invest for long-term, not short-term gains",
                    "rationale": "Long-term investing reduces volatility impact",
                    "source": "Investment fundamentals"
                }
            ]
        }
        
        # Find relevant advice
        topic_lower = topic.lower()
        if "runway" in topic_lower:
            return advice_database["runway"]
        elif "burn" in topic_lower:
            return advice_database["burn_rate"]
        else:
            return advice_database["default"]
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global instance
web_search = WebSearch()

