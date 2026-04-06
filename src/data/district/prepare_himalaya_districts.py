import argparse
from pathlib import Path

import geopandas as gpd

try:
    from src.common.himalaya_chunks import assign_chunk, list_chunks
except ModuleNotFoundError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[3]))
    from src.common.himalaya_chunks import assign_chunk, list_chunks


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--districts_file", type=str, required=True)
    parser.add_argument("--district_id_col", type=str, default="district_id")
    parser.add_argument("--district_name_col", type=str, default="district_name")
    parser.add_argument("--output_lookup_csv", type=str, default="data/processed/himalaya_district_lookup.csv")
    parser.add_argument("--output_geojson", type=str, default="data/processed/himalaya_districts_with_chunks.geojson")
    parser.add_argument("--output_chunks_dir", type=str, default="data/processed/district_chunks")
    return parser.parse_args()


def main():
    args = parse_args()

    gdf = gpd.read_file(args.districts_file).to_crs("EPSG:4326")
    if args.district_id_col not in gdf.columns:
        gdf[args.district_id_col] = gdf.index.astype(str)
    if args.district_name_col not in gdf.columns:
        gdf[args.district_name_col] = gdf[args.district_id_col].astype(str)

    centroids = gdf.geometry.centroid
    gdf["centroid_lon"] = centroids.x
    gdf["centroid_lat"] = centroids.y
    gdf["chunk"] = [assign_chunk(lat, lon) for lat, lon in zip(gdf["centroid_lat"], gdf["centroid_lon"])]
    gdf = gdf[gdf["chunk"].notna()].copy()

    lookup = gdf[
        [args.district_id_col, args.district_name_col, "chunk", "centroid_lat", "centroid_lon"]
    ].rename(
        columns={
            args.district_id_col: "district_id",
            args.district_name_col: "district_name",
        }
    )

    lookup_path = Path(args.output_lookup_csv)
    lookup_path.parent.mkdir(parents=True, exist_ok=True)
    lookup.to_csv(lookup_path, index=False)

    out_geojson = Path(args.output_geojson)
    out_geojson.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(out_geojson, driver="GeoJSON")

    chunks_dir = Path(args.output_chunks_dir)
    chunks_dir.mkdir(parents=True, exist_ok=True)
    for chunk in list_chunks():
        subset = gdf[gdf["chunk"] == chunk].copy()
        if subset.empty:
            continue
        chunk_file = chunks_dir / f"{chunk}.geojson"
        subset.to_file(chunk_file, driver="GeoJSON")

    print("Prepared Himalayan district chunk files")
    print("Lookup ->", lookup_path)
    print("GeoJSON ->", out_geojson)
    print("Chunks dir ->", chunks_dir)
    print("Districts:", len(lookup))


if __name__ == "__main__":
    main()
