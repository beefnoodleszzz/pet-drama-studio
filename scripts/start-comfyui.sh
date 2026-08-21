#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"
load_env

execute=false
if [[ "${1:-}" == "--execute" ]]; then execute=true; shift; fi
if [[ $# -gt 0 ]]; then printf 'Usage: %s [--execute]\n' "$0" >&2; exit 2; fi

studio_root="${PET_STUDIO_ROOT:-/root/autodl-tmp/pet-drama-studio}"
host="${COMFYUI_HOST:-127.0.0.1}"
port="${COMFYUI_PORT:-8188}"
require_absolute_safe_root "$studio_root" PET_STUDIO_ROOT

cmd=("$studio_root/venv/bin/python" "$studio_root/ComfyUI/main.py" --listen "$host" --port "$port")
printf 'ComfyUI command (pinned checkout, no auto-update):\n'
run_or_print "$execute" "${cmd[@]}"
