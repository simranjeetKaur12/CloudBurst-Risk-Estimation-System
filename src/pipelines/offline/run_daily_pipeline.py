from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REGIONS = ["himalayan_west", "uttarakhand", "sikkim"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run daily offline batch updates for latest features.")
    parser.add_argument("--days", type=int, default=10)
    parser.add_argument("--skip_download", action="store_true")
    return parser.parse_args()


def run(root: Path, *args: str) -> None:
    cmd = [sys.executable, *args]
    result = subprocess.run(cmd, cwd=root, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Failed: {' '.join(cmd)}")


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[3]

    if not args.skip_download:
        for region in REGIONS:
            run(root, "src/pipelines/offline/download_era5.py", "--region", region, "--days", str(args.days))
        run(root, "src/pipelines/offline/download_imerg.py", "--days", str(args.days))

    for region in REGIONS:
        run(root, "src/pipelines/offline/preprocess_era5.py", "--region", region, "--days", str(args.days))
        run(root, "src/pipelines/offline/preprocess_imerg.py", "--region", region)

    run(root, "src/pipelines/offline/merge_era5_imerg.py", "--regions", *REGIONS)
    run(root, "src/features/build_features.py")
    run(root, "src/pipelines/offline/generate_latest_features.py", "--days", str(args.days))


if __name__ == "__main__":
    main()
