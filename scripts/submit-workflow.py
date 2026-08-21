#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.request
import uuid
from pathlib import Path


def request_json(url: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit an API-format ComfyUI workflow")
    parser.add_argument("workflow", type=Path)
    parser.add_argument("--url", default="http://127.0.0.1:8188")
    parser.add_argument("--client-id", default=str(uuid.uuid4()))
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--poll-seconds", type=float, default=2)
    parser.add_argument("--timeout-seconds", type=float, default=1800)
    parser.add_argument("--execute", action="store_true", help="submit; default only validates and prints")
    args = parser.parse_args()

    workflow = json.loads(args.workflow.read_text())
    if not isinstance(workflow, dict) or not workflow:
        raise SystemExit("workflow must be a non-empty API-format JSON object")
    if not all(isinstance(node, dict) and "class_type" in node for node in workflow.values()):
        raise SystemExit("workflow is not API format: every top-level node must contain class_type")
    payload = {"prompt": workflow, "client_id": args.client_id}
    if not args.execute:
        print(json.dumps({"dry_run": True, "url": f"{args.url}/prompt", "nodes": len(workflow)}, indent=2))
        return 0

    result = request_json(f"{args.url.rstrip('/')}/prompt", payload)
    prompt_id = result["prompt_id"]
    print(json.dumps({"submitted": True, "prompt_id": prompt_id}, indent=2))
    if not args.wait:
        return 0
    deadline = time.monotonic() + args.timeout_seconds
    while time.monotonic() < deadline:
        history = request_json(f"{args.url.rstrip('/')}/history/{prompt_id}")
        if prompt_id in history:
            print(json.dumps(history[prompt_id], ensure_ascii=False, indent=2))
            return 0
        time.sleep(args.poll_seconds)
    raise SystemExit(f"timed out waiting for {prompt_id}")


if __name__ == "__main__":
    raise SystemExit(main())
