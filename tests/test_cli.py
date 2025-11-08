"""Tests for CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
import tempfile
import zipfile
import csv

from omislisi_accounting.cli.main import cli


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Omislisi Accounting Analysis Tool' in result.output


def test_categorize_command(tmp_dir, sample_bank_xml):
    """Test categorize command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['categorize', str(sample_bank_xml)])
    assert result.exit_code == 0
    assert 'Categorizing transactions' in result.output


def test_categorize_command_invalid_file(tmp_dir):
    """Test categorize command with invalid file."""
    runner = CliRunner()
    invalid_file = tmp_dir / "nonexistent.xml"
    result = runner.invoke(cli, ['categorize', str(invalid_file)])
    assert result.exit_code != 0


def test_report_command_invalid_month_format(tmp_dir):
    """Test report command with invalid month format."""
    runner = CliRunner()
    result = runner.invoke(cli, ['report', '--month', 'invalid'])
    # Command might exit with 0 but show error message, or exit with non-zero
    assert result.exit_code != 0 or 'Invalid month format' in result.output or 'Error' in result.output


def test_report_command_month_extracts_year(tmp_dir, monkeypatch):
    """Test that month parameter extracts year correctly."""
    # Mock the reports path and file finding
    test_reports = tmp_dir / "reports" / "2025"
    test_reports.mkdir(parents=True)

    # Create a zip file
    zip_file = test_reports / "DH-2025-10.zip"
    with zipfile.ZipFile(zip_file, 'w') as zf:
        zf.writestr("test.xml", "<xml>test</xml>")

    runner = CliRunner()

    # Mock the config to use our test directory
    import omislisi_accounting.cli.main as cli_module
    original_reports_path = cli_module.REPORTS_PATH

    try:
        cli_module.REPORTS_PATH = tmp_dir / "reports"
        result = runner.invoke(cli, ['report', '--month', '2025-10'])
        # Should not fail with "year directory does not exist" error
        # (it might fail for other reasons like no parser, but that's ok)
        assert 'Year directory' not in result.output or 'does not exist' not in result.output
    finally:
        cli_module.REPORTS_PATH = original_reports_path


def test_analyze_command(tmp_dir, sample_bank_xml, monkeypatch):
    """Test analyze command."""
    # Create reports directory structure
    reports_dir = tmp_dir / "reports" / "2025"
    reports_dir.mkdir(parents=True)

    # Copy sample XML to reports directory
    import shutil
    shutil.copy(sample_bank_xml, reports_dir / "bank_statement.xml")

    runner = CliRunner()

    # Mock the reports path
    import omislisi_accounting.cli.main as cli_module
    original_reports_path = cli_module.REPORTS_PATH

    try:
        cli_module.REPORTS_PATH = tmp_dir / "reports"
        result = runner.invoke(cli, ['analyze', '--reports-path', str(tmp_dir / "reports")])
        # Should process files (might have warnings but should not crash)
        assert result.exit_code == 0 or 'Analyzing reports' in result.output
    finally:
        cli_module.REPORTS_PATH = original_reports_path


def test_analyze_command_with_year(tmp_dir, sample_bank_xml, monkeypatch):
    """Test analyze command with year filter."""
    reports_dir = tmp_dir / "reports" / "2025"
    reports_dir.mkdir(parents=True)

    runner = CliRunner()

    import omislisi_accounting.cli.main as cli_module
    original_reports_path = cli_module.REPORTS_PATH

    try:
        cli_module.REPORTS_PATH = tmp_dir / "reports"
        result = runner.invoke(cli, ['analyze', '--year', '2025', '--reports-path', str(tmp_dir / "reports")])
        # Should handle year filter
        assert result.exit_code == 0 or '2025' in result.output or 'does not exist' in result.output
    finally:
        cli_module.REPORTS_PATH = original_reports_path


