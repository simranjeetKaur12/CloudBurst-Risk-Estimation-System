from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import earthaccess


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download IMERG data for the recent N-day window.")
    parser.add_argument("--days", type=int, default=10)
    parser.add_argument("--output_dir", default="data/raw/imerg/latest")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    end = datetime.utcnow()
    start = end - timedelta(days=max(1, args.days))

    earthaccess.login(strategy="environment", persist=False)
    results = earthaccess.search_data(
        short_name="GPM_3IMERGHH",
        version="07",
        temporal=(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")),
        provider="GES_DISC",
    )
    if not results:
        print("No IMERG granules found for requested window")
        return

    earthaccess.download(results, str(output_dir), threads=2)
    print(f"IMERG latest-window download complete ({args.days} days)")


if __name__ == "__main__":
    main()
