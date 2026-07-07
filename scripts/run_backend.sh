#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../backend"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
