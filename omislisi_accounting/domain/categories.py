"""Expense and income categories for the company."""

from typing import Dict, List, Optional

# Account number mappings (IBAN) to categories
ACCOUNT_CATEGORIES: Dict[str, str] = {
    "SI56290000059820339": "salary:students",  # Študentski servis - student salary payments
}

# Counterparty name mappings to categories
# These match against the deduped counterparty display names from the counterparties command
COUNTERPARTY_CATEGORIES: Dict[str, str] = {
    # Taxes (normalized without diacritics)
    "rs prehodni davcni podracun": "taxes:advance",  # Interim tax account - advance payments
    "prehodni davcni podracun": "taxes:advance",  # Interim tax account - advance payments
    "prehodni davcni podracun - proracun": "taxes",  # State budget account - general taxes
    "pdp - proracun drzave": "taxes",  # State budget account - general taxes
    "furs": "taxes",  # Financial Administration - general taxes
    "furs - prehodni podracun": "taxes:advance",  # Financial Administration interim account - advance payments

    # Social Security (normalized without diacritics)
    "prehodni davcni podracun - zpiz": "social_security:pension_disability",  # ZPIZ = Pension and Disability Insurance
    "prehodni davcni podracun - zzzs": "social_security:health",  # ZZZS = Health Insurance

    # Salary - Founders (normalized without diacritics)
    "mitja pritrznik": "salary:founders",
    "martin korenjak": "salary:founders",

    # Salary - Students (normalized without diacritics)
    "ss d.o.o.": "salary:students",
    "ss": "salary:students",
    "studentski servis": "salary:students",
    "studentski servis d.o.o.": "salary:students",
    "s. d.o.o.": "salary:students",

    # Salary - Employees (normalized without diacritics)
    "tjasa fatur": "salary:employees",
    "ana sinigoj": "salary:employees",

    # Salary - Contractual Sales (normalized without diacritics)
    "tomaz plesec": "salary:contractual_sales",
    "sanson sales": "salary:contractual_sales",
    "sanson sales tomaz plesec s.p.": "salary:contractual_sales",
    "valuna": "salary:contractual_sales",
    "valuna ajda hvastija s.p.": "salary:contractual_sales",
    "ajda hvastija": "salary:contractual_sales",
    "klemen bogataj": "salary:contractual_sales",
    "klemen bogataj s.p.": "salary:contractual_sales",
    "nejc pus": "salary:contractual_sales",
    "nejc pus s.p.": "salary:contractual_sales",

    # Professional Services - Accounting (normalized without diacritics)
    "in-fit": "professional_services:accounting",
    "in-fit d.o.o.": "professional_services:accounting",
    "ctrp": "professional_services:accounting",
    "društvo ctrp maribor": "professional_services:accounting",
    "društvo ctrp maribor so. p.": "professional_services:accounting",

    # Professional Services - Legal (normalized without diacritics)
    "notarka branka ivanusa": "professional_services:legal",
    "em-er": "professional_services:legal",
    "em-er matjaz rambaher": "professional_services:legal",
    "em-er matjaz rambaher s.p.": "professional_services:legal",

    # Salary - Contractual Programming (normalized without diacritics)
    "314": "salary:contractual_programming",
    "314 d.o.o.": "salary:contractual_programming",
    "foreach labs": "salary:contractual_programming",
    "foreach labs d.o.o.": "salary:contractual_programming",

    # Salary - Contractual SEO/Marketing (normalized without diacritics)
    "smartads": "salary:contractual_marketing",
    "smartads neza bizjak s.p.": "salary:contractual_marketing",

    # Salary - Contractual Design (normalized without diacritics)
    "orelia": "salary:contractual_design",
    "orelia solutions": "salary:contractual_design",
    "orelia solutions masa orel s.p.": "salary:contractual_design",

    # Software/Services - CRM
    "activecampaign": "software:crm",
    "activecampaign llc": "software:crm",

    # Software/Services - Email
    "mailchimp": "software:email",

    # Bradstreet
    "bradstreet": "software:credit_reporting",

    # Software/Services - SMS
    "ms3": "software:sms",
    "ms3 d.o.o.": "software:sms",

    # Postal Services (normalized without diacritics)
    "posta slovenije": "utilities:postal",
    "posta slovenije d.o.o.": "utilities:postal",
    "epps": "utilities:postal",
    "epps d.o.o.": "utilities:postal",

    # Mobile Services
    "a1": "utilities:mobile",
    "a1 slovenija": "utilities:mobile",
    "a1 slovenija, d. d.": "utilities:mobile",

    # Office/Coworking (normalized without diacritics)
    "kikštarter": "offices:coworking",
    "kikstarter": "offices:coworking",  # Alternative spelling
    "zadruga kikštarter center": "offices:coworking",
    "zadruga kikštarter center z.b.o.": "offices:coworking",
    "abc accelerator": "offices:coworking",
    "abc accelerator d.o.o.": "offices:coworking",
    "btc": "offices:coworking",
    "btc d.d.": "offices:coworking",

    # Web Hosting
    "contabo": "software:hosting",
    "contabo gmbh": "software:hosting",
    "infosplet": "software:hosting",
    "infosplet, d.o.o.": "software:hosting",
    "avant": "software:hosting",

    # Payment Processors - Stripe (income = sales, expenses = fees)
    # Note: Stripe income transactions are subscription payments (sales), not fees
    # Only Stripe expenses (fees) should be categorized as bank_fees
    # Special handling in categorize_transaction function overrides this for income
    "stripe": "bank_fees",

    # Software/Services - Automation
    "zapier": "software",
    "zapier, inc.": "software",

    "ahrefs": "software:seo",

    "lovable": "software:automation",
    "canva": "software:design",

    "openai": "software:ai",
    "claude": "software:ai",
    "anthropic": "software:ai",
    "jasper": "software:ai",

    # Software/Services - Development Tools
    "github": "software:development_tools",
    "github, inc.": "software:development_tools",
    "cursor": "software:development_tools",
    "circleci": "software:development_tools",

    "shutterstock": "marketing:stock_images",
    "shutterstock inc.": "marketing:stock_images",

    # Marketing - Facebook/Meta Ads
    "meta platforms": "marketing:facebook_ads",
    "meta platforms, inc.": "marketing:facebook_ads",
    "facebk": "marketing:facebook_ads",

    # Marketing - Google Ads (various formats)
    # Note: Don't map generic "google" - it's too broad and matches software services
    # Google Ads transactions are matched via description patterns (google + ads)

    # Marketing - SEO Services
    "seopro": "marketing:seo",
    "seopro igor bajsic": "marketing:seo",
    "seopro igor bajsic s.p.": "marketing:seo",

    # Marketing - Agencies
    "eggmedia": "marketing:agencies",
    "eggmedia d.o.o.": "marketing:agencies",
    "pro plus": "marketing:agencies",
    "pro plus d.o.o.": "marketing:agencies",
    "4future": "marketing:agencies",
    "4future dgt agency": "marketing:agencies",
    "4future dgt agency d.o.o.": "marketing:agencies",
    "termin informatika": "marketing:agencies",
    "termin informatika d.o.o.": "marketing:agencies",

    # Equipment (from description analysis)
    "mobileshop": "equipment",
    "mobileshop.eu": "equipment",

    # Amazon purchases
    "amzn": "amazon",
    "amazon": "amazon",

    # Benefits (income only - normalized without diacritics)
    "zzzs": "benefits",
    "zavod za zaposlovanje": "benefits",
    "generali sklad": "benefits",

    # Other - Media Services
    "media24": "other:media",
    "media24 d.o.o.": "other:media",
    "tsmedia": "other:media",
    "tsmedia d.o.o.": "other:media",
    "kip kop": "other:media",
    "kip kop d.o.o.": "other:media",
    "cre8": "other:media",
    "cre8 d.o.o.": "other:media",

    # Other - Hardware/Equipment
    "computeruniverse": "other:hardware",
    "computeruniverse gmbh": "other:hardware",
    "remarkable": "other:hardware",
    "remarkable operations": "other:hardware",
    "eu.store": "other:hardware",
    "eu.store.ui.com": "other:hardware",
    "senetic": "other:hardware",

    # Other - Travel
    "airbnb": "other:travel",
    "airbnb payments": "other:travel",
    "bestero": "other:travel",

    # Other - Events/Tickets
    "eventim": "other:events",
    "mojekarte": "other:events",

    # Other - Furniture/Office
    "bauhaus": "other:furniture",
    "pisarniški stoli": "other:furniture",
    "pisarniški stoli pivk": "other:furniture",

    # Other - AI Services
    "elevenlabs": "other:ai_services",
    "brevilabs": "other:ai_services",
    "scrap.io": "other:ai_services",
}


