"""Parser for bank XML transaction files (ISO 20022 camt.053 format)."""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from lxml import etree

from .base import TransactionParser


class BankParser(TransactionParser):
    """Parser for ISO 20022 camt.053 bank statement XML files."""

    # ISO 20022 camt.053 namespace
    NAMESPACE = {
        'camt': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.02'
    }

    def can_parse(self, file_path: Path) -> bool:
        """Check if this is a bank XML file (ISO 20022 camt.053 format)."""
        if file_path.suffix.lower() != ".xml":
            return False

        try:
            tree = etree.parse(str(file_path))
            root = tree.getroot()
            # Check for ISO 20022 camt.053 namespace
            return root.tag == '{urn:iso:std:iso:20022:tech:xsd:camt.053.001.02}Document'
        except:
            return False

    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse an ISO 20022 camt.053 bank statement XML file.

        Returns a list of transaction dictionaries with:
        - date: transaction date (YYYY-MM-DD)
        - amount: transaction amount (positive for income, negative for expense)
        - description: transaction description
        - type: 'income' or 'expense'
        - reference: transaction reference/invoice number
        - counterparty: counterparty name
        - account: account IBAN
        """
        transactions = []

        try:
            tree = etree.parse(str(file_path))
            root = tree.getroot()

            # Find all statement entries
            entries = root.findall('.//camt:Ntry', self.NAMESPACE)

            for entry in entries:
                # Check for reversal indicator - skip reversal transactions
                # Reversals are corrections/cancellations, not actual transactions
                rvsl_ind = entry.find('camt:RvslInd', self.NAMESPACE)
                if rvsl_ind is not None and rvsl_ind.text and rvsl_ind.text.lower() == 'true':
                    continue  # Skip reversal entries

                # Get amount and credit/debit indicator
                amt_elem = entry.find('camt:Amt', self.NAMESPACE)
                if amt_elem is None:
                    continue

                amount = float(amt_elem.text)
                cdt_dbt_ind = entry.find('camt:CdtDbtInd', self.NAMESPACE)

                # CRDT = Credit (income), DBIT = Debit (expense)
                # For expenses, amount is already positive in DBIT entries
                # We'll make expenses negative for consistency
                if cdt_dbt_ind is not None and cdt_dbt_ind.text == 'DBIT':
                    amount = -abs(amount)
                    transaction_type = 'expense'
                else:
                    amount = abs(amount)
                    transaction_type = 'income'

                # Get booking date
                bookg_dt_elem = entry.find('camt:BookgDt/camt:Dt', self.NAMESPACE)
                if bookg_dt_elem is None:
                    bookg_dt_elem = entry.find('camt:BookgDt/camt:DtTm', self.NAMESPACE)

                date_str = bookg_dt_elem.text if bookg_dt_elem is not None else None
                if date_str:
                    # Parse date (format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
                    try:
                        date_obj = datetime.fromisoformat(date_str.split('T')[0])
                        date = date_obj.strftime('%Y-%m-%d')
                    except:
                        date = date_str.split('T')[0]
                else:
                    date = None

                # Get transaction details
                tx_dtls = entry.find('camt:NtryDtls/camt:TxDtls', self.NAMESPACE)

                description = ""
                reference = ""
                counterparty = ""

                if tx_dtls is not None:
                    # Get description from remittance info
                    addtl_rmt_inf = tx_dtls.find('.//camt:AddtlRmtInf', self.NAMESPACE)
                    if addtl_rmt_inf is not None and addtl_rmt_inf.text:
                        description = addtl_rmt_inf.text.strip()

                    # Get reference (invoice number)
                    ref_elem = tx_dtls.find('.//camt:CdtrRefInf/camt:Ref', self.NAMESPACE)
                    if ref_elem is not None and ref_elem.text:
                        reference = ref_elem.text.strip()

                    # Get counterparty name and account
                    counterparty_account = ""
                    if transaction_type == 'income':
                        # For income, counterparty is the debtor (who paid us)
                        dbtr = tx_dtls.find('.//camt:Dbtr/camt:Nm', self.NAMESPACE)
                        if dbtr is not None and dbtr.text:
                            counterparty = dbtr.text.strip()
                        # Get debtor account (counterparty's account)
                        dbtr_acct = tx_dtls.find('.//camt:DbtrAcct/camt:Id/camt:IBAN', self.NAMESPACE)
                        if dbtr_acct is not None and dbtr_acct.text:
                            counterparty_account = dbtr_acct.text.strip()
                    else:
                        # For expenses, counterparty is the creditor (who we paid)
                        cdtr = tx_dtls.find('.//camt:Cdtr/camt:Nm', self.NAMESPACE)
                        if cdtr is not None and cdtr.text:
                            counterparty = cdtr.text.strip()
                        # Get creditor account (counterparty's account)
                        cdtr_acct = tx_dtls.find('.//camt:CdtrAcct/camt:Id/camt:IBAN', self.NAMESPACE)
                        if cdtr_acct is not None and cdtr_acct.text:
                            counterparty_account = cdtr_acct.text.strip()

                    # If no description, use counterparty name
                    if not description and counterparty:
                        description = counterparty

                # Get our account IBAN (for reference, but not used for counterparty grouping)
                account_elem = root.find('.//camt:Acct/camt:Id/camt:IBAN', self.NAMESPACE)
                our_account = account_elem.text if account_elem is not None else ""
                # Use counterparty account for grouping purposes
                account = counterparty_account

                # Get transaction ID
                tx_id_elem = entry.find('.//camt:TxId', self.NAMESPACE)
                tx_id = tx_id_elem.text if tx_id_elem is not None else ""

                transactions.append({
                    'date': date,
                    'amount': amount,
                    'description': description or 'Unknown transaction',
                    'type': transaction_type,
                    'reference': reference,
                    'counterparty': counterparty,
                    'account': account,
                    'transaction_id': tx_id,
                    'source': 'bank',
                })

        except Exception as e:
            raise ValueError(f"Error parsing bank file {file_path}: {e}")

        return transactions

