#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting Git hooks setup..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null
then
    echo "pre-commit not found. Installing via pip..."
    pip install pre-commit
fi

# Install the pre-commit hooks
echo "Installing pre-commit hooks for 'commit-msg' and 'pre-push'..."
pre-commit install --hook-type commit-msg --hook-type pre-push

echo "Setup complete! Git hooks are now active."
echo "Your commit messages will be checked by Commitizen, and your code will be formatted by Black before pushing."