# Expense categories
EXPENSE_CATEGORIES = {
    "bank_fees": [
        # English
        "fee", "bank fee", "transaction fee", "service charge", "payment processing fee",
        "credit card", "credit card payment",  # Credit card payments/fees
        # Slovenian
        "provizija", "prilivna provizija", "odlivna provizija",
        "vodenje računa", "vodenje poslovnega računa", "uporabnina", "banking fee",
        "dh-mobilni", "dh-poslovni", "dh-poslovni",
        "kreditna kartica",  # Credit card payments (not loans)
        "varnostni sms",  # Security SMS charges
        # Payment processor fees (when just "STRIPE" or "PAYPAL" as expense, it's usually a fee)
        # Note: Stripe/PayPal income transactions are sales (customers paying us)
    ],
    "software": [
        # English
        "software", "subscription", "license", "saas", "hosting", "cloud",
        # Slovenian
        "programiranje", "programska oprema",
        # Company names (be specific to avoid false positives)
        "contabo", "microsoft", "adobe", "paypal",
        "github", "aws", "azure", "digitalocean", "linode",
        # Note: "stripe" removed from expenses - Stripe income is sales (customers paying us)
        # Stripe expenses (fees) should be categorized as bank_fees or stay in other
        "google gsuite", "google*gsuite", "google cloud", "google workspace", "gsuite",  # Google services (not ads)
        "openai", "sentry", "circleci", "circleci.com"  # Software/SaaS services
        # Note: Generic "google" removed - matches "google ads" which should be marketing
    ],
    "professional_services": [
        # English
        "legal", "accounting", "consulting", "professional", "lawyer", "attorney",
        # Slovenian
        "računovodstvo", "računovodski", "svetovanje", "odvetnik", "pravnik",
        "računovodski studio", "svetovanje", "plesec", "tomaž plesec",
        # Company/Person names
        "ajda hvastija", "valuna",
        # Patterns - invoice numbers often indicate professional services
        "račun št."
    ],
    "office": [
        # English
        "office supplies", "stationery", "printer", "paper", "postage", "mail",
        # Slovenian
        "poštne storitve", "pošta", "papir", "tiskalnik"
    ],
    "utilities": [
        # English
        "electricity", "water", "internet", "phone", "utility", "gsm",
        # Slovenian
        "elektrika", "voda", "internet", "telefon", "gsm storitve", "mobilne storitve"
        # Note: Generic "mobile" removed - matches "mobileshop" (equipment purchase, not utility)
    ],
    "taxes": [
        # English
        "tax", "vat", "income tax", "corporate tax", "profit tax",
        # Slovenian - Taxes
        "davek", "davk", "ddv", "plačilo ddv",  # DDV = VAT
        "dohodnina",  # Personal income tax
        "davek od dobička", "davek na dohodek", "davek od dohodka pravnih oseb",  # Corporate taxes
        "akontacija davka", "akontacija ddpo",  # Advance tax payments (DDPO = Corporate Income Tax)
        "plačilo davka", "obračun davka",  # General tax payments
        # Note: "davk" added to catch variations like "davki", "davka", "davku", "davkom", etc.
    ],
    "social_security": [
        # Slovenian - Social Security Contributions (be specific to avoid false positives)
        # Pension and Disability Insurance
        "prispevek za piz", "prispevki za piz",  # PIZ = Pension and Disability Insurance
        "prispevek za ppd",  # PPD = Pension and Disability Insurance
        "prispevek za ppd in pb",  # Combined Pension and Work Injury
        # Health Insurance
        "prispevek za zz", "prispevek za zzzs",  # ZZ/ZZZS = Health Insurance
        "prispevki za zdravstvo",  # Health insurance contributions
        # Work Injury Insurance
        "prispevek za pb",  # PB = Work Injury Insurance
        # Parental Protection
        "prispevek za stv",  # STV = Parental Protection
        "prispevki za starševsko", "prispevki za starsevsko",  # Parental leave contributions
        # Employment/Unemployment Insurance
        "prispevek za zap",  # ZAP = Employment/Unemployment Insurance
        "prispevki za zaposlovanje",  # Employment contributions
        # Long-Term Care
        "prispevek za do",  # DO = Long-Term Care
        # Note: Removed generic "prispevek", "prispevki", "piz", "ppd", "pb", "stv", "zap", "do", "zz", "zzzs"
        # to avoid false positives. Only match specific contribution patterns.
    ],
    "salary": [
        # English
        "salary", "wage", "payroll", "employee", "bonus", "vacation",
        # Slovenian - be specific: "plača" means salary, not generic "plačilo" (payment)
        "plača", "placa", "plaèa", "izplačilo", "zaposleni", "regres", "bonus", "dopust"
        # Note: "plačilo" removed - too generic, matches invoice payments, refunds, etc.
        # Note: "placa" and "plaèa" added - alternative spellings/variants of "plača"
    ],
    "marketing": [
        # English
        "advertising", "marketing", "promotion", "social media", "facebook", "ads",
        "google ads", "google*ads", "facebk",  # Google Ads specifically, Facebook
        "seo",  # Search engine optimization
        # Slovenian
        "oglaševanje", "oglasevanje", "marketing", "promocija", "reklama"
    ],
    "loans": [
        # English - be specific to avoid false positives
        "loan repayment", "loan payment", "borrowing",
        # Slovenian - be specific
        "vracilo posojila", "odplačilo posojila"
        # Note: "credit" removed - too generic, matches "MESSAGE CREDIT" (SMS credits)
        # Note: "posojilo" and "kredit" removed - these are income, not expenses
        # Note: "kreditna kartica" removed - credit card payments are not loans, they're payment processing
    ],
    "travel": [
        # English
        "travel", "hotel", "flight", "transport", "fuel", "taxi", "uber",
        # Slovenian
        "potovanje", "hotel", "prevoz", "gorivo", "taksi", "letalska", "letalo"
        # Note: "let" removed - too short, matches "outlet", "omplet" (false positives)
    ],
    "meals": [
        # English
        "restaurant", "food", "lunch", "dinner", "cafe", "coffee",
        # Slovenian
        "restavracija", "hrana", "kosilo", "večerja", "kavarna", "kava"
    ],
    "equipment": [
        # English
        "equipment", "hardware", "computer", "monitor", "laptop", "printer",
        "cell phone", "mobile phone", "smartphone", "mobileshop",  # Phone purchases
        # Slovenian
        "oprema", "strojna oprema", "računalnik", "monitor", "prenosnik"
        # Note: Amazon purchases are now in "amazon" category, not equipment
    ],
    "amazon": [
        # Amazon purchases (various items)
        "amazon", "amzn", "amznbusiness", "amzn mktp"
    ],
    "compensations:expenses": [
        # Large refunds/compensations (>€1000)
        # These are matched programmatically based on amount and refund keywords
        # Note: Do not add keywords here - matching is done in categorize_transaction() based on amount
    ],
    "other": [],  # Default category
}

