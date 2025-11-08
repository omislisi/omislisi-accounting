"""Data collection for dashboard generation."""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

from omislisi_accounting.analysis.reporter import generate_summary, generate_category_breakdown
from omislisi_accounting.parsers.zip_handler import get_all_transaction_files
from omislisi_accounting.parsers.parser_factory import parse_all_files
from omislisi_accounting.domain.categories import categorize_transaction


def collect_dashboard_data(reports_path: Path, current_year: int, selected_month: datetime = None) -> Dict[str, Any]:
    """
    Collect all dashboard data for all time periods.

    Args:
        reports_path: Path to reports directory
        current_year: Current year for YTD calculations
        selected_month: Optional datetime for default month to show (defaults to most recent month with data)

    Returns:
        Dictionary with all dashboard data ready for JSON serialization
    """
    # Determine which years we need to load - load ALL available years
    years_to_load = set()

    # Find all available year directories
    for year_dir in sorted(reports_path.iterdir()):
        if year_dir.is_dir() and year_dir.name.isdigit():
            years_to_load.add(year_dir.name)

    # Also ensure we have current year and previous year for comparisons
    years_to_load.add(str(current_year))
    if current_year > 2020:  # Reasonable minimum
        years_to_load.add(str(current_year - 1))

    # Load all transactions from all available years
    all_transactions = []
    for year_str in sorted(years_to_load):
        year_reports_path = reports_path / year_str
        if year_reports_path.exists():
            files = get_all_transaction_files(year_reports_path)
            if files:
                year_transactions = parse_all_files(files, silent=True)
                # Add categories
                for transaction in year_transactions:
                    transaction['category'] = categorize_transaction(
                        transaction.get('description', ''),
                        transaction.get('type', ''),
                        transaction.get('amount'),
                        transaction.get('counterparty'),
                        transaction.get('account')
                    )
                all_transactions.extend(year_transactions)

    # Get all available months from transactions
    available_months = set()
    for tx in all_transactions:
        if tx.get('date'):
            month_str = tx['date'][:7]  # YYYY-MM
            available_months.add(month_str)

    available_months = sorted(available_months)

    # Determine default month to show
    if selected_month is None:
        # Use most recent month with data, or current month if no data yet
        if available_months:
            default_month_str = available_months[-1]
        else:
            default_month_str = datetime.now().strftime('%Y-%m')
    else:
        default_month_str = selected_month.strftime('%Y-%m')

    # Parse default month
    default_month_date = datetime.strptime(default_month_str, '%Y-%m')

    # Collect monthly data for ALL months
    all_monthly_data = {}
    for month_str in available_months:
        month_date = datetime.strptime(month_str, '%Y-%m')
        all_monthly_data[month_str] = get_current_month_data(all_transactions, month_date.year, month_date.month)

    # Determine date ranges for trends
    if available_months:
        first_month = datetime.strptime(available_months[0], '%Y-%m')
        last_month = datetime.strptime(available_months[-1], '%Y-%m')
        end_date = last_month
        # Start from first month, but ensure we have at least 12 months if possible
        start_date = first_month
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

    # Prepare transactions for JSON serialization (keep only essential fields)
    serializable_transactions = []
    for tx in all_transactions:
        source_file = tx.get('source_file', '')
        # Convert zip filename to PDF filename for Google Drive link
        pdf_filename = source_file.replace('.zip', '.pdf') if source_file.endswith('.zip') else source_file.replace('.csv', '.pdf')

        serializable_transactions.append({
            'date': tx.get('date', ''),
            'amount': tx.get('amount', 0),
            'description': tx.get('description', ''),
            'type': tx.get('type', ''),
            'counterparty': tx.get('counterparty', ''),
            'category': tx.get('category', ''),
            'reference': tx.get('reference', ''),
            'account': tx.get('account', ''),
            'source_file': source_file,
            'pdf_filename': pdf_filename,
        })

    # Collect data for all periods
    dashboard_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'current_year': current_year,
            'default_month': default_month_str,
            'available_months': available_months,
            'total_transactions': len(all_transactions),
        },
        'all_months': all_monthly_data,
        'current_month': all_monthly_data.get(default_month_str, get_current_month_data(all_transactions, default_month_date.year, default_month_date.month)),
        'ytd': get_ytd_data(all_transactions, current_year),
        'last_12_months': get_last_12_months_data(all_transactions, end_date),
        'year_comparison': get_year_comparison_data(all_transactions, current_year, current_year - 1),
        'monthly_trends': get_monthly_trends(all_transactions, start_date, end_date),
        'categories_and_tags': get_all_categories_and_tags(all_transactions),
        'all_counterparties': [cp['name'] for cp in get_counterparty_breakdowns(all_transactions, limit=1000)],
        'all_transactions': serializable_transactions,
    }

    return dashboard_data


