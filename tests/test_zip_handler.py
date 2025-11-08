"""Tests for zip file handling."""

import zipfile
import tempfile
from pathlib import Path

from omislisi_accounting.parsers.zip_handler import (
    extract_zip,
    find_xml_files,
    find_csv_files,
    get_all_transaction_files,
)


def test_extract_zip(tmp_path):
    """Test zip file extraction."""
    # Create a zip file
    zip_path = tmp_path / "test.zip"
    extract_dir = tmp_path / "extracted"

    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("file1.xml", "<xml>test</xml>")
        zf.writestr("subdir/file2.xml", "<xml>test2</xml>")

    extracted = extract_zip(zip_path, extract_dir)

    assert extracted == extract_dir
    assert (extract_dir / "file1.xml").exists()
    assert (extract_dir / "subdir" / "file2.xml").exists()


def test_find_xml_files(tmp_path):
    """Test finding XML files."""
    (tmp_path / "file1.xml").write_text("test")
    (tmp_path / "file2.txt").write_text("test")
    (tmp_path / "subdir").mkdir(parents=True)
    (tmp_path / "subdir" / "file3.xml").write_text("test")

    xml_files = list(find_xml_files(tmp_path))
    assert len(xml_files) == 2
    assert all(f.suffix == '.xml' for f in xml_files)


def test_find_csv_files(tmp_path):
    """Test finding CSV files."""
    (tmp_path / "file1.csv").write_text("test")
    (tmp_path / "file2.txt").write_text("test")
    (tmp_path / "subdir").mkdir(parents=True)
    (tmp_path / "subdir" / "file3.csv").write_text("test")

    csv_files = list(find_csv_files(tmp_path))
    assert len(csv_files) == 2
    assert all(f.suffix == '.csv' for f in csv_files)


def test_filter_macos_metadata_files(tmp_path):
    """Test that macOS metadata files are filtered out."""
    # Create valid XML files
    (tmp_path / "valid1.xml").write_text("<xml>test</xml>")
    (tmp_path / "valid2.xml").write_text("<xml>test</xml>")

    # Create macOS metadata files
    (tmp_path / "__MACOSX").mkdir()
    (tmp_path / "__MACOSX" / "metadata.xml").write_text("<xml>metadata</xml>")
    (tmp_path / "._hidden.xml").write_text("<xml>hidden</xml>")

    xml_files = list(find_xml_files(tmp_path))
    # Should only find the 2 valid files, not the metadata files
    assert len(xml_files) == 2
    assert all("__MACOSX" not in str(f) for f in xml_files)
    assert all(not f.name.startswith("._") for f in xml_files)

