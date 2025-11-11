"""Dashboard template rendering."""

import json
import urllib.parse
from pathlib import Path
from typing import Dict, Any
from string import Template


def render_dashboard(dashboard_data: Dict[str, Any], output_dir: Path):
    """Render all dashboard HTML pages.

    This function safely overwrites the output directory by:
    1. Cleaning all existing HTML files
    2. Removing and recreating the static directory
    3. Generating all new files

    This ensures no orphaned files are left behind when regenerating the dashboard.
    """
    import shutil

    output_dir.mkdir(parents=True, exist_ok=True)

    # Clean up existing HTML files to ensure no orphaned files
    # List of expected HTML files we generate
    expected_html_files = {
        'index.html',
        'ytd.html',
        'trends_12m.html',
        'categories.html',
        'counterparties.html'
    }

    # Remove all HTML files in the output directory (including any orphaned ones)
    for html_file in output_dir.glob('*.html'):
        html_file.unlink()

    # Remove and recreate static directory to ensure clean state
    static_dir = output_dir / "static"
    if static_dir.exists():
        shutil.rmtree(static_dir)
    static_dir.mkdir(exist_ok=True)

    # Copy static files
    templates_dir = Path(__file__).parent

    # Copy CSS and JS files
    css_source = templates_dir / "static" / "dashboard.css"
    js_source = templates_dir / "static" / "dashboard.js"

    if css_source.exists():
        shutil.copy(css_source, static_dir / "dashboard.css")
    if js_source.exists():
        shutil.copy(js_source, static_dir / "dashboard.js")

    # Render all pages (this will create the expected HTML files)
    render_index(dashboard_data, output_dir)
    render_categories(dashboard_data, output_dir)
    render_counterparties(dashboard_data, output_dir)
    render_category_trends(dashboard_data, output_dir)
    render_counterparty_trends(dashboard_data, output_dir)


def load_template(template_name: str) -> str:
    """Load a template file."""
    templates_dir = Path(__file__).parent
    template_path = templates_dir / template_name
    if template_path.exists():
        return template_path.read_text(encoding='utf-8')
    return ""


def render_base_template(page: str, page_title: str, content: str, dashboard_data: Dict[str, Any], show_month_selector: bool = True) -> str:
    """Render base template with page content."""
    template = load_template("base.html")
    if not template:
        return content

    # Set navigation active states
    nav_vars = {
        'nav_index': 'active' if page == 'index' else '',
        'nav_year_comparison': 'active' if page == 'year_comparison' else '',
        'nav_categories': 'active' if page == 'categories' else '',
        'nav_counterparties': 'active' if page == 'counterparties' else '',
        'nav_category_trends': 'active' if page == 'category_trends' else '',
        'nav_counterparty_trends': 'active' if page == 'counterparty_trends' else '',
    }

    # Month selector HTML - only show on pages that support month filtering
    month_selector_html = ''
    if show_month_selector:
        month_selector_html = '''    <div class="month-selector-bar">
        <div class="month-selector-container">
            <label for="month-selector" style="margin-right: 0.5rem; font-weight: 600;">Select Month:</label>
            <select id="month-selector" class="month-selector">
                <!-- Options will be populated by JavaScript -->
            </select>
        </div>
    </div>'''

    # Replace template variables
    result = template.replace("{{ page_title }}", page_title + " - " if page_title else "")
    result = result.replace("{{ content }}", content)
    result = result.replace("{{ generated_at }}", dashboard_data['metadata']['generated_at'])
    result = result.replace("{{ month_selector_html }}", month_selector_html)

    # Replace navigation variables
    for key, value in nav_vars.items():
        result = result.replace(f"{{{{ {key} }}}}", value)

    return result


