import argparse
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

import earthaccess
import pandas as pd
from tqdm import tqdm

try:
    from src.common.regions import list_regions, resolve_bbox
except ModuleNotFoundError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[3]))
    from src.common.regions import list_regions, resolve_bbox


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_year", type=int, required=True)
    parser.add_argument("--end_year", type=int, required=True)
    parser.add_argument("--months", type=int, nargs="+", default=[6, 7, 8, 9])
    parser.add_argument("--sleep", type=int, default=1)
    parser.add_argument("--raw_dir", type=str, default="data/raw/imerg")
    parser.add_argument("--processed_csv", type=str, default=None)
    parser.add_argument("--region", type=str, default="himalayan_west")
    parser.add_argument(
        "--bbox",
        type=str,
        default=None,
        help="Custom bbox in 'north,west,south,east'. Overrides --region preset.",
    )
    parser.add_argument("--list_regions", action="store_true")
    return parser.parse_args()


def download_imerg(args):
    region_key, _ = resolve_bbox(region=args.region, bbox=args.bbox)

    raw_root = Path(args.raw_dir) / region_key
    raw_root.mkdir(parents=True, exist_ok=True)

    if args.processed_csv:
        processed_csv = Path(args.processed_csv)
    else:
        candidate = Path(f"data/processed/imerg_processed_days_{region_key}.csv")
        legacy_candidate = Path("data/processed/imerg_processed_days.csv")
        processed_csv = legacy_candidate if region_key == "uttarakhand" and legacy_candidate.exists() else candidate
    processed_csv.parent.mkdir(parents=True, exist_ok=True)

    earthaccess.login(persist=True)

    processed_days = set()
    if processed_csv.exists():
        df_days = pd.read_csv(processed_csv, parse_dates=["date"])
        processed_days = set(df_days["date"].dt.date)

    logging.info("Region: %s", region_key)
    logging.info("Loaded %d processed days", len(processed_days))

    for year in range(args.start_year, args.end_year + 1):
        for month in args.months:
            start_date = datetime(year, month, 1)
            end_date = (
                datetime(year, month + 1, 1) - timedelta(days=1)
                if month < 12
                else datetime(year, 12, 31)
            )

            current = start_date
            while current <= end_date:
                day = current.date()

                if day in processed_days:
                    current += timedelta(days=1)
                    continue

                save_path = raw_root / f"{year}/{month:02d}/{current.day:02d}"
                save_path.mkdir(parents=True, exist_ok=True)

                if any(save_path.glob("*.HDF5")):
                    current += timedelta(days=1)
                    continue

                logging.info("Downloading %s for %s", day, region_key)
                results = earthaccess.search_data(
                    short_name="GPM_3IMERGHH",
                    version="07",
                    temporal=(
                        current.strftime("%Y-%m-%d"),
                        (current + timedelta(days=1)).strftime("%Y-%m-%d"),
                    ),
                    provider="GES_DISC",
                )

                if not results:
                    current += timedelta(days=1)
                    continue

                for granule in tqdm(results, desc="Granules", unit="file"):
                    earthaccess.download(granule, save_path, threads=1)
                    time.sleep(args.sleep)

                current += timedelta(days=1)

    logging.info("IMERG download completed for region: %s", region_key)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    if args.list_regions:
        print("\n".join(list_regions()))
        raise SystemExit(0)
    download_imerg(args)
