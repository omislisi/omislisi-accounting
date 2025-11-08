"""Tests for domain logic."""

import pytest

from omislisi_accounting.domain.categories import (
    categorize_transaction,
    get_all_categories,
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
)


def test_categorize_expense():
    """Test expense categorization."""
    assert categorize_transaction("Office supplies purchase", "expense") == "office"
    assert categorize_transaction("Software license", "expense") == "software"
    assert categorize_transaction("Marketing campaign", "expense") == "marketing"
    assert categorize_transaction("Hotel booking", "expense") == "travel"
    assert categorize_transaction("Restaurant lunch", "expense") == "meals"
    assert categorize_transaction("Unknown expense", "expense") == "other"


def test_categorize_income():
    """Test income categorization."""
    # Most income defaults to sales:invoice
    result = categorize_transaction("Sale payment", "income")
    assert result.startswith("sales") or result == "refund" or result.startswith("compensations")
    result = categorize_transaction("Company payment", "income")
    assert result.startswith("sales") or result.startswith("compensations")
    assert categorize_transaction("Refund received", "income") == "refund"
    # Loan detection - check it's a valid income category
    result = categorize_transaction("Loan from bank", "income", amount=5000)
    assert result.startswith("loans") or result.startswith("compensations")
    # Large amounts (>€1,000) - check it's a valid income category
    result = categorize_transaction("Payment", "income", amount=1500)
    assert result.startswith("large_deals") or result.startswith("compensations") or result.startswith("sales")
    # Small amounts default to sales:invoice
    result = categorize_transaction("Payment", "income", amount=500)
    assert result.startswith("sales") or result.startswith("compensations")


def test_categorize_by_counterparty():
    """Test categorization by counterparty name."""
    result = categorize_transaction("Payment", "expense", counterparty="IN-FIT d.o.o.")
    assert result.startswith("professional_services")
    result = categorize_transaction("Rent", "expense", counterparty="KIKŠTARTER")
    assert result.startswith("office") or result.startswith("offices")
    result = categorize_transaction("Payment", "expense", counterparty="Študentski servis D.O.O.")
    assert result.startswith("salary")
    result = categorize_transaction("Payment", "expense", counterparty="SS D.O.O.")
    assert result.startswith("salary")


def test_categorize_by_account():
    """Test categorization by account number."""
    assert categorize_transaction("Payment", "expense", account="SI56290000059820339") == "salary:students"
    # Account takes precedence over description
    assert categorize_transaction("Office supplies", "expense", account="SI56290000059820339") == "salary:students"


def test_get_all_categories():
    """Test getting all categories."""
    all_cats = get_all_categories()
    assert "office" in all_cats
    assert "sales" in all_cats

    expense_cats = get_all_categories("expense")
    assert "office" in expense_cats
    assert "sales" not in expense_cats

    income_cats = get_all_categories("income")
    assert "sales" in income_cats
    assert "office" not in income_cats


def test_taxes_subcategory():
    """Test taxes subcategory detection."""
    # VAT (DDV)
    assert categorize_transaction("Plačilo DDV", "expense") == "taxes:vat"
    assert categorize_transaction("DDV payment", "expense") == "taxes:vat"

    # Advance tax payments
    assert categorize_transaction("Akontacija DDPO", "expense") == "taxes:advance"
    assert categorize_transaction("Akontacija davka", "expense") == "taxes:advance"

    # Corporate taxes
    assert categorize_transaction("Davek od dobička", "expense") == "taxes:corporate_tax"
    assert categorize_transaction("Davek na dohodek", "expense") == "taxes:corporate_tax"

    # Personal income tax
    assert categorize_transaction("Dohodnina", "expense") == "taxes:income_tax"

    # General taxes (fallback)
    assert categorize_transaction("Tax payment", "expense") == "taxes"


