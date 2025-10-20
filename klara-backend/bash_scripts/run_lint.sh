#!/bin/bash

# Script to run code formatting and type checking

echo "Running ruff format..."
ruff format .

echo ""
echo "Running mypy type checking..."
mypy app/

echo ""
echo "✅ Done!"