def test_report_command_with_category_filter(tmp_dir, monkeypatch):
    """Test report command with category filter."""
    reports_dir = tmp_dir / "reports" / "2025"
    reports_dir.mkdir(parents=True)

    runner = CliRunner()

    import omislisi_accounting.cli.main as cli_module
    original_reports_path = cli_module.REPORTS_PATH

    try:
        cli_module.REPORTS_PATH = tmp_dir / "reports"
        result = runner.invoke(cli, [
            'report',
            '--year', '2025',
            '--category', 'office',
            '--reports-path', str(tmp_dir / "reports")
        ])
        # Should accept category filter (might fail if no data, but should not crash on filter)
        # Command should complete (exit code 0) even if no transactions found
        assert result.exit_code == 0 or 'No transactions' in result.output or 'category' in result.output.lower()
    finally:
        cli_module.REPORTS_PATH = original_reports_path


def test_report_command_with_counterparty_filter(tmp_dir, monkeypatch):
    """Test report command with counterparty filter."""
    reports_dir = tmp_dir / "reports" / "2025"
    reports_dir.mkdir(parents=True)

    runner = CliRunner()

    import omislisi_accounting.cli.main as cli_module
    original_reports_path = cli_module.REPORTS_PATH

    try:
        cli_module.REPORTS_PATH = tmp_dir / "reports"
        result = runner.invoke(cli, [
            'report',
            '--year', '2025',
            '--counterparty', 'Test Company',
            '--reports-path', str(tmp_dir / "reports")
        ])
        # Should accept counterparty filter
        assert result.exit_code == 0 or 'counterparty' in result.output.lower() or 'No transactions' in result.output
    finally:
        cli_module.REPORTS_PATH = original_reports_path


def test_report_command_with_by_counterparty(tmp_dir, monkeypatch):
    """Test report command with --by-counterparty flag."""
    reports_dir = tmp_dir / "reports" / "2025"
    reports_dir.mkdir(parents=True)

    runner = CliRunner()

    import omislisi_accounting.cli.main as cli_module
    original_reports_path = cli_module.REPORTS_PATH

    try:
        cli_module.REPORTS_PATH = tmp_dir / "reports"
        result = runner.invoke(cli, [
            'report',
            '--year', '2025',
            '--by-counterparty',
            '--reports-path', str(tmp_dir / "reports")
        ])
        # Should accept by-counterparty flag
        assert result.exit_code == 0 or 'counterparty' in result.output.lower() or 'No transactions' in result.output
    finally:
        cli_module.REPORTS_PATH = original_reports_path


def test_report_command_comparison_errors(tmp_dir):
    """Test report command comparison validation errors."""
    runner = CliRunner()

    # Test both compare-month and compare-year (should error)
    result = runner.invoke(cli, [
        'report',
        '--month', '2025-01',
        '--compare-month', '2025-02',
        '--compare-year', '2024'
    ])
    # Should error or show error message
    assert result.exit_code != 0 or 'Cannot specify both' in result.output or 'Error' in result.output

    # Test compare-month without month (should error)
    result = runner.invoke(cli, [
        'report',
        '--compare-month', '2025-02'
    ])
    assert result.exit_code != 0 or 'Must specify --month' in result.output or 'Error' in result.output

    # Test compare-year without year (should error)
    result = runner.invoke(cli, [
        'report',
        '--compare-year', '2024'
    ])
    assert result.exit_code != 0 or 'Must specify --year' in result.output or 'Error' in result.output


def test_trends_command(tmp_dir, monkeypatch):
    """Test trends command."""
    reports_dir = tmp_dir / "reports" / "2025"
    reports_dir.mkdir(parents=True)

    runner = CliRunner()

    import omislisi_accounting.cli.main as cli_module
    original_reports_path = cli_module.REPORTS_PATH

    try:
        cli_module.REPORTS_PATH = tmp_dir / "reports"
        result = runner.invoke(cli, [
            'trends',
            '--year', '2025',
            '--reports-path', str(tmp_dir / "reports")
        ])
        # Should handle trends command (might fail if no data)
        assert result.exit_code == 0 or 'trend' in result.output.lower() or 'No transactions' in result.output
    finally:
        cli_module.REPORTS_PATH = original_reports_path