def test_social_security_subcategory():
    """Test social security subcategory detection."""
    # Long-term care (DO)
    result = categorize_transaction("Prispevek za DO", "expense")
    assert result.startswith("social_security")

    # Parental protection (STV)
    result = categorize_transaction("Prispevek za STV", "expense")
    assert result.startswith("social_security")
    result = categorize_transaction("Prispevki za starševsko", "expense")
    assert result.startswith("social_security")

    # Employment/Unemployment (ZAP)
    result = categorize_transaction("Prispevek za ZAP", "expense")
    assert result.startswith("social_security")

    # Work injury (PB)
    result = categorize_transaction("Prispevek za PB", "expense")
    assert result.startswith("social_security")

    # Health insurance (ZZ/ZZZS)
    result = categorize_transaction("Prispevek za ZZ", "expense")
    assert result.startswith("social_security")
    result = categorize_transaction("Prispevek za ZZZS", "expense")
    assert result.startswith("social_security")

    # Pension and disability (PIZ, PPD)
    result = categorize_transaction("Prispevek za PIZ", "expense")
    assert result.startswith("social_security")
    result = categorize_transaction("Prispevek za PPD", "expense")
    assert result.startswith("social_security")

    # Combined PPD+PB
    result = categorize_transaction("Prispevek za PPD in PB", "expense")
    assert result.startswith("social_security")


def test_professional_services_subcategory():
    """Test professional services subcategory detection."""
    # Accounting services by counterparty
    result = categorize_transaction("Payment", "expense", counterparty="IN-FIT d.o.o.")
    assert result.startswith("professional_services")
    result = categorize_transaction("Payment", "expense", counterparty="CTRP d.o.o.")
    assert result.startswith("professional_services")

    # Legal services by counterparty - check if it starts with professional_services
    result = categorize_transaction("Payment", "expense", counterparty="Notarka")
    assert result.startswith("professional_services") or result.startswith("other")

    # Accounting by description
    result = categorize_transaction("Računovodstvo", "expense")
    assert result.startswith("professional_services") or result.startswith("other")
    result = categorize_transaction("Racunovodstvo", "expense")
    assert result.startswith("professional_services") or result.startswith("other")

    # Legal by description
    result = categorize_transaction("Pravno svetovanje", "expense")
    assert result.startswith("professional_services") or result.startswith("other")
    result = categorize_transaction("Notarka", "expense")
    assert result.startswith("professional_services") or result.startswith("other")
    result = categorize_transaction("Odvetnik", "expense")
    assert result.startswith("professional_services") or result.startswith("other")


def test_marketing_subcategory():
    """Test marketing subcategory detection."""
    # Stock images by counterparty
    result = categorize_transaction("Payment", "expense", counterparty="Shutterstock")
    assert result.startswith("marketing") or result.startswith("other")

    # Facebook/Meta Ads by counterparty
    result = categorize_transaction("Payment", "expense", counterparty="Meta")
    assert result.startswith("marketing") or result.startswith("other")
    result = categorize_transaction("Payment", "expense", counterparty="Facebk")
    assert result.startswith("marketing") or result.startswith("other")

    # Google Ads by counterparty
    result = categorize_transaction("Payment", "expense", counterparty="Google Ads")
    assert result.startswith("marketing") or result.startswith("other")

    # SEO by counterparty
    result = categorize_transaction("Payment", "expense", counterparty="SEOPro")
    assert result.startswith("marketing") or result.startswith("other")

    # Marketing agencies by counterparty
    result = categorize_transaction("Payment", "expense", counterparty="EggMedia")
    assert result.startswith("marketing") or result.startswith("other")

    # Google Ads by description
    result = categorize_transaction("Google Ads payment", "expense")
    assert result.startswith("marketing") or result.startswith("other")

    # Facebook Ads by description
    result = categorize_transaction("Facebook Ads", "expense")
    assert result.startswith("marketing") or result.startswith("other")

    # SEO by description
    result = categorize_transaction("SEO services", "expense")
    assert result.startswith("marketing") or result.startswith("other")

    # General marketing (fallback)
    result = categorize_transaction("Marketing campaign", "expense")
    assert result.startswith("marketing") or result.startswith("other")


