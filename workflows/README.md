# Workflows

The two `*.ui.json` files are pinned copies of official ComfyUI workflow templates from
`Comfy-Org/workflow_templates` commit `82b1954dc14c622be0f551d4020b4d8f961a5a48`:

- `flux2-multireference.ui.json` — official FLUX.2 Dev image/edit template.
- `ltx25-image-to-video.ui.json` — official LTX 2.5 I2V template.

They are UI-format source graphs and are intentionally kept unchanged for provenance. ComfyUI's
HTTP `/prompt` endpoint requires API-format JSON. During the first deployment, load each source
template in the pinned ComfyUI release, export its API format, save it beside the source as
`*.api.json`, then run `scripts/submit-workflow.py` in dry-run mode before any paid generation.

Do not edit the vendored source files. Make project-specific changes in versioned API copies and
record the source template commit plus ComfyUI commit in the job manifest.
