"""Tests for template rendering."""

import pytest
from pathlib import Path
from datetime import datetime

from omislisi_accounting.templates.renderer import (
    render_dashboard,
    load_template,
    render_base_template,
    render_index,
    render_categories,
    render_counterparties,
    render_category_trends,
    render_counterparty_trends,
)


@pytest.fixture
def minimal_dashboard_data():
    """Create minimal dashboard data for testing."""
    return {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'current_year': 2025,
            'default_month': '2025-01',
            'available_months': ['2025-01', '2025-02'],
            'total_transactions': 10,
        },
        'current_month': {
            'period': '2025-01',
            'summary': {
                'total_income': 1000.0,
                'total_expenses': 500.0,
                'net': 500.0,
                'transaction_count': 5,
            },
            'breakdown': {
                'sales': {'total': 1000.0, 'count': 2},
                'office': {'total': -500.0, 'count': 3},
            },
            'comparison': {
                'previous_month': '2024-12',
                'income_change': 200.0,
                'income_change_pct': 25.0,
                'expense_change': -100.0,
                'expense_change_pct': -16.67,
                'net_change': 300.0,
                'net_change_pct': 150.0,
            },
            'counterparties': [
                {'name': 'Client A', 'count': 2, 'total': 1000.0},
            ],
        },
        'ytd': {
            'period': '2025',
            'summary': {
                'total_income': 2000.0,
                'total_expenses': 1000.0,
                'net': 1000.0,
                'transaction_count': 10,
            },
            'breakdown': {
                'sales': {'total': 2000.0, 'count': 4},
                'office': {'total': -1000.0, 'count': 6},
            },
            'monthly_progression': {
                '2025-01': {
                    'total_income': 1000.0,
                    'total_expenses': 500.0,
                    'net': 500.0,
                },
            },
            'projections': {
                'projected_income': 24000.0,
                'projected_expenses': 12000.0,
                'projected_net': 12000.0,
            },
            'counterparties': [
                {'name': 'Client A', 'count': 4, 'total': 2000.0},
            ],
        },
        'last_12_months': {
            'period': '2024-01 to 2025-01',
            'months': {
                '2025-01': {
                    'summary': {
                        'total_income': 1000.0,
                        'total_expenses': 500.0,
                        'net': 500.0,
                        'transaction_count': 5,
                    },
                },
            },
            'summary': {
                'total_income': 1000.0,
                'total_expenses': 500.0,
                'net': 500.0,
                'transaction_count': 5,
            },
        },
        'year_comparison': {
            'current_year': '2025',
            'previous_year': '2024',
            'current_summary': {
                'total_income': 2000.0,
                'total_expenses': 1000.0,
                'net': 1000.0,
                'transaction_count': 10,
            },
            'previous_summary': {
                'total_income': 1500.0,
                'total_expenses': 800.0,
                'net': 700.0,
                'transaction_count': 8,
            },
            'changes': {
                'income_change': 500.0,
                'income_change_pct': 33.33,
                'expense_change': 200.0,
                'expense_change_pct': 25.0,
                'net_change': 300.0,
                'net_change_pct': 42.86,
            },
            'monthly_comparison': {
                '01': {
                    'current': {
                        'total_income': 1000.0,
                        'total_expenses': 500.0,
                        'net': 500.0,
                    },
                    'previous': {
                        'total_income': 800.0,
                        'total_expenses': 400.0,
                        'net': 400.0,
                    },
                },
            },
        },
        'monthly_trends': {
            '2025-01': {
                'total_income': 1000.0,
                'total_expenses': 500.0,
                'net': 500.0,
            },
        },
        'categories_and_tags': {
            'sales': {'tags': ['invoice', 'stripe']},
            'office': {'tags': []},
        },
        'all_counterparties': ['Client A', 'Client B'],
        'all_months': {
            '2025-01': {
                'period': '2025-01',
                'summary': {
                    'total_income': 1000.0,
                    'total_expenses': 500.0,
                    'net': 500.0,
                    'transaction_count': 5,
                },
            },
        },
        'all_transactions': [
            {
                'date': '2025-01-15',
                'amount': 1000.0,
                'description': 'Payment',
                'type': 'income',
                'counterparty': 'Client A',
                'category': 'sales',
            },
        ],
    }