def render_index(dashboard_data: Dict[str, Any], output_dir: Path):
    """Render overview page with period selector."""
    current_month = dashboard_data['current_month']
    ytd = dashboard_data['ytd']
    default_month = dashboard_data['metadata']['default_month']
    current_year = dashboard_data['metadata']['current_year']

    content = f"""
    <div class="card">
        <h2 class="card-header">Overview</h2>
        <div style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
            <div style="display: flex; align-items: center;">
                <label for="period-selector" style="margin-right: 0.5rem; font-weight: 600;">Period:</label>
                <select id="period-selector" class="month-selector" style="min-width: 200px;">
                    <option value="ytd">Year-to-Date</option>
                </select>
            </div>
            <div id="custom-range-container" style="display: none; padding: 0.75rem 1rem; background-color: #f8f9fa; border-radius: 4px; border: 1px solid #bdc3c7;">
                <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                    <div>
                        <label for="custom-range-start" style="display: block; margin-bottom: 0.5rem; font-weight: 600; font-size: 0.9rem;">Start Date:</label>
                        <input type="date" id="custom-range-start" class="month-selector" style="padding: 0.5rem;">
                    </div>
                    <div>
                        <label for="custom-range-end" style="display: block; margin-bottom: 0.5rem; font-weight: 600; font-size: 0.9rem;">End Date:</label>
                        <input type="date" id="custom-range-end" class="month-selector" style="padding: 0.5rem;">
                    </div>
                    <div style="display: flex; align-items: flex-end;">
                        <button id="apply-custom-range" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #3498db; border-radius: 4px; background: #3498db; color: white; font-weight: 600;">Apply Range</button>
                    </div>
                </div>
            </div>
        </div>
        <div id="year-progress-container" style="margin-bottom: 1.5rem; display: none;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 0.9rem; color: #7f8c8d;">Year Progress</span>
                <span id="year-progress-text" style="font-size: 0.9rem; font-weight: 600; color: #34495e;"></span>
            </div>
            <div class="progress-bar-container">
                <div id="year-progress-bar" class="progress-bar-fill" style="width: 0%;"></div>
            </div>
        </div>
        <div class="card-grid">
            <div class="metric-card">
                <div class="metric-label period-label">Income</div>
                <div class="metric-value period-income positive">
                    €{ytd['summary']['total_income']:,.2f}
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label period-label">Expenses</div>
                <div class="metric-value period-expenses negative">
                    €{ytd['summary']['total_expenses']:,.2f}
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label period-label">Net</div>
                <div class="metric-value period-net {'positive' if ytd['summary']['net'] >= 0 else 'negative'}">
                    €{ytd['summary']['net']:,.2f}
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label period-label">Transactions</div>
                <div class="metric-value period-transactions">{ytd['summary']['transaction_count']}</div>
            </div>
        </div>
        <div class="card-grid" id="health-indicators-grid" style="margin-top: 1rem;">
            <div class="metric-card">
                <div class="metric-label">Savings Rate</div>
                <div class="metric-value health-savings-rate">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Expense Ratio</div>
                <div class="metric-value health-expense-ratio">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Transaction</div>
                <div class="metric-value health-avg-transaction">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Income/Expense Ratio</div>
                <div class="metric-value health-income-expense-ratio">-</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Period Comparison</h2>
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th class="text-right">Selected Period</th>
                    <th class="text-right" id="comparison-period-label">Previous Period</th>
                    <th class="text-right">Change</th>
                    <th class="text-right">Change %</th>
                </tr>
            </thead>
            <tbody id="comparison-tbody">
                <tr>
                    <td>Income</td>
                    <td class="text-right period-income">€{ytd['summary']['total_income']:,.2f}</td>
                    <td class="text-right comparison-income">-</td>
                    <td class="text-right period-income-change">-</td>
                    <td class="text-right period-income-change-pct">-</td>
                </tr>
                <tr>
                    <td>Expenses</td>
                    <td class="text-right period-expenses">€{ytd['summary']['total_expenses']:,.2f}</td>
                    <td class="text-right comparison-expenses">-</td>
                    <td class="text-right period-expense-change">-</td>
                    <td class="text-right period-expense-change-pct">-</td>
                </tr>
                <tr>
                    <td>Net</td>
                    <td class="text-right period-net {'positive' if ytd['summary']['net'] >= 0 else 'negative'}">
                        €{ytd['summary']['net']:,.2f}
                    </td>
                    <td class="text-right comparison-net">-</td>
                    <td class="text-right period-net-change">-</td>
                    <td class="text-right period-net-change-pct">-</td>
                </tr>
            </tbody>
        </table>
        <div id="insights-container" style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #ecf0f1;">
            <p style="color: #7f8c8d; text-align: center; padding: 0.5rem;">No significant insights for this period.</p>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Net Comparison</h2>
        <div class="chart-container small">
            <canvas id="netComparisonChart"></canvas>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Monthly Breakdown</h2>
        <div class="chart-container small">
            <canvas id="monthlyBreakdownChart"></canvas>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Recent Trends</h2>
        <div class="chart-container small">
            <canvas id="recentTrendsChart"></canvas>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Top Categories & Counterparties</h2>
        <div id="top-items-container">
            <div style="margin-bottom: 2rem;">
                <h3 style="font-size: 1.1rem; margin-bottom: 1rem; color: #34495e;">Top Categories</h3>
                <div id="top-categories" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem;">
                    <div>
                        <h4 style="font-size: 0.95rem; margin-bottom: 0.75rem; color: #7f8c8d; font-weight: 600;">Income</h4>
                        <div id="top-income-categories" style="min-height: 200px;"></div>
                    </div>
                    <div>
                        <h4 style="font-size: 0.95rem; margin-bottom: 0.75rem; color: #7f8c8d; font-weight: 600;">Expenses</h4>
                        <div id="top-expense-categories" style="min-height: 200px;"></div>
                    </div>
                </div>
            </div>
            <div>
                <h3 style="font-size: 1.1rem; margin-bottom: 1rem; color: #34495e;">Top Counterparties</h3>
                <div id="top-counterparties" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem;">
                    <div>
                        <h4 style="font-size: 0.95rem; margin-bottom: 0.75rem; color: #7f8c8d; font-weight: 600;">Income</h4>
                        <div id="top-income-counterparties" style="min-height: 200px;"></div>
                    </div>
                    <div>
                        <h4 style="font-size: 0.95rem; margin-bottom: 0.75rem; color: #7f8c8d; font-weight: 600;">Expenses</h4>
                        <div id="top-expense-counterparties" style="min-height: 200px;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Category Breakdown</h2>
        <div id="category-pagination-controls" style="margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span id="category-pagination-info">Showing 1-50 of <span id="category-total-count">0</span></span>
            </div>
            <div>
                <button id="category-prev-btn" style="padding: 0.5rem 1rem; margin-right: 0.5rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white;" disabled>Previous</button>
                <button id="category-next-btn" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white;">Next</button>
            </div>
        </div>
        <table class="category-breakdown-table">
            <thead>
                <tr>
                    <th>Category</th>
                    <th class="text-right">Total</th>
                    <th class="text-center">Count</th>
                </tr>
            </thead>
            <tbody id="category-breakdown-tbody">
                <!-- Will be populated by JavaScript -->
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2 class="card-header">Counterparties</h2>
        <div id="counterparty-pagination-controls" style="margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span id="counterparty-pagination-info">Showing 1-50 of <span id="counterparty-total-count">0</span></span>
            </div>
            <div>
                <button id="counterparty-prev-btn" style="padding: 0.5rem 1rem; margin-right: 0.5rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white;" disabled>Previous</button>
                <button id="counterparty-next-btn" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white;">Next</button>
            </div>
        </div>
        <table class="counterparty-breakdown-table">
            <thead>
                <tr>
                    <th class="sortable" data-sort="name" style="cursor: pointer;">Counterparty</th>
                    <th class="text-center sortable" data-sort="count" style="cursor: pointer;">Count</th>
                    <th class="text-right sortable" data-sort="total" style="cursor: pointer;">Total</th>
                </tr>
            </thead>
            <tbody id="counterparty-breakdown-tbody">
                <!-- Will be populated by JavaScript -->
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2 class="card-header">Quick Links</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <a href="categories.html" style="padding: 1rem; background: #27ae60; color: white; text-decoration: none; border-radius: 4px; text-align: center;">
                Categories
            </a>
            <a href="counterparties.html" style="padding: 1rem; background: #e74c3c; color: white; text-decoration: none; border-radius: 4px; text-align: center;">
                Counterparties
            </a>
        </div>
    </div>

    <script id="dashboard-data" type="application/json">
    {json.dumps({
        'available_months': dashboard_data['metadata']['available_months'],
        'default_month': default_month,
        'current_year': current_year,
        'all_months': dashboard_data['all_months'],
        'all_transactions': dashboard_data.get('all_transactions', [])
    })}
    </script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const data = JSON.parse(document.getElementById('dashboard-data').textContent);
        // Initialize selector first
        if (typeof initializeOverviewPeriodSelector === 'function') {{
            initializeOverviewPeriodSelector(data);
        }}
        // Update view after a short delay to ensure functions are loaded
        setTimeout(function() {{
            if (typeof updateOverviewPeriodView === 'function') {{
                updateOverviewPeriodView(data, 'ytd');
            }} else {{
                // Fallback: manually trigger update when selector changes
                const selector = document.getElementById('period-selector');
                if (selector) {{
                    selector.addEventListener('change', function() {{
                        if (typeof updateOverviewPeriodView === 'function') {{
                            updateOverviewPeriodView(data, this.value);
                        }}
                    }});
                }}
            }}
        }}, 100);
    }});
    </script>
    """

    html = render_base_template('index', 'Overview', content, dashboard_data, show_month_selector=False)
    (output_dir / "index.html").write_text(html, encoding='utf-8')