def get_current_month_data(transactions: List[Dict[str, Any]], year: int, month: int) -> Dict[str, Any]:
    """Get current month summary and breakdowns."""
    month_str = f"{year}-{month:02d}"
    month_transactions = [
        tx for tx in transactions
        if tx.get('date') and tx['date'].startswith(month_str)
    ]

    summary = generate_summary(month_transactions)
    breakdown = generate_category_breakdown(month_transactions)

    # Get previous month for comparison
    if month == 1:
        prev_month_str = f"{year - 1}-12"
    else:
        prev_month_str = f"{year}-{month - 1:02d}"

    prev_month_transactions = [
        tx for tx in transactions
        if tx.get('date') and tx['date'].startswith(prev_month_str)
    ]
    prev_summary = generate_summary(prev_month_transactions)

    # Calculate changes
    income_change = summary['total_income'] - prev_summary['total_income']
    expense_change = summary['total_expenses'] - prev_summary['total_expenses']
    net_change = summary['net'] - prev_summary['net']

    income_change_pct = (income_change / prev_summary['total_income'] * 100) if prev_summary['total_income'] != 0 else 0
    expense_change_pct = (expense_change / prev_summary['total_expenses'] * 100) if prev_summary['total_expenses'] != 0 else 0
    net_change_pct = (net_change / abs(prev_summary['net']) * 100) if prev_summary['net'] != 0 else 0

    return {
        'period': month_str,
        'summary': summary,
        'breakdown': breakdown,
        'comparison': {
            'previous_month': prev_month_str,
            'income_change': income_change,
            'income_change_pct': income_change_pct,
            'expense_change': expense_change,
            'expense_change_pct': expense_change_pct,
            'net_change': net_change,
            'net_change_pct': net_change_pct,
        },
        'counterparties': get_counterparty_breakdowns(month_transactions, limit=1000),  # Include all for trends
    }


def get_ytd_data(transactions: List[Dict[str, Any]], year: int) -> Dict[str, Any]:
    """Get year-to-date summary and monthly progression."""
    year_str = str(year)
    ytd_transactions = [
        tx for tx in transactions
        if tx.get('date') and tx['date'].startswith(year_str)
    ]

    summary = generate_summary(ytd_transactions)
    breakdown = generate_category_breakdown(ytd_transactions)

    # Monthly progression
    monthly_data = {}
    for month in range(1, 13):
        month_str = f"{year}-{month:02d}"
        month_transactions = [
            tx for tx in ytd_transactions
            if tx.get('date') and tx['date'].startswith(month_str)
        ]
        if month_transactions:
            monthly_data[month_str] = generate_summary(month_transactions)

    # Projected annual (based on current progress)
    current_month = datetime.now().month
    if current_month > 0:
        avg_monthly_income = summary['total_income'] / current_month
        avg_monthly_expenses = summary['total_expenses'] / current_month
        projected_income = avg_monthly_income * 12
        projected_expenses = avg_monthly_expenses * 12
        projected_net = projected_income - projected_expenses
    else:
        projected_income = projected_expenses = projected_net = 0

    return {
        'period': year_str,
        'summary': summary,
        'breakdown': breakdown,
        'monthly_progression': monthly_data,
        'projections': {
            'projected_income': projected_income,
            'projected_expenses': projected_expenses,
            'projected_net': projected_net,
        },
        'counterparties': get_counterparty_breakdowns(ytd_transactions, limit=10000),  # Show all counterparties
    }


