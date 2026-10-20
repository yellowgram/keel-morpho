#!/usr/bin/env bash
# Kept so existing cron entries keep working. Equivalent to: python3 -m keel observe
set -euo pipefail
cd "$(dirname "$0")/.."
PY=python3
[[ -x .venv/bin/python ]] && PY=.venv/bin/python
exec "$PY" -m keel observe "$@"
