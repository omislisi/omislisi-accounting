"""Shared utilities for counterparty name normalization and grouping.

This module provides consistent counterparty normalization and grouping logic
used by both the CLI and dashboard to ensure identical results.
"""

import re
import unicodedata
from typing import Dict, Any, List
from collections import defaultdict


def normalize_counterparty_name(name: str) -> str:
    """Normalize counterparty name for grouping.

    This function standardizes counterparty names by:
    - Converting to lowercase
    - Removing diacritics (accents)
    - Normalizing legal suffixes (d.o.o., d.d., s.p., z.b.o.)
    - Handling special entity aliases (e.g., CTRP/IN-FIT)

    Args:
        name: Raw counterparty name from transaction

    Returns:
        Normalized counterparty name for grouping
    """
    normalized = name.lower()
    normalized = unicodedata.normalize('NFD', normalized)
    normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    # Handle "d. d." with space - normalize to "d.d." first
    normalized = re.sub(r'\bd\.\s*d\.\b', 'd.d.', normalized)
    normalized = re.sub(r'\bss\s+d\.o\.o\.', 'ss d.o.o.', normalized)
    normalized = re.sub(r'\bss\s+d\.o\.o\b', 'ss d.o.o.', normalized)
    normalized = re.sub(r',\s*(d\.o\.o\.?|d\.d\.?|s\.p\.?|z\.b\.o\.?)', r' \1', normalized)
    # Normalize legal suffixes - ensure consistent format with trailing period
    normalized = re.sub(r'\bd\.o\.o\.?\b', 'd.o.o.', normalized)
    normalized = re.sub(r'\bd\.d\.\.?\b', 'd.d.', normalized)
    normalized = re.sub(r'\bs\.p\.\.?\b', 's.p.', normalized)
    # Fix z.b.o. normalization - handle both with and without trailing period
    normalized = re.sub(r'\bz\.b\.o\.?\b', 'z.b.o.', normalized)
    normalized = re.sub(r'\.{2,}', '.', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    # Special entity aliases - normalize known variations to canonical form
    # CTRP and IN-FIT are the same entity
    if 'ctrp' in normalized or 'in-fit' in normalized or 'infit' in normalized:
        # Normalize to a canonical form (use the more common one)
        normalized = re.sub(r'.*(ctrp|in-fit|infit).*', 'in-fit d.o.o.', normalized)

    return normalized


def get_group_key(account: str, normalized_name: str) -> str:
    """Get a group key for counterparty aggregation.

    Always uses normalized name for grouping, not account number.
    Account numbers can be shared by multiple different counterparties,
    which causes incorrect grouping. Grouping by normalized name ensures
    that only counterparties with similar names are grouped together.

    Args:
        account: Account number from transaction (not used for grouping)
        normalized_name: Normalized counterparty name

    Returns:
        Group key string in format "name:{normalized_name}"
    """
    # Always group by normalized name, not account number
    # Account numbers can be shared by multiple different entities,
    # causing incorrect grouping
    return f"name:{normalized_name}"


def get_counterparty_breakdowns(transactions: List[Dict[str, Any]], limit: int = 20) -> List[Dict[str, Any]]:
    """Get counterparty breakdowns with consistent grouping logic.

    This is the canonical function for grouping transactions by counterparty.
    Both the CLI and dashboard use this function to ensure identical results.

    Args:
        transactions: List of transaction dictionaries
        limit: Maximum number of counterparties to return

    Returns:
        List of counterparty dictionaries with keys:
        - name: Most common name variant for this group
        - count: Number of transactions
        - total: Total amount (preserves sign: negative for expenses, positive for income)
        - account_numbers: List of account numbers associated with this group
    """
    # Aggregate by counterparty
    counterparty_stats = defaultdict(lambda: {
        'count': 0,
        'total': 0.0,
        'transactions': [],
        'name_variants': set(),
        'account_numbers': set()
    })
    group_keys = {}

    for tx in transactions:
        counterparty = tx.get('counterparty', '').strip() or 'Unknown'
        account = tx.get('account', '').strip() if tx.get('account') else ''
        normalized_name = normalize_counterparty_name(counterparty)
        group_key = get_group_key(account, normalized_name)
        # Preserve sign: expenses are negative, income is positive
        # This allows the frontend to distinguish between expenses and income for chart coloring
        amount = tx.get('amount', 0)

        if group_key not in group_keys:
            group_keys[group_key] = {
                'primary_account': account if account else None,
                'primary_name': counterparty,
                'name_variants': set([counterparty]),
                'account_numbers': set([account]) if account else set()
            }
        else:
            group_keys[group_key]['name_variants'].add(counterparty)
            if account:
                group_keys[group_key]['account_numbers'].add(account)

        counterparty_stats[group_key]['count'] += 1
        counterparty_stats[group_key]['total'] += amount
        counterparty_stats[group_key]['transactions'].append(tx)
        counterparty_stats[group_key]['name_variants'].add(counterparty)
        if account:
            counterparty_stats[group_key]['account_numbers'].add(account)

    # Convert to list and sort
    result = []
    for group_key, stats in counterparty_stats.items():
        group_info = group_keys[group_key]
        name_variants = stats['name_variants']
        most_common_name = max(name_variants, key=lambda n: sum(1 for tx in stats['transactions'] if tx.get('counterparty', '').strip() == n))

        result.append({
            'name': most_common_name,
            'count': stats['count'],
            'total': stats['total'],
            'account_numbers': list(stats['account_numbers']),
        })

    # Sort by absolute total amount descending (so largest expenses/income appear first)
    # This ensures both expenses and income are included, not just income
    result.sort(key=lambda x: abs(x['total']), reverse=True)

    return result[:limit]

