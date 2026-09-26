#!/usr/bin/env bash
# Run Keel observe exactly once. Never sign. Never touch targets/kits (killed track).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# Prefer python3 on PATH; optional local venv if present
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PY="$ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
else
  echo "python3 not found" >&2
  exit 1
fi
"$PY" scripts/hard_daily_observe.py
# Optional founder-only mirror (private tree). Public toolkit does not require this.
if [[ -d private/income ]] && [[ -f eth-credit-conservative/pack.md ]]; then
  cp eth-credit-conservative/pack.md private/income/pack_attach.md
fi
echo "keel_daily_observe_once done (targets/kits NOT run — killed track)"
