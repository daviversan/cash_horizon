"""Financial calculation tools for agent operations."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict

logger = logging.getLogger(__name__)


class FinancialCalculator:
    """
    Financial calculator tool for computing financial metrics.
    
    Provides calculations for:
    - Burn rate (monthly cash consumption)
    - Runway (months until cash runs out)
    - Category-wise spending analysis
    - Income vs expense tracking
    - Balance calculations
    - Growth rates
    """
    
    @staticmethod
    def calculate_burn_rate(
        transactions: List[Dict[str, Any]],
        period_months: int = 3
    ) -> Dict[str, Any]:
        """
        Calculate the monthly burn rate based on recent transactions.
        
        Burn rate = Average monthly expenses - Average monthly income
        
        Args:
            transactions: List of transaction dictionaries with date, amount, type
            period_months: Number of months to analyze (default 3)
            
        Returns:
            Dictionary with burn rate metrics
        """
        try:
            if not transactions:
                return {
                    "burn_rate": 0.0,
                    "avg_monthly_expenses": 0.0,
                    "avg_monthly_income": 0.0,
                    "net_burn": 0.0,
                    "period_months": period_months,
                    "transaction_count": 0
                }
            
            # Filter to recent period
            cutoff_date = datetime.utcnow() - timedelta(days=period_months * 30)
            recent_transactions = [
                t for t in transactions
                if datetime.fromisoformat(t["date"].replace("Z", "+00:00")) >= cutoff_date
            ]
            
            # Calculate monthly totals
            monthly_income = defaultdict(float)
            monthly_expenses = defaultdict(float)
            
            for transaction in recent_transactions:
                date = datetime.fromisoformat(transaction["date"].replace("Z", "+00:00"))
                month_key = date.strftime("%Y-%m")
                amount = float(transaction["amount"])
                
                if transaction["type"] == "income":
                    monthly_income[month_key] += amount
                else:  # expense
                    monthly_expenses[month_key] += amount
            
            # Calculate averages
            num_months = max(len(monthly_income), len(monthly_expenses), 1)
            avg_monthly_income = sum(monthly_income.values()) / num_months
            avg_monthly_expenses = sum(monthly_expenses.values()) / num_months
            net_burn = avg_monthly_expenses - avg_monthly_income
            
            result = {
                "burn_rate": round(net_burn, 2),
                "avg_monthly_expenses": round(avg_monthly_expenses, 2),
                "avg_monthly_income": round(avg_monthly_income, 2),
                "net_burn": round(net_burn, 2),
                "period_months": period_months,
                "transaction_count": len(recent_transactions),
                "months_analyzed": num_months
            }
            
            logger.debug(
                f"Calculated burn rate",
                extra={"burn_rate": result["burn_rate"], "months": num_months}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating burn rate: {e}", exc_info=True)
            return {
                "error": str(e),
                "burn_rate": 0.0
            }
    
    @staticmethod
    def calculate_runway(
        current_balance: float,
        monthly_burn_rate: float
    ) -> Dict[str, Any]:
        """
        Calculate runway (months until cash runs out).
        
        Runway = Current Balance / Monthly Burn Rate
        
        Args:
            current_balance: Current cash balance
            monthly_burn_rate: Monthly burn rate (should be positive for negative cash flow)
            
        Returns:
            Dictionary with runway metrics
        """
        try:
            if monthly_burn_rate <= 0:
                return {
                    "runway_months": float('inf'),
                    "runway_days": float('inf'),
                    "estimated_depletion_date": None,
                    "current_balance": current_balance,
                    "monthly_burn_rate": monthly_burn_rate,
                    "status": "positive_cash_flow"
                }
            
            runway_months = current_balance / monthly_burn_rate
            runway_days = runway_months * 30
            
            # Calculate estimated depletion date
            depletion_date = datetime.utcnow() + timedelta(days=runway_days)
            
            # Determine health status
            if runway_months < 3:
                status = "critical"
            elif runway_months < 6:
                status = "warning"
            elif runway_months < 12:
                status = "healthy"
            else:
                status = "excellent"
            
            result = {
                "runway_months": round(runway_months, 2),
                "runway_days": round(runway_days, 0),
                "estimated_depletion_date": depletion_date.strftime("%Y-%m-%d"),
                "current_balance": round(current_balance, 2),
                "monthly_burn_rate": round(monthly_burn_rate, 2),
                "status": status
            }
            
            logger.debug(
                f"Calculated runway",
                extra={"runway_months": result["runway_months"], "status": status}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating runway: {e}", exc_info=True)
            return {
                "error": str(e),
                "runway_months": 0.0
            }
    
    @staticmethod
    def analyze_spending_by_category(
        transactions: List[Dict[str, Any]],
        period_months: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze spending breakdown by category.
        
        Args:
            transactions: List of transaction dictionaries
            period_months: Optional period to analyze (None = all time)
            
        Returns:
            Dictionary with category breakdown
        """
        try:
            # Filter by period if specified
            if period_months:
                cutoff_date = datetime.utcnow() - timedelta(days=period_months * 30)
                transactions = [
                    t for t in transactions
                    if datetime.fromisoformat(t["date"].replace("Z", "+00:00")) >= cutoff_date
                ]
            
            # Group by category
            category_totals = defaultdict(float)
            category_counts = defaultdict(int)
            total_expenses = 0.0
            total_income = 0.0
            
            for transaction in transactions:
                amount = float(transaction["amount"])
                category = transaction.get("category", "Uncategorized")
                
                if transaction["type"] == "expense":
                    category_totals[category] += amount
                    category_counts[category] += 1
                    total_expenses += amount
                else:
                    total_income += amount
            
            # Calculate percentages
            categories = []
            for category, total in category_totals.items():
                percentage = (total / total_expenses * 100) if total_expenses > 0 else 0
                categories.append({
                    "category": category,
                    "total": round(total, 2),
                    "count": category_counts[category],
                    "percentage": round(percentage, 2),
                    "avg_per_transaction": round(total / category_counts[category], 2)
                })
            
            # Sort by total descending
            categories.sort(key=lambda x: x["total"], reverse=True)
            
            result = {
                "categories": categories,
                "total_expenses": round(total_expenses, 2),
                "total_income": round(total_income, 2),
                "net_position": round(total_income - total_expenses, 2),
                "transaction_count": len(transactions),
                "period_months": period_months or "all_time"
            }
            
            logger.debug(
                f"Analyzed spending by category",
                extra={"category_count": len(categories), "total_expenses": total_expenses}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing spending by category: {e}", exc_info=True)
            return {
                "error": str(e),
                "categories": []
            }
    
    @staticmethod
    def calculate_balance(
        initial_capital: float,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate current balance based on initial capital and transactions.
        
        Args:
            initial_capital: Starting capital
            transactions: List of all transactions
            
        Returns:
            Dictionary with balance information
        """
        try:
            total_income = sum(
                float(t["amount"])
                for t in transactions
                if t["type"] == "income"
            )
            
            total_expenses = sum(
                float(t["amount"])
                for t in transactions
                if t["type"] == "expense"
            )
            
            current_balance = initial_capital + total_income - total_expenses
            
            result = {
                "current_balance": round(current_balance, 2),
                "initial_capital": round(initial_capital, 2),
                "total_income": round(total_income, 2),
                "total_expenses": round(total_expenses, 2),
                "net_change": round(total_income - total_expenses, 2),
                "balance_status": "positive" if current_balance > 0 else "negative"
            }
            
            logger.debug(
                f"Calculated balance",
                extra={"current_balance": result["current_balance"]}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating balance: {e}", exc_info=True)
            return {
                "error": str(e),
                "current_balance": 0.0
            }
    
    @staticmethod
    def calculate_growth_rate(
        transactions: List[Dict[str, Any]],
        metric: str = "income",
        period_months: int = 6
    ) -> Dict[str, Any]:
        """
        Calculate month-over-month growth rate.
        
        Args:
            transactions: List of transactions
            metric: "income" or "expenses"
            period_months: Number of months to analyze
            
        Returns:
            Dictionary with growth rate metrics
        """
        try:
            # Filter to recent period
            cutoff_date = datetime.utcnow() - timedelta(days=period_months * 30)
            transactions = [
                t for t in transactions
                if datetime.fromisoformat(t["date"].replace("Z", "+00:00")) >= cutoff_date
                and t["type"] == metric
            ]
            
            # Group by month
            monthly_totals = defaultdict(float)
            for transaction in transactions:
                date = datetime.fromisoformat(transaction["date"].replace("Z", "+00:00"))
                month_key = date.strftime("%Y-%m")
                monthly_totals[month_key] += float(transaction["amount"])
            
            # Sort months
            sorted_months = sorted(monthly_totals.items())
            
            if len(sorted_months) < 2:
                return {
                    "growth_rate": 0.0,
                    "metric": metric,
                    "period_months": period_months,
                    "insufficient_data": True
                }
            
            # Calculate average growth rate
            growth_rates = []
            for i in range(1, len(sorted_months)):
                prev_month, prev_value = sorted_months[i-1]
                curr_month, curr_value = sorted_months[i]
                
                if prev_value > 0:
                    growth = ((curr_value - prev_value) / prev_value) * 100
                    growth_rates.append(growth)
            
            avg_growth_rate = sum(growth_rates) / len(growth_rates) if growth_rates else 0.0
            
            result = {
                "growth_rate": round(avg_growth_rate, 2),
                "metric": metric,
                "period_months": period_months,
                "months_analyzed": len(sorted_months),
                "monthly_values": [
                    {"month": month, "value": round(value, 2)}
                    for month, value in sorted_months
                ],
                "trend": "increasing" if avg_growth_rate > 0 else "decreasing"
            }
            
            logger.debug(
                f"Calculated growth rate",
                extra={"growth_rate": result["growth_rate"], "metric": metric}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating growth rate: {e}", exc_info=True)
            return {
                "error": str(e),
                "growth_rate": 0.0
            }
    
    @staticmethod
    def calculate_financial_health_score(
        current_balance: float,
        monthly_burn_rate: float,
        revenue_growth_rate: float,
        expense_growth_rate: float
    ) -> Dict[str, Any]:
        """
        Calculate an overall financial health score (0-100).
        
        Args:
            current_balance: Current cash balance
            monthly_burn_rate: Monthly burn rate
            revenue_growth_rate: Month-over-month revenue growth %
            expense_growth_rate: Month-over-month expense growth %
            
        Returns:
            Dictionary with health score and breakdown
        """
        try:
            score = 0
            factors = {}
            
            # Factor 1: Runway (max 40 points)
            if monthly_burn_rate > 0:
                runway_months = current_balance / monthly_burn_rate
                if runway_months >= 18:
                    runway_score = 40
                elif runway_months >= 12:
                    runway_score = 35
                elif runway_months >= 6:
                    runway_score = 25
                elif runway_months >= 3:
                    runway_score = 15
                else:
                    runway_score = 5
            else:
                runway_score = 40  # Positive cash flow
            
            factors["runway_score"] = runway_score
            score += runway_score
            
            # Factor 2: Revenue Growth (max 30 points)
            if revenue_growth_rate >= 20:
                revenue_score = 30
            elif revenue_growth_rate >= 10:
                revenue_score = 25
            elif revenue_growth_rate >= 0:
                revenue_score = 15
            else:
                revenue_score = 5
            
            factors["revenue_growth_score"] = revenue_score
            score += revenue_score
            
            # Factor 3: Expense Control (max 30 points)
            # Lower expense growth is better
            if expense_growth_rate < revenue_growth_rate:
                expense_score = 30  # Expenses growing slower than revenue
            elif expense_growth_rate < 5:
                expense_score = 25
            elif expense_growth_rate < 15:
                expense_score = 20
            elif expense_growth_rate < 30:
                expense_score = 10
            else:
                expense_score = 5
            
            factors["expense_control_score"] = expense_score
            score += expense_score
            
            # Determine rating
            if score >= 80:
                rating = "Excellent"
            elif score >= 60:
                rating = "Good"
            elif score >= 40:
                rating = "Fair"
            elif score >= 20:
                rating = "Poor"
            else:
                rating = "Critical"
            
            result = {
                "health_score": score,
                "rating": rating,
                "factors": factors,
                "recommendations": FinancialCalculator._get_recommendations(
                    runway_score, revenue_score, expense_score
                )
            }
            
            logger.debug(
                f"Calculated financial health score",
                extra={"score": score, "rating": rating}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}", exc_info=True)
            return {
                "error": str(e),
                "health_score": 0
            }
    
    @staticmethod
    def _get_recommendations(
        runway_score: int,
        revenue_score: int,
        expense_score: int
    ) -> List[str]:
        """Get recommendations based on scores."""
        recommendations = []
        
        if runway_score < 20:
            recommendations.append("URGENT: Extend runway by reducing expenses or raising capital")
        elif runway_score < 30:
            recommendations.append("Focus on extending runway to at least 12 months")
        
        if revenue_score < 15:
            recommendations.append("Prioritize revenue growth strategies")
        
        if expense_score < 20:
            recommendations.append("Control expense growth - expenses growing too fast")
        
        if not recommendations:
            recommendations.append("Maintain current trajectory")
        
        return recommendations


# Global instance
financial_calculator = FinancialCalculator()

