import argparse
import subprocess
import sys
from pathlib import Path

try:
    from src.common.himalaya_chunks import list_chunks, normalize_chunks
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from src.common.himalaya_chunks import list_chunks, normalize_chunks

ROOT = Path(__file__).resolve().parents[2]


def run(script: str, *args: str):
    cmd = [sys.executable, script, *args]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"Failed: {script}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--districts_file", type=str, required=True)
    parser.add_argument("--district_id_col", type=str, default="district_id")
    parser.add_argument("--district_name_col", type=str, default="district_name")
    parser.add_argument("--chunks", nargs="+", default=list_chunks())
    parser.add_argument("--start_year", type=int, required=True)
    parser.add_argument("--end_year", type=int, required=True)
    parser.add_argument("--skip_download", action="store_true")
    parser.add_argument("--monsoon_only", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    chunks = normalize_chunks(args.chunks)

    run(
        "src/data/district/prepare_himalaya_districts.py",
        "--districts_file",
        args.districts_file,
        "--district_id_col",
        args.district_id_col,
        "--district_name_col",
        args.district_name_col,
    )

    chunk_districts_geojson = "data/processed/himalaya_districts_with_chunks.geojson"
    for chunk in chunks:
        if not args.skip_download:
            run(
                "src/data/era5/download_era5.py",
                "--start_year",
                str(args.start_year),
                "--end_year",
                str(args.end_year),
                "--region",
                chunk,
            )
            run(
                "src/data/imerg/download_imerg.py",
                "--start_year",
                str(args.start_year),
                "--end_year",
                str(args.end_year),
                "--region",
                chunk,
            )

        run("src/data/era5/unzip_era5.py", "--region", chunk)
        run(
            "src/data/district/build_district_dataset.py",
            "--region",
            chunk,
            "--districts_file",
            chunk_districts_geojson,
            "--district_id_col",
            "district_id",
            "--district_name_col",
            "district_name",
            "--district_region_col",
            "chunk",
            "--start",
            f"{args.start_year}-01-01",
            "--end",
            f"{args.end_year + 1}-01-01",
            *("--monsoon_only",) if args.monsoon_only else (),
        )

    run(
        "src/models/train_chunk_ensemble.py",
        "--chunks",
        *chunks,
    )
    print("Himalaya chunk pipeline complete.")


if __name__ == "__main__":
    main()
