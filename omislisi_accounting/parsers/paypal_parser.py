"""Parser for PayPal CSV transaction files."""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import csv

from .base import TransactionParser


class PayPalParser(TransactionParser):
    """Parser for PayPal CSV transaction files."""

    # Transaction types to ignore (internal PayPal operations)
    IGNORE_TYPES = {
        'General Currency Conversion',
        'Bank Deposit to PP Account',
        'User Initiated Withdrawal',
    }

    def can_parse(self, file_path: Path) -> bool:
        """Check if this is a PayPal CSV file."""
        if file_path.suffix.lower() != ".csv":
            return False

        # Check if filename contains "paypal" (case insensitive)
        return "paypal" in file_path.name.lower()

    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse a PayPal CSV file.

        Returns a list of transaction dictionaries with:
        - date: transaction date (YYYY-MM-DD)
        - amount: transaction amount (positive for income, negative for expense)
        - description: transaction description
        - type: 'income' or 'expense'
        - reference: invoice ID or transaction reference
        - counterparty: counterparty name/email
        - currency: transaction currency
        - fee: PayPal fee
        """
        transactions = []

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
                reader = csv.DictReader(f)

                # Normalize field names (strip BOM and quotes that may be present)
                original_fieldnames = reader.fieldnames
                normalized_fieldnames = {}
                for field in original_fieldnames:
                    # Remove BOM, quotes, and whitespace
                    clean_field = field.strip().strip('"').strip('\ufeff').strip()
                    normalized_fieldnames[clean_field] = field

                for row in reader:
                    # Create normalized row with clean field names
                    normalized_row = {}
                    for clean_field, original_field in normalized_fieldnames.items():
                        normalized_row[clean_field] = row.get(original_field, '')
                    row = normalized_row
                    # Skip internal PayPal operations
                    description = row.get('Description', '').strip()
                    if description in self.IGNORE_TYPES:
                        continue

                    # Parse date (format: M/D/YYYY)
                    date_str = row.get('Date', '').strip()
                    if date_str:
                        try:
                            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
                            date = date_obj.strftime('%Y-%m-%d')
                        except:
                            date = date_str
                    else:
                        continue

                    # Get net amount (this is the actual amount after fees)
                    net_str = row.get('Net', '').strip().replace(',', '')
                    try:
                        net_amount = float(net_str)
                    except (ValueError, AttributeError):
                        continue

                    # Determine transaction type based on amount sign
                    # Negative amounts are expenses, positive are income
                    if net_amount < 0:
                        transaction_type = 'expense'
                        amount = net_amount  # Already negative
                    else:
                        transaction_type = 'income'
                        amount = net_amount

                    # Get additional fields
                    currency = row.get('Currency', 'EUR').strip()
                    fee_str = row.get('Fee', '').strip().replace(',', '')
                    try:
                        fee = float(fee_str) if fee_str else 0.0
                    except:
                        fee = 0.0

                    # Get counterparty information
                    counterparty = row.get('Name', '').strip()
                    if not counterparty:
                        counterparty = row.get('From Email Address', '').strip()

                    # Get reference (Invoice ID or Transaction ID)
                    reference = row.get('Invoice ID', '').strip()
                    if not reference:
                        reference = row.get('Transaction ID', '').strip()

                    # Build description if needed
                    if not description:
                        description = counterparty or 'PayPal transaction'

                    transactions.append({
                        'date': date,
                        'amount': amount,
                        'description': description,
                        'type': transaction_type,
                        'reference': reference,
                        'counterparty': counterparty,
                        'currency': currency,
                        'fee': fee,
                        'transaction_id': row.get('Transaction ID', '').strip(),
                        'source': 'paypal',
                    })

        except Exception as e:
            raise ValueError(f"Error parsing PayPal file {file_path}: {e}")

        return transactions
