#!/bin/bash
# Run tests for Team Alchemy

set -e

echo "Running Team Alchemy tests..."
echo "=============================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run pytest with coverage
echo ""
echo "Running unit tests..."
pytest tests/unit/ -v --cov=src/team_alchemy --cov-report=term-missing

echo ""
echo "Running integration tests..."
pytest tests/integration/ -v

echo ""
echo "All tests completed successfully!"
