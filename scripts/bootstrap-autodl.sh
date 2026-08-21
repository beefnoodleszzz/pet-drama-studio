#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"
load_env

execute=false
if [[ "${1:-}" == "--execute" ]]; then
  execute=true
elif [[ $# -gt 0 ]]; then
  printf 'Usage: %s [--execute]\n' "$0" >&2
  exit 2
fi

studio_root="${PET_STUDIO_ROOT:-/root/autodl-tmp/pet-drama-studio}"
reliable_root="${PET_STUDIO_RELIABLE_ROOT:-/root/autodl-fs/pet-drama-studio}"
comfyui_dir="$studio_root/ComfyUI"
comfyui_tag="v0.33.3"

require_absolute_safe_root "$studio_root" PET_STUDIO_ROOT
require_absolute_safe_root "$reliable_root" PET_STUDIO_RELIABLE_ROOT

printf 'Mode: %s\n' "$([[ "$execute" == true ]] && printf execute || printf dry-run)"
printf 'Local root: %s\nReliable root: %s\nComfyUI: %s\n' "$studio_root" "$reliable_root" "$comfyui_dir"

for dir in \
  "$studio_root/cache" "$studio_root/temp-frames" "$studio_root/jobs" \
  "$reliable_root/manifests" "$reliable_root/workflows" "$reliable_root/characters" \
  "$reliable_root/jobs" "$reliable_root/logs" "$reliable_root/approved-outputs"; do
  run_or_print "$execute" mkdir -p "$dir"
done

if [[ ! -d "$comfyui_dir/.git" ]]; then
  run_or_print "$execute" git clone --branch "$comfyui_tag" --depth 1 \
    https://github.com/Comfy-Org/ComfyUI.git "$comfyui_dir"
else
  printf 'ComfyUI checkout already exists; bootstrap will not update it automatically.\n'
fi

run_or_print "$execute" python3 -m venv --system-site-packages "$studio_root/venv"
run_or_print "$execute" "$studio_root/venv/bin/python" -m pip install --upgrade pip
run_or_print "$execute" "$studio_root/venv/bin/python" -m pip install "torchaudio==2.8.0"
run_or_print "$execute" "$studio_root/venv/bin/python" -m pip install -r "$PROJECT_ROOT/requirements-control.txt"
run_or_print "$execute" "$studio_root/venv/bin/python" -m pip install -r "$comfyui_dir/requirements.txt"

printf 'Bootstrap plan complete. No models are downloaded by this script.\n'
