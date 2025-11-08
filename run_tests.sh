#!/bin/bash
# Run tests for omislisi-accounting

set -e

echo "Running tests for omislisi-accounting..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run pytest
pytest -v tests/

echo ""
echo "Tests completed!"

