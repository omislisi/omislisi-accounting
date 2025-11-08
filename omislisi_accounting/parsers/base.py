"""Base parser interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any


class TransactionParser(ABC):
    """Base class for transaction parsers."""

    @abstractmethod
    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse a transaction file and return a list of transactions.

        Each transaction should be a dictionary with at least:
        - date: transaction date
        - amount: transaction amount (positive for income, negative for expense)
        - description: transaction description
        - type: 'income' or 'expense'
        """
        pass

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file."""
        pass

