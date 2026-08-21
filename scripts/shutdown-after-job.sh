#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "${1:-}" != "--execute" || "${2:-}" != "--confirm" || "${3:-}" != "SHUTDOWN" ]]; then
  printf 'Dry-run only. To shut down after verified sync, run:\n  %s --execute --confirm SHUTDOWN\n' "$0"
  exit 0
fi

printf 'Shutdown explicitly confirmed. Calling /usr/bin/shutdown now.\n'
exec /usr/bin/shutdown