# Income categories
# Note: Most income is subscription sales. Only specific patterns are excluded.
INCOME_CATEGORIES = {
    # Non-sales categories (checked first, before defaulting to sales)
    "loans": [
        # Company doesn't take loans - if someone pays us, it's a subscription
        # Only keep explicit loan patterns for historical/edge cases
        # Slovenian
        "posojilo", "posojilo omisli.si"  # Explicit loan patterns only
        # Note: "kreditna druzba" removed - those payments are subscriptions
        # Note: "kreditna kartica" removed - that's our credit card (expense)
        # Note: Generic "loan", "kredit", "credit" removed - too generic, matches subscriptions
    ],
    "transfers": [
        # English
        "transfer", "prenos", "saldacija",
        # Slovenian
        "prenos sredstev", "saldacija", "trr", "transfer", "sberbank"
    ],
    "benefits": [
        # English
        "benefit", "compensation", "grant", "subsidy",
        # Slovenian
        "zzzs",  # Health insurance - sick day compensation
        "zavod za zdravstveno zavarovanje",  # Full name of health insurance institute
        "zavod za zaposlovanje",  # Employment agency - grants covering salary expenses
        "generali sklad",  # Generali fund - insurance benefits
        "nadomestilo", "subvencija", "dodatek"  # Compensation, subsidy, allowance
    ],
    "refund": [
        # English
        "refund", "return", "reimbursement", "tax refund",
        # Slovenian
        "vračilo", "preplačilo", "povrnitev", "refund", "furs", "rs mf furs",  # Tax authority refunds
        "izterjava"  # Collection/refund
    ],
    "compensations:income": [
        # Large income deals (>€1,000) - custom deals, not subscriptions
        # This category is set programmatically for amounts > €1,000
        # but we include some keywords that indicate large deals
        "projekt", "project", "custom", "enterprise"
    ],
    "sales": [
        # Default category for subscription sales
        # Most income transactions are subscription payments
        # English
        "sale", "revenue", "payment", "invoice", "income", "earnings",
        "subscription", "yearly", "monthly", "quarterly", "tri-monthly",
        # Slovenian
        "plačilo", "takojšnje plačilo", "priliv", "račun", "računa",
        "št računa", "paket", "premium", "letni paket", "objava v imeniku",
        "naročnina", "letna", "mesečna", "četrtletna",
        # Patterns
        "d.o.o.", "s.p.", "sp", "doo",  # Company types indicate sales
        "-pro", "-oms", "-plč",  # Invoice number patterns
        "sent from revolut", "revolut", "stripe",  # Payment platforms (customers paying us)
        # Invoice number patterns (e.g., "2025-0936-PRO", "2022-0372-PRO")
        # Match invoice-like patterns with year-number format
        "2021-", "2022-", "2023-", "2024-", "2025-", "2026-"
    ],
    "other": [],  # Should rarely be used for income
}


