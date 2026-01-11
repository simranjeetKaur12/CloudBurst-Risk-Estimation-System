import zipfile
from pathlib import Path
import re

# ==========================
# PATHS
# ==========================
ZIP_FOLDER = Path("data/raw/era5")
ACCUM_FOLDER = ZIP_FOLDER / "accum"
INSTANT_FOLDER = ZIP_FOLDER / "instant"

ACCUM_FOLDER.mkdir(exist_ok=True)
INSTANT_FOLDER.mkdir(exist_ok=True)

# ==========================
# PROCESS FILES
# ==========================
for zip_path in ZIP_FOLDER.glob("era5_*.nc"):

    if not zipfile.is_zipfile(zip_path):
        print(f"❌ Not a zip: {zip_path.name}")
        continue

    # Extract year and month from filename
    match = re.search(r"era5_(\d{4})_(\d{2})", zip_path.name)
    if not match:
        print(f"⚠️ Skipping (cannot parse date): {zip_path.name}")
        continue

    year, month = match.groups()

    print(f"📦 Processing {zip_path.name}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():

            if "accum" in member.lower():
                out_path = ACCUM_FOLDER / f"era5_accum_{year}_{month}.nc"
            elif "instant" in member.lower():
                out_path = INSTANT_FOLDER / f"era5_instant_{year}_{month}.nc"
            else:
                print(f"⚠️ Unknown file inside zip: {member}")
                continue

            with zf.open(member) as src, open(out_path, "wb") as dst:
                dst.write(src.read())

            print(f"   ✅ Saved → {out_path.name}")

print("\n🎉 All files extracted and organized!")
