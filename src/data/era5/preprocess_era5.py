import os
import glob
import numpy as np
import pandas as pd
import xarray as xr

# ==============================
# CONFIG
# ==============================

RAW_ERA5_DIR = "data/raw/era5"
PROCESSED_DIR = "data/processed"

INSTANT_DIR = os.path.join(RAW_ERA5_DIR, "instant")
ACCUM_DIR = os.path.join(RAW_ERA5_DIR, "accum")

OUTPUT_FILE = os.path.join(PROCESSED_DIR, "era5_features_uttarakhand.csv")

# Uttarakhand bounding box
LAT_MIN, LAT_MAX = 28.0, 31.5
LON_MIN, LON_MAX = 77.0, 81.0

START_TIME = pd.Timestamp("2005-01-01")
END_TIME   = pd.Timestamp("2025-01-01")

INSTANT_VARS = ["t2m", "u10", "v10", "sp", "tcwv"]
ACCUM_VARS   = ["tp"]

os.makedirs(PROCESSED_DIR, exist_ok=True)

# ==============================
# HELPERS
# ==============================

def normalize_coords(ds):
    """Ensure latitude/longitude naming consistency"""
    if "latitude" not in ds.coords:
        if "lat" in ds.coords:
            ds = ds.rename({"lat": "latitude"})
    if "longitude" not in ds.coords:
        if "lon" in ds.coords:
            ds = ds.rename({"lon": "longitude"})
    return ds


def process_single_file(nc_file, agg="mean"):
    """
    Process one ERA5 NetCDF file safely:
    - Applies time filtering FIRST
    - Then spatial aggregation
    """

    ds = xr.open_dataset(nc_file)
    ds = normalize_coords(ds)

    # Rename time coordinate
    if "valid_time" in ds.coords:
        ds = ds.rename({"valid_time": "time"})

    # Spatial subset
    ds = ds.sel(
        latitude=slice(LAT_MAX, LAT_MIN),
        longitude=slice(LON_MIN, LON_MAX),
    )

    # Convert time safely
    time_index = pd.to_datetime(ds.time.values).floor("h")

    # Apply STRICT temporal mask FIRST
    time_mask = (time_index >= START_TIME) & (time_index < END_TIME)

    if not time_mask.any():
        return None

    ds = ds.isel(time=time_mask)
    time_index = time_index[time_mask]

    data = {}
    vars_to_use = INSTANT_VARS if agg == "mean" else ACCUM_VARS

    for var in vars_to_use:
        if var not in ds:
            continue

        da = ds[var]

        # Spatial aggregation
        if agg == "mean":
            da = da.mean(dim=["latitude", "longitude"], skipna=True)
        else:
            da = da.sum(dim=["latitude", "longitude"], skipna=True)

        values = da.values

        # Final safety check
        if values.ndim == 0:
            values = np.repeat(values, len(time_index))

        data[var] = values

    if not data:
        return None

    df = pd.DataFrame(data, index=time_index)
    df.index.name = "time"

    return df


def process_directory(nc_dir, agg):
    """Process all NetCDF files in a directory"""
    files = sorted(glob.glob(os.path.join(nc_dir, "*.nc")))
    dfs = []

    for f in files:
        df = process_single_file(f, agg)
        if df is not None and not df.empty:
            dfs.append(df)

    if not dfs:
        return None

    return pd.concat(dfs).sort_index()


# ==============================
# MAIN PIPELINE
# ==============================

def main():
    print("\n🚀 Starting ERA5 preprocessing\n")

    print("Processing INSTANT variables...")
    df_instant = process_directory(INSTANT_DIR, agg="mean")

    print("Processing ACCUMULATED variables...")
    df_accum = process_directory(ACCUM_DIR, agg="sum")

    if df_instant is None and df_accum is None:
        raise RuntimeError("No ERA5 data processed. Check raw files.")

    # Merge on time
    if df_instant is not None and df_accum is not None:
        df = df_instant.join(df_accum, how="inner")
    else:
        df = df_instant if df_instant is not None else df_accum

    # Final cleanup
    df = df[~df.index.duplicated()]
    df = df.sort_index()

    # Final sanity check
    print("\nNaN check after FIX:")
    print(df.isna().sum())

    df.reset_index().to_csv(OUTPUT_FILE, index=False)

    print("\n🎉 ERA5 preprocessing DONE")
    print(f"✅ Saved → {OUTPUT_FILE}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")


if __name__ == "__main__":
    main()