def render_current_month(dashboard_data: Dict[str, Any], output_dir: Path):
    """Render current month page with period selector."""
    current_month = dashboard_data['current_month']
    default_month = dashboard_data['metadata']['default_month']
    current_year = dashboard_data['metadata']['current_year']

    content = f"""
    <div class="card">
        <h2 class="card-header">Period View</h2>
        <div style="margin-bottom: 1.5rem;">
            <label for="period-selector" style="margin-right: 0.5rem; font-weight: 600;">Period:</label>
            <select id="period-selector" class="month-selector" style="min-width: 200px;">
                <option value="month:{default_month}">{default_month}</option>
            </select>
        </div>
        <div class="card-grid">
            <div class="metric-card">
                <div class="metric-label period-label">Income</div>
                <div class="metric-value period-income positive">€{current_month['summary']['total_income']:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label period-label">Expenses</div>
                <div class="metric-value period-expenses negative">€{current_month['summary']['total_expenses']:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label period-label">Net</div>
                <div class="metric-value period-net {'positive' if current_month['summary']['net'] >= 0 else 'negative'}">
                    €{current_month['summary']['net']:,.2f}
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label period-label">Transactions</div>
                <div class="metric-value period-transactions">{current_month['summary']['transaction_count']}</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Period Comparison</h2>
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th class="text-right">Selected Period</th>
                    <th class="text-right" id="comparison-period-label">Previous Period</th>
                    <th class="text-right">Change</th>
                    <th class="text-right">Change %</th>
                </tr>
            </thead>
            <tbody id="comparison-tbody">
                <tr>
                    <td>Income</td>
                    <td class="text-right period-income">€{current_month['summary']['total_income']:,.2f}</td>
                    <td class="text-right comparison-income">€{current_month['summary']['total_income'] - current_month['comparison']['income_change']:,.2f}</td>
                    <td class="text-right period-income-change {'positive' if current_month['comparison']['income_change'] >= 0 else 'negative'}">
                        €{current_month['comparison']['income_change']:,.2f}
                    </td>
                    <td class="text-right period-income-change-pct {'positive' if current_month['comparison']['income_change_pct'] >= 0 else 'negative'}">
                        {current_month['comparison']['income_change_pct']:+.1f}%
                    </td>
                </tr>
                <tr>
                    <td>Expenses</td>
                    <td class="text-right period-expenses">€{current_month['summary']['total_expenses']:,.2f}</td>
                    <td class="text-right comparison-expenses">€{current_month['summary']['total_expenses'] - current_month['comparison']['expense_change']:,.2f}</td>
                    <td class="text-right period-expense-change {'positive' if current_month['comparison']['expense_change'] <= 0 else 'negative'}">
                        €{current_month['comparison']['expense_change']:,.2f}
                    </td>
                    <td class="text-right period-expense-change-pct {'positive' if current_month['comparison']['expense_change_pct'] <= 0 else 'negative'}">
                        {current_month['comparison']['expense_change_pct']:+.1f}%
                    </td>
                </tr>
                <tr>
                    <td>Net</td>
                    <td class="text-right period-net {'positive' if current_month['summary']['net'] >= 0 else 'negative'}">
                        €{current_month['summary']['net']:,.2f}
                    </td>
                    <td class="text-right comparison-net">€{current_month['summary']['net'] - current_month['comparison']['net_change']:,.2f}</td>
                    <td class="text-right period-net-change {'positive' if current_month['comparison']['net_change'] >= 0 else 'negative'}">
                        €{current_month['comparison']['net_change']:,.2f}
                    </td>
                    <td class="text-right period-net-change-pct {'positive' if current_month['comparison']['net_change_pct'] >= 0 else 'negative'}">
                        {current_month['comparison']['net_change_pct']:+.1f}%
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2 class="card-header">Category Breakdown</h2>
        <div id="category-pagination-controls" style="margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span id="category-pagination-info">Showing 1-50 of <span id="category-total-count">0</span></span>
            </div>
            <div>
                <button id="category-prev-btn" style="padding: 0.5rem 1rem; margin-right: 0.5rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white;" disabled>Previous</button>
                <button id="category-next-btn" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white;">Next</button>
            </div>
        </div>
        <table class="category-breakdown-table">
            <thead>
                <tr>
                    <th>Category</th>
                    <th class="text-right">Total</th>
                    <th class="text-center">Count</th>
                </tr>
            </thead>
            <tbody id="category-breakdown-tbody">
                <!-- Will be populated by JavaScript -->
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2 class="card-header">Counterparties</h2>
        <div id="counterparty-pagination-controls" style="margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span id="counterparty-pagination-info">Showing 1-50 of <span id="counterparty-total-count">0</span></span>
            </div>
            <div>
                <button id="counterparty-prev-btn" style="padding: 0.5rem 1rem; margin-right: 0.5rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white;" disabled>Previous</button>
                <button id="counterparty-next-btn" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white;">Next</button>
            </div>
        </div>
        <table class="counterparty-breakdown-table">
            <thead>
                <tr>
                    <th>Counterparty</th>
                    <th class="text-center">Count</th>
                    <th class="text-right">Total</th>
                </tr>
            </thead>
            <tbody id="counterparty-breakdown-tbody">
                <!-- Will be populated by JavaScript -->
            </tbody>
        </table>
    </div>

    <script id="dashboard-data" type="application/json">
    {json.dumps({
        'available_months': dashboard_data['metadata']['available_months'],
        'default_month': default_month,
        'current_year': current_year,
        'all_months': dashboard_data['all_months'],
        'all_transactions': dashboard_data.get('all_transactions', [])
    })}
    </script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const data = JSON.parse(document.getElementById('dashboard-data').textContent);
        initializePeriodViewSelector(data);
        updatePeriodView(data, 'month:{default_month}');
    }});
    </script>
    """

    html = render_base_template('current_month', 'Period View', content, dashboard_data, show_month_selector=False)
    (output_dir / "current_month.html").write_text(html, encoding='utf-8')


def render_ytd(dashboard_data: Dict[str, Any], output_dir: Path):
    """Render year-to-date page."""
    ytd = dashboard_data['ytd']

    # Build monthly progression data for chart
    monthly_labels = sorted(ytd['monthly_progression'].keys())
    monthly_income = [ytd['monthly_progression'][m]['total_income'] for m in monthly_labels]
    monthly_expenses = [ytd['monthly_progression'][m]['total_expenses'] for m in monthly_labels]
    monthly_net = [ytd['monthly_progression'][m]['net'] for m in monthly_labels]

    # Build category breakdown
    category_rows = ""
    for cat, data in sorted(ytd['breakdown'].items(), key=lambda x: abs(x[1].get('total', 0)), reverse=True):
        total = data.get('total', 0)
        count = data.get('count', 0)
        category_rows += f"""
        <tr>
            <td>{cat}</td>
            <td class="text-right">€{total:,.2f}</td>
            <td class="text-center">{count}</td>
        </tr>
        """

    content = f"""
    <div class="card">
        <h2 class="card-header">Year-to-Date: {ytd['period']}</h2>
        <div class="card-grid">
            <div class="metric-card">
                <div class="metric-label">Total Income</div>
                <div class="metric-value positive">€{ytd['summary']['total_income']:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Expenses</div>
                <div class="metric-value negative">€{ytd['summary']['total_expenses']:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Net</div>
                <div class="metric-value {'positive' if ytd['summary']['net'] >= 0 else 'negative'}">
                    €{ytd['summary']['net']:,.2f}
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Transactions</div>
                <div class="metric-value">{ytd['summary']['transaction_count']}</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Projected Annual</h2>
        <div class="card-grid">
            <div class="metric-card">
                <div class="metric-label">Projected Income</div>
                <div class="metric-value positive">€{ytd['projections']['projected_income']:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Projected Expenses</div>
                <div class="metric-value negative">€{ytd['projections']['projected_expenses']:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Projected Net</div>
                <div class="metric-value {'positive' if ytd['projections']['projected_net'] >= 0 else 'negative'}">
                    €{ytd['projections']['projected_net']:,.2f}
                </div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Monthly Progression</h2>
        <div class="chart-container">
            <canvas id="ytdProgressionChart"></canvas>
        </div>
    </div>

    <div class="card">
        <div class="expandable-section">
            <div class="expandable-header collapsed">
                <h2 class="card-header" style="margin: 0;">Category Breakdown</h2>
            </div>
            <div class="expandable-content">
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th class="text-right">Total</th>
                            <th class="text-center">Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        {category_rows}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script id="dashboard-data" type="application/json">
    {json.dumps({
        'monthly_labels': monthly_labels,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_net': monthly_net,
        'available_months': dashboard_data['metadata']['available_months'],
        'default_month': dashboard_data['metadata']['default_month'],
        'all_months': dashboard_data['all_months']
    })}
    </script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const data = JSON.parse(document.getElementById('dashboard-data').textContent);
        createLineChart('ytdProgressionChart', {{
            labels: data.monthly_labels,
            datasets: [
                {{
                    label: 'Income',
                    data: data.monthly_income,
                    borderColor: 'rgb(39, 174, 96)',
                    backgroundColor: 'rgba(39, 174, 96, 0.1)',
                    tension: 0.1
                }},
                {{
                    label: 'Expenses',
                    data: data.monthly_expenses,
                    borderColor: 'rgb(231, 76, 60)',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.1
                }},
                {{
                    label: 'Net',
                    data: data.monthly_net,
                    borderColor: 'rgb(52, 152, 219)',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.1
                }}
            ]
        }});
    }});
    </script>
    """

    html = render_base_template('ytd', f"Year-to-Date - {ytd['period']}", content, dashboard_data, show_month_selector=False)
    (output_dir / "ytd.html").write_text(html, encoding='utf-8')