def _get_taxes_subcategory(description_lower: str) -> str:
    """Determine the taxes subcategory based on description."""
    # Check for VAT (DDV) - most specific first
    if "plačilo ddv" in description_lower or "ddv" in description_lower:
        return "taxes:vat"
    # Check for advance tax payments
    if "akontacija ddpo" in description_lower or "akontacija davka" in description_lower:
        return "taxes:advance"
    # Check for corporate taxes
    if "davek od dobička" in description_lower or "davek na dohodek" in description_lower or "davek od dohodka pravnih oseb" in description_lower:
        return "taxes:corporate_tax"
    # Check for personal income tax
    if "dohodnina" in description_lower:
        return "taxes:income_tax"
    # Default to general taxes
    return "taxes"


def _get_social_security_subcategory(description_lower: str) -> str:
    """Determine the social_security subcategory based on description."""
    # Check for Long-Term Care (DO) - most specific first
    if "prispevek za do" in description_lower:
        return "social_security:long_term_care"
    # Check for Parental Protection (STV)
    if "prispevek za stv" in description_lower or "prispevki za starševsko" in description_lower or "prispevki za starsevsko" in description_lower:
        return "social_security:parental"
    # Check for Employment/Unemployment (ZAP)
    if "prispevek za zap" in description_lower or "prispevki za zaposlovanje" in description_lower:
        return "social_security:unemployment"
    # Check for Work Injury (PB) - check before PPD since PPD+PB is combined
    if "prispevek za ppd in pb" in description_lower:
        return "social_security:pension_disability"  # Combined, categorize as pension_disability
    if "prispevek za pb" in description_lower and "ppd" not in description_lower:
        return "social_security:work_injury"
    # Check for Health Insurance (ZZ/ZZZS)
    if "prispevek za zz" in description_lower or "prispevek za zzzs" in description_lower or "prispevki za zdravstvo" in description_lower:
        return "social_security:health"
    # Check for Pension and Disability (PIZ, PPD)
    if "prispevek za piz" in description_lower or "prispevki za piz" in description_lower or "prispevek za ppd" in description_lower:
        return "social_security:pension_disability"
    # Default to general social_security
    return "social_security"


