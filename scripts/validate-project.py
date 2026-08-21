#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def main() -> int:
    models = json.loads((ROOT / "config/models.yaml").read_text())
    repositories = models["repositories"]
    seen_targets: set[str] = set()
    total = 0
    for key, repository in repositories.items():
        if not COMMIT.fullmatch(repository["revision"]):
            fail(f"invalid revision for {key}")
    for model in models["models"]:
        if model["repository"] not in repositories:
            fail(f"unknown repository for {model['id']}")
        if model["target_path"] in seen_targets:
            fail(f"duplicate target_path {model['target_path']}")
        seen_targets.add(model["target_path"])
        if Path(model["target_path"]).is_absolute() or ".." in Path(model["target_path"]).parts:
            fail(f"unsafe target path for {model['id']}")
        if not SHA256.fullmatch(model["sha256"]):
            fail(f"invalid sha256 for {model['id']}")
        if int(model["size_bytes"]) <= 0:
            fail(f"invalid size for {model['id']}")
        total += int(model["size_bytes"])
    if total != int(models["policy"]["estimated_total_bytes"]):
        fail(f"manifest total mismatch: {total}")

    for path in (ROOT / "workflows").glob("*.ui.json"):
        graph = json.loads(path.read_text())
        if not isinstance(graph.get("nodes"), list) or not graph["nodes"]:
            fail(f"invalid UI workflow: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        print(f"workflow {path.name}: {len(graph['nodes'])} nodes sha256={digest}")

    schema = json.loads((ROOT / "schemas/shot-spec.schema.json").read_text())
    if schema.get("type") != "object":
        fail("invalid ShotSpec schema")
    for relative in (
        "stories/example-project/shots/s001.yaml",
        "characters/example-character/character.yaml",
        "jobs/example-job/job.yaml",
    ):
        if not (ROOT / relative).read_text().strip():
            fail(f"empty YAML example: {relative}")

    print(f"models: {len(models['models'])}; total: {total} bytes ({total / 1024**3:.2f} GiB)")
    print("project validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
