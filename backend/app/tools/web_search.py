"""Web search tool for investment research and market data."""

import logging
from typing import Any, Dict, List, Optional
import httpx
from datetime import datetime

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False
    logger.warning("Google API client not installed. Install with: pip install google-api-python-client")

from app.config import settings

logger = logging.getLogger(__name__)


class WebSearch:
    """
    Web search tool for researching investment options and market data.
    
    Integrates with Google Custom Search API for real-time web search.
    Falls back to curated recommendations if API is not configured.
    
    Features:
    - Investment option research (real-time via Google Search)
    - Market trends (real-time financial news)
    - Financial advice aggregation (from trusted sources)
    - Automatic fallback to curated data if API unavailable
    """
    
    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None):
        """
        Initialize web search tool.
        
        Args:
            api_key: Google Custom Search API key (or uses settings.google_search_api_key)
            search_engine_id: Programmable Search Engine ID (or uses settings.google_search_engine_id)
        """
        self.api_key = api_key or settings.google_search_api_key
        self.search_engine_id = search_engine_id or settings.google_search_engine_id
        self.enabled = settings.google_search_enabled and GOOGLE_SEARCH_AVAILABLE
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Initialize Google Search service if available
        self.search_service = None
        if self.enabled and self.api_key and self.search_engine_id:
            try:
                self.search_service = build("customsearch", "v1", developerKey=self.api_key)
                logger.info("Google Custom Search API initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Search API: {e}. Using fallback mode.")
                self.enabled = False
        else:
            logger.info("Google Search API not configured. Using curated fallback data.")
    
    async def _google_search(
        self,
        query: str,
        num_results: int = None,
        date_restrict: Optional[str] = None,
        site_search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform Google Custom Search API query.
        
        Args:
            query: Search query string
            num_results: Number of results to return (max 10 per request)
            date_restrict: Date restriction (e.g., 'd7' for last 7 days, 'm1' for last month)
            site_search: Restrict search to specific site
            
        Returns:
            List of search result dictionaries
        """
        if not self.enabled or not self.search_service:
            return []
        
        try:
            num_results = num_results or settings.search_max_results
            
            # Build search parameters
            search_params = {
                'q': query,
                'cx': self.search_engine_id,
                'num': min(num_results, 10),  # API limit is 10 per request
                'safe': settings.search_safe_mode
            }
            
            if date_restrict:
                search_params['dateRestrict'] = date_restrict
            
            if site_search:
                search_params['siteSearch'] = site_search
            
            # Execute search
            result = self.search_service.cse().list(**search_params).execute()
            
            # Parse results
            search_results = []
            if 'items' in result:
                for item in result['items']:
                    search_results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': item.get('displayLink', ''),
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            logger.info(f"Google Search returned {len(search_results)} results for query: {query}")
            return search_results
            
        except HttpError as e:
            logger.error(f"Google Search API error: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Error performing Google search: {e}", exc_info=True)
            return []
    
    async def search_investment_options(
        self,
        company_stage: str = "early",
        risk_tolerance: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Search for suitable investment options using Google Search or curated data.
        
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
            
            # Try real-time Google Search first
            google_results = []
            if self.enabled:
                # Construct optimized search query for financial sites
                search_query = f"best {risk_tolerance} risk investment options for startups {company_stage} stage 2024"
                google_results = await self._google_search(
                    query=search_query,
                    num_results=5,
                    date_restrict='m3'  # Last 3 months for current data
                )
            
            # Get curated recommendations (always include as baseline)
            curated_options = self._get_curated_investment_options(
                company_stage,
                risk_tolerance
            )
            
            # Build result combining both sources
            result = {
                "query": f"Investment options for {company_stage} stage {risk_tolerance} risk",
                "timestamp": datetime.utcnow().isoformat(),
                "options": curated_options,
                "web_research": google_results if google_results else [],
                "source": "google_search_and_curated" if google_results else "curated_recommendations",
                "search_enabled": self.enabled
            }
            
            logger.info(
                f"Found {len(curated_options)} curated options + {len(google_results)} web results"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching investment options: {e}", exc_info=True)
            return {
                "error": str(e),
                "options": [],
                "web_research": []
            }
    
    async def search_market_trends(
        self,
        industry: str,
        region: str = "global"
    ) -> Dict[str, Any]:
        """
        Search for market trends in specific industry using real-time news.
        
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
            
            # Try real-time Google Search for news
            google_results = []
            if self.enabled:
                # Search for recent market trends and news
                search_query = f"{industry} market trends {region} news analysis 2024"
                google_results = await self._google_search(
                    query=search_query,
                    num_results=5,
                    date_restrict='m1'  # Last month for current trends
                )
            
            # Get general market insights as fallback
            fallback_trends = self._get_market_trends(industry, region)
            
            result = {
                "query": f"{industry} market trends in {region}",
                "timestamp": datetime.utcnow().isoformat(),
                "trends": fallback_trends,
                "news_articles": google_results if google_results else [],
                "source": "google_news_and_analysis" if google_results else "market_analysis",
                "search_enabled": self.enabled
            }
            
            logger.info(
                f"Found {len(fallback_trends)} trend insights + {len(google_results)} news articles"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching market trends: {e}", exc_info=True)
            return {
                "error": str(e),
                "trends": [],
                "news_articles": []
            }
    
    async def search_financial_advice(
        self,
        topic: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for financial advice on specific topic from trusted sources.
        
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
            
            # Try real-time Google Search from financial advisory sites
            google_results = []
            if self.enabled:
                # Build context-aware search query
                search_query = f"{topic} financial advice best practices"
                if context:
                    search_query += f" {context}"
                
                google_results = await self._google_search(
                    query=search_query,
                    num_results=5,
                    date_restrict='y1'  # Last year for relevant advice
                )
            
            # Get curated advice as baseline
            curated_advice = self._get_financial_advice(topic, context)
            
            result = {
                "query": topic,
                "context": context,
                "timestamp": datetime.utcnow().isoformat(),
                "advice": curated_advice,
                "web_sources": google_results if google_results else [],
                "source": "google_search_and_curated" if google_results else "financial_advisory",
                "search_enabled": self.enabled
            }
            
            logger.info(
                f"Found {len(curated_advice)} curated advice + {len(google_results)} web sources"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching financial advice: {e}", exc_info=True)
            return {
                "error": str(e),
                "advice": [],
                "web_sources": []
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

