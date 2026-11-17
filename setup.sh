#!/usr/bin/env bash
# Idempotent setup: checks the environment and creates the local database.
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 não encontrado. Instale Python 3.11+ (ex.: brew install python)." >&2
  exit 1
fi
if command -v pnpm >/dev/null 2>&1 && [ -f package.json ]; then
  pnpm install --silent || echo "pnpm install falhou (opcional); o painel ainda roda com: python3 -m outbound serve"
fi
python3 -m outbound doctor