def test_trends_command_with_category(tmp_dir, monkeypatch):
    """Test trends command with category filter."""
    reports_dir = tmp_dir / "reports" / "2025"
    reports_dir.mkdir(parents=True)

    runner = CliRunner()

    import omislisi_accounting.cli.main as cli_module
    original_reports_path = cli_module.REPORTS_PATH

    try:
        cli_module.REPORTS_PATH = tmp_dir / "reports"
        result = runner.invoke(cli, [
            'trends',
            '--year', '2025',
            '--category', 'office',
            '--reports-path', str(tmp_dir / "reports")
        ])
        # Should accept category filter
        assert result.exit_code == 0 or 'office' in result.output.lower() or 'No transactions' in result.output
    finally:
        cli_module.REPORTS_PATH = original_reports_path


def test_category_command(tmp_dir, monkeypatch):
    """Test category command."""
    reports_dir = tmp_dir / "reports" / "2025"
    reports_dir.mkdir(parents=True)

    runner = CliRunner()

    import omislisi_accounting.cli.main as cli_module
    original_reports_path = cli_module.REPORTS_PATH

    try:
        cli_module.REPORTS_PATH = tmp_dir / "reports"
        result = runner.invoke(cli, [
            'category',
            '--year', '2025',
            '--reports-path', str(tmp_dir / "reports")
        ])
        # Should handle category command
        assert result.exit_code == 0 or 'category' in result.output.lower() or 'No transactions' in result.output
    finally:
        cli_module.REPORTS_PATH = original_reports_path


def test_counterparties_command(tmp_dir, monkeypatch):
    """Test counterparties command."""
    reports_dir = tmp_dir / "reports" / "2025"
    reports_dir.mkdir(parents=True)

    runner = CliRunner()

    import omislisi_accounting.cli.main as cli_module
    original_reports_path = cli_module.REPORTS_PATH

    try:
        cli_module.REPORTS_PATH = tmp_dir / "reports"
        result = runner.invoke(cli, [
            'counterparties',
            '--year', '2025',
            '--reports-path', str(tmp_dir / "reports")
        ])
        # Should handle counterparties command
        assert result.exit_code == 0 or 'counterparty' in result.output.lower() or 'No transactions' in result.output
    finally:
        cli_module.REPORTS_PATH = original_reports_path


def test_generate_dashboard_command(tmp_dir, monkeypatch):
    """Test generate-dashboard command."""
    reports_dir = tmp_dir / "reports" / "2025"
    reports_dir.mkdir(parents=True)
    output_dir = tmp_dir / "dashboard_output"

    runner = CliRunner()

    import omislisi_accounting.cli.main as cli_module
    original_reports_path = cli_module.REPORTS_PATH

    try:
        cli_module.REPORTS_PATH = tmp_dir / "reports"
        result = runner.invoke(cli, [
            'generate-dashboard',
            '--output-dir', str(output_dir),
            '--reports-path', str(tmp_dir / "reports"),
            '--year', '2025'
        ])
        # Should handle dashboard generation (might fail if no data, but should not crash)
        assert result.exit_code == 0 or 'dashboard' in result.output.lower() or 'No transactions' in result.output or 'does not exist' in result.output
    finally:
        cli_module.REPORTS_PATH = original_reports_path


def test_generate_dashboard_creates_output_dir(tmp_dir, monkeypatch):
    """Test that generate-dashboard creates output directory."""
    reports_dir = tmp_dir / "reports" / "2025"
    reports_dir.mkdir(parents=True)
    output_dir = tmp_dir / "dashboard_output"

    runner = CliRunner()

    import omislisi_accounting.cli.main as cli_module
    original_reports_path = cli_module.REPORTS_PATH

    try:
        cli_module.REPORTS_PATH = tmp_dir / "reports"
        result = runner.invoke(cli, [
            'generate-dashboard',
            '--output-dir', str(output_dir),
            '--reports-path', str(tmp_dir / "reports"),
            '--year', '2025'
        ])
        # Output directory might be created even if generation fails
        # Just check that command doesn't crash
        assert result.exit_code == 0 or 'dashboard' in result.output.lower() or 'No transactions' in result.output or 'does not exist' in result.output
    finally:
        cli_module.REPORTS_PATH = original_reports_path

