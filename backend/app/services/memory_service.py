"""Memory service for long-term storage of agent insights."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_session import AgentSession, AgentStatus, AgentType
from app.database import get_async_session

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Service for managing long-term memory of agent insights.
    
    This service provides:
    - Storage and retrieval of past agent analyses
    - Historical insight tracking
    - Pattern recognition across sessions
    - Context building for future agent calls
    
    Uses the AgentSession database table for persistent storage.
    """
    
    async def get_recent_insights(
        self,
        company_id: int,
        agent_type: Optional[AgentType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent agent insights for a company.
        
        Args:
            company_id: ID of the company
            agent_type: Optional filter by agent type
            limit: Maximum number of insights to return
            
        Returns:
            List of insight dictionaries
        """
        try:
            async for db in get_async_session():
                # Build query
                query = select(AgentSession).where(
                    and_(
                        AgentSession.company_id == company_id,
                        AgentSession.status == AgentStatus.COMPLETED
                    )
                )
                
                # Filter by agent type if provided
                if agent_type:
                    query = query.where(AgentSession.agent_type == agent_type)
                
                # Order by most recent and limit
                query = query.order_by(desc(AgentSession.created_at)).limit(limit)
                
                # Execute query
                result = await db.execute(query)
                sessions = result.scalars().all()
                
                # Format results
                insights = []
                for session in sessions:
                    insights.append({
                        "session_id": session.session_id,
                        "agent_type": session.agent_type.value,
                        "created_at": session.created_at.isoformat(),
                        "input_data": session.input_data,
                        "output_data": session.output_data,
                        "execution_time_ms": session.execution_time_ms,
                        "token_count": session.token_count
                    })
                
                logger.info(
                    f"Retrieved {len(insights)} insights for company {company_id}",
                    extra={
                        "company_id": company_id,
                        "agent_type": agent_type.value if agent_type else "all",
                        "count": len(insights)
                    }
                )
                
                return insights
                
        except Exception as e:
            logger.error(
                f"Error retrieving insights",
                extra={"company_id": company_id, "error": str(e)},
                exc_info=True
            )
            return []
    
    async def get_latest_analysis(
        self,
        company_id: int,
        agent_type: AgentType
    ) -> Optional[Dict[str, Any]]:
        """
        Get the most recent completed analysis for a company and agent type.
        
        Args:
            company_id: ID of the company
            agent_type: Type of agent
            
        Returns:
            Latest analysis dictionary or None
        """
        insights = await self.get_recent_insights(
            company_id=company_id,
            agent_type=agent_type,
            limit=1
        )
        
        return insights[0] if insights else None
    
    async def get_historical_trends(
        self,
        company_id: int,
        agent_type: AgentType,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get historical trend data for a company and agent type.
        
        Args:
            company_id: ID of the company
            agent_type: Type of agent
            days: Number of days to look back
            
        Returns:
            List of historical insights
        """
        try:
            async for db in get_async_session():
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                query = select(AgentSession).where(
                    and_(
                        AgentSession.company_id == company_id,
                        AgentSession.agent_type == agent_type,
                        AgentSession.status == AgentStatus.COMPLETED,
                        AgentSession.created_at >= cutoff_date
                    )
                ).order_by(AgentSession.created_at)
                
                result = await db.execute(query)
                sessions = result.scalars().all()
                
                # Extract key metrics over time
                trends = []
                for session in sessions:
                    trends.append({
                        "timestamp": session.created_at.isoformat(),
                        "output_data": session.output_data
                    })
                
                logger.info(
                    f"Retrieved {len(trends)} historical trends",
                    extra={
                        "company_id": company_id,
                        "agent_type": agent_type.value,
                        "days": days
                    }
                )
                
                return trends
                
        except Exception as e:
            logger.error(
                f"Error retrieving historical trends",
                extra={
                    "company_id": company_id,
                    "agent_type": agent_type.value,
                    "error": str(e)
                },
                exc_info=True
            )
            return []
    
    async def build_context_from_memory(
        self,
        company_id: int,
        agent_type: Optional[AgentType] = None
    ) -> Dict[str, Any]:
        """
        Build context for an agent call using historical memory.
        
        Args:
            company_id: ID of the company
            agent_type: Optional agent type filter
            
        Returns:
            Context dictionary with historical insights
        """
        try:
            # Get recent insights
            recent_insights = await self.get_recent_insights(
                company_id=company_id,
                agent_type=agent_type,
                limit=5
            )
            
            # Build context
            context = {
                "company_id": company_id,
                "has_previous_analyses": len(recent_insights) > 0,
                "previous_analysis_count": len(recent_insights),
                "recent_insights": recent_insights
            }
            
            # Add summary of most recent analysis if available
            if recent_insights:
                latest = recent_insights[0]
                context["latest_analysis"] = {
                    "agent_type": latest["agent_type"],
                    "timestamp": latest["created_at"],
                    "summary": self._extract_summary(latest["output_data"])
                }
            
            return context
            
        except Exception as e:
            logger.error(
                f"Error building context from memory",
                extra={"company_id": company_id, "error": str(e)},
                exc_info=True
            )
            return {"company_id": company_id, "has_previous_analyses": False}
    
    async def get_performance_metrics(
        self,
        company_id: Optional[int] = None,
        agent_type: Optional[AgentType] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get performance metrics for agent executions.
        
        Args:
            company_id: Optional company ID filter
            agent_type: Optional agent type filter
            days: Number of days to analyze
            
        Returns:
            Dictionary of performance metrics
        """
        try:
            async for db in get_async_session():
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                # Build query
                query = select(AgentSession).where(
                    AgentSession.created_at >= cutoff_date
                )
                
                if company_id:
                    query = query.where(AgentSession.company_id == company_id)
                
                if agent_type:
                    query = query.where(AgentSession.agent_type == agent_type)
                
                result = await db.execute(query)
                sessions = result.scalars().all()
                
                # Calculate metrics
                total_executions = len(sessions)
                completed = sum(1 for s in sessions if s.status == AgentStatus.COMPLETED)
                failed = sum(1 for s in sessions if s.status == AgentStatus.FAILED)
                
                avg_execution_time = (
                    sum(s.execution_time_ms for s in sessions) / total_executions
                    if total_executions > 0 else 0
                )
                
                total_tokens = sum(s.token_count for s in sessions)
                
                metrics = {
                    "period_days": days,
                    "total_executions": total_executions,
                    "completed_executions": completed,
                    "failed_executions": failed,
                    "success_rate": completed / total_executions if total_executions > 0 else 0,
                    "avg_execution_time_ms": avg_execution_time,
                    "total_tokens_used": total_tokens,
                    "avg_tokens_per_execution": (
                        total_tokens / total_executions if total_executions > 0 else 0
                    )
                }
                
                logger.info(
                    f"Calculated performance metrics",
                    extra={"metrics": metrics}
                )
                
                return metrics
                
        except Exception as e:
            logger.error(
                f"Error calculating performance metrics",
                extra={"error": str(e)},
                exc_info=True
            )
            return {
                "period_days": days,
                "total_executions": 0,
                "error": str(e)
            }
    
    def _extract_summary(self, output_data: Dict[str, Any]) -> str:
        """
        Extract a brief summary from output data.
        
        Args:
            output_data: Agent output data
            
        Returns:
            Summary string
        """
        # Try to extract key summary fields
        if isinstance(output_data, dict):
            if "response" in output_data:
                response = output_data["response"]
                # Truncate to first 200 characters
                if isinstance(response, str):
                    return response[:200] + ("..." if len(response) > 200 else "")
            
            if "insights" in output_data:
                return str(output_data["insights"])[:200]
        
        return "No summary available"


# Global memory service instance
memory_service = MemoryService()

