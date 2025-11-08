"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def tmp_dir():
    """Create a temporary directory for tests."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def sample_bank_xml(tmp_dir):
    """Create a sample bank XML file for testing."""
    xml_file = tmp_dir / "bank_statement.xml"
    xml_file.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
  <BkToCstmrStmt>
    <Stmt>
      <Acct><Id><IBAN>SI123456789</IBAN></Id></Acct>
      <Ntry>
        <Amt Ccy="EUR">100.00</Amt>
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
              </Strd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
    </Stmt>
  </BkToCstmrStmt>
</Document>''')
    return xml_file


@pytest.fixture
def sample_paypal_csv(tmp_dir):
    """Create a sample PayPal CSV file for testing."""
    csv_file = tmp_dir / "Paypal-2025-10.csv"
    csv_file.write_text('''Date,Time,Time Zone,Description,Currency,Gross,Fee,Net,Balance,Transaction ID,From Email Address,Name,Bank Name,Bank Account,Shipping and Handling Amount,Sales Tax,Invoice ID,Reference Txn ID
10/1/2025,12:00:00,America/Los_Angeles,Subscription Payment,EUR,-18.30,0.00,-18.30,100.00,TEST123,,Test Company,,,,INV-001,''')
    return csv_file

