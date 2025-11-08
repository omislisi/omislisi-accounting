"""Tests for analysis and reporting."""

import pytest

from omislisi_accounting.analysis.reporter import (
    generate_summary,
    generate_category_breakdown,
)


def test_generate_summary_empty():
    """Test summary generation with empty transactions."""
    summary = generate_summary([])
    assert summary['total_income'] == 0.0
    assert summary['total_expenses'] == 0.0
    assert summary['net'] == 0.0
    assert summary['transaction_count'] == 0


def test_generate_summary():
    """Test summary generation with transactions."""
    transactions = [
        {'type': 'income', 'amount': 1000.0, 'date': '2025-10-01'},
        {'type': 'income', 'amount': 500.0, 'date': '2025-10-02'},
        {'type': 'expense', 'amount': -200.0, 'date': '2025-10-03'},
        {'type': 'expense', 'amount': -150.0, 'date': '2025-10-04'},
    ]

    summary = generate_summary(transactions)
    assert summary['total_income'] == 1500.0
    assert summary['total_expenses'] == 350.0
    assert summary['net'] == 1150.0
    assert summary['transaction_count'] == 4
    assert summary['income_count'] == 2
    assert summary['expense_count'] == 2


def test_generate_category_breakdown():
    """Test category breakdown generation."""
    transactions = [
        {'type': 'income', 'amount': 1000.0, 'category': 'sales'},
        {'type': 'expense', 'amount': -200.0, 'category': 'office'},
        {'type': 'expense', 'amount': -150.0, 'category': 'office'},
        {'type': 'expense', 'amount': -100.0, 'category': 'software'},
    ]

    breakdown = generate_category_breakdown(transactions)

    assert 'sales' in breakdown
    assert breakdown['sales']['total'] == 1000.0
    assert breakdown['sales']['count'] == 1

    assert 'office' in breakdown
    assert breakdown['office']['total'] == -350.0
    assert breakdown['office']['count'] == 2

    assert 'software' in breakdown
    assert breakdown['software']['total'] == -100.0
    assert breakdown['software']['count'] == 1


def test_generate_category_breakdown_empty():
    """Test category breakdown with empty transactions."""
    breakdown = generate_category_breakdown([])
    assert breakdown == {}

