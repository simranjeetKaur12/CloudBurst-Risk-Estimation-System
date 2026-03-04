import argparse
import logging
import re
import zipfile
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", type=str, default="himalayan_west")
    parser.add_argument("--input_dir", type=str, default="data/raw/era5")
    return parser.parse_args()


def extract_files(base_dir: Path):
    accum_folder = base_dir / "accum"
    instant_folder = base_dir / "instant"
    accum_folder.mkdir(exist_ok=True)
    instant_folder.mkdir(exist_ok=True)

    for file_path in base_dir.glob("era5_*"):
        if file_path.suffix == ".nc":
            logging.info("Already extracted: %s", file_path.name)
            continue

        if not zipfile.is_zipfile(file_path):
            logging.warning("Skipping non-zip: %s", file_path.name)
            continue

        match = re.search(r"era5_[a-z_]+_(\d{4})_(\d{2})", file_path.name)
        if not match:
            match = re.search(r"era5_(\d{4})_(\d{2})", file_path.name)
        if not match:
            continue

        year, month = match.groups()

        with zipfile.ZipFile(file_path, "r") as archive:
            for member in archive.namelist():
                if "accum" in member.lower():
                    out_path = accum_folder / f"era5_accum_{year}_{month}.nc"
                elif "instant" in member.lower():
                    out_path = instant_folder / f"era5_instant_{year}_{month}.nc"
                else:
                    continue

                if out_path.exists():
                    continue

                with archive.open(member) as src, open(out_path, "wb") as dst:
                    dst.write(src.read())
                logging.info("Saved -> %s", out_path.name)

    logging.info("ERA5 extraction complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    region_dir = Path(args.input_dir) / args.region
    if not region_dir.exists():
        # Backward compatibility: data/raw/era5 directly contains files.
        region_dir = Path(args.input_dir)
    extract_files(region_dir)
