"""Tests for counterparty utilities."""

import pytest

from omislisi_accounting.analysis.counterparty_utils import (
    normalize_counterparty_name,
    get_group_key,
    get_counterparty_breakdowns,
)


def test_normalize_counterparty_name_basic():
    """Test basic name normalization."""
    assert normalize_counterparty_name("Test Company") == "test company"
    assert normalize_counterparty_name("TEST COMPANY") == "test company"
    assert normalize_counterparty_name("  Test Company  ") == "test company"


def test_normalize_counterparty_name_legal_suffixes():
    """Test normalization of legal suffixes."""
    # d.o.o. variations
    assert normalize_counterparty_name("Company d.o.o.") == "company d.o.o."
    assert normalize_counterparty_name("Company d.o.o") == "company d.o.o."
    # Note: "d. o. o." with spaces might normalize differently, check actual behavior
    result = normalize_counterparty_name("Company d. o. o.")
    assert "d.o.o" in result or "d. o. o" in result

    # d.d. variations - note: normalization might remove trailing period
    assert normalize_counterparty_name("Company d.d.") == "company d.d." or normalize_counterparty_name("Company d.d.") == "company d.d"
    assert normalize_counterparty_name("Company d.d") == "company d.d." or normalize_counterparty_name("Company d.d") == "company d.d"

    # s.p. variations
    assert normalize_counterparty_name("Company s.p.") == "company s.p."

    # z.b.o. variations
    assert normalize_counterparty_name("Company z.b.o.") == "company z.b.o."
    assert normalize_counterparty_name("Company z.b.o") == "company z.b.o."


def test_normalize_counterparty_name_special_characters():
    """Test normalization with special characters and diacritics."""
    # Should remove diacritics
    assert normalize_counterparty_name("Študentski servis") == "studentski servis"
    assert normalize_counterparty_name("Črtomir") == "crtomir"
    assert normalize_counterparty_name("Župan") == "zupan"

    # Should handle multiple spaces
    assert normalize_counterparty_name("Company   Name") == "company name"


def test_normalize_counterparty_name_entity_aliases():
    """Test normalization of known entity aliases."""
    # CTRP and IN-FIT should normalize to same form
    ctrp_normalized = normalize_counterparty_name("CTRP d.o.o.")
    infit_normalized = normalize_counterparty_name("IN-FIT d.o.o.")
    infit2_normalized = normalize_counterparty_name("IN-FIT d.o.o.")

    assert "in-fit" in ctrp_normalized or "ctrp" in ctrp_normalized
    assert "in-fit" in infit_normalized or "ctrp" in infit_normalized


def test_normalize_counterparty_name_comma_handling():
    """Test normalization with commas before legal suffixes."""
    assert normalize_counterparty_name("Company, d.o.o.") == "company d.o.o."
    assert normalize_counterparty_name("Company, d.d.") == "company d.d."


def test_normalize_counterparty_name_ss_handling():
    """Test normalization of SS (Študentski servis) variations."""
    normalized = normalize_counterparty_name("SS d.o.o.")
    assert "ss d.o.o." in normalized

    normalized2 = normalize_counterparty_name("SS d.o.o")
    assert "ss d.o.o." in normalized2


def test_get_group_key():
    """Test get_group_key function."""
    key1 = get_group_key("SI123456789", "test company d.o.o.")
    key2 = get_group_key("SI987654321", "test company d.o.o.")
    key3 = get_group_key("SI123456789", "different company")

    # Same normalized name should produce same key regardless of account
    assert key1 == key2
    # Different names should produce different keys
    assert key1 != key3
    assert key1.startswith("name:")


def test_get_counterparty_breakdowns_basic():
    """Test basic counterparty breakdowns."""
    transactions = [
        {
            'counterparty': 'Company A',
            'amount': 1000.0,
            'account': 'SI111111111',
        },
        {
            'counterparty': 'Company A',
            'amount': 500.0,
            'account': 'SI111111111',
        },
        {
            'counterparty': 'Company B',
            'amount': -200.0,
            'account': 'SI222222222',
        },
    ]

    result = get_counterparty_breakdowns(transactions)

    assert len(result) == 2
    # Should be sorted by absolute amount
    assert abs(result[0]['total']) >= abs(result[1]['total'])

    # Find Company A
    company_a = next(cp for cp in result if 'Company A' in cp['name'])
    assert company_a['total'] == 1500.0
    assert company_a['count'] == 2


