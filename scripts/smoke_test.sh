#!/usr/bin/env bash
set -euo pipefail

python3.12 -m venv .venv-smoke
source .venv-smoke/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
dropraw doctor
dropraw --version
dropraw --help
pytest
