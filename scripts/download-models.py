#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Download only models pinned in config/models.yaml")
    parser.add_argument("--manifest", type=Path, default=Path("config/models.yaml"))
    parser.add_argument("--model-root", type=Path)
    parser.add_argument("--family", choices=("flux2", "ltx25"))
    parser.add_argument("--execute", action="store_true", help="perform network writes; default is dry-run")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.manifest.read_text())
    model_root = args.model_root or Path(data["policy"]["model_root"])
    if not model_root.is_absolute() or str(model_root) in {"/", "/root"}:
        raise SystemExit(f"unsafe model root: {model_root}")

    repositories = data["repositories"]
    selected = [m for m in data["models"] if args.family is None or m["family"] == args.family]
    token = os.environ.get("HF_TOKEN", "")
    endpoint = os.environ.get("HF_ENDPOINT", "https://huggingface.co").rstrip("/")

    for model in selected:
        target = model_root / model["target_path"]
        expected_size = int(model["size_bytes"])
        expected_hash = model["sha256"]
        if target.exists():
            actual_size = target.stat().st_size
            if actual_size != expected_size:
                print(f"ERROR size {target}: {actual_size} != {expected_size}", file=sys.stderr)
                return 1
            actual_hash = sha256_file(target)
            if actual_hash != expected_hash:
                print(f"ERROR sha256 {target}: {actual_hash} != {expected_hash}", file=sys.stderr)
                return 1
            print(f"verified {target}")
            continue

        if args.verify_only:
            print(f"MISSING {target}", file=sys.stderr)
            return 1

        repo = repositories[model["repository"]]
        url = f"{endpoint}/{repo['repo_id']}/resolve/{repo['revision']}/{model['source_path']}"
        if not args.execute:
            print(f"[dry-run] download {model['id']} ({expected_size} bytes) -> {target}")
            continue
        if repo.get("gated") and not token:
            print(f"HF_TOKEN is required for gated repository {repo['repo_id']}", file=sys.stderr)
            return 2

        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_suffix(target.suffix + ".partial")
        offset = partial.stat().st_size if partial.exists() else 0
        request = urllib.request.Request(url)
        if token:
            request.add_header("Authorization", f"Bearer {token}")
        if offset:
            request.add_header("Range", f"bytes={offset}-")
        print(f"downloading {model['id']} -> {target} (resume={offset} bytes)", flush=True)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                if offset and response.status != 206:
                    offset = 0
                mode = "ab" if offset else "wb"
                downloaded = offset
                next_report = downloaded + 1024 * 1024 * 1024
                with partial.open(mode) as output:
                    while chunk := response.read(8 * 1024 * 1024):
                        output.write(chunk)
                        downloaded += len(chunk)
                        if downloaded >= next_report:
                            percent = downloaded * 100 / expected_size
                            print(f"  {model['id']}: {percent:.1f}% ({downloaded}/{expected_size})", flush=True)
                            next_report = downloaded + 1024 * 1024 * 1024
        except (OSError, urllib.error.URLError) as exc:
            print(f"download interrupted for {model['id']}: {exc}; partial file retained", file=sys.stderr)
            raise
        if partial.stat().st_size != expected_size or sha256_file(partial) != expected_hash:
            partial.unlink(missing_ok=True)
            print(f"verification failed for {model['id']}", file=sys.stderr)
            return 1
        partial.replace(target)
        print(f"verified {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
