"""Main CLI entry point."""

import click
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from omislisi_accounting.config import REPORTS_PATH
from omislisi_accounting.parsers.zip_handler import get_all_transaction_files
from omislisi_accounting.parsers.parser_factory import parse_all_files
from omislisi_accounting.domain.categories import categorize_transaction
from omislisi_accounting.analysis.reporter import generate_summary, generate_category_breakdown

# Configure logging to show warnings via click
class ClickHandler(logging.Handler):
    """Logging handler that outputs to click.echo."""
    def emit(self, record):
        try:
            msg = self.format(record)
            click.echo(f"Warning: {msg}", err=True)
        except Exception:
            self.handleError(record)

# Set up logging for parser warnings
logging.basicConfig(level=logging.WARNING, handlers=[ClickHandler()])


@click.group()
@click.version_option()
def cli():
    """Omislisi Accounting Analysis Tool - Analyze bank and PayPal transactions."""
    pass


@cli.command()
@click.option(
    "--reports-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=REPORTS_PATH,
    help="Path to the reports directory containing zip files",
)
@click.option("--year", help="Filter by year (e.g., 2025)")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed processing information")
def analyze(reports_path: Path, year: str, verbose: bool):
    """Analyze all transactions from zip files in the reports directory."""
    click.echo(f"Analyzing reports from: {reports_path}")

    # Filter by year if specified
    if year:
        reports_path = reports_path / year
        if not reports_path.exists():
            click.echo(f"Error: Year directory {reports_path} does not exist", err=True)
            return

    click.echo("Finding transaction files...")
    files = get_all_transaction_files(reports_path)
    click.echo(f"Found {len(files)} transaction files")

    if verbose and files:
        click.echo("\nFiles to process:")
        for file_path, source_path in files[:10]:  # Show first 10 files
            click.echo(f"  - {file_path.name} (from {source_path.name})")
        if len(files) > 10:
            click.echo(f"  ... and {len(files) - 10} more files")

    if not files:
        click.echo("No transaction files found!", err=True)
        return

    click.echo("Parsing transactions...")
    transactions = parse_all_files(files, silent=not verbose)
    click.echo(f"Parsed {len(transactions)} transactions")

    # Add categories
    for transaction in transactions:
        transaction['category'] = categorize_transaction(
            transaction.get('description', ''),
            transaction.get('type', ''),
            transaction.get('amount'),
            transaction.get('counterparty'),
            transaction.get('account')
        )

    # Generate summary
    summary = generate_summary(transactions)

    click.echo("\n=== Summary ===")
    click.echo(f"Total Income: €{summary['total_income']:,.2f}")
    click.echo(f"Total Expenses: €{summary['total_expenses']:,.2f}")
    click.echo(f"Net: €{summary['net']:,.2f}")
    click.echo(f"Transaction Count: {summary['transaction_count']}")
    click.echo(f"  - Income: {summary['income_count']}")
    click.echo(f"  - Expenses: {summary['expense_count']}")

    # Category breakdown
    breakdown = generate_category_breakdown(transactions)
    if breakdown:
        click.echo("\n=== Category Breakdown ===")
        for category, data in sorted(breakdown.items(), key=lambda x: abs(x[1]['total']), reverse=True):
            # Check if category has tags
            if "tags" in data and data["tags"]:
                click.echo(f"{category}: €{data['total']:,.2f} ({data['count']} transactions)")
                # Display tag breakdown
                for tag, tag_data in sorted(data["tags"].items(), key=lambda x: abs(x[1]['total']), reverse=True):
                    click.echo(f"  └─ {tag}: €{tag_data['total']:,.2f} ({tag_data['count']} transactions)")
            else:
                click.echo(f"{category}: €{data['total']:,.2f} ({data['count']} transactions)")

    click.echo("\nAnalysis complete!")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def categorize(input_file: Path):
    """Categorize expenses from a transaction file."""
    click.echo(f"Categorizing transactions from: {input_file}")

    from omislisi_accounting.parsers.parser_factory import get_parser

    parser = get_parser(input_file)
    if not parser:
        click.echo(f"Error: No parser found for {input_file}", err=True)
        return

    transactions = parser.parse(input_file)

    # Add categories
    for transaction in transactions:
        transaction['category'] = categorize_transaction(
            transaction.get('description', ''),
            transaction.get('type', ''),
            transaction.get('amount'),
            transaction.get('counterparty'),
            transaction.get('account')
        )

    click.echo(f"\nCategorized {len(transactions)} transactions:")
    for tx in transactions:
        click.echo(f"  {tx['date']} | {tx['type']:8} | €{tx['amount']:8.2f} | {tx['category']:20} | {tx['description'][:50]}")