def render_trends_12m(dashboard_data: Dict[str, Any], output_dir: Path):
    """Render last 12 months trends page."""
    trends_12m = dashboard_data['last_12_months']
    monthly_data = trends_12m['months']

    # Prepare chart data
    monthly_labels = sorted(monthly_data.keys())
    monthly_income = [monthly_data[m]['summary']['total_income'] for m in monthly_labels]
    monthly_expenses = [monthly_data[m]['summary']['total_expenses'] for m in monthly_labels]
    monthly_net = [monthly_data[m]['summary']['net'] for m in monthly_labels]

    # Build monthly breakdown table
    monthly_rows = ""
    prev_net = None
    for month in monthly_labels:
        summary = monthly_data[month]['summary']
        change_str = ""
        if prev_net is not None:
            net_change = summary['net'] - prev_net
            change_pct = (net_change / abs(prev_net) * 100) if prev_net != 0 else 0
            change_str = f"€{net_change:,.2f} ({change_pct:+.1f}%)"
        else:
            change_str = "-"

        monthly_rows += f"""
        <tr>
            <td>{month}</td>
            <td class="text-right">€{summary['total_income']:,.2f}</td>
            <td class="text-right">€{summary['total_expenses']:,.2f}</td>
            <td class="text-right {'positive' if summary['net'] >= 0 else 'negative'}">€{summary['net']:,.2f}</td>
            <td class="text-right">{change_str}</td>
            <td class="text-center">{summary['transaction_count']}</td>
        </tr>
        """
        prev_net = summary['net']

    content = f"""
    <div class="card">
        <h2 class="card-header">Last 12 Months: {trends_12m['period']}</h2>
        <div class="card-grid">
            <div class="metric-card">
                <div class="metric-label">Total Income</div>
                <div class="metric-value positive">€{trends_12m['summary']['total_income']:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Expenses</div>
                <div class="metric-value negative">€{trends_12m['summary']['total_expenses']:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Net</div>
                <div class="metric-value {'positive' if trends_12m['summary']['net'] >= 0 else 'negative'}">
                    €{trends_12m['summary']['net']:,.2f}
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Transactions</div>
                <div class="metric-value">{trends_12m['summary']['transaction_count']}</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Monthly Trends</h2>
        <div class="chart-container">
            <canvas id="trends12mChart"></canvas>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Monthly Breakdown</h2>
        <table>
            <thead>
                <tr>
                    <th>Month</th>
                    <th class="text-right">Income</th>
                    <th class="text-right">Expenses</th>
                    <th class="text-right">Net</th>
                    <th class="text-right">Change</th>
                    <th class="text-center">Txns</th>
                </tr>
            </thead>
            <tbody>
                {monthly_rows}
            </tbody>
        </table>
    </div>

    <script id="dashboard-data" type="application/json">
    {json.dumps({
        'monthly_labels': monthly_labels,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_net': monthly_net,
        'available_months': dashboard_data['metadata']['available_months'],
        'default_month': dashboard_data['metadata']['default_month'],
        'all_months': dashboard_data['all_months']
    })}
    </script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const data = JSON.parse(document.getElementById('dashboard-data').textContent);
        createLineChart('trends12mChart', {{
            labels: data.monthly_labels,
            datasets: [
                {{
                    label: 'Income',
                    data: data.monthly_income,
                    borderColor: 'rgb(39, 174, 96)',
                    backgroundColor: 'rgba(39, 174, 96, 0.1)',
                    tension: 0.1
                }},
                {{
                    label: 'Expenses',
                    data: data.monthly_expenses,
                    borderColor: 'rgb(231, 76, 60)',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.1
                }},
                {{
                    label: 'Net',
                    data: data.monthly_net,
                    borderColor: 'rgb(52, 152, 219)',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.1
                }}
            ]
        }});
    }});
    </script>
    """

    html = render_base_template('trends_12m', f"Last 12 Months - {trends_12m['period']}", content, dashboard_data, show_month_selector=False)
    (output_dir / "trends_12m.html").write_text(html, encoding='utf-8')


def render_year_comparison(dashboard_data: Dict[str, Any], output_dir: Path):
    """Render year comparison page."""
    comparison = dashboard_data['year_comparison']

    # Build comparison table
    comparison_rows = f"""
    <tr>
        <td>Income</td>
        <td class="text-right">€{comparison['current_summary']['total_income']:,.2f}</td>
        <td class="text-right">€{comparison['previous_summary']['total_income']:,.2f}</td>
        <td class="text-right {'positive' if comparison['changes']['income_change'] >= 0 else 'negative'}">
            €{comparison['changes']['income_change']:,.2f}
        </td>
        <td class="text-right {'positive' if comparison['changes']['income_change_pct'] >= 0 else 'negative'}">
            {comparison['changes']['income_change_pct']:+.1f}%
        </td>
    </tr>
    <tr>
        <td>Expenses</td>
        <td class="text-right">€{comparison['current_summary']['total_expenses']:,.2f}</td>
        <td class="text-right">€{comparison['previous_summary']['total_expenses']:,.2f}</td>
        <td class="text-right {'positive' if comparison['changes']['expense_change'] <= 0 else 'negative'}">
            €{comparison['changes']['expense_change']:,.2f}
        </td>
        <td class="text-right {'positive' if comparison['changes']['expense_change_pct'] <= 0 else 'negative'}">
            {comparison['changes']['expense_change_pct']:+.1f}%
        </td>
    </tr>
    <tr>
        <td>Net</td>
        <td class="text-right {'positive' if comparison['current_summary']['net'] >= 0 else 'negative'}">
            €{comparison['current_summary']['net']:,.2f}
        </td>
        <td class="text-right {'positive' if comparison['previous_summary']['net'] >= 0 else 'negative'}">
            €{comparison['previous_summary']['net']:,.2f}
        </td>
        <td class="text-right {'positive' if comparison['changes']['net_change'] >= 0 else 'negative'}">
            €{comparison['changes']['net_change']:,.2f}
        </td>
        <td class="text-right {'positive' if comparison['changes']['net_change_pct'] >= 0 else 'negative'}">
            {comparison['changes']['net_change_pct']:+.1f}%
        </td>
    </tr>
    <tr>
        <td>Transactions</td>
        <td class="text-right">{comparison['current_summary']['transaction_count']}</td>
        <td class="text-right">{comparison['previous_summary']['transaction_count']}</td>
        <td class="text-right">
            {comparison['current_summary']['transaction_count'] - comparison['previous_summary']['transaction_count']:+d}
        </td>
        <td></td>
    </tr>
    """

    # Build monthly comparison data for chart
    monthly_labels = []
    current_values = []
    previous_values = []
    for month in sorted(comparison['monthly_comparison'].keys()):
        monthly_labels.append(month)
        curr = comparison['monthly_comparison'][month]['current']
        prev = comparison['monthly_comparison'][month]['previous']
        current_values.append(curr['net'] if curr else 0)
        previous_values.append(prev['net'] if prev else 0)

    # Determine which months are being compared
    months_compared = sorted(comparison['monthly_comparison'].keys())
    if months_compared:
        period_label = f"YTD ({months_compared[0]} to {months_compared[-1]})"
    else:
        period_label = "YTD"

    content = f"""
    <div class="card">
        <h2 class="card-header">Year Comparison: {comparison['current_year']} vs {comparison['previous_year']} ({period_label})</h2>
        <p style="margin-bottom: 1rem; color: #666;">Comparing only months available in {comparison['current_year']} (year-to-date) with the same months from {comparison['previous_year']}.</p>
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th class="text-right">{comparison['current_year']}</th>
                    <th class="text-right">{comparison['previous_year']}</th>
                    <th class="text-right">Change</th>
                    <th class="text-right">Change %</th>
                </tr>
            </thead>
            <tbody>
                {comparison_rows}
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2 class="card-header">Monthly Net Comparison</h2>
        <div class="chart-container">
            <canvas id="yearComparisonChart"></canvas>
        </div>
    </div>

    <script id="dashboard-data" type="application/json">
    {json.dumps({
        'monthly_labels': monthly_labels,
        'current_values': current_values,
        'previous_values': previous_values,
        'available_months': dashboard_data['metadata']['available_months'],
        'default_month': dashboard_data['metadata']['default_month'],
        'all_months': dashboard_data['all_months']
    })}
    </script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const data = JSON.parse(document.getElementById('dashboard-data').textContent);
        createBarChart('yearComparisonChart', {{
            labels: data.monthly_labels,
            datasets: [
                {{
                    label: '{comparison['current_year']}',
                    data: data.current_values,
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',
                    borderColor: 'rgb(52, 152, 219)',
                    borderWidth: 1
                }},
                {{
                    label: '{comparison['previous_year']}',
                    data: data.previous_values,
                    backgroundColor: 'rgba(149, 165, 166, 0.7)',
                    borderColor: 'rgb(149, 165, 166)',
                    borderWidth: 1
                }}
            ]
        }});
    }});
    </script>
    """

    html = render_base_template('year_comparison', f"Year Comparison - {comparison['current_year']} vs {comparison['previous_year']}", content, dashboard_data, show_month_selector=False)
    (output_dir / "year_comparison.html").write_text(html, encoding='utf-8')


