"""Tests for dashboard data collection."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from omislisi_accounting.analysis.dashboard_data import (
    collect_dashboard_data,
    get_current_month_data,
    get_ytd_data,
    get_last_12_months_data,
    get_year_comparison_data,
    get_monthly_trends,
    get_category_trends,
    get_counterparty_trends,
    get_all_categories_and_tags,
)


@pytest.fixture
def sample_transactions():
    """Create sample transactions for testing."""
    return [
        {
            'date': '2025-01-15',
            'amount': 1000.0,
            'type': 'income',
            'description': 'Payment from client',
            'counterparty': 'Client A',
            'category': 'sales',
            'account': 'SI123456789',
        },
        {
            'date': '2025-01-20',
            'amount': -200.0,
            'type': 'expense',
            'description': 'Office supplies',
            'counterparty': 'Office Store',
            'category': 'office',
            'account': 'SI987654321',
        },
        {
            'date': '2025-02-10',
            'amount': 1500.0,
            'type': 'income',
            'description': 'Large payment',
            'counterparty': 'Client B',
            'category': 'large_deals',
            'account': 'SI123456789',
        },
        {
            'date': '2025-02-15',
            'amount': -150.0,
            'type': 'expense',
            'description': 'Software license',
            'counterparty': 'Software Inc',
            'category': 'software',
            'account': 'SI987654321',
        },
        {
            'date': '2024-12-20',
            'amount': 800.0,
            'type': 'income',
            'description': 'Previous year payment',
            'counterparty': 'Client C',
            'category': 'sales',
            'account': 'SI123456789',
        },
    ]


@pytest.fixture
def transactions_with_tags():
    """Create transactions with category tags."""
    return [
        {
            'date': '2025-01-15',
            'amount': -500.0,
            'type': 'expense',
            'description': 'Salary payment',
            'counterparty': 'Employee A',
            'category': 'salary:founders',
            'account': 'SI111111111',
        },
        {
            'date': '2025-01-20',
            'amount': -300.0,
            'type': 'expense',
            'description': 'Salary payment',
            'counterparty': 'Employee B',
            'category': 'salary:employees',
            'account': 'SI111111111',
        },
        {
            'date': '2025-02-10',
            'amount': -400.0,
            'type': 'expense',
            'description': 'Salary payment',
            'counterparty': 'Employee A',
            'category': 'salary:founders',
            'account': 'SI111111111',
        },
    ]


def test_get_current_month_data(sample_transactions):
    """Test get_current_month_data function."""
    result = get_current_month_data(sample_transactions, 2025, 1)

    assert result['period'] == '2025-01'
    assert result['summary']['total_income'] == 1000.0
    assert result['summary']['total_expenses'] == 200.0
    assert result['summary']['net'] == 800.0
    assert result['summary']['transaction_count'] == 2
    assert 'office' in result['breakdown']
    assert 'sales' in result['breakdown']
    assert result['comparison']['previous_month'] == '2024-12'


def test_get_current_month_data_no_previous_month(sample_transactions):
    """Test get_current_month_data when there's no previous month data."""
    # Only January transactions
    jan_transactions = [tx for tx in sample_transactions if tx['date'].startswith('2025-01')]
    result = get_current_month_data(jan_transactions, 2025, 1)

    assert result['period'] == '2025-01'
    # Should still calculate comparison (will be 0 if no previous month)
    assert 'comparison' in result


def test_get_current_month_data_january_wraps_to_previous_year(sample_transactions):
    """Test that January correctly compares to December of previous year."""
    result = get_current_month_data(sample_transactions, 2025, 1)

    # Should compare to 2024-12
    assert result['comparison']['previous_month'] == '2024-12'
    # Should have comparison values calculated
    assert 'income_change' in result['comparison']


def test_get_ytd_data(sample_transactions):
    """Test get_ytd_data function."""
    result = get_ytd_data(sample_transactions, 2025)

    assert result['period'] == '2025'
    assert result['summary']['total_income'] == 2500.0
    assert result['summary']['total_expenses'] == 350.0
    assert result['summary']['net'] == 2150.0
    assert '2025-01' in result['monthly_progression']
    assert '2025-02' in result['monthly_progression']
    assert 'projections' in result
    assert 'projected_income' in result['projections']


def test_get_ytd_data_empty_year():
    """Test get_ytd_data with no transactions for the year."""
    result = get_ytd_data([], 2025)

    assert result['period'] == '2025'
    assert result['summary']['total_income'] == 0.0
    assert result['summary']['total_expenses'] == 0.0
    assert result['summary']['net'] == 0.0
    assert result['monthly_progression'] == {}


