#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

load_env() {
  if [[ -f "$PROJECT_ROOT/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$PROJECT_ROOT/.env"
    set +a
  fi
}

run_or_print() {
  local execute="$1"
  shift
  if [[ "$execute" == "true" ]]; then
    "$@"
  else
    printf '[dry-run]'
    printf ' %q' "$@"
    printf '\n'
  fi
}

require_absolute_safe_root() {
  local value="$1"
  local label="$2"
  if [[ -z "$value" || "$value" != /* || "$value" == "/" || "$value" == "/root" ]]; then
    printf 'Unsafe %s: %q\n' "$label" "$value" >&2
    exit 2
  fi
}
