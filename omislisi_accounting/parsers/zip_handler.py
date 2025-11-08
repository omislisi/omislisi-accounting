"""Handle zip files containing XML transaction files."""

import zipfile
from pathlib import Path
from typing import List, Iterator
import tempfile
import shutil
import atexit


# Track temporary directories for cleanup
_temp_dirs = []


def _cleanup_temp_dirs():
    """Clean up temporary directories on exit."""
    for temp_dir in _temp_dirs:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass


atexit.register(_cleanup_temp_dirs)


def extract_zip(zip_path: Path, extract_to: Path = None, cleanup: bool = True) -> Path:
    """
    Extract a zip file to a temporary directory or specified path.

    Args:
        zip_path: Path to the zip file
        extract_to: Optional destination directory. If None, uses temp directory.
        cleanup: If True and using temp directory, register for cleanup on exit

    Returns:
        Path to the extracted directory
    """
    if extract_to is None:
        extract_to = Path(tempfile.mkdtemp(prefix="omislisi_"))
        if cleanup:
            _temp_dirs.append(extract_to)

    extract_to.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    return extract_to


def _is_valid_transaction_file(file_path: Path) -> bool:
    """
    Check if a file is a valid transaction file (not a macOS metadata file).

    Filters out:
    - Files in __MACOSX directories
    - Files starting with ._ (macOS resource forks)

    Args:
        file_path: Path to check

    Returns:
        True if file should be processed, False otherwise
    """
    # Skip __MACOSX directories (macOS metadata)
    if "__MACOSX" in file_path.parts:
        return False

    # Skip files starting with ._ (macOS resource forks)
    if file_path.name.startswith("._"):
        return False

    return True


def find_xml_files(directory: Path) -> Iterator[Path]:
    """
    Find all XML files in a directory recursively, excluding macOS metadata files.

    Args:
        directory: Directory to search

    Yields:
        Path objects for valid XML files
    """
    for xml_file in directory.rglob("*.xml"):
        # Skip if it's actually a directory (some zip entries are directories)
        if xml_file.is_dir():
            continue

        # Skip if file doesn't exist (might be a directory entry from zip)
        if not xml_file.exists() or not xml_file.is_file():
            continue

        if _is_valid_transaction_file(xml_file):
            yield xml_file


def find_csv_files(directory: Path) -> Iterator[Path]:
    """
    Find all CSV files in a directory recursively, excluding macOS metadata files.

    Args:
        directory: Directory to search

    Yields:
        Path objects for valid CSV files
    """
    for csv_file in directory.rglob("*.csv"):
        if _is_valid_transaction_file(csv_file):
            yield csv_file


def process_zip_files(reports_path: Path, pattern: str = "*.zip") -> Iterator[tuple[Path, Path]]:
    """
    Process all zip files in the reports directory (recursively).

    Args:
        reports_path: Base directory to search for zip files
        pattern: Glob pattern for zip files (default: "*.zip")

    Yields:
        Tuple of (zip_path, extracted_directory_path)
    """
    for zip_file in reports_path.rglob(pattern):
        extracted_dir = extract_zip(zip_file)
        yield zip_file, extracted_dir


def get_all_transaction_files(reports_path: Path) -> List[tuple[Path, Path]]:
    """
    Get all transaction files (XML from zips, CSV files) from the reports directory.

    Args:
        reports_path: Base directory containing reports

    Returns:
        List of tuples: (transaction_file_path, source_file_path)
        - For bank XML files: source_file_path is the zip file
        - For PayPal CSV files: source_file_path is the CSV file itself
    """
    files = []

    # Process zip files and extract XML files
    for zip_path, extracted_dir in process_zip_files(reports_path):
        xml_files = list(find_xml_files(extracted_dir))
        # Each XML file came from this zip file
        for xml_file in xml_files:
            files.append((xml_file, zip_path))

    # Find CSV files (PayPal) directly
    csv_files = list(find_csv_files(reports_path))
    # Each CSV file is its own source
    for csv_file in csv_files:
        files.append((csv_file, csv_file))

    return files

