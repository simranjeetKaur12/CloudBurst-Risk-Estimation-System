from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import Point


def load_districts(
    districts_file: str,
    district_id_col: str = "district_id",
    district_name_col: str = "district_name",
    region_col: str | None = None,
    region_value: str | None = None,
) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(districts_file)
    gdf = gdf.to_crs("EPSG:4326")

    if region_col and region_col in gdf.columns and region_value:
        gdf = gdf[gdf[region_col].astype(str).str.lower() == region_value.lower()].copy()

    if district_id_col not in gdf.columns:
        gdf[district_id_col] = gdf.index.astype(str)
    if district_name_col not in gdf.columns:
        gdf[district_name_col] = gdf[district_id_col].astype(str)

    if gdf.empty:
        raise ValueError(f"No districts found from {districts_file} after filtering.")

    return gdf[[district_id_col, district_name_col, "geometry"]].rename(
        columns={district_id_col: "district_id", district_name_col: "district_name"}
    )


def district_bbox_nwse(districts_gdf: gpd.GeoDataFrame) -> tuple[float, float, float, float]:
    minx, miny, maxx, maxy = districts_gdf.total_bounds
    # north, west, south, east
    return maxy, minx, miny, maxx


def build_cell_index_map(
    lat_values: np.ndarray,
    lon_values: np.ndarray,
    districts_gdf: gpd.GeoDataFrame,
) -> dict[str, dict[str, np.ndarray | str]]:
    lon_grid, lat_grid = np.meshgrid(lon_values, lat_values)
    lon_flat = lon_grid.ravel()
    lat_flat = lat_grid.ravel()

    points = gpd.GeoSeries([Point(xy) for xy in zip(lon_flat, lat_flat)], crs="EPSG:4326")

    index_map: dict[str, dict[str, np.ndarray | str]] = {}
    n_lon = len(lon_values)

    for _, district in districts_gdf.iterrows():
        district_id = str(district["district_id"])
        district_name = str(district["district_name"])
        mask = points.within(district.geometry).to_numpy()
        flat_idx = np.where(mask)[0]

        if len(flat_idx) == 0:
            continue

        lat_idx = (flat_idx // n_lon).astype(np.int64)
        lon_idx = (flat_idx % n_lon).astype(np.int64)
        index_map[district_id] = {
            "district_name": district_name,
            "lat_idx": lat_idx,
            "lon_idx": lon_idx,
        }

    if not index_map:
        raise ValueError(
            "No grid cells mapped to district polygons. Check CRS and district boundary extent."
        )

    return index_map