@cli.command()
@click.option("--month", help="Month in YYYY-MM format")
@click.option("--year", help="Year (e.g., 2025)")
@click.option("--compare-month", help="Compare with another month in YYYY-MM format")
@click.option("--compare-year", help="Compare with another year (e.g., 2024)")
@click.option("--category", help="Filter by category (e.g., 'salary' or 'salary:founders')")
@click.option("--counterparty", help="Filter by counterparty name (case-insensitive, partial match supported)")
@click.option("--by-counterparty", is_flag=True, help="Show counterparty breakdown in addition to category breakdown")
@click.option("--counterparty-limit", type=int, default=20, help="Maximum number of counterparties to show (when --by-counterparty is used)")
@click.option(
    "--reports-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=REPORTS_PATH,
    help="Path to the reports directory",
)
def report(month: str, year: str, compare_month: str, compare_year: str, category: str, counterparty: str, by_counterparty: bool, counterparty_limit: int, reports_path: Path):
    """Generate a monthly or yearly report."""
    # Validate comparison options
    if compare_month and compare_year:
        click.echo("Error: Cannot specify both --compare-month and --compare-year", err=True)
        return

    if compare_month and not month:
        click.echo("Error: Must specify --month when using --compare-month", err=True)
        return

    if compare_year and not year:
        click.echo("Error: Must specify --year when using --compare-year", err=True)
        return

    # Validate comparison period formats
    if compare_month:
        try:
            datetime.strptime(compare_month, '%Y-%m')
        except ValueError:
            click.echo(f"Error: Invalid compare-month format. Use YYYY-MM (e.g., 2025-08)", err=True)
            return

    # Determine if we're in comparison mode
    is_comparison = bool(compare_month or compare_year)

    # Extract year from month if month is specified but year is not
    if month and not year:
        try:
            month_date = datetime.strptime(month, '%Y-%m')
            year = str(month_date.year)
        except ValueError:
            click.echo(f"Error: Invalid month format. Use YYYY-MM (e.g., 2025-08)", err=True)
            return

    # Validate month format if provided
    if month:
        try:
            datetime.strptime(month, '%Y-%m')
        except ValueError:
            click.echo(f"Error: Invalid month format. Use YYYY-MM (e.g., 2025-08)", err=True)
            return

    def get_transactions_for_period(period_month: str = None, period_year: str = None, base_reports_path: Path = None):
        """Helper function to get transactions for a specific period."""
        period_reports_path = base_reports_path or reports_path

        # Filter by year if specified
        if period_year:
            # If base_reports_path is already a year directory, go to parent first
            if base_reports_path and base_reports_path.name.isdigit():
                period_reports_path = base_reports_path.parent / period_year
            else:
                period_reports_path = reports_path / period_year
            if not period_reports_path.exists():
                return []
        elif period_month:
            # Extract year from month and use that directory
            period_year_from_month = period_month[:4]
            if base_reports_path and base_reports_path.name.isdigit():
                period_reports_path = base_reports_path.parent / period_year_from_month
            else:
                period_reports_path = reports_path / period_year_from_month
            if not period_reports_path.exists():
                return []

        files = get_all_transaction_files(period_reports_path)
        if not files:
            return []

        period_transactions = parse_all_files(files, silent=True)

        # Filter by month if specified
        if period_month:
            period_transactions = [
                tx for tx in period_transactions
                if tx.get('date') and tx['date'].startswith(period_month)
            ]

        # Add categories
        for transaction in period_transactions:
            transaction['category'] = categorize_transaction(
                transaction.get('description', ''),
                transaction.get('type', ''),
                transaction.get('amount'),
                transaction.get('counterparty'),
                transaction.get('account')
            )

        return period_transactions

    # Get base period transactions
    base_reports_path = reports_path
    if year:
        base_reports_path = reports_path / year
        if not base_reports_path.exists():
            click.echo(f"Error: Year directory {base_reports_path} does not exist", err=True)
            return

    click.echo(f"Generating report for: {month or year or 'all'}")
    if is_comparison:
        compare_period = compare_month or compare_year
        click.echo(f"Comparing with: {compare_period}")
    click.echo(f"Using reports from: {base_reports_path}")

    transactions = get_transactions_for_period(month, year, base_reports_path)

    if not transactions:
        click.echo(f"No transactions found for {month or year or 'all'}", err=True)
        return

    click.echo(f"Found {len(transactions)} transactions for base period")

    def apply_filters(tx_list: list, cat_filter: str = None, cp_filter: str = None) -> list:
        """Apply category and counterparty filters to a transaction list."""
        filtered = tx_list

        # Filter by category if specified
        if cat_filter:
            from omislisi_accounting.domain.categories import get_all_categories

            all_categories = get_all_categories()
            category_lower = cat_filter.lower()

            if ":" in category_lower:
                filtered = [
                    tx for tx in filtered
                    if tx.get('category', '').lower() == category_lower
                ]
            else:
                filtered = [
                    tx for tx in filtered
                    if tx.get('category', '').lower().startswith(category_lower + ':') or
                       tx.get('category', '').lower() == category_lower
                ]

        # Filter by counterparty if specified
        if cp_filter:
            from omislisi_accounting.analysis.counterparty_utils import normalize_counterparty_name
            cp_search = normalize_counterparty_name(cp_filter)
            filtered = [
                tx for tx in filtered
                if cp_search in normalize_counterparty_name(tx.get('counterparty', ''))
            ]

        return filtered

    # Get comparison period transactions if in comparison mode
    compare_transactions = []
    if is_comparison:
        compare_year_for_path = None
        if compare_year:
            compare_year_for_path = compare_year
        elif compare_month:
            # Extract year from compare_month
            compare_year_for_path = compare_month[:4]

        compare_transactions = get_transactions_for_period(compare_month, compare_year_for_path, reports_path)
        click.echo(f"Found {len(compare_transactions)} transactions for comparison period")

        if not compare_transactions:
            click.echo(f"Warning: No transactions found for comparison period {compare_month or compare_year}", err=True)

    # Apply filters to base period
    original_count = len(transactions)
    transactions = apply_filters(transactions, category, counterparty)
    if category or counterparty:
        click.echo(f"Filtered base period to {len(transactions)} transactions (from {original_count} total)")

    if not transactions:
        click.echo(f"No transactions found for base period after filtering", err=True)
        return

    # Apply filters to comparison period
    if is_comparison:
        original_compare_count = len(compare_transactions)
        compare_transactions = apply_filters(compare_transactions, category, counterparty)
        if category or counterparty:
            click.echo(f"Filtered comparison period to {len(compare_transactions)} transactions (from {original_compare_count} total)")

    # Validate category if specified (before filtering)
    if category:
        from omislisi_accounting.domain.categories import get_all_categories
        all_categories = get_all_categories()
        category_lower = category.lower()

        is_valid = False
        if ":" in category_lower:
            base_cat, tag = category_lower.split(":", 1)
            if base_cat in [c.lower() for c in all_categories]:
                is_valid = True
        else:
            if category_lower in [c.lower() for c in all_categories]:
                is_valid = True

        if not is_valid:
            click.echo(f"Error: Unknown category '{category}'", err=True)
            click.echo(f"\nAvailable categories:")
            for cat in sorted(all_categories):
                click.echo(f"  - {cat}")
            click.echo(f"\nYou can also use tags like 'salary:founders', 'salary:students', etc.")
            return

    # Generate summaries
    summary = generate_summary(transactions)
    breakdown = generate_category_breakdown(transactions)

    compare_summary = None
    compare_breakdown = None
    if is_comparison:
        compare_summary = generate_summary(compare_transactions)
        compare_breakdown = generate_category_breakdown(compare_transactions)

    # Display report
    click.echo("\n" + "="*80)
    report_title = month or year or 'ALL TIME'
    if category:
        report_title += f" - Category: {category}"
    if counterparty:
        report_title += f" - Counterparty: {counterparty}"

    if is_comparison:
        compare_period_label = compare_month or compare_year
        click.echo(f"COMPARISON REPORT: {report_title} vs {compare_period_label}")
    else:
        click.echo(f"REPORT: {report_title}")
    click.echo("="*80)

    if is_comparison:
        # Side-by-side comparison
        base_label = month or year or 'ALL TIME'
        compare_label = compare_month or compare_year

        click.echo(f"\n{'Metric':<25} {base_label:>20} {compare_label:>20} {'Change':>15}")
        click.echo("-" * 80)

        # Income
        income_diff = summary['total_income'] - compare_summary['total_income']
        income_pct = (income_diff / compare_summary['total_income'] * 100) if compare_summary['total_income'] != 0 else (float('inf') if income_diff > 0 else float('-inf'))
        income_change_str = f"€{income_diff:>13,.2f}"
        if abs(income_pct) < float('inf'):
            income_change_str += f" ({income_pct:+.1f}%)"
        click.echo(f"{'Total Income':<25} €{summary['total_income']:>18,.2f} €{compare_summary['total_income']:>18,.2f} {income_change_str}")

        # Expenses
        expense_diff = summary['total_expenses'] - compare_summary['total_expenses']
        expense_pct = (expense_diff / compare_summary['total_expenses'] * 100) if compare_summary['total_expenses'] != 0 else (float('inf') if expense_diff > 0 else float('-inf'))
        expense_change_str = f"€{expense_diff:>13,.2f}"
        if abs(expense_pct) < float('inf'):
            expense_change_str += f" ({expense_pct:+.1f}%)"
        click.echo(f"{'Total Expenses':<25} €{summary['total_expenses']:>18,.2f} €{compare_summary['total_expenses']:>18,.2f} {expense_change_str}")

        # Net
        net_diff = summary['net'] - compare_summary['net']
        net_pct = (net_diff / abs(compare_summary['net']) * 100) if compare_summary['net'] != 0 else (float('inf') if net_diff > 0 else float('-inf'))
        net_change_str = f"€{net_diff:>13,.2f}"
        if abs(net_pct) < float('inf'):
            net_change_str += f" ({net_pct:+.1f}%)"
        click.echo(f"{'Net':<25} €{summary['net']:>18,.2f} €{compare_summary['net']:>18,.2f} {net_change_str}")

        # Transaction counts
        tx_diff = summary['transaction_count'] - compare_summary['transaction_count']
        tx_change_str = f"{tx_diff:+d}"
        click.echo(f"{'Transactions':<25} {summary['transaction_count']:>20} {compare_summary['transaction_count']:>20} {tx_change_str:>15}")

        # Category breakdown comparison
        if breakdown or compare_breakdown:
            click.echo("\n--- Category Breakdown Comparison ---")
            all_categories = set(breakdown.keys()) | set(compare_breakdown.keys() if compare_breakdown else [])

            for cat in sorted(all_categories, key=lambda c: abs(breakdown.get(c, {}).get('total', 0) or compare_breakdown.get(c, {}).get('total', 0) if compare_breakdown else 0), reverse=True):
                base_data = breakdown.get(cat, {})
                compare_data = compare_breakdown.get(cat, {}) if compare_breakdown else {}

                base_total = base_data.get('total', 0)
                compare_total = compare_data.get('total', 0)
                base_count = base_data.get('count', 0)
                compare_count = compare_data.get('count', 0)

                cat_diff = base_total - compare_total
                cat_pct = (cat_diff / abs(compare_total) * 100) if compare_total != 0 else (float('inf') if cat_diff > 0 else float('-inf'))
                cat_change_str = f"€{cat_diff:>13,.2f}"
                if abs(cat_pct) < float('inf'):
                    cat_change_str += f" ({cat_pct:+.1f}%)"

                click.echo(f"\n{cat:<25} {base_label:>20} {compare_label:>20} {'Change':>15}")
                click.echo(f"{'  Total':<25} €{base_total:>18,.2f} €{compare_total:>18,.2f} {cat_change_str}")
                click.echo(f"{'  Count':<25} {base_count:>20} {compare_count:>20} {base_count - compare_count:+d}")

                # Show tag breakdown if present
                if "tags" in base_data and base_data["tags"]:
                    all_tags = set(base_data["tags"].keys()) | set(compare_data.get("tags", {}).keys() if compare_data else [])
                    for tag in sorted(all_tags, key=lambda t: abs(base_data["tags"].get(t, {}).get('total', 0) or compare_data.get("tags", {}).get(t, {}).get('total', 0) if compare_data and "tags" in compare_data else 0), reverse=True):
                        base_tag_data = base_data["tags"].get(tag, {})
                        compare_tag_data = compare_data.get("tags", {}).get(tag, {}) if compare_data and "tags" in compare_data else {}

                        base_tag_total = base_tag_data.get('total', 0)
                        compare_tag_total = compare_tag_data.get('total', 0)
                        base_tag_count = base_tag_data.get('count', 0)
                        compare_tag_count = compare_tag_data.get('count', 0)

                        tag_diff = base_tag_total - compare_tag_total
                        tag_pct = (tag_diff / abs(compare_tag_total) * 100) if compare_tag_total != 0 else (float('inf') if tag_diff > 0 else float('-inf'))
                        tag_change_str = f"€{tag_diff:>13,.2f}"
                        if abs(tag_pct) < float('inf'):
                            tag_change_str += f" ({tag_pct:+.1f}%)"

                        click.echo(f"  └─ {tag:<22} €{base_tag_total:>18,.2f} €{compare_tag_total:>18,.2f} {tag_change_str}")
    else:
        # Regular single period report
        click.echo(f"\nTotal Income:     €{summary['total_income']:>15,.2f}")
        click.echo(f"Total Expenses:  €{summary['total_expenses']:>15,.2f}")
        click.echo(f"Net:             €{summary['net']:>15,.2f}")
        click.echo(f"\nTransactions: {summary['transaction_count']} ({summary['income_count']} income, {summary['expense_count']} expenses)")

        if breakdown:
            click.echo("\n--- Category Breakdown ---")
            for category, data in sorted(breakdown.items(), key=lambda x: abs(x[1]['total']), reverse=True):
                # Check if category has tags
                if "tags" in data and data["tags"]:
                    click.echo(f"{category:25} €{data['total']:>12,.2f} ({data['count']:>4} txns)")
                    # Display tag breakdown
                    for tag, tag_data in sorted(data["tags"].items(), key=lambda x: abs(x[1]['total']), reverse=True):
                        click.echo(f"  └─ {tag:22} €{tag_data['total']:>12,.2f} ({tag_data['count']:>4} txns)")
                else:
                    click.echo(f"{category:25} €{data['total']:>12,.2f} ({data['count']:>4} txns)")

    if by_counterparty:
        # Use shared counterparty breakdown function for consistency
        from omislisi_accounting.analysis.counterparty_utils import get_counterparty_breakdowns

        # Get counterparty breakdowns using shared logic
        counterparty_list = get_counterparty_breakdowns(transactions, limit=counterparty_limit * 10)

        # Build a map of counterparty name to transactions for category lookup
        counterparty_to_txs = defaultdict(list)
        for tx in transactions:
            counterparty = tx.get('counterparty', '').strip() or 'Unknown'
            counterparty_to_txs[counterparty].append(tx)

        # Convert to display format and separate by transaction type
        counterparty_display = {}
        for cp in counterparty_list:
            # Get all transactions for this counterparty group
            # We need to match transactions by normalized name
            from omislisi_accounting.analysis.counterparty_utils import normalize_counterparty_name
            cp_normalized = normalize_counterparty_name(cp['name'])
            matching_txs = []
            for tx in transactions:
                tx_counterparty = tx.get('counterparty', '').strip() or 'Unknown'
                tx_normalized = normalize_counterparty_name(tx_counterparty)
                if tx_normalized == cp_normalized:
                    matching_txs.append(tx)

            counterparty_display[cp['name']] = {
                'count': cp['count'],
                'total': cp['total'],
                'transactions': matching_txs
            }

        # Separate counterparties by transaction type (income vs expense)
        income_counterparties = {}
        expense_counterparties = {}

        def get_category_display(transactions):
            """Get the category/tag for a set of transactions."""
            if not transactions:
                return ""

            # Get all categories from transactions
            categories = [tx.get('category', 'other') for tx in transactions if tx.get('category')]

            if not categories:
                return ""

            # Count category occurrences
            from collections import Counter
            category_counts = Counter(categories)

            # If all transactions have the same category, return it
            if len(category_counts) == 1:
                return list(category_counts.keys())[0]

            # If multiple categories, show the most common one(s)
            # Get the most common category
            most_common = category_counts.most_common(1)[0]

            # If it represents more than 50% of transactions, show just that one
            if most_common[1] / len(categories) > 0.5:
                return most_common[0]

            # Otherwise, show top 2 categories
            top_categories = category_counts.most_common(2)
            if len(top_categories) == 2:
                return f"{top_categories[0][0]}, {top_categories[1][0]}"
            else:
                return most_common[0]

        for counterparty, stats in counterparty_display.items():
            # Calculate income and expense totals separately
            income_txs = [tx for tx in stats['transactions'] if tx.get('type') == 'income']
            expense_txs = [tx for tx in stats['transactions'] if tx.get('type') == 'expense']

            income_total = sum(tx.get('amount', 0) for tx in income_txs)
            expense_total = sum(tx.get('amount', 0) for tx in expense_txs)

            if income_txs:
                income_counterparties[counterparty] = {
                    'count': len(income_txs),
                    'total': income_total,
                    'transactions': income_txs,
                    'category': get_category_display(income_txs)
                }

            if expense_txs:
                expense_counterparties[counterparty] = {
                    'count': len(expense_txs),
                    'total': expense_total,
                    'transactions': expense_txs,
                    'category': get_category_display(expense_txs)
                }

        # Sort income counterparties by total amount (descending)
        sorted_income = sorted(
            income_counterparties.items(),
            key=lambda x: abs(x[1]['total']),
            reverse=True
        )

        # Sort expense counterparties by total amount (descending)
        sorted_expense = sorted(
            expense_counterparties.items(),
            key=lambda x: abs(x[1]['total']),
            reverse=True
        )

        # Apply limit to each separately
        displayed_income_count = len(sorted_income)
        displayed_expense_count = len(sorted_expense)
        sorted_income = sorted_income[:counterparty_limit]
        sorted_expense = sorted_expense[:counterparty_limit]

        # Display income counterparties
        if sorted_income:
            click.echo(f"\n--- Income Counterparties (Top {min(displayed_income_count, counterparty_limit)}) ---")
            click.echo(f"\n{'Counterparty':<45} {'Count':>6} {'Total Amount':>15} {'Category':<35}")
            click.echo("-" * 105)

            for counterparty, stats in sorted_income:
                counterparty_display = counterparty[:44] if len(counterparty) <= 44 else counterparty[:41] + "..."
                category = stats.get('category', '') if stats.get('category') else ''
                click.echo(f"{counterparty_display:<45} {stats['count']:>6}  €{stats['total']:>13,.2f} {category:<35}")

            if displayed_income_count > counterparty_limit:
                click.echo(f"\n... and {displayed_income_count - counterparty_limit} more income counterparties (use --counterparty-limit to see more)")

        # Display expense counterparties
        if sorted_expense:
            click.echo(f"\n--- Expense Counterparties (Top {min(displayed_expense_count, counterparty_limit)}) ---")
            click.echo(f"\n{'Counterparty':<45} {'Count':>6} {'Total Amount':>15} {'Category':<35}")
            click.echo("-" * 105)

            for counterparty, stats in sorted_expense:
                counterparty_display = counterparty[:44] if len(counterparty) <= 44 else counterparty[:41] + "..."
                category = stats.get('category', '') if stats.get('category') else ''
                click.echo(f"{counterparty_display:<45} {stats['count']:>6}  €{stats['total']:>13,.2f} {category:<35}")

            if displayed_expense_count > counterparty_limit:
                click.echo(f"\n... and {displayed_expense_count - counterparty_limit} more expense counterparties (use --counterparty-limit to see more)")

    click.echo("\nReport generated!")