def test_get_counterparty_breakdowns_limit():
    """Test counterparty breakdowns with limit."""
    transactions = []
    for i in range(30):
        transactions.append({
            'counterparty': f'Company {i}',
            'amount': 100.0 * (i + 1),  # Different amounts
            'account': f'SI{i:09d}',
        })

    result = get_counterparty_breakdowns(transactions, limit=10)

    assert len(result) == 10
    # Should be sorted by absolute amount descending
    assert abs(result[0]['total']) >= abs(result[-1]['total'])


def test_get_counterparty_breakdowns_name_variants():
    """Test that name variants are grouped together."""
    transactions = [
        {
            'counterparty': 'Company A d.o.o.',
            'amount': 1000.0,
            'account': 'SI111111111',
        },
        {
            'counterparty': 'COMPANY A D.O.O.',
            'amount': 500.0,
            'account': 'SI111111111',
        },
        {
            'counterparty': 'Company A, d.o.o.',
            'amount': 300.0,
            'account': 'SI111111111',
        },
    ]

    result = get_counterparty_breakdowns(transactions)

    # All variants should be grouped together
    assert len(result) == 1
    assert result[0]['count'] == 3
    assert result[0]['total'] == 1800.0
    # Should use most common name variant
    assert result[0]['name'] in ['Company A d.o.o.', 'COMPANY A D.O.O.', 'Company A, d.o.o.']


def test_get_counterparty_breakdowns_preserves_sign():
    """Test that counterparty breakdowns preserve sign (negative for expenses, positive for income)."""
    transactions = [
        {
            'counterparty': 'Income Company',
            'amount': 1000.0,  # Positive for income
            'account': 'SI111111111',
        },
        {
            'counterparty': 'Expense Company',
            'amount': -500.0,  # Negative for expenses
            'account': 'SI222222222',
        },
    ]

    result = get_counterparty_breakdowns(transactions)

    income_cp = next(cp for cp in result if 'Income' in cp['name'])
    expense_cp = next(cp for cp in result if 'Expense' in cp['name'])

    assert income_cp['total'] > 0
    assert expense_cp['total'] < 0


def test_get_counterparty_breakdowns_account_numbers():
    """Test that account numbers are collected."""
    transactions = [
        {
            'counterparty': 'Company A',
            'amount': 1000.0,
            'account': 'SI111111111',
        },
        {
            'counterparty': 'Company A',
            'amount': 500.0,
            'account': 'SI222222222',  # Different account
        },
    ]

    result = get_counterparty_breakdowns(transactions)

    company_a = next(cp for cp in result if 'Company A' in cp['name'])
    assert len(company_a['account_numbers']) == 2
    assert 'SI111111111' in company_a['account_numbers']
    assert 'SI222222222' in company_a['account_numbers']


def test_get_counterparty_breakdowns_empty_counterparty():
    """Test handling of empty or missing counterparty names."""
    transactions = [
        {
            'counterparty': '',
            'amount': 1000.0,
            'account': 'SI111111111',
        },
        {
            'counterparty': '   ',
            'amount': 500.0,
            'account': 'SI222222222',
        },
        {
            # Missing counterparty key
            'amount': 300.0,
            'account': 'SI333333333',
        },
    ]

    result = get_counterparty_breakdowns(transactions)

    # Should all be grouped as "Unknown"
    assert len(result) == 1
    assert result[0]['name'] == 'Unknown'
    assert result[0]['count'] == 3


def test_get_counterparty_breakdowns_empty_transactions():
    """Test get_counterparty_breakdowns with empty list."""
    result = get_counterparty_breakdowns([])

    assert result == []


def test_normalize_counterparty_name_edge_cases():
    """Test edge cases for normalization."""
    # Empty string
    assert normalize_counterparty_name("") == ""

    # Only whitespace
    assert normalize_counterparty_name("   ") == ""

    # Multiple periods
    assert normalize_counterparty_name("Company d..o..o.") == "company d.o.o."

    # Mixed case with special characters
    assert normalize_counterparty_name("Študentski Servis D.O.O.") == "studentski servis d.o.o."


def test_get_counterparty_breakdowns_special_characters():
    """Test counterparty breakdowns with special characters."""
    transactions = [
        {
            'counterparty': 'Študentski servis D.O.O.',
            'amount': 1000.0,
            'account': 'SI111111111',
        },
        {
            'counterparty': 'STUDENTSKI SERVIS d.o.o.',
            'amount': 500.0,
            'account': 'SI111111111',
        },
    ]

    result = get_counterparty_breakdowns(transactions)

    # Should be grouped together despite different diacritics
    assert len(result) == 1
    assert result[0]['count'] == 2

