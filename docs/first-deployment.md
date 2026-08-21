# First deployment checklist

This checklist does not authorize spending. Stop before creating an AutoDL instance until the user
has approved the current machine, storage configuration, and estimated cost.

## Before renting

1. Recheck RTX 5090 inventory, hourly price, CPU, RAM, driver, rental end date, and data-disk expansion capacity.
2. Select one GPU, at least 90GB RAM, and 200GB total local data disk.
3. Show the complete configuration and expected GPU plus persistent-disk cost to the user.
4. Confirm the user has accepted the Hugging Face LTX 2.5 license.
5. Obtain explicit authorization to create the instance and incur charges.

## After SSH is available

1. Copy or clone this repository onto the instance.
2. Run `scripts/bootstrap-autodl.sh` without arguments and review the dry-run.
3. Run `scripts/bootstrap-autodl.sh --execute` only after the dry-run is approved.
4. Put `HF_TOKEN` in `.env` or the process environment; never print or commit it.
5. Run `scripts/check-runtime.py` and save its JSON output with the deployment log.
6. Run `scripts/download-models.sh` and review the complete dry-run and byte total.
7. Run `scripts/download-models.sh --execute`; every file must pass size and SHA256 verification.
8. Run `scripts/download-models.sh --verify-only` before starting ComfyUI.
9. Start the pinned ComfyUI checkout and run `scripts/health-check.py`.

## Golden smoke tests

1. Load each pinned official UI template and export an API-format copy.
2. Validate API copies with `scripts/submit-workflow.py <file>` in dry-run mode.
3. Generate one FLUX.2 reference image and record cold/warm latency, peak VRAM, and peak RAM.
4. Generate one 3–5 second LTX 2.5 I2V clip with prompt enhancement and temporal upscaling disabled.
5. Repeat only with explicit bounds; do not retry indefinitely.
6. Sync workflows, logs, manifests, and approved outputs to `/root/autodl-fs`.
7. Verify the reliable copy, then explicitly confirm shutdown.