@cli.command()
@click.option("--year", help="Year to analyze (e.g., 2025). Required if --from-month not specified.")
@click.option("--from-month", help="Start month in YYYY-MM format (e.g., 2025-01)")
@click.option("--to-month", help="End month in YYYY-MM format (e.g., 2025-12). Defaults to end of year if --year specified, or same as --from-month if only --from-month specified.")
@click.option("--category", help="Filter by category (e.g., 'salary' or 'salary:founders')")
@click.option("--counterparty", help="Filter by counterparty name (case-insensitive, partial match supported)")
@click.option(
    "--reports-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=REPORTS_PATH,
    help="Path to the reports directory",
)
def trends(year: str, from_month: str, to_month: str, category: str, counterparty: str, reports_path: Path):
    """Show month-by-month trends for a category or counterparty over a time range."""
    from collections import defaultdict

    # Validate inputs
    if not year and not from_month:
        click.echo("Error: Must specify either --year or --from-month", err=True)
        return

    if from_month:
        try:
            datetime.strptime(from_month, '%Y-%m')
        except ValueError:
            click.echo(f"Error: Invalid --from-month format. Use YYYY-MM (e.g., 2025-01)", err=True)
            return

        if to_month:
            try:
                datetime.strptime(to_month, '%Y-%m')
            except ValueError:
                click.echo(f"Error: Invalid --to-month format. Use YYYY-MM (e.g., 2025-12)", err=True)
                return
        else:
            # Default to same as from_month if not specified
            to_month = from_month
    else:
        # Year specified, default to full year
        if not to_month:
            to_month = f"{year}-12"
        if not from_month:
            from_month = f"{year}-01"

    # Validate category if specified
    if category:
        from omislisi_accounting.domain.categories import get_all_categories
        all_categories = get_all_categories()
        category_lower = category.lower()

        is_valid = False
        if ":" in category_lower:
            base_cat, tag = category_lower.split(":", 1)
            if base_cat in [c.lower() for c in all_categories]:
                is_valid = True
        else:
            if category_lower in [c.lower() for c in all_categories]:
                is_valid = True

        if not is_valid:
            click.echo(f"Error: Unknown category '{category}'", err=True)
            click.echo(f"\nAvailable categories:")
            for cat in sorted(all_categories):
                click.echo(f"  - {cat}")
            return

    # Generate list of months to analyze
    start_date = datetime.strptime(from_month, '%Y-%m')
    end_date = datetime.strptime(to_month, '%Y-%m')

    months_to_analyze = []
    current = start_date
    while current <= end_date:
        months_to_analyze.append(current.strftime('%Y-%m'))
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    # Determine which years we need to load
    years_to_load = set()
    for month_str in months_to_analyze:
        years_to_load.add(month_str[:4])

    click.echo(f"Analyzing trends from {from_month} to {to_month}")
    if category:
        click.echo(f"Filter: Category = {category}")
    if counterparty:
        click.echo(f"Filter: Counterparty = {counterparty}")
    click.echo(f"Loading data from years: {', '.join(sorted(years_to_load))}")

    # Get all transactions from all required years
    all_transactions = []
    for year_str in sorted(years_to_load):
        year_reports_path = reports_path / year_str
        if not year_reports_path.exists():
            click.echo(f"Warning: Year directory {year_reports_path} does not exist, skipping", err=True)
            continue

        files = get_all_transaction_files(year_reports_path)
        if files:
            year_transactions = parse_all_files(files, silent=True)
            all_transactions.extend(year_transactions)
            click.echo(f"Loaded {len(year_transactions)} transactions from {year_str}")

    if not all_transactions:
        click.echo("No transaction files found!", err=True)
        return

    # Add categories
    for transaction in all_transactions:
        transaction['category'] = categorize_transaction(
            transaction.get('description', ''),
            transaction.get('type', ''),
            transaction.get('amount'),
            transaction.get('counterparty'),
            transaction.get('account')
        )

    # Helper function to apply filters
    def apply_filters(tx_list: list, cat_filter: str = None, cp_filter: str = None) -> list:
        """Apply category and counterparty filters to a transaction list."""
        filtered = tx_list

        if cat_filter:
            category_lower = cat_filter.lower()
            if ":" in category_lower:
                filtered = [
                    tx for tx in filtered
                    if tx.get('category', '').lower() == category_lower
                ]
            else:
                filtered = [
                    tx for tx in filtered
                    if tx.get('category', '').lower().startswith(category_lower + ':') or
                       tx.get('category', '').lower() == category_lower
                ]

        if cp_filter:
            import re
            import unicodedata

            def normalize_counterparty_name(name: str) -> str:
                normalized = name.lower()
                normalized = unicodedata.normalize('NFD', normalized)
                normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
                normalized = re.sub(r'\bss\s+d\.o\.o\.', 'ss d.o.o.', normalized)
                normalized = re.sub(r'\bss\s+d\.o\.o\b', 'ss d.o.o.', normalized)
                normalized = re.sub(r',\s*(d\.o\.o\.?|d\.d\.?|s\.p\.?|z\.b\.o\.?)', r' \1', normalized)
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
                    normalized = re.sub(r'.*(ctrp|in-fit|infit).*', 'in-fit d.o.o.', normalized)

                return normalized

            cp_search = normalize_counterparty_name(cp_filter)
            filtered = [
                tx for tx in filtered
                if cp_search in normalize_counterparty_name(tx.get('counterparty', ''))
            ]

        return filtered

    # Analyze each month
    monthly_data = {}
    for month_str in months_to_analyze:
        month_transactions = [
            tx for tx in all_transactions
            if tx.get('date') and tx['date'].startswith(month_str)
        ]

        # Apply filters
        month_transactions = apply_filters(month_transactions, category, counterparty)

        # Generate summary
        summary = generate_summary(month_transactions)
        monthly_data[month_str] = {
            'summary': summary,
            'transactions': month_transactions
        }

    # Display trends
    click.echo("\n" + "="*90)
    trend_title = f"TRENDS: {from_month} to {to_month}"
    if category:
        trend_title += f" - Category: {category}"
    if counterparty:
        trend_title += f" - Counterparty: {counterparty}"
    click.echo(trend_title)
    click.echo("="*90)

    # Table header
    click.echo(f"\n{'Month':<12} {'Income':>15} {'Expenses':>15} {'Net':>15} {'Change':>15} {'Txns':>8}")
    click.echo("-" * 90)

    prev_net = None
    for month_str in months_to_analyze:
        data = monthly_data[month_str]
        summary = data['summary']

        # Calculate change from previous month
        change_str = ""
        if prev_net is not None:
            net_change = summary['net'] - prev_net
            change_pct = (net_change / abs(prev_net) * 100) if prev_net != 0 else (float('inf') if net_change > 0 else float('-inf'))
            if abs(change_pct) < float('inf'):
                change_str = f"€{net_change:>12,.2f} ({change_pct:+.1f}%)"
            else:
                change_str = f"€{net_change:>12,.2f}"
        else:
            change_str = "-"

        click.echo(f"{month_str:<12} €{summary['total_income']:>13,.2f} €{summary['total_expenses']:>13,.2f} €{summary['net']:>13,.2f} {change_str:>15} {summary['transaction_count']:>8}")

        prev_net = summary['net']

    # Summary statistics
    click.echo("\n" + "-" * 90)
    total_income = sum(d['summary']['total_income'] for d in monthly_data.values())
    total_expenses = sum(d['summary']['total_expenses'] for d in monthly_data.values())
    total_net = sum(d['summary']['net'] for d in monthly_data.values())
    total_txns = sum(d['summary']['transaction_count'] for d in monthly_data.values())
    avg_net = total_net / len(monthly_data) if monthly_data else 0

    click.echo(f"{'Total':<12} €{total_income:>13,.2f} €{total_expenses:>13,.2f} €{total_net:>13,.2f} {'':>15} {total_txns:>8}")
    click.echo(f"{'Average':<12} {'':>15} {'':>15} €{avg_net:>13,.2f} {'':>15} {total_txns // len(monthly_data) if monthly_data else 0:>8}")

    # Show category breakdown if category filter not specified
    if not category and not counterparty:
        click.echo("\n--- Category Breakdown by Month ---")
        # Get all categories across all months
        all_cats = set()
        for data in monthly_data.values():
            breakdown = generate_category_breakdown(data['transactions'])
            all_cats.update(breakdown.keys())

        # Show top categories
        category_totals = defaultdict(float)
        for data in monthly_data.values():
            breakdown = generate_category_breakdown(data['transactions'])
            for cat, cat_data in breakdown.items():
                category_totals[cat] += abs(cat_data.get('total', 0))

        top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:10]

        for cat, _ in top_categories:
            click.echo(f"\n{cat}:")
            click.echo(f"{'Month':<12} {'Total':>15} {'Count':>8}")
            click.echo("-" * 40)
            for month_str in months_to_analyze:
                data = monthly_data[month_str]
                breakdown = generate_category_breakdown(data['transactions'])
                cat_data = breakdown.get(cat, {})
                cat_total = cat_data.get('total', 0)
                cat_count = cat_data.get('count', 0)
                if cat_count > 0:
                    click.echo(f"{month_str:<12} €{cat_total:>13,.2f} {cat_count:>8}")

    click.echo("\nTrends analysis complete!")


