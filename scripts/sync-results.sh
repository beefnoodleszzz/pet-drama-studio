#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"
load_env

execute=false
if [[ "${1:-}" == "--execute" ]]; then execute=true; shift; fi
if [[ $# -ne 1 ]]; then printf 'Usage: %s [--execute] JOB_ID\n' "$0" >&2; exit 2; fi
job_id="$1"
if [[ ! "$job_id" =~ ^[A-Za-z0-9._-]+$ ]]; then printf 'Invalid JOB_ID\n' >&2; exit 2; fi

local_root="${PET_STUDIO_ROOT:-/root/autodl-tmp/pet-drama-studio}"
reliable_root="${PET_STUDIO_RELIABLE_ROOT:-/root/autodl-fs/pet-drama-studio}"
require_absolute_safe_root "$local_root" PET_STUDIO_ROOT
require_absolute_safe_root "$reliable_root" PET_STUDIO_RELIABLE_ROOT
source_dir="$local_root/jobs/$job_id/"
target_dir="$reliable_root/jobs/$job_id/"

if [[ "$execute" == true && ! -d "$source_dir" ]]; then printf 'Missing source: %s\n' "$source_dir" >&2; exit 1; fi
run_or_print "$execute" mkdir -p "$target_dir"
run_or_print "$execute" rsync -a --checksum --partial "$source_dir" "$target_dir"
printf 'Sync %s. Verify the reliable copy before shutdown.\n' "$([[ "$execute" == true ]] && printf complete || printf planned)"