def test_get_last_12_months_data(sample_transactions):
    """Test get_last_12_months_data function."""
    end_date = datetime(2025, 2, 28)
    result = get_last_12_months_data(sample_transactions, end_date)

    assert 'period' in result
    assert 'months' in result
    assert 'summary' in result
    assert result['summary']['total_income'] > 0
    assert result['summary']['total_expenses'] > 0
    assert '2025-01' in result['months'] or '2025-02' in result['months']


def test_get_last_12_months_data_empty():
    """Test get_last_12_months_data with empty transactions."""
    end_date = datetime(2025, 2, 28)
    result = get_last_12_months_data([], end_date)

    assert 'period' in result
    assert 'months' in result
    assert result['summary']['total_income'] == 0.0
    assert result['summary']['total_expenses'] == 0.0


def test_get_year_comparison_data(sample_transactions):
    """Test get_year_comparison_data function."""
    result = get_year_comparison_data(sample_transactions, 2025, 2024)

    assert result['current_year'] == '2025'
    assert result['previous_year'] == '2024'
    assert 'current_summary' in result
    assert 'previous_summary' in result
    assert 'changes' in result
    assert 'income_change' in result['changes']
    assert 'expense_change' in result['changes']
    assert 'net_change' in result['changes']
    assert 'monthly_comparison' in result


def test_get_year_comparison_data_no_previous_year(sample_transactions):
    """Test get_year_comparison_data when previous year has no data."""
    # Only 2025 transactions
    current_year_tx = [tx for tx in sample_transactions if tx['date'].startswith('2025')]
    result = get_year_comparison_data(current_year_tx, 2025, 2024)

    assert result['current_year'] == '2025'
    assert result['previous_year'] == '2024'
    # Should still have structure even if previous year is empty
    assert result['previous_summary']['total_income'] == 0.0


def test_get_monthly_trends(sample_transactions):
    """Test get_monthly_trends function."""
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 2, 28)
    result = get_monthly_trends(sample_transactions, start_date, end_date)

    assert '2025-01' in result
    assert '2025-02' in result
    assert result['2025-01']['total_income'] == 1000.0
    assert result['2025-02']['total_income'] == 1500.0


def test_get_monthly_trends_empty_range(sample_transactions):
    """Test get_monthly_trends with no transactions in range."""
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 2, 28)
    result = get_monthly_trends(sample_transactions, start_date, end_date)

    assert result == {}


def test_get_category_trends(sample_transactions):
    """Test get_category_trends function."""
    result = get_category_trends(sample_transactions, 'sales')

    assert '2025-01' in result
    assert result['2025-01']['total'] == 1000.0
    assert result['2025-01']['count'] == 1


def test_get_category_trends_with_tag(transactions_with_tags):
    """Test get_category_trends with category tag."""
    result = get_category_trends(transactions_with_tags, 'salary', tag='founders')

    assert '2025-01' in result
    assert '2025-02' in result
    assert result['2025-01']['total'] == -500.0
    assert result['2025-02']['total'] == -400.0
    assert result['2025-01']['count'] == 1
    assert result['2025-02']['count'] == 1


def test_get_category_trends_base_category_with_tags(transactions_with_tags):
    """Test get_category_trends for base category when tags exist."""
    result = get_category_trends(transactions_with_tags, 'salary')

    # Should include all tags
    assert '2025-01' in result
    assert '2025-02' in result
    # Total should include both founders and employees
    assert result['2025-01']['total'] == -800.0  # -500 (founders) + -300 (employees)
    assert result['2025-01']['count'] == 2


def test_get_category_trends_nonexistent_category(sample_transactions):
    """Test get_category_trends with category that doesn't exist."""
    result = get_category_trends(sample_transactions, 'nonexistent')

    # Should return empty data for all months
    assert len(result) > 0
    for month_data in result.values():
        assert month_data['total'] == 0
        assert month_data['count'] == 0


def test_get_counterparty_trends(sample_transactions):
    """Test get_counterparty_trends function."""
    result = get_counterparty_trends(sample_transactions, 'Client A')

    assert '2025-01' in result
    assert result['2025-01']['total'] == 1000.0
    assert result['2025-01']['count'] == 1