@cli.command()
@click.argument("category")
@click.option("--year", help="Filter by year (e.g., 2025)")
@click.option("--month", help="Filter by month in YYYY-MM format")
@click.option("--type", type=click.Choice(['income', 'expense', 'all'], case_sensitive=False), default='all', help="Transaction type")
@click.option("--min-amount", type=float, help="Minimum amount (absolute value)")
@click.option("--max-amount", type=float, help="Maximum amount (absolute value)")
@click.option("--limit", type=int, default=50, help="Maximum number of transactions to show")
@click.option("--sort", type=click.Choice(['date', 'amount', 'description'], case_sensitive=False), default='date', help="Sort by")
@click.option("--by-counterparty", is_flag=True, help="Aggregate and show breakdown by counterparty instead of individual transactions")
@click.option(
    "--reports-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=REPORTS_PATH,
    help="Path to the reports directory",
)
def category(
    category: str,
    year: str,
    month: str,
    type: str,
    min_amount: float,
    max_amount: float,
    limit: int,
    sort: str,
    by_counterparty: bool,
    reports_path: Path
):
    """Drill down into a specific category to see individual transactions."""
    from omislisi_accounting.domain.categories import get_all_categories

    # Validate category (support base categories and tags)
    all_categories = get_all_categories()
    category_lower = category.lower()

    # Check if it's a base category or a tagged category
    is_valid = False
    if ":" in category_lower:
        # Check if tagged category exists (e.g., "salary:founders")
        base_cat, tag = category_lower.split(":", 1)
        if base_cat in [c.lower() for c in all_categories]:
            is_valid = True
    else:
        # Check if base category exists (e.g., "salary")
        if category_lower in [c.lower() for c in all_categories]:
            is_valid = True

    if not is_valid:
        click.echo(f"Error: Unknown category '{category}'", err=True)
        click.echo(f"\nAvailable categories:")
        for cat in sorted(all_categories):
            click.echo(f"  - {cat}")
        click.echo(f"\nYou can also use tags like 'salary:founders', 'salary:students', etc.")
        return

    # Extract year from month if needed
    if month and not year:
        try:
            month_date = datetime.strptime(month, '%Y-%m')
            year = str(month_date.year)
        except ValueError:
            click.echo(f"Error: Invalid month format. Use YYYY-MM (e.g., 2025-08)", err=True)
            return

    # Filter by year if specified
    if year:
        reports_path = reports_path / year
        if not reports_path.exists():
            click.echo(f"Error: Year directory {reports_path} does not exist", err=True)
            return

    click.echo(f"Loading transactions from: {reports_path}")
    files = get_all_transaction_files(reports_path)
    transactions = parse_all_files(files, silent=True)

    # Filter by month if specified
    if month:
        transactions = [
            tx for tx in transactions
            if tx.get('date') and tx['date'].startswith(month)
        ]

    # Categorize transactions
    for transaction in transactions:
        transaction['category'] = categorize_transaction(
            transaction.get('description', ''),
            transaction.get('type', ''),
            transaction.get('amount'),
            transaction.get('counterparty'),
            transaction.get('account')
        )

    # Filter by category (case-insensitive)
    # Support both base category (e.g., "salary") and tagged category (e.g., "salary:founders")
    category_lower = category.lower()
    if ":" in category_lower:
        # Specific tag requested (e.g., "salary:founders")
        category_transactions = [
            tx for tx in transactions
            if tx.get('category', '').lower() == category_lower
        ]
    else:
        # Base category requested - match all tags (e.g., "salary" matches "salary:founders", "salary:students", etc.)
        category_transactions = [
            tx for tx in transactions
            if tx.get('category', '').lower().startswith(category_lower + ':') or
               tx.get('category', '').lower() == category_lower
        ]

    # Filter by type
    if type != 'all':
        category_transactions = [
            tx for tx in category_transactions
            if tx.get('type', '').lower() == type.lower()
        ]

    # Filter by amount
    if min_amount is not None:
        category_transactions = [
            tx for tx in category_transactions
            if abs(tx.get('amount', 0)) >= min_amount
        ]

    if max_amount is not None:
        category_transactions = [
            tx for tx in category_transactions
            if abs(tx.get('amount', 0)) <= max_amount
        ]

    # Sort transactions
    if sort == 'date':
        category_transactions.sort(key=lambda x: x.get('date', ''), reverse=True)
    elif sort == 'amount':
        category_transactions.sort(key=lambda x: abs(x.get('amount', 0)), reverse=True)
    elif sort == 'description':
        category_transactions.sort(key=lambda x: x.get('description', '').lower())

    # Calculate summary (before limiting)
    total_count = len(category_transactions)
    total_amount = sum(tx.get('amount', 0) for tx in category_transactions)
    income_count = len([tx for tx in category_transactions if tx.get('type') == 'income'])
    expense_count = len([tx for tx in category_transactions if tx.get('type') == 'expense'])

    # Display results
    click.echo("\n" + "=" * 80)
    click.echo(f"CATEGORY: {category.upper()}")
    click.echo("=" * 80)
    if month:
        click.echo(f"Period: {month}")
    elif year:
        click.echo(f"Year: {year}")
    else:
        click.echo("Period: All time")

    click.echo(f"\nSummary:")
    click.echo(f"  Total Amount: €{total_amount:>15,.2f}")
    click.echo(f"  Income: {income_count:4} transactions")
    click.echo(f"  Expenses: {expense_count:4} transactions")

    if not category_transactions:
        click.echo("\nNo transactions found matching the criteria.")
        return

    if by_counterparty:
        # Use shared counterparty breakdown function for consistency
        from omislisi_accounting.analysis.counterparty_utils import get_counterparty_breakdowns

        # Get counterparty breakdowns using shared logic
        counterparty_list = get_counterparty_breakdowns(category_transactions, limit=limit * 10)

        # Convert to display format
        counterparty_display = {}
        for cp in counterparty_list:
            # Get all transactions for this counterparty group
            from omislisi_accounting.analysis.counterparty_utils import normalize_counterparty_name
            cp_normalized = normalize_counterparty_name(cp['name'])
            matching_txs = []
            for tx in category_transactions:
                tx_counterparty = tx.get('counterparty', '').strip() or 'Unknown'
                tx_normalized = normalize_counterparty_name(tx_counterparty)
                if tx_normalized == cp_normalized:
                    matching_txs.append(tx)

            counterparty_display[cp['name']] = {
                'count': cp['count'],
                'total': cp['total'],
                'transactions': matching_txs
            }

        # Sort counterparties by absolute total (like dashboard)
        sorted_counterparties = sorted(
            counterparty_display.items(),
            key=lambda x: abs(x[1]['total']),
            reverse=True
        )

        # Apply limit
        displayed_count = len(sorted_counterparties)
        sorted_counterparties = sorted_counterparties[:limit]

        click.echo(f"\nCounterparty Breakdown ({displayed_count} unique counterparties):")
        click.echo(f"\n{'Counterparty':<50} {'Count':>8} {'Total Amount':>15}")
        click.echo("-" * 80)

        for counterparty, stats in sorted_counterparties:
            counterparty_display = counterparty[:49] if len(counterparty) <= 49 else counterparty[:46] + "..."
            total_amount = stats['total']
            amount_str = f"€{total_amount:>13,.2f}" if total_amount >= 0 else f"€{total_amount:>12,.2f}"
            click.echo(f"{counterparty_display:<50} {stats['count']:>8}  {amount_str}")

        if displayed_count > limit:
            click.echo(f"\n... and {displayed_count - limit} more counterparties (use --limit to see more)")
    else:
        # Show individual transactions
        category_transactions = category_transactions[:limit]

        click.echo(f"\nShowing {len(category_transactions)} of {total_count} transactions")

        if category_transactions:
            click.echo(f"\n{'Date':<12} {'Type':<10} {'Amount':>12} {'Source File':<25} {'Description':<30}")
            click.echo("-" * 100)
            for tx in category_transactions:
                date_str = tx.get('date', 'N/A')[:10] if tx.get('date') else 'N/A'
                tx_type = tx.get('type', 'unknown')[:9]
                amount = tx.get('amount', 0)
                source_file = tx.get('source_file', 'unknown')[:24]
                desc = tx.get('description', '')[:29]
                click.echo(f"{date_str:<12} {tx_type:<10} €{amount:>11,.2f} {source_file:<25} {desc:<30}")

            if total_count > limit:
                click.echo(f"\n... and {total_count - limit} more transactions (use --limit to see more)")