def _get_professional_services_subcategory(description_lower: str, counterparty_normalized: str = None) -> str:
    """Determine the professional_services subcategory based on description and counterparty."""
    # Check counterparty first (most reliable)
    if counterparty_normalized:
        if "in-fit" in counterparty_normalized or "ctrp" in counterparty_normalized:
            return "professional_services:accounting"
        if "notarka" in counterparty_normalized or ("em-er" in counterparty_normalized and "rambaher" in counterparty_normalized):
            return "professional_services:legal"

    # Check description for accounting keywords
    if "računovodstvo" in description_lower or "racunovodstvo" in description_lower:
        return "professional_services:accounting"

    # Check description for legal keywords
    if "pravno" in description_lower or "notarka" in description_lower or "odvetnik" in description_lower or "pravnik" in description_lower:
        return "professional_services:legal"

    # Default to general professional_services
    return "professional_services"


def _get_marketing_subcategory(description_lower: str, counterparty_normalized: str = None) -> str:
    """Determine the marketing subcategory based on description and counterparty."""
    # Check counterparty first (most reliable)
    if counterparty_normalized:
        # Stock images
        if "shutterstock" in counterparty_normalized:
            return "marketing:stock_images"

        # Facebook/Meta Ads
        if "meta" in counterparty_normalized or "facebk" in counterparty_normalized:
            return "marketing:facebook_ads"

        # Google Ads (various formats)
        if ("google" in counterparty_normalized and "ads" in counterparty_normalized) or "googleadwordseu" in counterparty_normalized:
            return "marketing:google_ads"

        # SEO Services
        if "seopro" in counterparty_normalized:
            return "marketing:seo"

        # Marketing Agencies
        if any(agency in counterparty_normalized for agency in ["eggmedia", "pro plus", "4future", "termin informatika"]):
            return "marketing:agencies"

    # Check description for Google Ads (various formats)
    if "google" in description_lower and ("ads" in description_lower or "adwordseu" in description_lower):
        return "marketing:google_ads"

    # Check description for Facebook Ads
    if "facebk" in description_lower or ("facebook" in description_lower and "ads" in description_lower):
        return "marketing:facebook_ads"

    # Check description for SEO
    if "seo" in description_lower:
        return "marketing:seo"

    # Check description for stock images
    if "shutterstock" in description_lower:
        return "marketing:stock_images"

    # Default to general marketing
    return "marketing"


