#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src:.
export ESO_STEP_DELAY="${ESO_STEP_DELAY:-0.12}"
python3 -m pip install -q -r requirements.txt
(cd web && npm install && npm run build)
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
