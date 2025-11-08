"""Generate reports from transaction data."""

from typing import List, Dict, Any
from datetime import datetime
import pandas as pd


def generate_summary(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a summary of transactions.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Summary dictionary with totals, counts, etc.
    """
    if not transactions:
        return {
            "total_income": 0.0,
            "total_expenses": 0.0,
            "net": 0.0,
            "transaction_count": 0,
        }

    df = pd.DataFrame(transactions)

    income_df = df[df["type"] == "income"]
    expense_df = df[df["type"] == "expense"]

    # Sum amounts (pandas returns 0.0 for empty series)
    income = income_df["amount"].sum()
    # Expenses are stored as negative, so we take absolute value
    expenses = abs(expense_df["amount"].sum())

    return {
        "total_income": float(income),
        "total_expenses": float(expenses),
        "net": float(income - expenses),
        "transaction_count": len(transactions),
        "income_count": len(income_df),
        "expense_count": len(expense_df),
    }


def generate_category_breakdown(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Generate a breakdown by category.

    Supports tags in format "category:tag" - groups by base category but preserves tag info.

    Returns:
        Dictionary with category names as keys and totals as values
        For tagged categories (e.g., "salary:founders"), groups by base category ("salary")
        but includes tag breakdown in a nested structure
    """
    if not transactions:
        return {}

    df = pd.DataFrame(transactions)

    breakdown = {}
    tag_breakdown = {}  # For categories with tags

    for category in df["category"].unique():
        category_df = df[df["category"] == category]

        # Check if category has a tag (format: "category:tag")
        if ":" in category:
            base_category, tag = category.split(":", 1)

            # Initialize base category if not exists
            if base_category not in breakdown:
                breakdown[base_category] = {
                    "total": 0.0,
                    "count": 0,
                    "tags": {}
                }

            # Add to base category totals
            category_total = float(category_df["amount"].sum())
            breakdown[base_category]["total"] += category_total
            breakdown[base_category]["count"] += len(category_df)

            # Store tag breakdown
            if "tags" not in breakdown[base_category]:
                breakdown[base_category]["tags"] = {}
            breakdown[base_category]["tags"][tag] = {
                "total": category_total,
                "count": len(category_df),
            }
        else:
            # Regular category without tags
            breakdown[category] = {
                "total": float(category_df["amount"].sum()),
                "count": len(category_df),
            }

    return breakdown

