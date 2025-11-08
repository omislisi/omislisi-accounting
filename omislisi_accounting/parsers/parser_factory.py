"""Factory for creating appropriate parsers."""

import logging
from pathlib import Path
from typing import Optional, List

from .base import TransactionParser
from .bank_parser import BankParser
from .paypal_parser import PayPalParser

logger = logging.getLogger(__name__)


def get_parser(file_path: Path) -> Optional[TransactionParser]:
    """
    Get the appropriate parser for a given file.

    Args:
        file_path: Path to the transaction file

    Returns:
        Parser instance or None if no parser can handle the file
    """
    parsers: List[TransactionParser] = [
        PayPalParser(),
        BankParser(),
    ]

    for parser in parsers:
        if parser.can_parse(file_path):
            return parser

    return None


def _is_macos_metadata_file(file_path: Path) -> bool:
    """
    Check if a file is a macOS metadata file that should be ignored.

    Args:
        file_path: Path to check

    Returns:
        True if file is macOS metadata, False otherwise
    """
    # Check for __MACOSX directories
    if "__MACOSX" in file_path.parts:
        return True

    # Check for ._ prefix (macOS resource forks)
    if file_path.name.startswith("._"):
        return True

    return False


def parse_all_files(file_paths, silent: bool = False) -> List[dict]:
    """
    Parse multiple files and return all transactions.

    Args:
        file_paths: List of file paths to parse, or list of tuples (file_path, source_file_path)
        silent: If True, suppress warning messages

    Returns:
        List of all transactions from all files, each with 'source_file' field
    """
    all_transactions = []
    skipped_files = []

    # Handle both old format (list of Path) and new format (list of tuples)
    if file_paths and isinstance(file_paths[0], tuple):
        # New format: list of (file_path, source_file_path) tuples
        file_source_pairs = file_paths
    else:
        # Old format: list of Path objects (for backwards compatibility)
        file_source_pairs = [(fp, fp) for fp in file_paths]

    for file_path, source_file_path in file_source_pairs:
        # Skip macOS metadata files silently
        if _is_macos_metadata_file(file_path):
            continue

        # Skip if it's a directory (some zip entries are directories)
        if file_path.is_dir():
            continue

        # Skip if file doesn't exist
        if not file_path.exists() or not file_path.is_file():
            if not silent:
                logger.debug(f"Skipping non-file: {file_path}")
            continue

        parser = get_parser(file_path)
        if parser:
            try:
                transactions = parser.parse(file_path)
                # Add source file information to each transaction
                source_file_name = source_file_path.name if isinstance(source_file_path, Path) else str(source_file_path)
                for transaction in transactions:
                    transaction['source_file'] = source_file_name
                all_transactions.extend(transactions)
            except Exception as e:
                if not silent:
                    logger.warning(f"Failed to parse {file_path}: {e}")
                    skipped_files.append(str(file_path))
        else:
            if not silent:
                logger.warning(f"No parser found for {file_path}")
                skipped_files.append(str(file_path))

    if skipped_files and not silent:
        logger.warning(f"Skipped {len(skipped_files)} file(s) that could not be parsed")

    return all_transactions

