from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge processed ERA5 and IMERG files.")
    parser.add_argument("--regions", nargs="+", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[3]
    cmd = [
        sys.executable,
        "src/data/imerg/merge_era5_imerg.py",
        "--regions",
        *args.regions,
    ]
    result = subprocess.run(cmd, cwd=root, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
