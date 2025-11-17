"""Chart data generation tools for frontend visualization."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


class ChartGenerator:
    """
    Chart generator tool for creating visualization-ready data.
    
    Generates data structures for:
    - Time-series charts (burn rate, balance over time)
    - Category breakdown (pie/bar charts)
    - Forecast projections
    - Trend analysis
    """
    
    @staticmethod
    def generate_burn_rate_chart(
        transactions: List[Dict[str, Any]],
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Generate monthly burn rate chart data.
        
        Args:
            transactions: List of transaction dictionaries
            months: Number of months to include
            
        Returns:
            Chart data dictionary
        """
        try:
            # Filter to date range
            cutoff_date = datetime.utcnow() - timedelta(days=months * 30)
            recent_transactions = [
                t for t in transactions
                if datetime.fromisoformat(t["date"].replace("Z", "+00:00")) >= cutoff_date
            ]
            
            # Group by month
            monthly_data = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})
            
            for transaction in recent_transactions:
                date = datetime.fromisoformat(transaction["date"].replace("Z", "+00:00"))
                month_key = date.strftime("%Y-%m")
                amount = float(transaction["amount"])
                
                if transaction["type"] == "income":
                    monthly_data[month_key]["income"] += amount
                else:
                    monthly_data[month_key]["expenses"] += amount
            
            # Sort by month and calculate burn rate
            sorted_months = sorted(monthly_data.items())
            
            chart_data = []
            for month, data in sorted_months:
                burn_rate = data["expenses"] - data["income"]
                chart_data.append({
                    "month": month,
                    "month_label": datetime.strptime(month, "%Y-%m").strftime("%b %Y"),
                    "income": round(data["income"], 2),
                    "expenses": round(data["expenses"], 2),
                    "burn_rate": round(burn_rate, 2),
                    "net_cash_flow": round(-burn_rate, 2)
                })
            
            result = {
                "type": "burn_rate_chart",
                "data": chart_data,
                "months": len(chart_data),
                "period": f"{months} months"
            }
            
            logger.debug(f"Generated burn rate chart with {len(chart_data)} data points")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating burn rate chart: {e}", exc_info=True)
            return {
                "type": "burn_rate_chart",
                "data": [],
                "error": str(e)
            }
    
    @staticmethod
    def generate_category_breakdown_chart(
        transactions: List[Dict[str, Any]],
        transaction_type: str = "expense",
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Generate category breakdown chart data (for pie/bar charts).
        
        Args:
            transactions: List of transaction dictionaries
            transaction_type: "income" or "expense"
            top_n: Number of top categories to show
            
        Returns:
            Chart data dictionary
        """
        try:
            # Filter by type
            filtered_transactions = [
                t for t in transactions
                if t["type"] == transaction_type
            ]
            
            # Group by category
            category_totals = defaultdict(float)
            for transaction in filtered_transactions:
                category = transaction.get("category", "Uncategorized")
                category_totals[category] += float(transaction["amount"])
            
            # Sort and take top N
            sorted_categories = sorted(
                category_totals.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            top_categories = sorted_categories[:top_n]
            
            # Calculate total and percentages
            total = sum(amount for _, amount in top_categories)
            
            chart_data = []
            for category, amount in top_categories:
                percentage = (amount / total * 100) if total > 0 else 0
                chart_data.append({
                    "category": category,
                    "amount": round(amount, 2),
                    "percentage": round(percentage, 2)
                })
            
            # Add "Other" category if needed
            if len(sorted_categories) > top_n:
                other_amount = sum(
                    amount for _, amount in sorted_categories[top_n:]
                )
                other_percentage = (other_amount / (total + other_amount) * 100)
                chart_data.append({
                    "category": "Other",
                    "amount": round(other_amount, 2),
                    "percentage": round(other_percentage, 2)
                })
            
            result = {
                "type": "category_breakdown_chart",
                "transaction_type": transaction_type,
                "data": chart_data,
                "total": round(total, 2),
                "category_count": len(category_totals)
            }
            
            logger.debug(
                f"Generated category breakdown chart: {len(chart_data)} categories",
                extra={"transaction_type": transaction_type, "total": total}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating category chart: {e}", exc_info=True)
            return {
                "type": "category_breakdown_chart",
                "data": [],
                "error": str(e)
            }
    
    @staticmethod
    def generate_runway_forecast_chart(
        current_balance: float,
        monthly_burn_rate: float,
        forecast_months: int = 12
    ) -> Dict[str, Any]:
        """
        Generate runway forecast chart showing projected balance over time.
        
        Args:
            current_balance: Current cash balance
            monthly_burn_rate: Monthly burn rate
            forecast_months: Number of months to forecast
            
        Returns:
            Chart data dictionary
        """
        try:
            chart_data = []
            balance = current_balance
            current_date = datetime.utcnow()
            
            for month in range(forecast_months + 1):
                forecast_date = current_date + relativedelta(months=month)
                
                chart_data.append({
                    "month": forecast_date.strftime("%Y-%m"),
                    "month_label": forecast_date.strftime("%b %Y"),
                    "balance": round(max(0, balance), 2),
                    "is_projected": month > 0,
                    "is_depleted": balance <= 0
                })
                
                # Calculate next month's balance
                balance -= monthly_burn_rate
            
            # Find depletion point
            depletion_month = None
            for i, point in enumerate(chart_data):
                if point["is_depleted"] and depletion_month is None:
                    depletion_month = i
                    break
            
            result = {
                "type": "runway_forecast_chart",
                "data": chart_data,
                "current_balance": round(current_balance, 2),
                "monthly_burn_rate": round(monthly_burn_rate, 2),
                "forecast_months": forecast_months,
                "depletion_month": depletion_month
            }
            
            logger.debug(
                f"Generated runway forecast chart: {forecast_months} months",
                extra={"depletion_month": depletion_month}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating runway forecast chart: {e}", exc_info=True)
            return {
                "type": "runway_forecast_chart",
                "data": [],
                "error": str(e)
            }
    
    @staticmethod
    def generate_balance_history_chart(
        initial_capital: float,
        transactions: List[Dict[str, Any]],
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Generate balance over time chart.
        
        Args:
            initial_capital: Starting capital
            transactions: List of transaction dictionaries
            months: Number of months to include
            
        Returns:
            Chart data dictionary
        """
        try:
            # Filter and sort transactions
            cutoff_date = datetime.utcnow() - timedelta(days=months * 30)
            transactions = [
                t for t in transactions
                if datetime.fromisoformat(t["date"].replace("Z", "+00:00")) >= cutoff_date
            ]
            transactions.sort(key=lambda t: t["date"])
            
            # Calculate cumulative balance by month
            monthly_balance = defaultdict(float)
            balance = initial_capital
            
            for transaction in transactions:
                date = datetime.fromisoformat(transaction["date"].replace("Z", "+00:00"))
                month_key = date.strftime("%Y-%m")
                amount = float(transaction["amount"])
                
                if transaction["type"] == "income":
                    balance += amount
                else:
                    balance -= amount
                
                # Store the end-of-month balance (will be overwritten)
                monthly_balance[month_key] = balance
            
            # Generate chart data
            sorted_months = sorted(monthly_balance.items())
            
            chart_data = []
            for month, balance in sorted_months:
                chart_data.append({
                    "month": month,
                    "month_label": datetime.strptime(month, "%Y-%m").strftime("%b %Y"),
                    "balance": round(balance, 2),
                    "is_positive": balance > 0
                })
            
            result = {
                "type": "balance_history_chart",
                "data": chart_data,
                "initial_capital": round(initial_capital, 2),
                "final_balance": round(balance, 2),
                "months": len(chart_data)
            }
            
            logger.debug(
                f"Generated balance history chart: {len(chart_data)} data points",
                extra={"final_balance": balance}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating balance history chart: {e}", exc_info=True)
            return {
                "type": "balance_history_chart",
                "data": [],
                "error": str(e)
            }
    
    @staticmethod
    def generate_trend_chart(
        transactions: List[Dict[str, Any]],
        metric: str = "income",
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Generate trend chart for income or expenses.
        
        Args:
            transactions: List of transaction dictionaries
            metric: "income" or "expenses"
            months: Number of months to include
            
        Returns:
            Chart data dictionary
        """
        try:
            # Filter transactions
            cutoff_date = datetime.utcnow() - timedelta(days=months * 30)
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
            
            # Sort and create chart data
            sorted_months = sorted(monthly_totals.items())
            
            chart_data = []
            previous_value = None
            
            for month, value in sorted_months:
                growth_rate = None
                if previous_value and previous_value > 0:
                    growth_rate = ((value - previous_value) / previous_value) * 100
                
                chart_data.append({
                    "month": month,
                    "month_label": datetime.strptime(month, "%Y-%m").strftime("%b %Y"),
                    "value": round(value, 2),
                    "growth_rate": round(growth_rate, 2) if growth_rate is not None else None
                })
                
                previous_value = value
            
            # Calculate overall trend
            if len(chart_data) >= 2:
                first_value = chart_data[0]["value"]
                last_value = chart_data[-1]["value"]
                overall_growth = (
                    ((last_value - first_value) / first_value * 100)
                    if first_value > 0 else 0
                )
            else:
                overall_growth = 0
            
            result = {
                "type": "trend_chart",
                "metric": metric,
                "data": chart_data,
                "overall_growth_rate": round(overall_growth, 2),
                "months": len(chart_data)
            }
            
            logger.debug(
                f"Generated trend chart for {metric}: {len(chart_data)} data points",
                extra={"overall_growth": overall_growth}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating trend chart: {e}", exc_info=True)
            return {
                "type": "trend_chart",
                "data": [],
                "error": str(e)
            }
    
    @staticmethod
    def generate_combined_dashboard_data(
        initial_capital: float,
        transactions: List[Dict[str, Any]],
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Generate all chart data for a complete dashboard.
        
        Args:
            initial_capital: Starting capital
            transactions: List of transaction dictionaries
            months: Number of months to include
            
        Returns:
            Dictionary with all chart data
        """
        try:
            result = {
                "burn_rate_chart": ChartGenerator.generate_burn_rate_chart(
                    transactions, months
                ),
                "expense_breakdown": ChartGenerator.generate_category_breakdown_chart(
                    transactions, "expense", 10
                ),
                "income_breakdown": ChartGenerator.generate_category_breakdown_chart(
                    transactions, "income", 10
                ),
                "balance_history": ChartGenerator.generate_balance_history_chart(
                    initial_capital, transactions, months
                ),
                "income_trend": ChartGenerator.generate_trend_chart(
                    transactions, "income", months
                ),
                "expense_trend": ChartGenerator.generate_trend_chart(
                    transactions, "expense", months
                )
            }
            
            logger.info(f"Generated combined dashboard data for {months} months")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating combined dashboard data: {e}", exc_info=True)
            return {
                "error": str(e)
            }


# Global instance
chart_generator = ChartGenerator()

