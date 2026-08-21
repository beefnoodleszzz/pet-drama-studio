#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"
load_env

python_bin="${PET_STUDIO_ROOT:-/root/autodl-tmp/pet-drama-studio}/venv/bin/python"
if [[ ! -x "$python_bin" ]]; then
  python_bin=python3
fi
exec "$python_bin" "$SCRIPT_DIR/download-models.py" --manifest "$PROJECT_ROOT/config/models.yaml" "$@"
