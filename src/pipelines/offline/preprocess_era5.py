from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess ERA5 for one region and latest time window.")
    parser.add_argument("--region", required=True)
    parser.add_argument("--days", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    now = datetime.utcnow()
    start = (now - timedelta(days=max(1, args.days))).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")

    cmd = [
        sys.executable,
        "src/data/era5/preprocess_era5.py",
        "--region",
        args.region,
        "--start",
        start,
        "--end",
        end,
    ]
    result = subprocess.run(cmd, cwd=Path(__file__).resolve().parents[3], check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
