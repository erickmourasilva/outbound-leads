#!/usr/bin/env bash
# Idempotent setup (macOS/Linux): installs what is missing and reports what is left to do by hand.
# Pass --check to only verify. Windows: use setup.ps1.
set -euo pipefail
cd "$(dirname "$0")"
PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo '{"ok": false, "error": "Python não encontrado. Instale Python 3.10+ (ex.: brew install python ou sudo apt install python3)."}' >&2
  exit 1
fi
exec "$PY" -m outbound setup "$@"
