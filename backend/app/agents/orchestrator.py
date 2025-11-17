"""Orchestrator for coordinating multi-agent workflows."""

import logging
import asyncio
from typing import Any, Dict, List, Optional
from enum import Enum

from app.agents.financial_analyst_agent import FinancialAnalystAgent
from app.agents.runway_predictor_agent import RunwayPredictorAgent
from app.agents.investment_advisor_agent import InvestmentAdvisorAgent
from app.services.session_service import session_service
from app.services.memory_service import memory_service

logger = logging.getLogger(__name__)


class WorkflowType(str, Enum):
    """Types of agent workflows."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CUSTOM = "custom"


class AgentOrchestrator:
    """
    Orchestrator for coordinating multi-agent workflows.
    
    Capabilities:
    - Sequential agent execution (Agent 1 → Agent 2 → Agent 3)
    - Parallel agent execution (all agents simultaneously)
    - Custom workflows with dependencies
    - Session management across agents
    - Error handling and fallback strategies
    - Aggregated results compilation
    
    Workflow patterns:
    - SEQUENTIAL: Financial Analyst → Runway Predictor → Investment Advisor
      (Investment Advisor depends on Runway Predictor results)
    
    - PARALLEL: All agents run simultaneously
      (When agents don't depend on each other's results)
    """
    
    def __init__(self, company_id: int, session_id: Optional[str] = None):
        """
        Initialize orchestrator.
        
        Args:
            company_id: ID of the company
            session_id: Optional shared session ID for all agents
        """
        self.company_id = company_id
        self.session_id = session_id or f"orchestrator_{company_id}"
        
        logger.info(
            f"Initialized orchestrator",
            extra={"company_id": company_id, "session_id": self.session_id}
        )
    
    async def run_full_analysis(
        self,
        transactions: List[Dict[str, Any]],
        company_data: Dict[str, Any],
        workflow_type: WorkflowType = WorkflowType.SEQUENTIAL
    ) -> Dict[str, Any]:
        """
        Run a complete financial analysis using all three agents.
        
        Args:
            transactions: List of transaction dictionaries
            company_data: Company information
            workflow_type: Type of workflow (sequential or parallel)
            
        Returns:
            Aggregated results from all agents
        """
        try:
            logger.info(
                f"Starting full analysis",
                extra={
                    "company_id": self.company_id,
                    "workflow_type": workflow_type,
                    "transaction_count": len(transactions)
                }
            )
            
            # Create session for this analysis
            session_service.create_session(
                session_id=self.session_id,
                company_id=self.company_id,
                agent_type="orchestrator",
                initial_context={
                    "workflow_type": workflow_type,
                    "company_name": company_data.get("name", "Unknown"),
                    "transaction_count": len(transactions)
                }
            )
            
            # Build context from memory
            historical_context = await memory_service.build_context_from_memory(
                company_id=self.company_id
            )
            
            # Execute based on workflow type
            if workflow_type == WorkflowType.SEQUENTIAL:
                results = await self._run_sequential_workflow(
                    transactions,
                    company_data,
                    historical_context
                )
            elif workflow_type == WorkflowType.PARALLEL:
                results = await self._run_parallel_workflow(
                    transactions,
                    company_data,
                    historical_context
                )
            else:
                raise ValueError(f"Unsupported workflow type: {workflow_type}")
            
            # Aggregate results
            aggregated = self._aggregate_results(results)
            
            # Update session context
            session_service.update_context(
                self.session_id,
                {"completed": True, "results": aggregated}
            )
            
            logger.info(
                f"Completed full analysis",
                extra={
                    "company_id": self.company_id,
                    "workflow_type": workflow_type
                }
            )
            
            return aggregated
            
        except Exception as e:
            logger.error(
                f"Error in full analysis",
                extra={"company_id": self.company_id, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def _run_sequential_workflow(
        self,
        transactions: List[Dict[str, Any]],
        company_data: Dict[str, Any],
        historical_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run agents sequentially: Analyst → Runway → Investment.
        
        This pattern is useful when later agents need results from earlier ones.
        """
        results = {}
        
        try:
            # Step 1: Financial Analyst
            logger.info("Step 1: Running Financial Analyst Agent")
            analyst = FinancialAnalystAgent(
                company_id=self.company_id,
                session_id=f"{self.session_id}_analyst"
            )
            
            analyst_result = await analyst.analyze(transactions, company_data)
            results["financial_analyst"] = analyst_result
            
            # Step 2: Runway Predictor
            logger.info("Step 2: Running Runway Predictor Agent")
            runway_predictor = RunwayPredictorAgent(
                company_id=self.company_id,
                session_id=f"{self.session_id}_runway"
            )
            
            runway_result = await runway_predictor.predict_runway(
                transactions,
                company_data
            )
            results["runway_predictor"] = runway_result
            
            # Step 3: Investment Advisor (uses runway results)
            logger.info("Step 3: Running Investment Advisor Agent")
            investment_advisor = InvestmentAdvisorAgent(
                company_id=self.company_id,
                session_id=f"{self.session_id}_investment"
            )
            
            # Pass runway information to investment advisor via company_data
            enhanced_company_data = {
                **company_data,
                "runway_analysis": runway_result.get("analysis", {}),
                "financial_analysis": analyst_result.get("analysis", {})
            }
            
            investment_result = await investment_advisor.advise(
                transactions,
                enhanced_company_data
            )
            results["investment_advisor"] = investment_result
            
            return results
            
        except Exception as e:
            logger.error(
                f"Error in sequential workflow",
                extra={"completed_steps": list(results.keys()), "error": str(e)},
                exc_info=True
            )
            
            # Return partial results if any steps completed
            results["error"] = str(e)
            results["status"] = "partial"
            return results
    
    async def _run_parallel_workflow(
        self,
        transactions: List[Dict[str, Any]],
        company_data: Dict[str, Any],
        historical_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run all agents in parallel.
        
        This pattern is faster but agents don't share results with each other.
        """
        try:
            # Create all agents
            analyst = FinancialAnalystAgent(
                company_id=self.company_id,
                session_id=f"{self.session_id}_analyst"
            )
            
            runway_predictor = RunwayPredictorAgent(
                company_id=self.company_id,
                session_id=f"{self.session_id}_runway"
            )
            
            investment_advisor = InvestmentAdvisorAgent(
                company_id=self.company_id,
                session_id=f"{self.session_id}_investment"
            )
            
            # Run all agents in parallel
            logger.info("Running all agents in parallel")
            
            analyst_task = analyst.analyze(transactions, company_data)
            runway_task = runway_predictor.predict_runway(transactions, company_data)
            investment_task = investment_advisor.advise(transactions, company_data)
            
            # Wait for all to complete
            analyst_result, runway_result, investment_result = await asyncio.gather(
                analyst_task,
                runway_task,
                investment_task,
                return_exceptions=True
            )
            
            # Handle any exceptions
            results = {}
            
            if isinstance(analyst_result, Exception):
                logger.error(f"Financial Analyst failed: {analyst_result}")
                results["financial_analyst"] = {"error": str(analyst_result), "status": "failed"}
            else:
                results["financial_analyst"] = analyst_result
            
            if isinstance(runway_result, Exception):
                logger.error(f"Runway Predictor failed: {runway_result}")
                results["runway_predictor"] = {"error": str(runway_result), "status": "failed"}
            else:
                results["runway_predictor"] = runway_result
            
            if isinstance(investment_result, Exception):
                logger.error(f"Investment Advisor failed: {investment_result}")
                results["investment_advisor"] = {"error": str(investment_result), "status": "failed"}
            else:
                results["investment_advisor"] = investment_result
            
            return results
            
        except Exception as e:
            logger.error(
                f"Error in parallel workflow",
                extra={"error": str(e)},
                exc_info=True
            )
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def run_single_agent(
        self,
        agent_type: str,
        transactions: List[Dict[str, Any]],
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a single agent.
        
        Args:
            agent_type: Type of agent ("analyst", "runway", "investment")
            transactions: List of transactions
            company_data: Company information
            
        Returns:
            Agent results
        """
        try:
            logger.info(
                f"Running single agent: {agent_type}",
                extra={"company_id": self.company_id, "agent_type": agent_type}
            )
            
            if agent_type == "analyst":
                agent = FinancialAnalystAgent(
                    company_id=self.company_id,
                    session_id=f"{self.session_id}_{agent_type}"
                )
                result = await agent.analyze(transactions, company_data)
            
            elif agent_type == "runway":
                agent = RunwayPredictorAgent(
                    company_id=self.company_id,
                    session_id=f"{self.session_id}_{agent_type}"
                )
                result = await agent.predict_runway(transactions, company_data)
            
            elif agent_type == "investment":
                agent = InvestmentAdvisorAgent(
                    company_id=self.company_id,
                    session_id=f"{self.session_id}_{agent_type}"
                )
                result = await agent.advise(transactions, company_data)
            
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error running single agent",
                extra={"agent_type": agent_type, "error": str(e)},
                exc_info=True
            )
            raise
    
    def _aggregate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate results from multiple agents into a unified response.
        
        Args:
            results: Dictionary of agent results
            
        Returns:
            Aggregated results
        """
        aggregated = {
            "company_id": self.company_id,
            "session_id": self.session_id,
            "agents": {}
        }
        
        # Extract key information from each agent
        for agent_type, agent_result in results.items():
            if agent_type in ["error", "status"]:
                aggregated[agent_type] = agent_result
                continue
            
            if isinstance(agent_result, dict):
                aggregated["agents"][agent_type] = {
                    "status": agent_result.get("status", "unknown"),
                    "insights": agent_result.get("insights", ""),
                    "analysis": agent_result.get("analysis", {}),
                    "timestamp": agent_result.get("timestamp")
                }
        
        # Calculate overall health summary
        aggregated["summary"] = self._generate_summary(results)
        
        return aggregated
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary from all agent results."""
        summary = {
            "agents_completed": 0,
            "agents_failed": 0,
            "overall_status": "unknown"
        }
        
        for agent_type, agent_result in results.items():
            if agent_type in ["error", "status"]:
                continue
            
            if isinstance(agent_result, dict):
                if agent_result.get("status") == "completed":
                    summary["agents_completed"] += 1
                else:
                    summary["agents_failed"] += 1
        
        # Determine overall status
        total_agents = summary["agents_completed"] + summary["agents_failed"]
        if summary["agents_completed"] == total_agents:
            summary["overall_status"] = "success"
        elif summary["agents_completed"] > 0:
            summary["overall_status"] = "partial"
        else:
            summary["overall_status"] = "failed"
        
        # Extract key metrics if available
        if "runway_predictor" in results:
            runway_analysis = results["runway_predictor"].get("analysis", {})
            runway_info = runway_analysis.get("runway", {})
            summary["runway_months"] = runway_info.get("runway_months", 0)
            summary["runway_status"] = runway_info.get("status", "unknown")
        
        if "financial_analyst" in results:
            analyst_analysis = results["financial_analyst"].get("analysis", {})
            balance_info = analyst_analysis.get("balance", {})
            summary["current_balance"] = balance_info.get("current_balance", 0)
        
        if "investment_advisor" in results:
            investment_analysis = results["investment_advisor"].get("analysis", {})
            readiness = investment_analysis.get("readiness", {})
            summary["investment_readiness"] = readiness.get("readiness", "unknown")
        
        return summary


# Convenience function for creating orchestrator
def create_orchestrator(company_id: int, session_id: Optional[str] = None) -> AgentOrchestrator:
    """
    Create an agent orchestrator instance.
    
    Args:
        company_id: ID of the company
        session_id: Optional session ID
        
    Returns:
        AgentOrchestrator instance
    """
    return AgentOrchestrator(company_id, session_id)