def render_categories(dashboard_data: Dict[str, Any], output_dir: Path):
    """Render categories page."""
    # Get all categories from YTD data for initial table rendering
    ytd = dashboard_data['ytd']
    breakdown = ytd['breakdown']

    # Build initial category list (will be updated by JavaScript)
    category_rows = ""
    for cat, data in sorted(breakdown.items(), key=lambda x: abs(x[1].get('total', 0)), reverse=True):
        total = data.get('total', 0)
        count = data.get('count', 0)
        # Format with proper color for positive/negative
        amount_color = '#27ae60' if total >= 0 else '#e74c3c'
        sign = '+' if total >= 0 else ''
        formatted_total = f"€{sign}{abs(total):,.2f}"

        category_rows += f"""
        <tr>
            <td><a href="category_trends.html?category={cat.replace(' ', '%20')}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">{cat}</a></td>
            <td class="text-right" style="color: {amount_color}; font-weight: 600;">{formatted_total}</td>
            <td class="text-center">{count}</td>
        </tr>
        """

        # Add tag breakdown if present
        if 'tags' in data and data['tags']:
            for tag, tag_data in sorted(data['tags'].items(), key=lambda x: abs(x[1].get('total', 0)), reverse=True):
                tag_total = tag_data.get('total', 0)
                tag_count = tag_data.get('count', 0)
                tag_amount_color = '#27ae60' if tag_total >= 0 else '#e74c3c'
                tag_sign = '+' if tag_total >= 0 else ''
                formatted_tag_total = f"€{tag_sign}{abs(tag_total):,.2f}"

                category_rows += f"""
                <tr style="background-color: #f8f9fa;">
                    <td style="padding-left: 2rem;">└─ <a href="category_trends.html?category={cat.replace(' ', '%20')}&tag={tag.replace(' ', '%20')}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">{tag}</a></td>
                    <td class="text-right" style="color: {tag_amount_color}; font-weight: 600;">{formatted_tag_total}</td>
                    <td class="text-center">{tag_count}</td>
                </tr>
                """

    content = f"""
    <div class="card">
        <h2 class="card-header">Categories by Type</h2>
        <div style="margin-bottom: 1.5rem; display: flex; gap: 2rem; align-items: center; flex-wrap: wrap;">
            <div>
                <label for="period-selector" style="margin-right: 0.5rem; font-weight: 600;">Period:</label>
                <select id="period-selector" class="month-selector" style="min-width: 200px;">
                    <option value="ytd">Year-to-Date</option>
                </select>
            </div>
            <div>
                <label style="margin-right: 0.5rem; font-weight: 600;">Show:</label>
                <label style="margin-right: 1rem; cursor: pointer;">
                    <input type="radio" name="type-filter" value="both" checked style="margin-right: 0.25rem;">
                    Both
                </label>
                <label style="margin-right: 1rem; cursor: pointer;">
                    <input type="radio" name="type-filter" value="income" style="margin-right: 0.25rem;">
                    Income Only
                </label>
                <label style="cursor: pointer;">
                    <input type="radio" name="type-filter" value="expense" style="margin-right: 0.25rem;">
                    Expense Only
                </label>
            </div>
            <div>
                <label style="margin-right: 0.5rem; font-weight: 600;">Compare:</label>
                <label style="cursor: pointer;">
                    <input type="checkbox" id="compare-toggle" style="margin-right: 0.25rem;">
                    Show Comparison
                </label>
            </div>
        </div>
        <div style="margin-bottom: 1.5rem; display: flex; gap: 2rem; align-items: center; flex-wrap: wrap;">
            <div>
                <label for="category-search" style="margin-right: 0.5rem; font-weight: 600;">Search:</label>
                <input type="text" id="category-search" placeholder="Search categories..." style="padding: 0.5rem; border: 1px solid #bdc3c7; border-radius: 4px; min-width: 200px;">
            </div>
            <div>
                <label for="category-amount-min" style="margin-right: 0.5rem; font-weight: 600;">Min Amount:</label>
                <input type="number" id="category-amount-min" step="0.01" placeholder="0.00" style="padding: 0.5rem; border: 1px solid #bdc3c7; border-radius: 4px; width: 120px;">
            </div>
            <div>
                <label for="category-amount-max" style="margin-right: 0.5rem; font-weight: 600;">Max Amount:</label>
                <input type="number" id="category-amount-max" step="0.01" placeholder="0.00" style="padding: 0.5rem; border: 1px solid #bdc3c7; border-radius: 4px; width: 120px;">
            </div>
        </div>
        <div id="category-comparison-summary" style="display: none; margin-bottom: 1.5rem;">
            <div class="card-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
                <div class="metric-card">
                    <div class="metric-label">Current Period</div>
                    <div class="metric-value" id="category-current-total">€0.00</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label" id="category-comparison-label">Previous Period</div>
                    <div class="metric-value" id="category-comparison-total">€0.00</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Change</div>
                    <div class="metric-value" id="category-change-total">€0.00</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Change %</div>
                    <div class="metric-value" id="category-change-pct">0.0%</div>
                </div>
            </div>
            <div style="margin-top: 1.5rem;">
                <div class="chart-container" style="height: 300px;">
                    <canvas id="categoryComparisonChart"></canvas>
                </div>
            </div>
            <div id="category-insights-container" style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #ecf0f1; display: none;">
                <h3 style="font-size: 1rem; margin-bottom: 1rem; color: #34495e; font-weight: 600;">Key Insights</h3>
                <div id="category-insights-content" style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;">
                    <p style="color: #7f8c8d; text-align: center; padding: 0.5rem;">No significant insights for this period.</p>
                </div>
            </div>
        </div>
        <div class="counterparty-charts-grid">
            <div>
                <h3 style="font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: #27ae60; text-align: center;">Income Categories</h3>
                <div class="chart-container" style="height: 350px;">
                    <canvas id="incomeChart"></canvas>
                </div>
            </div>
            <div>
                <h3 style="font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: #e74c3c; text-align: center;">Expense Categories</h3>
                <div class="chart-container" style="height: 350px;">
                    <canvas id="expenseChart"></canvas>
                </div>
            </div>
        </div>
        <div style="margin-top: 1rem; text-align: center;">
            <a href="category_trends.html" style="color: #3498db; text-decoration: none; font-weight: 600;">View Category Trends →</a>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">All Categories</h2>
        <div style="margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <p style="margin: 0; color: #666;">Click on any category or subcategory to view its trends over time.</p>
            <div style="display: flex; gap: 0.5rem;">
                <button id="export-categories-csv" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white; font-size: 0.9rem;">📥 Export CSV</button>
                <button id="copy-categories-link" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white; font-size: 0.9rem;">🔗 Copy Link</button>
            </div>
        </div>
        <div style="margin-bottom: 1rem;">
            <input type="text" id="category-table-search" placeholder="Search in table..." style="padding: 0.5rem; border: 1px solid #bdc3c7; border-radius: 4px; width: 100%; max-width: 400px;">
        </div>
        <table>
            <thead>
                <tr>
                    <th style="width: 30px;"></th>
                    <th>Category</th>
                    <th class="text-right">Total</th>
                    <th class="text-right">% of Total</th>
                    <th class="text-right">% of Income</th>
                    <th class="text-right">% of Expenses</th>
                    <th class="text-center">Count</th>
                    <th class="text-right">Avg Amount</th>
                    <th class="text-right">Avg/Month</th>
                    <th class="text-center" style="width: 100px;">Trend</th>
                    <th class="text-right comparison-column" style="display: none;">Previous Period</th>
                    <th class="text-right comparison-column" style="display: none;">Change</th>
                    <th class="text-right comparison-column" style="display: none;">Change %</th>
                </tr>
            </thead>
            <tbody id="categories-tbody">
                {category_rows}
            </tbody>
        </table>
    </div>
    """

    # Build JSON data separately (before appending to content)
    json_data_dict = {
        'available_months': dashboard_data['metadata']['available_months'],
        'default_month': dashboard_data['metadata']['default_month'],
        'all_months': dashboard_data['all_months'],
        'current_year': dashboard_data['metadata']['current_year'],
        'all_transactions': dashboard_data.get('all_transactions', [])  # Include all transactions for filtering
    }
    json_data_str = json.dumps(json_data_dict)

    content += f"""
    <script id="dashboard-data" type="application/json">
    {json_data_str}
    </script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const data = JSON.parse(document.getElementById('dashboard-data').textContent);
        initializeCategoriesPeriodSelector(data);
        updateCategoriesView(data, 'ytd');
    }});
    </script>
    """

    html = render_base_template('categories', 'Categories', content, dashboard_data, show_month_selector=False)
    (output_dir / "categories.html").write_text(html, encoding='utf-8')


