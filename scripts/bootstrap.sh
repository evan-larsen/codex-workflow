#!/usr/bin/env bash
set -euo pipefail
archive=''
project=''
codex_home=''
checksums=''
while [[ $# -gt 0 ]]; do
  case "$1" in
    --archive) archive="$2"; shift 2;;
    --project) project="$2"; shift 2;;
    --codex-home) codex_home="$2"; shift 2;;
    --checksums) checksums="$2"; shift 2;;
    *) echo "unknown option: $1" >&2; exit 2;;
  esac
done
[[ -n "$archive" && -n "$project" ]] || { echo 'usage: bootstrap.sh --archive ZIP --project DIR [--codex-home DIR] [--checksums FILE]' >&2; exit 2; }
archive="$(cd "$(dirname "$archive")" && pwd)/$(basename "$archive")"
checksums="${checksums:-$(dirname "$archive")/SHA256SUMS}"
expected="$(awk -v file="$(basename "$archive")" '$2==file || $2=="*"file {print tolower($1); exit}' "$checksums")"
actual="$(sha256sum "$archive" | awk '{print tolower($1)}')"
[[ -n "$expected" && "$expected" == "$actual" ]] || { echo 'release ZIP checksum mismatch or missing entry' >&2; exit 1; }
temp="$(mktemp -d)"
cleanup() { rm -rf "$temp"; }
trap cleanup EXIT
unzip -q "$archive" -d "$temp"
[[ -d "$temp/codex_workflow" ]] || { echo 'archive lacks codex_workflow root' >&2; exit 1; }
[[ "$(find "$temp" -mindepth 1 -maxdepth 1 | wc -l)" -eq 1 ]] || { echo 'archive must contain exactly one top-level directory' >&2; exit 1; }
python_cmd="${CODEX_WORKFLOW_PYTHON:-python3}"
workflow="$temp/codex_workflow/workflow.py"
"$python_cmd" "$workflow" check-compatibility --json
"$python_cmd" "$workflow" validate --package-root "$temp/codex_workflow" --json
args=("$workflow" bootstrap --package-root "$temp/codex_workflow" --project "$project")
[[ -n "$codex_home" ]] && args+=(--codex-home "$codex_home")
exec "$python_cmd" "${args[@]}"