def test_get_counterparty_trends_normalized(sample_transactions):
    """Test that counterparty trends use normalized names."""
    # Add transaction with slightly different counterparty name
    transactions = sample_transactions + [{
        'date': '2025-03-10',
        'amount': 500.0,
        'type': 'income',
        'description': 'Payment',
        'counterparty': 'CLIENT A',  # Different case
        'category': 'sales',
        'account': 'SI123456789',
    }]

    result = get_counterparty_trends(transactions, 'Client A')

    # Should match both 'Client A' and 'CLIENT A' due to normalization
    assert '2025-01' in result
    assert '2025-03' in result
    assert result['2025-01']['total'] == 1000.0
    assert result['2025-03']['total'] == 500.0


def test_get_counterparty_trends_nonexistent(sample_transactions):
    """Test get_counterparty_trends with counterparty that doesn't exist."""
    result = get_counterparty_trends(sample_transactions, 'Nonexistent Company')

    # Should return empty data for all months
    assert len(result) > 0
    for month_data in result.values():
        assert month_data['total'] == 0
        assert month_data['count'] == 0


def test_get_all_categories_and_tags(sample_transactions, transactions_with_tags):
    """Test get_all_categories_and_tags function."""
    all_tx = sample_transactions + transactions_with_tags
    result = get_all_categories_and_tags(all_tx)

    assert 'sales' in result
    assert 'office' in result
    assert 'software' in result
    assert 'salary' in result
    assert 'founders' in result['salary']['tags']
    assert 'employees' in result['salary']['tags']
    assert isinstance(result['salary']['tags'], list)


def test_get_all_categories_and_tags_no_tags(sample_transactions):
    """Test get_all_categories_and_tags with transactions without tags."""
    result = get_all_categories_and_tags(sample_transactions)

    assert 'sales' in result
    assert 'office' in result
    # Categories without tags should have empty tags list
    assert result['sales']['tags'] == []


def test_get_all_categories_and_tags_empty():
    """Test get_all_categories_and_tags with empty transactions."""
    result = get_all_categories_and_tags([])

    assert result == {}


def test_collect_dashboard_data_empty_reports_path(tmp_dir, monkeypatch):
    """Test collect_dashboard_data with empty reports directory."""
    # Mock the file finding functions to return empty lists
    from omislisi_accounting.parsers.zip_handler import get_all_transaction_files
    from omislisi_accounting.parsers.parser_factory import parse_all_files

    def mock_get_files(path):
        return []

    monkeypatch.setattr('omislisi_accounting.analysis.dashboard_data.get_all_transaction_files', mock_get_files)

    result = collect_dashboard_data(tmp_dir, 2025)

    assert 'metadata' in result
    assert result['metadata']['current_year'] == 2025
    assert result['metadata']['total_transactions'] == 0
    assert result['ytd']['summary']['total_income'] == 0.0


def test_collect_dashboard_data_with_selected_month(tmp_dir, monkeypatch, sample_transactions):
    """Test collect_dashboard_data with selected_month parameter."""
    from omislisi_accounting.parsers.zip_handler import get_all_transaction_files
    from omislisi_accounting.parsers.parser_factory import parse_all_files

    def mock_get_files(path):
        return []

    def mock_parse_files(files, silent=False):
        return sample_transactions

    monkeypatch.setattr('omislisi_accounting.analysis.dashboard_data.get_all_transaction_files', mock_get_files)
    monkeypatch.setattr('omislisi_accounting.analysis.dashboard_data.parse_all_files', mock_parse_files)

    selected_month = datetime(2025, 2, 1)
    result = collect_dashboard_data(tmp_dir, 2025, selected_month=selected_month)

    assert result['metadata']['default_month'] == '2025-02'
    assert 'current_month' in result


def test_get_current_month_data_edge_cases():
    """Test get_current_month_data with edge cases."""
    # Empty transactions
    result = get_current_month_data([], 2025, 1)
    assert result['summary']['total_income'] == 0.0
    assert result['summary']['total_expenses'] == 0.0

    # Month with only income
    income_only = [{
        'date': '2025-01-15',
        'amount': 1000.0,
        'type': 'income',
        'description': 'Payment',
        'counterparty': 'Client',
        'category': 'sales',
    }]
    result = get_current_month_data(income_only, 2025, 1)
    assert result['summary']['total_income'] == 1000.0
    assert result['summary']['total_expenses'] == 0.0

    # Month with only expenses
    expense_only = [{
        'date': '2025-01-15',
        'amount': -500.0,
        'type': 'expense',
        'description': 'Purchase',
        'counterparty': 'Vendor',
        'category': 'office',
    }]
    result = get_current_month_data(expense_only, 2025, 1)
    assert result['summary']['total_income'] == 0.0
    assert result['summary']['total_expenses'] == 500.0