def get_last_12_months_data(transactions: List[Dict[str, Any]], end_date: datetime) -> Dict[str, Any]:
    """Get last 12 months rolling data."""
    start_date = end_date - timedelta(days=365)

    # Generate list of months
    months_to_analyze = []
    current = start_date.replace(day=1)  # Start from first day of month
    while current <= end_date:
        months_to_analyze.append(current.strftime('%Y-%m'))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    monthly_data = {}
    for month_str in months_to_analyze:
        month_transactions = [
            tx for tx in transactions
            if tx.get('date') and tx['date'].startswith(month_str)
        ]
        if month_transactions:
            monthly_data[month_str] = {
                'summary': generate_summary(month_transactions),
                'breakdown': generate_category_breakdown(month_transactions),
            }

    # Calculate totals
    total_income = sum(d['summary']['total_income'] for d in monthly_data.values())
    total_expenses = sum(d['summary']['total_expenses'] for d in monthly_data.values())
    total_net = total_income - total_expenses

    return {
        'period': f"{months_to_analyze[0]} to {months_to_analyze[-1]}",
        'months': monthly_data,
        'summary': {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net': total_net,
            'transaction_count': sum(d['summary']['transaction_count'] for d in monthly_data.values()),
        },
    }


def get_year_comparison_data(transactions: List[Dict[str, Any]], current_year: int, previous_year: int) -> Dict[str, Any]:
    """Get year-over-year comparison data - comparing only months that exist in current year (YTD comparison)."""
    current_year_str = str(current_year)
    previous_year_str = str(previous_year)

    # Get all current year transactions
    all_current_transactions = [
        tx for tx in transactions
        if tx.get('date') and tx['date'].startswith(current_year_str)
    ]

    # Find which months exist in current year
    current_year_months = set()
    for tx in all_current_transactions:
        if tx.get('date'):
            month_str = tx['date'][:7]  # YYYY-MM
            if month_str.startswith(current_year_str):
                month_num = month_str.split('-')[1]  # Extract MM
                current_year_months.add(month_num)

    # Only compare months that exist in current year (YTD comparison)
    current_transactions = []
    previous_transactions = []
    monthly_comparison = {}

    for month_num in sorted(current_year_months):
        month_str = f"{int(month_num):02d}"  # Ensure 2-digit format

        # Get current year month transactions
        current_month_tx = [
            tx for tx in all_current_transactions
            if tx.get('date', '').startswith(f"{current_year_str}-{month_str}")
        ]
        current_transactions.extend(current_month_tx)

        # Get previous year same month transactions
        previous_month_tx = [
            tx for tx in transactions
            if tx.get('date', '') and tx['date'].startswith(f"{previous_year_str}-{month_str}")
        ]
        previous_transactions.extend(previous_month_tx)

        # Store monthly comparison
        monthly_comparison[month_str] = {
            'current': generate_summary(current_month_tx) if current_month_tx else None,
            'previous': generate_summary(previous_month_tx) if previous_month_tx else None,
        }

    current_summary = generate_summary(current_transactions)
    previous_summary = generate_summary(previous_transactions)
    current_breakdown = generate_category_breakdown(current_transactions)
    previous_breakdown = generate_category_breakdown(previous_transactions)

    # Calculate changes
    income_change = current_summary['total_income'] - previous_summary['total_income']
    expense_change = current_summary['total_expenses'] - previous_summary['total_expenses']
    net_change = current_summary['net'] - previous_summary['net']

    income_change_pct = (income_change / previous_summary['total_income'] * 100) if previous_summary['total_income'] != 0 else 0
    expense_change_pct = (expense_change / previous_summary['total_expenses'] * 100) if previous_summary['total_expenses'] != 0 else 0
    net_change_pct = (net_change / abs(previous_summary['net']) * 100) if previous_summary['net'] != 0 else 0

    return {
        'current_year': current_year_str,
        'previous_year': previous_year_str,
        'current_summary': current_summary,
        'previous_summary': previous_summary,
        'current_breakdown': current_breakdown,
        'previous_breakdown': previous_breakdown,
        'changes': {
            'income_change': income_change,
            'income_change_pct': income_change_pct,
            'expense_change': expense_change,
            'expense_change_pct': expense_change_pct,
            'net_change': net_change,
            'net_change_pct': net_change_pct,
        },
        'monthly_comparison': monthly_comparison,
    }