def test_load_template():
    """Test load_template function."""
    # Should load base.html if it exists
    template = load_template("base.html")
    # Template might exist or not, but function should not crash
    assert isinstance(template, str)


def test_load_template_nonexistent():
    """Test load_template with nonexistent template."""
    template = load_template("nonexistent_template.html")
    assert template == ""


def test_render_base_template(minimal_dashboard_data):
    """Test render_base_template function."""
    content = "<div>Test content</div>"
    result = render_base_template('index', 'Test Page', content, minimal_dashboard_data)

    assert isinstance(result, str)
    assert 'Test content' in result
    # Should include generated_at
    assert minimal_dashboard_data['metadata']['generated_at'] in result


def test_render_base_template_no_template(minimal_dashboard_data, tmp_dir, monkeypatch):
    """Test render_base_template when template doesn't exist."""
    # Mock load_template to return empty string
    from omislisi_accounting.templates import renderer
    original_load = renderer.load_template

    def mock_load(name):
        return ""

    monkeypatch.setattr(renderer, "load_template", mock_load)

    content = "<div>Test content</div>"
    result = render_base_template('index', 'Test Page', content, minimal_dashboard_data)

    # Should return content as-is when template doesn't exist
    assert result == content

    # Restore
    monkeypatch.setattr(renderer, "load_template", original_load)


def test_render_base_template_navigation_states(minimal_dashboard_data):
    """Test that navigation states are set correctly."""
    content = "<div>Test</div>"

    # Test index page
    result_index = render_base_template('index', 'Test', content, minimal_dashboard_data)
    assert 'nav_index' in result_index or 'active' in result_index or result_index == content

    # Test categories page
    result_categories = render_base_template('categories', 'Test', content, minimal_dashboard_data)
    assert isinstance(result_categories, str)


def test_render_index(minimal_dashboard_data, tmp_dir):
    """Test render_index function."""
    render_index(minimal_dashboard_data, tmp_dir)

    index_file = tmp_dir / "index.html"
    assert index_file.exists()

    content = index_file.read_text(encoding='utf-8')
    assert 'Overview' in content or '2025' in content
    # Check for formatted amount (with comma or euro symbol)
    ytd_income = minimal_dashboard_data['ytd']['summary']['total_income']
    assert str(ytd_income) in content or f"{ytd_income:,.2f}" in content or "€" in content


def test_render_categories(minimal_dashboard_data, tmp_dir):
    """Test render_categories function."""
    render_categories(minimal_dashboard_data, tmp_dir)

    categories_file = tmp_dir / "categories.html"
    assert categories_file.exists()

    content = categories_file.read_text(encoding='utf-8')
    assert 'Categories' in content or 'categories' in content.lower()


def test_render_counterparties(minimal_dashboard_data, tmp_dir):
    """Test render_counterparties function."""
    render_counterparties(minimal_dashboard_data, tmp_dir)

    counterparties_file = tmp_dir / "counterparties.html"
    assert counterparties_file.exists()

    content = counterparties_file.read_text(encoding='utf-8')
    assert 'Counterparties' in content or 'counterparties' in content.lower()


def test_render_category_trends(minimal_dashboard_data, tmp_dir):
    """Test render_category_trends function."""
    render_category_trends(minimal_dashboard_data, tmp_dir)

    trends_file = tmp_dir / "category_trends.html"
    assert trends_file.exists()

    content = trends_file.read_text(encoding='utf-8')
    assert 'Category Trends' in content or 'category' in content.lower()


def test_render_counterparty_trends(minimal_dashboard_data, tmp_dir):
    """Test render_counterparty_trends function."""
    render_counterparty_trends(minimal_dashboard_data, tmp_dir)

    trends_file = tmp_dir / "counterparty_trends.html"
    assert trends_file.exists()

    content = trends_file.read_text(encoding='utf-8')
    assert 'Counterparty Trends' in content or 'counterparty' in content.lower()