@cli.command()
@click.option("--year", help="Filter by year (e.g., 2025)")
@click.option("--month", help="Filter by month in YYYY-MM format")
@click.option("--min-amount", type=float, help="Minimum total amount per counterparty")
@click.option("--limit", type=int, default=50, help="Maximum number of counterparties to show")
@click.option("--sort", type=click.Choice(['count', 'amount', 'name'], case_sensitive=False), default='count', help="Sort by: count (frequency), amount (total), or name")
@click.option(
    "--reports-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=REPORTS_PATH,
    help="Path to the reports directory",
)
def counterparties(
    year: str,
    month: str,
    min_amount: float,
    limit: int,
    sort: str,
    reports_path: Path
):
    """List counterparties and aggregate transactions (expenses and income) by frequency and total amount."""
    from omislisi_accounting.analysis.counterparty_utils import get_counterparty_breakdowns

    # Extract year from month if needed
    if month and not year:
        try:
            month_date = datetime.strptime(month, '%Y-%m')
            year = str(month_date.year)
        except ValueError:
            click.echo(f"Error: Invalid month format. Use YYYY-MM (e.g., 2025-08)", err=True)
            return

    # Filter by year if specified
    if year:
        reports_path = reports_path / year
        if not reports_path.exists():
            click.echo(f"Error: Year directory {reports_path} does not exist", err=True)
            return

    click.echo(f"Loading transactions from: {reports_path}")
    files = get_all_transaction_files(reports_path)
    transactions = parse_all_files(files, silent=True)

    # Filter by month if specified
    if month:
        transactions = [
            tx for tx in transactions
            if tx.get('date') and tx['date'].startswith(month)
        ]

    # Include both expenses and income (like dashboard)
    # Don't filter - show all transactions
    if not transactions:
        click.echo("\nNo transactions found matching the criteria.")
        return

    # Use the same grouping logic as the dashboard - no aggressive merging
    # This ensures both tools work the same way
    counterparty_list = get_counterparty_breakdowns(transactions, limit=limit * 10)  # Get more than limit for filtering

    # Convert to dictionary format for compatibility with existing code
    counterparty_stats = {}
    for cp in counterparty_list:
        # Check if we should filter by minimum amount
        if min_amount is not None and abs(cp['total']) < min_amount:
            continue

        counterparty_stats[cp['name']] = {
            'count': cp['count'],
            'total': cp['total'],
            'transactions': []  # Not needed for display
        }

    # Sort counterparties
    if sort == 'count':
        sorted_counterparties = sorted(
            counterparty_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
    elif sort == 'amount':
        # Sort by absolute value (like dashboard) so largest expenses/income appear first
        sorted_counterparties = sorted(
            counterparty_stats.items(),
            key=lambda x: abs(x[1]['total']),
            reverse=True
        )
    else:  # sort == 'name'
        sorted_counterparties = sorted(counterparty_stats.items(), key=lambda x: x[0].lower())

    # Display results
    click.echo("\n" + "="*80)
    click.echo("COUNTERPARTY ANALYSIS")
    click.echo("="*80)

    if month:
        click.echo(f"Month: {month}")
    elif year:
        click.echo(f"Year: {year}")
    else:
        click.echo("Period: All time")

    # Calculate totals for display
    total_expenses = sum(abs(tx.get('amount', 0)) for tx in transactions if tx.get('type') == 'expense')
    total_income = sum(tx.get('amount', 0) for tx in transactions if tx.get('type') == 'income')
    expense_count = sum(1 for tx in transactions if tx.get('type') == 'expense')
    income_count = sum(1 for tx in transactions if tx.get('type') == 'income')

    click.echo(f"\nTotal transactions: {len(transactions)}")
    click.echo(f"  Expenses: {expense_count} transactions, €{total_expenses:,.2f}")
    click.echo(f"  Income: {income_count} transactions, €{total_income:,.2f}")
    click.echo(f"Unique counterparties: {len(counterparty_stats)}")

    if sorted_counterparties:
        click.echo(f"\n{'Counterparty':<50} {'Count':>8} {'Total Amount':>15}")
        click.echo("-" * 80)

        for counterparty, stats in sorted_counterparties[:limit]:
            counterparty_display = counterparty[:49] if len(counterparty) <= 49 else counterparty[:46] + "..."
            # Format: counterparty (50 chars) + space + count (8 chars) + space + € + amount (14 chars)
            # Show amount with sign preserved (negative for expenses, positive for income)
            total_amount = stats['total']
            amount_str = f"€{total_amount:>13,.2f}" if total_amount >= 0 else f"€{total_amount:>12,.2f}"
            click.echo(f"{counterparty_display:<50} {stats['count']:>8}  {amount_str}")

        if len(sorted_counterparties) > limit:
            click.echo(f"\n... and {len(sorted_counterparties) - limit} more counterparties (use --limit to see more)")

        # Summary statistics
        # Calculate totals from all transactions, not just displayed ones
        total_all = sum(tx.get('amount', 0) for tx in transactions)
        click.echo(f"\nNet total (income - expenses): €{total_all:,.2f}")
        if len(counterparty_stats) > 0:
            click.echo(f"Average per counterparty: €{total_all / len(counterparty_stats):,.2f}")
    else:
        click.echo("\nNo counterparties found matching the criteria.")


@cli.command()
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path("./dashboard"),
    help="Directory to write HTML files",
)
@click.option(
    "--reports-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=REPORTS_PATH,
    help="Path to the reports directory",
)
@click.option(
    "--year",
    type=int,
    default=None,
    help="Current year for YTD calculations (defaults to current year)",
)
@click.option(
    "--month",
    help="Default month to show in YYYY-MM format (defaults to most recent month with data). The dashboard will include all months and allow switching between them.",
)
def generate_dashboard(output_dir: Path, reports_path: Path, year: int, month: str):
    """Generate static HTML dashboard with financial trends and analysis."""
    from omislisi_accounting.analysis.dashboard_data import collect_dashboard_data
    from omislisi_accounting.templates.renderer import render_dashboard

    # Determine current year
    if year is None:
        year = datetime.now().year

    # Validate and parse month if provided
    selected_month = None
    if month:
        try:
            month_date = datetime.strptime(month, '%Y-%m')
            selected_month = month_date
            # Update year if month is in a different year
            if month_date.year != year:
                year = month_date.year
        except ValueError:
            click.echo(f"Error: Invalid month format. Use YYYY-MM (e.g., 2025-08)", err=True)
            return

    click.echo(f"Generating dashboard for year {year}...")
    if selected_month:
        click.echo(f"Default month: {month}")
    click.echo(f"Using reports from: {reports_path}")
    click.echo(f"Output directory: {output_dir}")
    click.echo("Note: Dashboard will include all available months with month selector")

    # Collect dashboard data
    click.echo("Collecting transaction data...")
    try:
        dashboard_data = collect_dashboard_data(reports_path, year, selected_month)
        click.echo(f"Collected data for {dashboard_data['metadata']['total_transactions']} transactions")
    except Exception as e:
        click.echo(f"Error collecting data: {e}", err=True)
        import traceback
        traceback.print_exc()
        return

    # Render dashboard
    click.echo("Rendering HTML pages...")
    try:
        render_dashboard(dashboard_data, output_dir)
        click.echo(f"\nDashboard generated successfully in {output_dir}")
        click.echo(f"Open {output_dir / 'index.html'} in your browser to view the dashboard")
    except Exception as e:
        click.echo(f"Error rendering dashboard: {e}", err=True)
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    cli()

