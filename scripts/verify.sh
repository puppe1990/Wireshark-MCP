#!/usr/bin/env sh
# Gate único local: formatação, lint e testes.
set -e

.venv/bin/ruff format --check .
.venv/bin/ruff check .
.venv/bin/python -m pytest -q
