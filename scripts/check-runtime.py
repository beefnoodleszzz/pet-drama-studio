#!/usr/bin/env python3
from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys


def command_output(command: list[str]) -> str | None:
    if not shutil.which(command[0]):
        return None
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT, timeout=10).strip()
    except (OSError, subprocess.SubprocessError):
        return None


def main() -> int:
    report: dict[str, object] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "nvidia_smi": command_output([
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader,nounits",
        ]),
    }
    try:
        import torch

        report["torch"] = torch.__version__
        report["torch_cuda"] = torch.version.cuda
        report["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            report["gpu"] = {
                "name": props.name,
                "vram_bytes": props.total_memory,
                "compute_capability": f"{props.major}.{props.minor}",
            }
    except ImportError:
        report["torch"] = None
        report["cuda_available"] = False

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["nvidia_smi"] is None or not report["cuda_available"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