def get_monthly_trends(transactions: List[Dict[str, Any]], start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Get monthly trends data for charting."""
    monthly_data = {}
    current = start_date.replace(day=1)

    while current <= end_date:
        month_str = current.strftime('%Y-%m')
        month_transactions = [
            tx for tx in transactions
            if tx.get('date') and tx['date'].startswith(month_str)
        ]

        if month_transactions:
            summary = generate_summary(month_transactions)
            monthly_data[month_str] = summary

        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    return monthly_data


def get_counterparty_breakdowns(transactions: List[Dict[str, Any]], limit: int = 20) -> List[Dict[str, Any]]:
    """Get top counterparties by frequency and amount.

    This function delegates to the shared counterparty_utils module
    to ensure consistency between CLI and dashboard.
    """
    from omislisi_accounting.analysis.counterparty_utils import get_counterparty_breakdowns as _get_counterparty_breakdowns
    return _get_counterparty_breakdowns(transactions, limit=limit)


def get_category_trends(transactions: List[Dict[str, Any]], category: str, tag: str = None) -> Dict[str, Any]:
    """
    Get monthly trends for a specific category or category:tag combination.

    Args:
        transactions: All transactions
        category: Category name
        tag: Optional tag/subcategory name

    Returns:
        Dictionary with monthly data: {month_str: {total, count, ...}}
    """
    monthly_data = {}

    # Get all available months
    available_months = set()
    for tx in transactions:
        if tx.get('date'):
            month_str = tx['date'][:7]  # YYYY-MM
            available_months.add(month_str)

    available_months = sorted(available_months)

    for month_str in available_months:
        month_transactions = [
            tx for tx in transactions
            if tx.get('date') and tx['date'].startswith(month_str)
        ]

        # Filter by category and tag
        filtered_tx = []
        for tx in month_transactions:
            tx_category = tx.get('category', '')
            if ':' in tx_category:
                base_cat, tx_tag = tx_category.split(':', 1)
                if tag:
                    # Looking for specific tag
                    if base_cat == category and tx_tag == tag:
                        filtered_tx.append(tx)
                else:
                    # Looking for base category (all tags)
                    if base_cat == category:
                        filtered_tx.append(tx)
            else:
                # No tag in transaction
                if not tag and tx_category == category:
                    filtered_tx.append(tx)

        if filtered_tx:
            total = sum(tx.get('amount', 0) for tx in filtered_tx)
            count = len(filtered_tx)
            monthly_data[month_str] = {
                'total': total,
                'count': count,
            }
        else:
            monthly_data[month_str] = {
                'total': 0,
                'count': 0,
            }

    return monthly_data


def get_counterparty_trends(transactions: List[Dict[str, Any]], counterparty_name: str) -> Dict[str, Any]:
    """
    Get monthly trends for a specific counterparty.

    Args:
        transactions: All transactions
        counterparty_name: Counterparty name to filter by

    Returns:
        Dictionary with monthly data: {month_str: {total, count, ...}}
    """
    from collections import defaultdict
    from omislisi_accounting.analysis.counterparty_utils import normalize_counterparty_name

    # Normalize the search name using shared function
    normalized_search = normalize_counterparty_name(counterparty_name)

    # Get all available months
    available_months = set()
    for tx in transactions:
        if tx.get('date'):
            month_str = tx['date'][:7]  # YYYY-MM
            available_months.add(month_str)

    available_months = sorted(available_months)

    monthly_data = {}
    for month_str in available_months:
        month_transactions = [
            tx for tx in transactions
            if tx.get('date') and tx['date'].startswith(month_str)
        ]

        # Filter by counterparty (using normalization)
        filtered_tx = []
        for tx in month_transactions:
            tx_counterparty = tx.get('counterparty', '').strip() or 'Unknown'
            normalized_tx = normalize_counterparty_name(tx_counterparty)
            if normalized_tx == normalized_search:
                filtered_tx.append(tx)

        if filtered_tx:
            total = sum(tx.get('amount', 0) for tx in filtered_tx)
            count = len(filtered_tx)
            monthly_data[month_str] = {
                'total': total,
                'count': count,
            }
        else:
            monthly_data[month_str] = {
                'total': 0,
                'count': 0,
            }

    return monthly_data


def get_all_categories_and_tags(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Get all categories and their tags from all transactions.

    Returns:
        Dictionary: {category: {tags: [tag1, tag2, ...], ...}}
    """
    categories = {}

    for tx in transactions:
        category = tx.get('category', '')
        if not category:
            continue

        if ':' in category:
            base_category, tag = category.split(':', 1)
            if base_category not in categories:
                categories[base_category] = {'tags': set()}
            categories[base_category]['tags'].add(tag)
        else:
            if category not in categories:
                categories[category] = {'tags': set()}

    # Convert sets to lists for JSON serialization
    result = {}
    for cat, data in categories.items():
        result[cat] = {
            'tags': sorted(list(data['tags']))
        }

    return result