def _get_other_subcategory(description_lower: str, counterparty_normalized: str = None) -> str:
    """Determine the other subcategory based on description and counterparty."""
    # Check counterparty first (most reliable)
    if counterparty_normalized:
        # Media Services
        if any(media in counterparty_normalized for media in ["media24", "tsmedia", "kip kop", "cre8"]):
            return "other:media"

        # Hardware/Equipment
        if any(hw in counterparty_normalized for hw in ["computeruniverse", "remarkable", "eu.store", "senetic"]):
            return "other:hardware"

        # Travel
        if any(travel in counterparty_normalized for travel in ["airbnb", "bestero"]):
            return "other:travel"

        # Events/Tickets
        if any(event in counterparty_normalized for event in ["eventim", "mojekarte"]):
            return "other:events"

        # Furniture/Office
        if any(furniture in counterparty_normalized for furniture in ["bauhaus", "pisarniški stoli"]):
            return "other:furniture"

        # AI Services
        if any(ai in counterparty_normalized for ai in ["elevenlabs", "brevilabs", "scrap.io"]):
            return "other:ai_services"

    # Check description for patterns
    # Media Services
    if any(word in description_lower for word in ["media", "oglaševanje", "reklama"]):
        return "other:media"

    # Travel
    if any(word in description_lower for word in ["airbnb", "hotel", "travel", "bestero"]):
        return "other:travel"

    # Events/Tickets
    if any(word in description_lower for word in ["eventim", "mojekarte", "vstopnica", "ticket"]):
        return "other:events"

    # Printing Services
    if any(word in description_lower for word in ["tisk", "digitalni tisk", "print", "printing"]):
        return "other:printing"

    # Furniture/Office
    if any(word in description_lower for word in ["bauhaus", "stol", "furniture", "pisarniški"]):
        return "other:furniture"

    # AI Services
    if any(word in description_lower for word in ["elevenlabs", "brevilabs", "scrap.io", "ai"]):
        return "other:ai_services"

    # Hardware/Equipment
    if any(word in description_lower for word in ["computeruniverse", "remarkable", "hardware", "equipment"]):
        return "other:hardware"

    # Default to general other
    return "other"


def _get_sales_subcategory(description_lower: str, counterparty_normalized: str = None) -> str:
    """Determine the sales subcategory based on description and counterparty."""
    # Check for Stripe (payment processor for subscriptions)
    if counterparty_normalized and "stripe" in counterparty_normalized:
        return "sales:stripe"
    if "stripe" in description_lower:
        return "sales:stripe"
    # Default to invoice (all other sales)
    return "sales:invoice"


