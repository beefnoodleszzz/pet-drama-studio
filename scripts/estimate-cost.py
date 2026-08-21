#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate AutoDL GPU and paid local-disk cost")
    parser.add_argument("--gpu-hours", type=float, required=True)
    parser.add_argument("--gpu-cny-per-hour", type=float, default=2.78)
    parser.add_argument("--disk-total-gb", type=float, default=200)
    parser.add_argument("--disk-free-gb", type=float, default=50)
    parser.add_argument("--disk-cny-per-gb-day", type=float, default=0.0066)
    parser.add_argument("--disk-days", type=float, default=1)
    args = parser.parse_args()
    paid_disk = max(0.0, args.disk_total_gb - args.disk_free_gb)
    gpu = args.gpu_hours * args.gpu_cny_per_hour
    disk = paid_disk * args.disk_cny_per_gb_day * args.disk_days
    print(json.dumps({
        "gpu_cny": round(gpu, 2),
        "disk_cny": round(disk, 2),
        "total_cny": round(gpu + disk, 2),
        "assumptions": {
            "gpu_hours": args.gpu_hours,
            "gpu_cny_per_hour": args.gpu_cny_per_hour,
            "paid_disk_gb": paid_disk,
            "disk_days": args.disk_days,
        },
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
