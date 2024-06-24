#!/bin/sh

pip install -r requirements_for_developmers.txt

pre-commit install --config hooks/.pre-commit-config.yaml

echo "Modules are installed, pre-commit is configured"