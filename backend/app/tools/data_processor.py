"""Data processing tools for CSV parsing and validation."""

import logging
import csv
import io
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Data processor tool for parsing and validating transaction data.
    
    Provides functionality for:
    - CSV file parsing
    - Data validation and cleaning
    - Batch import preparation
    - Date parsing and normalization
    - Amount validation
    """
    
    # Expected CSV columns
    REQUIRED_COLUMNS = ["date", "amount", "category", "type"]
    OPTIONAL_COLUMNS = ["description"]
    VALID_TYPES = ["income", "expense"]
    
    @staticmethod
    def parse_csv(
        csv_content: str,
        company_id: int
    ) -> Dict[str, Any]:
        """
        Parse CSV content and validate transaction data.
        
        Expected CSV format:
        date,amount,category,type,description
        2024-01-15,1500.00,Salaries,expense,Employee payroll
        
        Args:
            csv_content: CSV file content as string
            company_id: ID of the company
            
        Returns:
            Dictionary with parsed transactions and validation results
        """
        try:
            logger.info(f"Parsing CSV for company {company_id}")
            
            # Parse CSV
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            # Validate headers
            if not reader.fieldnames:
                return {
                    "success": False,
                    "error": "CSV file is empty or has no headers",
                    "transactions": []
                }
            
            missing_cols = set(DataProcessor.REQUIRED_COLUMNS) - set(reader.fieldnames)
            if missing_cols:
                return {
                    "success": False,
                    "error": f"Missing required columns: {', '.join(missing_cols)}",
                    "transactions": []
                }
            
            # Process rows
            transactions = []
            errors = []
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                result = DataProcessor._validate_transaction_row(
                    row,
                    company_id,
                    row_num
                )
                
                if result["valid"]:
                    transactions.append(result["transaction"])
                else:
                    errors.append({
                        "row": row_num,
                        "error": result["error"],
                        "data": row
                    })
            
            success = len(transactions) > 0
            
            result = {
                "success": success,
                "transactions": transactions,
                "total_rows": len(transactions) + len(errors),
                "valid_rows": len(transactions),
                "invalid_rows": len(errors),
                "errors": errors
            }
            
            logger.info(
                f"Parsed CSV: {len(transactions)} valid, {len(errors)} invalid",
                extra={
                    "company_id": company_id,
                    "valid_count": len(transactions),
                    "error_count": len(errors)
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to parse CSV: {str(e)}",
                "transactions": []
            }
    
    @staticmethod
    def _validate_transaction_row(
        row: Dict[str, str],
        company_id: int,
        row_num: int
    ) -> Dict[str, Any]:
        """
        Validate a single transaction row.
        
        Args:
            row: CSV row as dictionary
            company_id: Company ID
            row_num: Row number for error reporting
            
        Returns:
            Dictionary with validation result
        """
        try:
            # Validate and parse date
            date_result = DataProcessor.parse_date(row["date"])
            if not date_result["valid"]:
                return {
                    "valid": False,
                    "error": f"Invalid date: {date_result['error']}"
                }
            
            # Validate and parse amount
            amount_result = DataProcessor.validate_amount(row["amount"])
            if not amount_result["valid"]:
                return {
                    "valid": False,
                    "error": f"Invalid amount: {amount_result['error']}"
                }
            
            # Validate type
            transaction_type = row["type"].strip().lower()
            if transaction_type not in DataProcessor.VALID_TYPES:
                return {
                    "valid": False,
                    "error": f"Invalid type: must be 'income' or 'expense', got '{transaction_type}'"
                }
            
            # Validate category (not empty)
            category = row["category"].strip()
            if not category:
                return {
                    "valid": False,
                    "error": "Category cannot be empty"
                }
            
            # Build transaction object
            transaction = {
                "company_id": company_id,
                "date": date_result["date"].isoformat(),
                "amount": amount_result["amount"],
                "category": category,
                "type": transaction_type,
                "description": row.get("description", "").strip()
            }
            
            return {
                "valid": True,
                "transaction": transaction
            }
            
        except KeyError as e:
            return {
                "valid": False,
                "error": f"Missing required field: {e}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    @staticmethod
    def parse_date(date_str: str) -> Dict[str, Any]:
        """
        Parse date string to datetime object.
        
        Supports formats:
        - YYYY-MM-DD
        - MM/DD/YYYY
        - DD-MM-YYYY
        
        Args:
            date_str: Date string
            
        Returns:
            Dictionary with parsed date or error
        """
        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%d/%m/%Y"
        ]
        
        date_str = date_str.strip()
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return {
                    "valid": True,
                    "date": parsed_date,
                    "format": fmt
                }
            except ValueError:
                continue
        
        return {
            "valid": False,
            "error": f"Could not parse date '{date_str}'. Expected formats: YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY"
        }
    
    @staticmethod
    def validate_amount(amount_str: str) -> Dict[str, Any]:
        """
        Validate and parse amount string.
        
        Args:
            amount_str: Amount string (e.g., "1500.00", "$1,500.00")
            
        Returns:
            Dictionary with parsed amount or error
        """
        try:
            # Clean the amount string
            cleaned = amount_str.strip()
            cleaned = cleaned.replace("$", "")
            cleaned = cleaned.replace(",", "")
            cleaned = cleaned.replace(" ", "")
            
            # Parse to Decimal for precision
            amount = Decimal(cleaned)
            
            # Validate positive
            if amount < 0:
                return {
                    "valid": False,
                    "error": "Amount must be positive (use 'type' field to indicate income/expense)"
                }
            
            # Validate reasonable range
            if amount > Decimal("999999999.99"):
                return {
                    "valid": False,
                    "error": "Amount exceeds maximum value"
                }
            
            return {
                "valid": True,
                "amount": float(amount)
            }
            
        except (InvalidOperation, ValueError) as e:
            return {
                "valid": False,
                "error": f"Invalid number format: {str(e)}"
            }
    
    @staticmethod
    def clean_transactions(
        transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Clean and normalize transaction data.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Cleaned transaction list
        """
        cleaned = []
        
        for transaction in transactions:
            cleaned_transaction = {
                "company_id": transaction["company_id"],
                "date": transaction["date"],
                "amount": round(float(transaction["amount"]), 2),
                "category": transaction["category"].strip().title(),
                "type": transaction["type"].lower(),
                "description": transaction.get("description", "").strip()
            }
            cleaned.append(cleaned_transaction)
        
        logger.debug(f"Cleaned {len(cleaned)} transactions")
        
        return cleaned
    
    @staticmethod
    def validate_batch(
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate a batch of transactions for consistency.
        
        Checks:
        - All transactions have required fields
        - Date ranges are reasonable
        - No duplicate transactions
        - Categories are consistent
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Validation result dictionary
        """
        try:
            if not transactions:
                return {
                    "valid": False,
                    "error": "No transactions to validate"
                }
            
            issues = []
            warnings = []
            
            # Check for required fields
            for i, transaction in enumerate(transactions):
                missing = [
                    field for field in ["company_id", "date", "amount", "category", "type"]
                    if field not in transaction
                ]
                if missing:
                    issues.append(f"Transaction {i}: Missing fields {missing}")
            
            # Check date ranges
            dates = [
                datetime.fromisoformat(t["date"])
                for t in transactions
                if "date" in t
            ]
            
            if dates:
                oldest = min(dates)
                newest = max(dates)
                date_range_days = (newest - oldest).days
                
                if date_range_days > 1825:  # 5 years
                    warnings.append(f"Transaction date range spans {date_range_days} days (>5 years)")
            
            # Check for potential duplicates
            transaction_keys = []
            for transaction in transactions:
                if all(k in transaction for k in ["date", "amount", "category"]):
                    key = f"{transaction['date']}_{transaction['amount']}_{transaction['category']}"
                    if key in transaction_keys:
                        warnings.append(f"Potential duplicate: {key}")
                    transaction_keys.append(key)
            
            # Check categories
            categories = set(t.get("category") for t in transactions if t.get("category"))
            if len(categories) > 50:
                warnings.append(f"Large number of categories ({len(categories)}) - consider consolidating")
            
            valid = len(issues) == 0
            
            result = {
                "valid": valid,
                "transaction_count": len(transactions),
                "issues": issues,
                "warnings": warnings,
                "categories": list(categories),
                "date_range": {
                    "oldest": oldest.isoformat() if dates else None,
                    "newest": newest.isoformat() if dates else None,
                    "days": date_range_days if dates else 0
                }
            }
            
            logger.info(
                f"Validated batch: {len(transactions)} transactions",
                extra={
                    "valid": valid,
                    "issues": len(issues),
                    "warnings": len(warnings)
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating batch: {e}", exc_info=True)
            return {
                "valid": False,
                "error": f"Validation failed: {str(e)}"
            }
    
    @staticmethod
    def generate_summary_statistics(
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics for a set of transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Summary statistics dictionary
        """
        try:
            if not transactions:
                return {
                    "count": 0,
                    "total_income": 0.0,
                    "total_expenses": 0.0,
                    "net": 0.0
                }
            
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
            
            categories = set(t["category"] for t in transactions)
            
            dates = [
                datetime.fromisoformat(t["date"])
                for t in transactions
            ]
            
            return {
                "count": len(transactions),
                "total_income": round(total_income, 2),
                "total_expenses": round(total_expenses, 2),
                "net": round(total_income - total_expenses, 2),
                "unique_categories": len(categories),
                "categories": list(categories),
                "date_range": {
                    "start": min(dates).isoformat() if dates else None,
                    "end": max(dates).isoformat() if dates else None
                },
                "avg_transaction_size": round(
                    (total_income + total_expenses) / len(transactions), 2
                )
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}", exc_info=True)
            return {
                "count": 0,
                "error": str(e)
            }


# Global instance
data_processor = DataProcessor()