def render_counterparties(dashboard_data: Dict[str, Any], output_dir: Path):
    """Render counterparties page."""
    ytd = dashboard_data['ytd']
    counterparties = ytd['counterparties']

    # Build counterparty table (initial render - will be replaced by JavaScript)
    # Keep this for initial page load, but JavaScript will handle dynamic updates
    counterparty_rows = ""
    for cp in counterparties:
        total_amount = cp['total']
        is_negative = total_amount < 0
        sign = '-' if is_negative else '+'
        abs_amount = abs(total_amount)
        formatted_amount = f"€{sign}{abs_amount:,.2f}"
        amount_color = '#e74c3c' if is_negative else '#27ae60'
        # Escape counterparty name for URL - use proper URL encoding
        url_name = urllib.parse.quote(cp['name'], safe='')
        # Use single quotes for f-string to avoid triple-quote issues
        counterparty_rows += f'''<tr>
            <td><a href="counterparty_trends.html?counterparty={url_name}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">{cp['name']}</a></td>
            <td class="text-center">{cp['count']}</td>
            <td class="text-right" style="color: {amount_color}; font-weight: 600;">{formatted_amount}</td>
        </tr>
        '''

    # Separate counterparties into income (positive) and expenses (negative)
    income_counterparties = [cp for cp in counterparties if cp['total'] > 0]
    expense_counterparties = [cp for cp in counterparties if cp['total'] < 0]

    # Sort by absolute amount and take top 10 for each
    income_counterparties.sort(key=lambda x: abs(x['total']), reverse=True)
    expense_counterparties.sort(key=lambda x: abs(x['total']), reverse=True)

    top_income = income_counterparties[:10]
    top_expenses = expense_counterparties[:10]

    # Prepare chart data for income (positive amounts)
    income_labels = [cp['name'] for cp in top_income]
    income_data = [cp['total'] for cp in top_income]  # Keep positive values

    # Prepare chart data for expenses (negative amounts, but show as positive in chart)
    expense_labels = [cp['name'] for cp in top_expenses]
    expense_data = [abs(cp['total']) for cp in top_expenses]  # Convert to positive for display

    # Build JSON data separately to avoid nested f-string issues
    json_data = json.dumps({
        'income': {
            'labels': income_labels,
            'data': income_data,
            'counterparties': income_counterparties
        },
        'expenses': {
            'labels': expense_labels,
            'data': expense_data,
            'counterparties': expense_counterparties
        },
        'counterparties': counterparties,  # Include all counterparties for sorting
        'available_months': dashboard_data['metadata']['available_months'],
        'default_month': dashboard_data['metadata']['default_month'],
        'current_year': dashboard_data['metadata']['current_year'],
        'all_months': dashboard_data['all_months'],
        'all_transactions': dashboard_data.get('all_transactions', [])  # Include all transactions for filtering
    })

    # Build content using list join to avoid triple-quote concatenation issues
    content_parts = [
        '''<div class="card">
        <h2 class="card-header">Counterparties by Type</h2>
        <div style="margin-bottom: 1.5rem; display: flex; gap: 2rem; align-items: center; flex-wrap: wrap;">
            <div>
                <label for="period-selector" style="margin-right: 0.5rem; font-weight: 600;">Period:</label>
                <select id="period-selector" class="month-selector" style="min-width: 200px;">
                    <option value="ytd">Year-to-Date</option>
                </select>
            </div>
            <div>
                <label style="margin-right: 0.5rem; font-weight: 600;">Show:</label>
                <label style="margin-right: 1rem; cursor: pointer;">
                    <input type="radio" name="type-filter" value="both" checked style="margin-right: 0.25rem;">
                    Both
                </label>
                <label style="margin-right: 1rem; cursor: pointer;">
                    <input type="radio" name="type-filter" value="income" style="margin-right: 0.25rem;">
                    Income Only
                </label>
                <label style="cursor: pointer;">
                    <input type="radio" name="type-filter" value="expense" style="margin-right: 0.25rem;">
                    Expense Only
                </label>
            </div>
            <div>
                <label style="margin-right: 0.5rem; font-weight: 600;">Compare:</label>
                <label style="cursor: pointer;">
                    <input type="checkbox" id="compare-toggle" style="margin-right: 0.25rem;">
                    Show Comparison
                </label>
            </div>
        </div>
        <div style="margin-bottom: 1.5rem; display: flex; gap: 2rem; align-items: center; flex-wrap: wrap;">
            <div>
                <label for="counterparty-search" style="margin-right: 0.5rem; font-weight: 600;">Search:</label>
                <input type="text" id="counterparty-search" placeholder="Search counterparties..." style="padding: 0.5rem; border: 1px solid #bdc3c7; border-radius: 4px; min-width: 200px;">
            </div>
            <div>
                <label for="counterparty-amount-min" style="margin-right: 0.5rem; font-weight: 600;">Min Amount:</label>
                <input type="number" id="counterparty-amount-min" step="0.01" placeholder="0.00" style="padding: 0.5rem; border: 1px solid #bdc3c7; border-radius: 4px; width: 120px;">
            </div>
            <div>
                <label for="counterparty-amount-max" style="margin-right: 0.5rem; font-weight: 600;">Max Amount:</label>
                <input type="number" id="counterparty-amount-max" step="0.01" placeholder="0.00" style="padding: 0.5rem; border: 1px solid #bdc3c7; border-radius: 4px; width: 120px;">
            </div>
        </div>
        <div id="counterparty-comparison-summary" style="display: none; margin-bottom: 1.5rem;">
            <div class="card-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
                <div class="metric-card">
                    <div class="metric-label">Current Period</div>
                    <div class="metric-value" id="counterparty-current-total">€0.00</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label" id="counterparty-comparison-label">Previous Period</div>
                    <div class="metric-value" id="counterparty-comparison-total">€0.00</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Change</div>
                    <div class="metric-value" id="counterparty-change-total">€0.00</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Change %</div>
                    <div class="metric-value" id="counterparty-change-pct">0.0%</div>
                </div>
            </div>
            <div style="margin-top: 1.5rem;">
                <div class="chart-container" style="height: 300px;">
                    <canvas id="counterpartyComparisonChart"></canvas>
                </div>
            </div>
            <div id="counterparty-insights-container" style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #ecf0f1; display: none;">
                <h3 style="font-size: 1rem; margin-bottom: 1rem; color: #34495e; font-weight: 600;">Key Insights</h3>
                <div id="counterparty-insights-content" style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;">
                    <p style="color: #7f8c8d; text-align: center; padding: 0.5rem;">No significant insights for this period.</p>
                </div>
            </div>
        </div>
        <div class="counterparty-charts-grid">
            <div>
                <h3 style="font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: #27ae60; text-align: center;">Income Counterparties</h3>
                <div class="chart-container" style="height: 350px;">
                    <canvas id="incomeChart"></canvas>
                </div>
            </div>
            <div>
                <h3 style="font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: #e74c3c; text-align: center;">Expense Counterparties</h3>
                <div class="chart-container" style="height: 350px;">
                    <canvas id="expenseChart"></canvas>
                </div>
            </div>
        </div>
        <div style="margin-top: 1rem; text-align: center;">
            <a href="counterparty_trends.html" style="color: #3498db; text-decoration: none; font-weight: 600;">View Counterparty Trends →</a>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">All Counterparties</h2>
        <div style="margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <p style="margin: 0; color: #666;">Click on any counterparty to view its trends over time. Click column headers to sort.</p>
            <div style="display: flex; gap: 0.5rem;">
                <button id="export-counterparties-csv" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white; font-size: 0.9rem;">📥 Export CSV</button>
                <button id="copy-counterparties-link" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white; font-size: 0.9rem;">🔗 Copy Link</button>
            </div>
        </div>
        <div style="margin-bottom: 1rem;">
            <input type="text" id="counterparty-table-search" placeholder="Search in table..." style="padding: 0.5rem; border: 1px solid #bdc3c7; border-radius: 4px; width: 100%; max-width: 400px;">
        </div>
        <div id="counterparty-pagination-controls" style="margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span id="counterparty-pagination-info">Showing 1-50 of <span id="counterparty-total-count">0</span></span>
            </div>
            <div>
                <button id="counterparty-prev-btn" style="padding: 0.5rem 1rem; margin-right: 0.5rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white;" disabled>Previous</button>
                <button id="counterparty-next-btn" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white;">Next</button>
            </div>
        </div>
        <table id="counterparties-table" class="data-table">
            <thead>
                <tr>
                    <th style="width: 30px;"></th>
                    <th class="sortable" data-sort="name">Counterparty <span class="sort-indicator">↕</span></th>
                    <th class="sortable text-right" data-sort="total">Total <span class="sort-indicator">↕</span></th>
                    <th class="sortable text-right" data-sort="percentage">% of Total <span class="sort-indicator">↕</span></th>
                    <th class="text-right">% of Income</th>
                    <th class="text-right">% of Expenses</th>
                    <th class="sortable text-center" data-sort="count">Count <span class="sort-indicator">↕</span></th>
                    <th class="text-right">Avg Amount</th>
                    <th class="text-right">Avg/Month</th>
                    <th class="text-center" style="width: 100px;">Trend</th>
                    <th class="text-right comparison-column sortable" data-sort="previous" style="display: none;">Previous Period <span class="sort-indicator">↕</span></th>
                    <th class="text-right comparison-column sortable" data-sort="change" style="display: none;">Change <span class="sort-indicator">↕</span></th>
                    <th class="text-right comparison-column sortable" data-sort="changePct" style="display: none;">Change % <span class="sort-indicator">↕</span></th>
                </tr>
            </thead>
            <tbody id="counterparties-tbody">
                ''',
        counterparty_rows,
        '''            </tbody>
        </table>
    </div>

    <script id="dashboard-data" type="application/json">
    ''',
        json_data,
        '''    </script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const data = JSON.parse(document.getElementById('dashboard-data').textContent);

        // Initialize table sorting first
        initializeCounterpartiesTableSorting(data);

        // Initialize period selector
        initializeCounterpartiesPeriodSelector(data);

        // Initial render with YTD data
        updateCounterpartiesView(data, 'ytd');
    });
    </script>
    '''
    ]
    content = ''.join(content_parts)

    html = render_base_template('counterparties', 'Counterparties', content, dashboard_data, show_month_selector=False)
    (output_dir / "counterparties.html").write_text(html, encoding='utf-8')


