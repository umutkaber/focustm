#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python3.12 --version
if [ ! -x .venv/bin/python ]; then python3.12 -m venv .venv; fi
.venv/bin/python -m pip install -r requirements.txt
echo "Kurulum tamamlandı. Başlatmak için: bash calistir_mac.sh"
