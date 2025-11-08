# Omislisi Accounting Analysis Tool

A Python CLI tool for analyzing bank account and PayPal transactions from XML files in zip archives.

## Features

- **Bank Statement Parsing**: Supports ISO 20022 camt.053 XML format (used by European banks)
- **PayPal CSV Parsing**: Parses PayPal transaction exports
- **Automatic Categorization**: Categorizes transactions based on description keywords (supports Slovenian and English)
- **Financial Analysis**: Generates summaries and category breakdowns
- **Category Drill-Down**: View individual transactions within any category with filtering options
- **Flexible Filtering**: Filter by year, month, amount, transaction type, and more
- **Static HTML Dashboard**: Generate multi-page dashboard with charts and trends for monitoring financial performance

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .  # Install package in development mode
```

Or use the setup script:
```bash
./setup_venv.sh
```

3. Configure the reports path:
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml and set your reports_path
   ```

   Alternatively, you can override it with the `OMISLISI_REPORTS_PATH` environment variable.

## Usage

```bash
# Activate virtual environment first
source venv/bin/activate

# Show help
oa --help

# Analyze all transactions (default path)
oa analyze

# Analyze transactions for a specific year
oa analyze --year 2025

# Generate a monthly report
oa report --month 2025-08

# Generate a yearly report
oa report --year 2025

# Categorize transactions from a specific file
oa categorize /path/to/file.xml
oa categorize /path/to/Paypal-2025-08.csv

# Drill down into a specific category
oa category sales --year 2025
oa category large_deals --year 2025 --sort amount
oa category bank_fees --type expense --min-amount 10 --limit 20

# Use custom reports path
oa analyze --reports-path /path/to/reports

# Generate static HTML dashboard (includes all available months)
oa generate-dashboard --output-dir ./dashboard

# Generate dashboard with specific default month (dashboard still includes all months)
oa generate-dashboard --month 2025-08 --output-dir ./dashboard
```

## Supported File Formats

### Bank Statements
- **Format**: ISO 20022 camt.053 XML
- **Location**: Zip files (e.g., `DH-2025-08.zip`) containing XML files
- **Structure**: Each zip contains a directory with daily XML statement files

### PayPal Transactions
- **Format**: CSV export from PayPal
- **Location**: Direct CSV files (e.g., `Paypal-2025-08.csv`)
- **Note**: Internal PayPal operations (currency conversions, deposits) are automatically filtered out

## Project Structure

- `omislisi_accounting/` - Main package
  - `cli/` - CLI command handlers
  - `parsers/` - Parsers for bank XML and PayPal CSV
    - `bank_parser.py` - ISO 20022 camt.053 parser
    - `paypal_parser.py` - PayPal CSV parser
    - `zip_handler.py` - Zip file extraction utilities
  - `domain/` - Domain knowledge (categories, rules, etc.)
    - `categories.py` - Expense/income categorization logic
  - `analysis/` - Analysis and reporting modules
    - `reporter.py` - Summary and breakdown generation
    - `dashboard_data.py` - Dashboard data collection and aggregation
    - `counterparty_utils.py` - Counterparty name normalization and grouping
  - `templates/` - HTML template rendering
    - `renderer.py` - Dashboard HTML generation
    - `static/` - CSS and JavaScript files
- `tests/` - Comprehensive unit tests
  - `test_analysis.py` - Tests for reporter module
  - `test_cli.py` - Tests for CLI commands
  - `test_config.py` - Tests for configuration
  - `test_dashboard_data.py` - Tests for dashboard data collection
  - `test_counterparty_utils.py` - Tests for counterparty utilities
  - `test_domain.py` - Tests for categorization logic
  - `test_parsers.py` - Tests for parsers
  - `test_renderer.py` - Tests for template rendering
  - `test_zip_handler.py` - Tests for zip file handling
- `config.py` - Configuration settings

## Testing

The project includes comprehensive test coverage for all Python modules. Run the test suite with pytest:

```bash
# Install test dependencies (pytest is already in requirements.txt)
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_parsers.py

# Run tests with coverage report (requires pytest-cov)
pytest --cov=omislisi_accounting --cov-report=html
```

### Test Coverage

The test suite includes:

- **CLI Commands**: All CLI commands including analyze, report, trends, category, counterparties, and generate-dashboard
- **Parsers**: Bank XML parser, PayPal CSV parser, and parser factory
- **Domain Logic**: Transaction categorization with subcategories and edge cases
- **Analysis**: Summary generation, category breakdowns, and dashboard data collection
- **Counterparty Utils**: Name normalization, grouping, and breakdown generation
- **Template Rendering**: Dashboard HTML generation and template loading
- **Zip Handling**: File extraction and filtering

All tests use pytest fixtures and follow consistent patterns for maintainability.

## Dashboard Generation

Generate a static HTML dashboard with multiple pages showing financial trends and analysis:

```bash
# Generate dashboard in default location (./dashboard)
oa generate-dashboard

# Generate dashboard in custom location
oa generate-dashboard --output-dir /path/to/dashboard

# Generate dashboard for specific year
oa generate-dashboard --year 2025
```

The dashboard includes:
- **Overview**: Key metrics and quick trends for the selected month
- **Month View**: Detailed analysis for the selected month with month-over-month comparison
- **Year-to-Date**: YTD totals, monthly progression, and projections
- **Last 12 Months**: Rolling 12-month trends and monthly breakdowns
- **Year Comparison**: Year-over-year comparison with charts
- **Categories**: Category breakdowns with visualizations
- **Counterparties**: Top counterparties analysis

The dashboard includes **all available months** from your transaction data. Use the month selector dropdown at the top of any page to switch between months and view their details. The `--month` option only sets the default month to display when the dashboard first loads (defaults to the most recent month with data).

**Safe Overwrite**: The dashboard generation safely overwrites the output directory each time it runs. All existing HTML files are removed, and the static directory is recreated, ensuring no orphaned files are left behind. You can safely run `oa generate-dashboard` every month without worrying about leftover files.

### Automated Updates

Use the provided script for automated dashboard updates:

```bash
# Manual update
./scripts/update_dashboard.sh

# Set up cron job for daily updates (example)
0 2 * * * /path/to/omislisi-accounting/scripts/update_dashboard.sh
```

The generated dashboard is fully static (HTML, CSS, JavaScript) and can be hosted on any web server or file hosting service.

## Deployment

The dashboard can be deployed to a production server using Fabric. See [deploy/README.md](deploy/README.md) for detailed deployment instructions.

### Quick Start

1. **Install dependencies** (including deployment tools):
   ```bash
   pip install -r requirements.txt
   ```

   This includes `fab-classic` (Fabric 1.x compatible) for deployment.

2. **Deploy to server**:
   ```bash
   fab web deploy
   ```

   This will automatically generate the dashboard from your local transaction data and deploy it to the server.

### Initial Setup

For first-time deployment, run:

```bash
fab web setup
```

This sets up:
- Nginx configuration
- SSL certificate (Let's Encrypt)
- HTTP Basic Auth

See [deploy/README.md](deploy/README.md) for complete deployment documentation.

## Customization

### Adding Categories

Edit `omislisi_accounting/domain/categories.py` to add or modify expense/income categories and their keyword mappings.

### Custom Parsers

To add support for additional file formats, create a new parser class inheriting from `TransactionParser` in `omislisi_accounting/parsers/base.py` and register it in `parser_factory.py`.