def render_category_trends(dashboard_data: Dict[str, Any], output_dir: Path):
    """Render category trends page with selector and zoomable chart."""
    categories_and_tags = dashboard_data.get('categories_and_tags', {})
    all_months = dashboard_data.get('all_months', {})

    # Build category options HTML - include both categories and category:tag combinations
    category_options = '<option value="">-- Select Category or Subcategory --</option>'
    for cat in sorted(categories_and_tags.keys()):
        # Add base category option
        category_options += f'<option value="{cat}">{cat}</option>'
        # Add category:tag options if tags exist
        if categories_and_tags[cat].get('tags'):
            for tag in sorted(categories_and_tags[cat]['tags']):
                category_tag_value = f"{cat}:{tag}"
                category_tag_display = f"{cat}: {tag}"
                category_options += f'<option value="{category_tag_value}">{category_tag_display}</option>'

    # Compute trends for all categories (we'll do this in JS from monthly data)
    # But we need monthly breakdowns - let's add that to the data

    content = f"""
    <div class="card">
        <h2 class="card-header">Category Trends</h2>
        <div style="margin-bottom: 1.5rem;">
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <label for="category-selector" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Categories & Subcategories (compare multiple):</label>
                    <div class="multi-select-container">
                        <div class="searchable-select-container">
                            <input type="text" id="category-selector" class="searchable-select-input" placeholder="Search and add categories or subcategories..." autocomplete="off">
                            <select id="category-selector-hidden" style="display: none;">
                                {category_options}
                            </select>
                            <div id="category-selector-dropdown" class="searchable-select-dropdown"></div>
                        </div>
                        <div id="category-selected-items" class="selected-items-container"></div>
                    </div>
                </div>
                <div>
                    <label for="year-selector" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Year:</label>
                    <select id="year-selector" class="month-selector" style="width: 100%;">
                        <option value="all">All Time</option>
                    </select>
                </div>
                <div>
                    <label for="group-by-selector" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Group By:</label>
                    <select id="group-by-selector" class="month-selector" style="width: 100%;">
                        <option value="month">Month</option>
                        <option value="quarter">Quarter</option>
                        <option value="year">Year</option>
                    </select>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <label for="date-start" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Start Date:</label>
                    <input type="date" id="date-start" class="month-selector" style="width: 100%; padding: 0.5rem;">
                </div>
                <div>
                    <label for="date-end" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">End Date:</label>
                    <input type="date" id="date-end" class="month-selector" style="width: 100%; padding: 0.5rem;">
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <label for="amount-min" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Min Amount:</label>
                    <input type="number" id="amount-min" step="0.01" placeholder="0.00" class="month-selector" style="width: 100%; padding: 0.5rem;">
                </div>
                <div>
                    <label for="amount-max" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Max Amount:</label>
                    <input type="number" id="amount-max" step="0.01" placeholder="0.00" class="month-selector" style="width: 100%; padding: 0.5rem;">
                </div>
            </div>
        </div>
        <div style="margin-bottom: 1rem; display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
            <label style="cursor: pointer;">
                <input type="checkbox" id="cumulative-toggle" style="margin-right: 0.25rem;">
                Show Cumulative Totals
            </label>
            <div style="margin-left: auto; display: flex; gap: 0.5rem;">
                <button id="export-category-chart-png" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white; font-size: 0.9rem;">📊 Export Chart (PNG)</button>
                <button id="copy-category-trends-link" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white; font-size: 0.9rem;">🔗 Copy Link</button>
            </div>
        </div>
        <div class="chart-container" style="height: 500px;">
            <canvas id="categoryTrendChart"></canvas>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Summary</h2>
        <div id="category-trend-summary" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <div class="metric-card">
                <div class="metric-label">Total</div>
                <div class="metric-value" id="trend-total">€0.00</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Transactions</div>
                <div class="metric-value" id="trend-count">0</div>
            </div>
            <div class="metric-card">
                <div class="metric-label" id="trend-avg-label">Average per Month</div>
                <div class="metric-value" id="trend-avg">€0.00</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Projections</h2>
        <div id="category-trend-projections" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <div class="metric-card">
                <div class="metric-label">Next Period Projection</div>
                <div class="metric-value" id="category-projection-next">€0.00</div>
                <div style="font-size: 0.8rem; color: #7f8c8d; margin-top: 0.25rem;" id="category-projection-confidence-next">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Annual Projection (YTD)</div>
                <div class="metric-value" id="category-projection-annual">€0.00</div>
                <div style="font-size: 0.8rem; color: #7f8c8d; margin-top: 0.25rem;" id="category-projection-confidence-annual">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Trend Direction</div>
                <div class="metric-value" id="category-trend-direction">-</div>
                <div style="font-size: 0.8rem; color: #7f8c8d; margin-top: 0.25rem;" id="category-trend-strength">-</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Transactions</h2>
        <div style="overflow-x: auto;">
            <table id="category-transactions-table" class="data-table">
                <thead>
                    <tr>
                        <th class="sortable" data-sort="date">Date <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="description">Description <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="counterparty">Counterparty <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="category">Category <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="amount">Amount <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="type">Type <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="source_file">Source <span class="sort-indicator">↕</span></th>
                    </tr>
                </thead>
                <tbody id="category-transactions-tbody">
                    <tr>
                        <td colspan="7" style="text-align: center; padding: 2rem; color: #7f8c8d;">
                            Select categories or subcategories to view transactions
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script id="dashboard-data" type="application/json">
    {json.dumps({
        'categories_and_tags': categories_and_tags,
        'all_months': all_months,
        'available_months': dashboard_data['metadata']['available_months'],
        'default_month': dashboard_data['metadata']['default_month'],
        'all_transactions': dashboard_data.get('all_transactions', []),
    })}
    </script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        initializeCategoryTrends();
    }});
    </script>
    """

    html = render_base_template('category_trends', 'Category Trends', content, dashboard_data, show_month_selector=False)
    (output_dir / "category_trends.html").write_text(html, encoding='utf-8')