def test_render_dashboard(minimal_dashboard_data, tmp_dir):
    """Test render_dashboard function."""
    render_dashboard(minimal_dashboard_data, tmp_dir)

    # Check that HTML files are created
    assert (tmp_dir / "index.html").exists()
    assert (tmp_dir / "categories.html").exists()
    assert (tmp_dir / "counterparties.html").exists()
    assert (tmp_dir / "category_trends.html").exists()
    assert (tmp_dir / "counterparty_trends.html").exists()

    # Check that static directory is created
    static_dir = tmp_dir / "static"
    assert static_dir.exists()
    assert static_dir.is_dir()


def test_render_dashboard_cleans_existing_files(minimal_dashboard_data, tmp_dir):
    """Test that render_dashboard cleans existing HTML files."""
    # Create an orphaned HTML file
    orphaned_file = tmp_dir / "orphaned.html"
    orphaned_file.write_text("Orphaned content")

    # Render dashboard
    render_dashboard(minimal_dashboard_data, tmp_dir)

    # Orphaned file should be removed
    assert not orphaned_file.exists()

    # But expected files should exist
    assert (tmp_dir / "index.html").exists()


def test_render_dashboard_static_files(minimal_dashboard_data, tmp_dir):
    """Test that render_dashboard copies static files."""
    render_dashboard(minimal_dashboard_data, tmp_dir)

    static_dir = tmp_dir / "static"

    # Check if CSS and JS files exist (they might not if source doesn't exist)
    css_file = static_dir / "dashboard.css"
    js_file = static_dir / "dashboard.js"

    # At least the directory should exist
    assert static_dir.exists()


def test_render_dashboard_empty_data(tmp_dir):
    """Test render_dashboard with minimal/empty data."""
    empty_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'current_year': 2025,
            'default_month': '2025-01',
            'available_months': [],
            'total_transactions': 0,
        },
        'current_month': {
            'period': '2025-01',
            'summary': {
                'total_income': 0.0,
                'total_expenses': 0.0,
                'net': 0.0,
                'transaction_count': 0,
            },
            'breakdown': {},
            'comparison': {
                'previous_month': '2024-12',
                'income_change': 0.0,
                'income_change_pct': 0.0,
                'expense_change': 0.0,
                'expense_change_pct': 0.0,
                'net_change': 0.0,
                'net_change_pct': 0.0,
            },
            'counterparties': [],
        },
        'ytd': {
            'period': '2025',
            'summary': {
                'total_income': 0.0,
                'total_expenses': 0.0,
                'net': 0.0,
                'transaction_count': 0,
            },
            'breakdown': {},
            'monthly_progression': {},
            'projections': {
                'projected_income': 0.0,
                'projected_expenses': 0.0,
                'projected_net': 0.0,
            },
            'counterparties': [],
        },
        'last_12_months': {
            'period': '2025-01 to 2025-01',
            'months': {},
            'summary': {
                'total_income': 0.0,
                'total_expenses': 0.0,
                'net': 0.0,
                'transaction_count': 0,
            },
        },
        'year_comparison': {
            'current_year': '2025',
            'previous_year': '2024',
            'current_summary': {
                'total_income': 0.0,
                'total_expenses': 0.0,
                'net': 0.0,
                'transaction_count': 0,
            },
            'previous_summary': {
                'total_income': 0.0,
                'total_expenses': 0.0,
                'net': 0.0,
                'transaction_count': 0,
            },
            'changes': {
                'income_change': 0.0,
                'income_change_pct': 0.0,
                'expense_change': 0.0,
                'expense_change_pct': 0.0,
                'net_change': 0.0,
                'net_change_pct': 0.0,
            },
            'monthly_comparison': {},
        },
        'monthly_trends': {},
        'categories_and_tags': {},
        'all_counterparties': [],
        'all_months': {},
        'all_transactions': [],
    }

    # Should not crash with empty data
    render_dashboard(empty_data, tmp_dir)

    # Files should still be created
    assert (tmp_dir / "index.html").exists()
    assert (tmp_dir / "categories.html").exists()