def categorize_transaction(
    description: str,
    transaction_type: str,
    amount: float = None,
    counterparty: str = None,
    account: str = None
) -> str:
    """
    Categorize a transaction based on its description, amount, counterparty, and account.

    Args:
        description: Transaction description
        transaction_type: 'income' or 'expense'
        amount: Transaction amount (optional, used for income threshold logic)
        counterparty: Counterparty/payer/recipient name (optional)
        account: Bank account IBAN (optional)

    Returns:
        Category name
    """
    # Check account number first (most specific)
    # Note: Salary-related account mappings should only apply to expenses, not income
    if account and account in ACCOUNT_CATEGORIES:
        category = ACCOUNT_CATEGORIES[account]
        # Salary categories should only apply to expenses, not income
        if transaction_type == "income" and category.startswith("salary"):
            # Skip account-based salary categorization for income
            pass
        else:
            return category

    # Normalize counterparty name for use in categorization (needed for sales subcategory determination)
    counterparty_normalized = None
    if counterparty:
        import re
        import unicodedata

        # Normalize counterparty name (same logic as counterparties command)
        counterparty_normalized = counterparty.lower()
        counterparty_normalized = unicodedata.normalize('NFD', counterparty_normalized)
        counterparty_normalized = ''.join(c for c in counterparty_normalized if unicodedata.category(c) != 'Mn')
        # Normalize "ss" to "ss d.o.o." only when "ss" is a standalone word (not part of other words like "fitness", "express")
        # Use word boundaries to ensure "ss" is standalone, and it must be followed by "d.o.o." or similar
        counterparty_normalized = re.sub(r'\bss\s+d\.o\.o\.', 'ss d.o.o.', counterparty_normalized)
        counterparty_normalized = re.sub(r'\bss\s+d\.o\.o\b', 'ss d.o.o.', counterparty_normalized)
        counterparty_normalized = re.sub(r',\s*(d\.o\.o\.?|d\.d\.?|s\.p\.?|z\.b\.o\.?)', r' \1', counterparty_normalized)
        counterparty_normalized = re.sub(r'\bd\.o\.o\.?\b', 'd.o.o.', counterparty_normalized)
        counterparty_normalized = re.sub(r'\bd\.d\.\.?\b', 'd.d.', counterparty_normalized)
        counterparty_normalized = re.sub(r'\bs\.p\.\.?\b', 's.p.', counterparty_normalized)
        counterparty_normalized = re.sub(r'\bz\.b\.o\.\.?\b', 'z.b.o.', counterparty_normalized)
        counterparty_normalized = re.sub(r'\.{2,}', '.', counterparty_normalized)
        counterparty_normalized = re.sub(r'\s+', ' ', counterparty_normalized).strip()

    # Check counterparty name second (normalize for better matching)
    if counterparty:
        # Try exact match first, then word-boundary-aware substring match
        # For short keys like "ss", require word boundaries to avoid false positives
        for counterparty_key, category in COUNTERPARTY_CATEGORIES.items():
            matched = False
            if counterparty_key == counterparty_normalized:
                matched = True
            elif len(counterparty_key) <= 3:
                # For short keys (like "ss"), require word boundaries to avoid false positives
                # e.g., "ss" should match "ss d.o.o." but not "amznbusiness" or "cf fitness"
                pattern = r'\b' + re.escape(counterparty_key) + r'\b'
                if re.search(pattern, counterparty_normalized):
                    matched = True
            elif " d.o.o." in counterparty_key or " d.d." in counterparty_key or " s.p." in counterparty_key:
                # For keys containing legal suffixes, require word boundary before the key
                # e.g., "ss d.o.o." should match "ss d.o.o." but not "fitness d.o.o."
                # Check if the key appears as a complete phrase (word boundary before first word)
                pattern = r'\b' + re.escape(counterparty_key)
                if re.search(pattern, counterparty_normalized):
                    matched = True
            else:
                # For longer keys without legal suffixes, substring match is safer
                if counterparty_key in counterparty_normalized:
                    matched = True

            if matched:
                # Salary categories should only apply to expenses, not income
                # If this is income and the category is salary-related, skip it
                if transaction_type == "income" and category.startswith("salary"):
                    continue
                # Benefits categories should only apply to income, not expenses
                # If this is an expense and the category is benefits, skip it
                if transaction_type == "expense" and category == "benefits":
                    continue
                # Stripe: income transactions are sales:stripe (subscription payments), expenses are fees
                # Check if counterparty is Stripe (normalized)
                if counterparty_normalized and ("stripe" in counterparty_normalized):
                    if transaction_type == "income":
                        return "sales:stripe"  # Stripe income = subscription payments via Stripe
                    elif transaction_type == "expense" and category == "bank_fees":
                        return category  # Stripe expenses = fees (already mapped correctly)
                # If counterparty was mapped to bank_fees but this is income, skip it
                # (let description-based categorization handle it, which will default to sales:invoice)
                if transaction_type == "income" and category == "bank_fees":
                    continue
                # Special handling: If counterparty maps to taxes:advance but description contains "Prispevek",
                # it's actually a social security contribution, not an advance tax payment
                if description and category == "taxes:advance":
                    description_lower = description.lower()
                    # Check if this is actually a social security contribution
                    if ("prispevek" in description_lower or "prispevki" in description_lower):
                        return _get_social_security_subcategory(description_lower)
                    # Otherwise, it's a legitimate advance tax payment
                    return category
                # If counterparty maps to taxes, social_security, professional_services, marketing, or other without subcategory, determine subcategory from description
                if description and category == "taxes":
                    return _get_taxes_subcategory(description.lower())
                elif description and category == "social_security":
                    return _get_social_security_subcategory(description.lower())
                elif description and category == "professional_services":
                    return _get_professional_services_subcategory(description.lower(), counterparty_normalized)
                elif description and category == "marketing":
                    return _get_marketing_subcategory(description.lower(), counterparty_normalized)
                elif description and category == "other":
                    return _get_other_subcategory(description.lower(), counterparty_normalized)
                return category

    if not description:
        return "other"

    description_lower = description.lower()

    categories = INCOME_CATEGORIES if transaction_type == "income" else EXPENSE_CATEGORIES

    # Special handling for income: check non-sales categories first
    if transaction_type == "income":
        # Check non-sales categories first (loans, transfers, benefits, refunds)
        # Note: large_deals is NOT checked here - it's amount-based only
        non_sales_categories = ["loans", "transfers", "benefits", "refund"]

        for category in non_sales_categories:
            if category in categories:
                keywords = categories[category]
                sorted_keywords = sorted(keywords, key=len, reverse=True)
                for keyword in sorted_keywords:
                    if keyword in description_lower:
                        return category

        # Check for large deals (> €1,000) - these might be custom deals, not subscriptions
        # This is purely amount-based: any income > €1,000 is a large deal
        # Exclude certain counterparties that should always be regular sales
        if amount is not None and amount > 1000:
            # Check if this is from a counterparty that should always be regular sales
            if counterparty_normalized:
                sales_only_counterparties = [
                    "ss d.o.o.", "ss", "studentski servis",  # SS D.O.O. (Študentski Servis)
                    "optispin d.o.o.", "optispin"  # OPTISPIN D.O.O. - always sales:invoice
                ]
                if any(cp in counterparty_normalized for cp in sales_only_counterparties):
                    # These counterparties should always be regular sales, not large deals
                    return _get_sales_subcategory(description_lower, counterparty_normalized)
            return "compensations:income"

        # Default: most income is subscription sales
        # Determine subcategory (stripe vs invoice)
        return _get_sales_subcategory(description_lower, counterparty_normalized)

    # For expenses, check all categories
    # Special handling: Large refunds (>€1000) go to compensations:expenses
    if transaction_type == "expense" and amount is not None and abs(amount) > 1000:
        refund_keywords = ["vračilo", "vracilo", "preplačilo", "preplacilo", "refund", "compensation"]
        if any(keyword in description_lower for keyword in refund_keywords):
            return "compensations:expenses"

    for category, keywords in categories.items():
        if category == "other":
            continue

        # Sort keywords by length (longest first) for more specific matches
        sorted_keywords = sorted(keywords, key=len, reverse=True)

        for keyword in sorted_keywords:
            if keyword in description_lower:
                # For taxes, social_security, professional_services, marketing, and other, determine subcategory
                if category == "taxes":
                    return _get_taxes_subcategory(description_lower)
                elif category == "social_security":
                    return _get_social_security_subcategory(description_lower)
                elif category == "professional_services":
                    return _get_professional_services_subcategory(description_lower, counterparty_normalized)
                elif category == "marketing":
                    return _get_marketing_subcategory(description_lower, counterparty_normalized)
                elif category == "other":
                    return _get_other_subcategory(description_lower, counterparty_normalized)
                return category

    # If we reach here, no category matched - check if we can determine an "other" subcategory for expenses
    if transaction_type == "expense":
        return _get_other_subcategory(description_lower, counterparty_normalized)

    return "other"


def get_all_categories(transaction_type: Optional[str] = None) -> List[str]:
    """Get all available categories, optionally filtered by transaction type."""
    if transaction_type == "income":
        categories = list(INCOME_CATEGORIES.keys())
        # Add base category for subcategories
        if "compensations:income" in categories:
            categories.append("compensations")
        return categories
    elif transaction_type == "expense":
        categories = list(EXPENSE_CATEGORIES.keys())
        # Add base category for subcategories
        if "compensations:expenses" in categories:
            categories.append("compensations")
        return categories
    else:
        categories = list(set(EXPENSE_CATEGORIES.keys()) | set(INCOME_CATEGORIES.keys()))
        # Add base category for subcategories if any subcategory exists
        if "compensations:expenses" in categories or "compensations:income" in categories:
            categories.append("compensations")
        return categories

