#!/usr/bin/env bash
# Run the PackRight web MVP locally.
cd "$(dirname "$0")"
source .venv/bin/activate
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
