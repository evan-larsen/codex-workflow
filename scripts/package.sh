#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_cmd="${CODEX_WORKFLOW_PYTHON:-python3}"
exec "$python_cmd" "$root/scripts/package.py" --root "$root" "$@"
