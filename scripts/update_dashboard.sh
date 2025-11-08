#!/bin/bash
# Update dashboard script for automated dashboard generation

set -e

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project directory
cd "$PROJECT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Generate dashboard
echo "Generating dashboard..."
oa generate-dashboard --output-dir ./dashboard

echo "Dashboard updated successfully!"

# Optional: Add commands here to sync to hosting location
# Example:
# rsync -avz ./dashboard/ user@host:/path/to/web/dashboard/
# or
# cp -r ./dashboard/* /path/to/hosting/location/


