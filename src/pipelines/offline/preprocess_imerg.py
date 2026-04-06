from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess IMERG and aggregate to hourly.")
    parser.add_argument("--region", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[3]

    preprocess_cmd = [
        sys.executable,
        "src/data/imerg/preprocess_imerg.py",
        "--region",
        args.region,
    ]
    aggregate_cmd = [
        sys.executable,
        "src/data/imerg/aggregate_imerg.py",
        "--region",
        args.region,
    ]

    for cmd in (preprocess_cmd, aggregate_cmd):
        result = subprocess.run(cmd, cwd=root, check=False)
        if result.returncode != 0:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
