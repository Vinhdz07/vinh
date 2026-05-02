#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .

echo
echo "Cai dat xong."
echo "Hay copy .env.example thanh .env va dien thong tin bot Telegram."
