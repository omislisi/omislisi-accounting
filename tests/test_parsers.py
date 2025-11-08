"""Tests for parsers."""

import tempfile
from pathlib import Path
import pytest
import csv

from omislisi_accounting.parsers.bank_parser import BankParser
from omislisi_accounting.parsers.paypal_parser import PayPalParser
from omislisi_accounting.parsers.parser_factory import get_parser, parse_all_files


def test_bank_parser_can_parse():
    """Test BankParser can identify ISO 20022 XML files."""
    parser = BankParser()

    # Create a temporary XML file with ISO 20022 namespace
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
  <BkToCstmrStmt>
    <Stmt>
      <Ntry>
        <Amt Ccy="EUR">100.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <BookgDt><Dt>2025-10-01</Dt></BookgDt>
      </Ntry>
    </Stmt>
  </BkToCstmrStmt>
</Document>''')
        xml_path = Path(f.name)

    try:
        assert parser.can_parse(xml_path) is True
        assert parser.can_parse(Path("test.csv")) is False
    finally:
        xml_path.unlink()


def test_bank_parser_parse():
    """Test BankParser parses transactions correctly."""
    parser = BankParser()

    # Create a minimal valid ISO 20022 XML
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
  <BkToCstmrStmt>
    <Stmt>
      <Acct><Id><IBAN>SI123456789</IBAN></Id></Acct>
      <Ntry>
        <Amt Ccy="EUR">100.50</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <BookgDt><Dt>2025-10-01</Dt></BookgDt>
        <NtryDtls>
          <TxDtls>
            <RltdPties>
              <Dbtr><Nm>Test Company</Nm></Dbtr>
            </RltdPties>
            <RmtInf>
              <Strd>
                <AddtlRmtInf>Test payment</AddtlRmtInf>
                <CdtrRefInf><Ref>INV-001</Ref></CdtrRefInf>
              </Strd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
      <Ntry>
        <Amt Ccy="EUR">50.25</Amt>
        <CdtDbtInd>DBIT</CdtDbtInd>
        <BookgDt><Dt>2025-10-02</Dt></BookgDt>
        <NtryDtls>
          <TxDtls>
            <RltdPties>
              <Cdtr><Nm>Vendor Inc</Nm></Cdtr>
            </RltdPties>
            <RmtInf>
              <Strd>
                <AddtlRmtInf>Purchase</AddtlRmtInf>
              </Strd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
    </Stmt>
  </BkToCstmrStmt>
</Document>''')
        xml_path = Path(f.name)

    try:
        transactions = parser.parse(xml_path)

        assert len(transactions) == 2
        assert transactions[0]['type'] == 'income'
        assert transactions[0]['amount'] == 100.50
        assert transactions[0]['date'] == '2025-10-01'
        assert transactions[0]['description'] == 'Test payment'
        assert transactions[0]['counterparty'] == 'Test Company'
        assert transactions[0]['reference'] == 'INV-001'

        assert transactions[1]['type'] == 'expense'
        assert transactions[1]['amount'] == -50.25
        assert transactions[1]['date'] == '2025-10-02'
    finally:
        xml_path.unlink()


def test_paypal_parser_can_parse():
    """Test PayPalParser can identify PayPal CSV files."""
    parser = PayPalParser()

    assert parser.can_parse(Path("Paypal-2025-10.csv")) is True
    assert parser.can_parse(Path("paypal-2025-10.csv")) is True
    assert parser.can_parse(Path("test.csv")) is False
    assert parser.can_parse(Path("test.xml")) is False


def test_paypal_parser_parse(tmp_path):
    """Test PayPalParser parses CSV correctly."""
    parser = PayPalParser()

    csv_file = tmp_path / "Paypal-2025-10.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Date', 'Time', 'Time Zone', 'Description', 'Currency', 'Gross',
            'Fee', 'Net', 'Balance', 'Transaction ID', 'From Email Address',
            'Name', 'Bank Name', 'Bank Account', 'Shipping and Handling Amount',
            'Sales Tax', 'Invoice ID', 'Reference Txn ID'
        ])
        writer.writeheader()
        writer.writerow({
            'Date': '10/1/2025',
            'Time': '12:00:00',
            'Time Zone': 'America/Los_Angeles',
            'Description': 'Subscription Payment',
            'Currency': 'EUR',
            'Gross': '-18.30',
            'Fee': '0.00',
            'Net': '-18.30',
            'Balance': '100.00',
            'Transaction ID': 'TEST123',
            'From Email Address': '',
            'Name': 'Test Company',
            'Bank Name': '',
            'Bank Account': '',
            'Shipping and Handling Amount': '0.00',
            'Sales Tax': '0.00',
            'Invoice ID': 'INV-001',
            'Reference Txn ID': ''
        })
        writer.writerow({
            'Date': '10/2/2025',
            'Time': '12:00:00',
            'Time Zone': 'America/Los_Angeles',
            'Description': 'General Currency Conversion',  # Should be filtered
            'Currency': 'EUR',
            'Gross': '18.30',
            'Fee': '0.00',
            'Net': '18.30',
            'Balance': '118.30',
            'Transaction ID': 'TEST124',
            'From Email Address': '',
            'Name': '',
            'Bank Name': '',
            'Bank Account': '',
            'Shipping and Handling Amount': '0.00',
            'Sales Tax': '0.00',
            'Invoice ID': '',
            'Reference Txn ID': ''
        })

    transactions = parser.parse(csv_file)

    # Should only have 1 transaction (currency conversion filtered out)
    assert len(transactions) == 1
    assert transactions[0]['type'] == 'expense'
    assert transactions[0]['amount'] == -18.30
    assert transactions[0]['date'] == '2025-10-01'
    assert transactions[0]['description'] == 'Subscription Payment'
    assert transactions[0]['counterparty'] == 'Test Company'
    assert transactions[0]['reference'] == 'INV-001'


def test_parser_factory():
    """Test parser factory returns correct parser."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write('''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
  <BkToCstmrStmt><Stmt></Stmt></BkToCstmrStmt>
</Document>''')
        xml_path = Path(f.name)

    csv_path = Path("Paypal-2025-10.csv")

    try:
        bank_parser = get_parser(xml_path)
        assert bank_parser is not None
        assert isinstance(bank_parser, BankParser)

        paypal_parser = get_parser(csv_path)
        assert paypal_parser is not None
        assert isinstance(paypal_parser, PayPalParser)

        unknown_parser = get_parser(Path("unknown.txt"))
        assert unknown_parser is None
    finally:
        xml_path.unlink()


def test_parse_all_files_filters_macos_metadata(tmp_path):
    """Test that parse_all_files silently filters out macOS metadata files."""
    from omislisi_accounting.parsers.parser_factory import parse_all_files, _is_macos_metadata_file

    # Create a valid XML file
    valid_xml = tmp_path / "valid.xml"
    valid_xml.write_text('''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
  <BkToCstmrStmt><Stmt></Stmt></BkToCstmrStmt>
</Document>''')

    # Create macOS metadata file
    macos_metadata = tmp_path / "._metadata.xml"
    macos_metadata.write_text("<xml>metadata</xml>")

    # parse_all_files should silently skip the metadata file
    files = [valid_xml, macos_metadata]
    transactions = parse_all_files(files, silent=True)

    # Should not raise warnings and should process the valid file
    assert _is_macos_metadata_file(macos_metadata) is True
    assert _is_macos_metadata_file(valid_xml) is False