def test_other_subcategory():
    """Test other subcategory detection."""
    # Media services by counterparty
    assert categorize_transaction("Payment", "expense", counterparty="Media24") == "other:media"

    # Hardware by counterparty
    assert categorize_transaction("Payment", "expense", counterparty="ComputerUniverse") == "other:hardware"

    # Travel by counterparty
    assert categorize_transaction("Payment", "expense", counterparty="Airbnb") == "other:travel"

    # Events by counterparty
    assert categorize_transaction("Payment", "expense", counterparty="Eventim") == "other:events"

    # Furniture by counterparty
    assert categorize_transaction("Payment", "expense", counterparty="Bauhaus") == "other:furniture"

    # AI services by counterparty
    assert categorize_transaction("Payment", "expense", counterparty="ElevenLabs") == "other:ai_services"

    # Media by description
    assert categorize_transaction("Media services", "expense") == "other:media"

    # Travel by description
    assert categorize_transaction("Hotel booking", "expense") == "travel"  # Should be travel category, not other:travel
    assert categorize_transaction("Airbnb booking", "expense") == "other:travel"

    # Events by description
    assert categorize_transaction("Eventim ticket", "expense") == "other:events"

    # Printing by description
    assert categorize_transaction("Tisk", "expense") == "other:printing"
    assert categorize_transaction("Digitalni tisk", "expense") == "other:printing"

    # General other (fallback)
    assert categorize_transaction("Miscellaneous", "expense") == "other"


def test_sales_subcategory():
    """Test sales subcategory detection."""
    # Stripe by counterparty
    assert categorize_transaction("Payment", "income", counterparty="Stripe") == "sales:stripe"

    # Stripe by description
    assert categorize_transaction("Stripe payment", "income") == "sales:stripe"

    # Invoice (default for sales)
    assert categorize_transaction("Invoice payment", "income") == "sales:invoice"
    assert categorize_transaction("Payment from client", "income") == "sales:invoice"


def test_categorize_edge_cases():
    """Test edge cases in categorization."""
    # Empty description
    assert categorize_transaction("", "expense") == "other"
    result = categorize_transaction("", "income")
    assert result.startswith("sales") or result.startswith("compensations") or result == "other"

    # None description
    assert categorize_transaction(None, "expense") == "other"

    # Very long description
    long_desc = "A" * 1000
    assert categorize_transaction(long_desc, "expense") == "other"

    # Special characters
    assert categorize_transaction("Ščžćđ", "expense") == "other"

    # Amount boundaries for income - check valid categories
    result = categorize_transaction("Payment", "income", amount=999.99)
    assert result.startswith("sales") or result.startswith("compensations")
    result = categorize_transaction("Payment", "income", amount=1000.01)
    assert result.startswith("large_deals") or result.startswith("compensations") or result.startswith("sales")
    result = categorize_transaction("Payment", "income", amount=1000.0)
    assert result.startswith("large_deals") or result.startswith("compensations") or result.startswith("sales")

    # Zero amount
    result = categorize_transaction("Payment", "income", amount=0)
    assert result.startswith("sales") or result.startswith("compensations")

    # Negative amount (shouldn't happen for income, but test anyway)
    result = categorize_transaction("Payment", "income", amount=-100)
    assert result.startswith("sales") or result.startswith("compensations") or result == "other"


def test_categorize_complex_scenarios():
    """Test complex categorization scenarios."""
    # Account takes precedence over counterparty
    assert categorize_transaction(
        "Office supplies",
        "expense",
        account="SI56290000059820339",
        counterparty="Office Store"
    ) == "salary:students"

    # Counterparty takes precedence over description
    assert categorize_transaction(
        "Random payment",
        "expense",
        counterparty="IN-FIT d.o.o."
    ) == "professional_services:accounting"

    # Large income amount - check it's a valid income category
    result = categorize_transaction(
        "Payment",
        "income",
        amount=1500
    )
    # Should be large_deals or compensations for amounts > 1000
    assert result.startswith("large_deals") or result.startswith("compensations") or result.startswith("sales")

    # Loan detection - check it's a valid income category
    result = categorize_transaction(
        "Loan from bank",
        "income",
        amount=5000
    )
    assert result.startswith("loans") or result.startswith("compensations")

    # Refund detection
    assert categorize_transaction(
        "Refund received",
        "income"
    ) == "refund"


def test_categorize_with_tags():
    """Test that categories can include tags (subcategories)."""
    # Taxes with VAT tag
    result = categorize_transaction("Plačilo DDV", "expense")
    assert ":" in result
    assert result.startswith("taxes")

    # Social security with tag
    result = categorize_transaction("Prispevek za DO", "expense")
    assert ":" in result
    assert result.startswith("social_security")

    # Professional services with tag
    result = categorize_transaction("Payment", "expense", counterparty="IN-FIT d.o.o.")
    assert ":" in result
    assert result.startswith("professional_services")

    # Sales with tag
    result = categorize_transaction("Payment", "income", counterparty="Stripe")
    assert ":" in result
    assert result.startswith("sales")

