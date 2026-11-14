#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "Önce bash kur_mac.sh çalıştırın."
  exit 1
fi
exec .venv/bin/python -m streamlit run app.py