def render_counterparty_trends(dashboard_data: Dict[str, Any], output_dir: Path):
    """Render counterparty trends page with selector and zoomable chart."""
    all_counterparties = dashboard_data.get('all_counterparties', [])
    all_months = dashboard_data.get('all_months', {})

    # Build counterparty options HTML
    counterparty_options = '<option value="">-- Select Counterparty --</option>'
    for cp in sorted(all_counterparties):
        # Escape quotes in counterparty names
        escaped_cp = cp.replace('"', '&quot;').replace("'", "&#39;")
        counterparty_options += f'<option value="{escaped_cp}">{cp}</option>'

    content = f"""
    <div class="card">
        <h2 class="card-header">Counterparty Trends</h2>
        <div style="margin-bottom: 1.5rem;">
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <label for="counterparty-selector" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Counterparties (compare multiple):</label>
                    <div class="multi-select-container">
                        <div class="searchable-select-container">
                            <input type="text" id="counterparty-selector" class="searchable-select-input" placeholder="Search and add counterparties..." autocomplete="off">
                            <select id="counterparty-selector-hidden" style="display: none;">
                                {counterparty_options}
                            </select>
                            <div id="counterparty-selector-dropdown" class="searchable-select-dropdown"></div>
                        </div>
                        <div id="counterparty-selected-items" class="selected-items-container"></div>
                    </div>
                </div>
                <div>
                    <label for="year-selector" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Year:</label>
                    <select id="year-selector" class="month-selector" style="width: 100%;">
                        <option value="all">All Time</option>
                    </select>
                </div>
                <div>
                    <label for="group-by-selector" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Group By:</label>
                    <select id="group-by-selector" class="month-selector" style="width: 100%;">
                        <option value="month">Month</option>
                        <option value="quarter">Quarter</option>
                        <option value="year">Year</option>
                    </select>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <label for="date-start" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Start Date:</label>
                    <input type="date" id="date-start" class="month-selector" style="width: 100%; padding: 0.5rem;">
                </div>
                <div>
                    <label for="date-end" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">End Date:</label>
                    <input type="date" id="date-end" class="month-selector" style="width: 100%; padding: 0.5rem;">
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <label for="amount-min" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Min Amount:</label>
                    <input type="number" id="amount-min" step="0.01" placeholder="0.00" class="month-selector" style="width: 100%; padding: 0.5rem;">
                </div>
                <div>
                    <label for="amount-max" style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Max Amount:</label>
                    <input type="number" id="amount-max" step="0.01" placeholder="0.00" class="month-selector" style="width: 100%; padding: 0.5rem;">
                </div>
            </div>
        </div>
        <div style="margin-bottom: 1rem; display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
            <label style="cursor: pointer;">
                <input type="checkbox" id="cumulative-toggle" style="margin-right: 0.25rem;">
                Show Cumulative Totals
            </label>
            <div style="margin-left: auto; display: flex; gap: 0.5rem;">
                <button id="export-counterparty-chart-png" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white; font-size: 0.9rem;">📊 Export Chart (PNG)</button>
                <button id="copy-counterparty-trends-link" style="padding: 0.5rem 1rem; cursor: pointer; border: 1px solid #bdc3c7; border-radius: 4px; background: white; font-size: 0.9rem;">🔗 Copy Link</button>
            </div>
        </div>
        <div class="chart-container" style="height: 500px;">
            <canvas id="counterpartyTrendChart"></canvas>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Summary</h2>
        <div id="counterparty-trend-summary" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <div class="metric-card">
                <div class="metric-label">Total</div>
                <div class="metric-value" id="trend-total">€0.00</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Transactions</div>
                <div class="metric-value" id="trend-count">0</div>
            </div>
            <div class="metric-card">
                <div class="metric-label" id="trend-avg-label">Average per Month</div>
                <div class="metric-value" id="trend-avg">€0.00</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Projections</h2>
        <div id="counterparty-trend-projections" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <div class="metric-card">
                <div class="metric-label">Next Period Projection</div>
                <div class="metric-value" id="counterparty-projection-next">€0.00</div>
                <div style="font-size: 0.8rem; color: #7f8c8d; margin-top: 0.25rem;" id="counterparty-projection-confidence-next">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Annual Projection (YTD)</div>
                <div class="metric-value" id="counterparty-projection-annual">€0.00</div>
                <div style="font-size: 0.8rem; color: #7f8c8d; margin-top: 0.25rem;" id="counterparty-projection-confidence-annual">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Trend Direction</div>
                <div class="metric-value" id="counterparty-trend-direction">-</div>
                <div style="font-size: 0.8rem; color: #7f8c8d; margin-top: 0.25rem;" id="counterparty-trend-strength">-</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2 class="card-header">Transactions</h2>
        <div style="overflow-x: auto;">
            <table id="counterparty-transactions-table" class="data-table">
                <thead>
                    <tr>
                        <th class="sortable" data-sort="date">Date <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="description">Description <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="counterparty">Counterparty <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="category">Category <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="amount">Amount <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="type">Type <span class="sort-indicator">↕</span></th>
                        <th class="sortable" data-sort="source_file">Source <span class="sort-indicator">↕</span></th>
                    </tr>
                </thead>
                <tbody id="counterparty-transactions-tbody">
                    <tr>
                        <td colspan="7" style="text-align: center; padding: 2rem; color: #7f8c8d;">
                            Select counterparties to view transactions
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script id="dashboard-data" type="application/json">
    {json.dumps({
        'all_counterparties': all_counterparties,
        'all_months': all_months,
        'available_months': dashboard_data['metadata']['available_months'],
        'default_month': dashboard_data['metadata']['default_month'],
        'current_year': dashboard_data['metadata']['current_year'],
        'all_transactions': dashboard_data.get('all_transactions', []),
    })}
    </script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        initializeCounterpartyTrends();
    }});
    </script>
    """

    html = render_base_template('counterparty_trends', 'Counterparty Trends', content, dashboard_data, show_month_selector=False)
    (output_dir / "counterparty_trends.html").write_text(html, encoding='utf-8')


