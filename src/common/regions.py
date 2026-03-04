from __future__ import annotations

from typing import Iterable

REGION_BBOXES: dict[str, list[float]] = {
    # [north, west, south, east]
    "uttarakhand": [31.5, 77.0, 28.0, 81.0],
    "himalayan_west": [31.5, 77.0, 28.0, 81.0],
    "himalayan_central": [31.8, 81.0, 27.8, 86.5],
    "himalayan_east": [29.8, 86.5, 26.5, 92.5],
    # India-focused Himalayan chunks for chunk-wise model training.
    "indian_himalaya_west": [37.5, 72.0, 29.0, 79.0],
    "indian_himalaya_central": [33.5, 78.0, 26.0, 88.5],
    "indian_himalaya_east": [30.5, 88.0, 24.0, 97.5],
    "western": [37.5, 72.0, 29.0, 79.0],
    "central": [31.5, 77.0, 28.0, 81.5],
    "eastern": [30.5, 87.5, 24.0, 97.5],
    "western_ghats": [20.8, 72.5, 8.0, 78.8],
    "northeast_hills": [28.8, 88.0, 22.0, 97.5],
}


def list_regions() -> list[str]:
    return sorted(REGION_BBOXES.keys())


def parse_bbox_string(bbox: str) -> list[float]:
    parts = [p.strip() for p in bbox.split(",")]
    if len(parts) != 4:
        raise ValueError("BBox must contain 4 comma-separated values: north,west,south,east")
    values = [float(v) for v in parts]
    north, west, south, east = values
    if south >= north:
        raise ValueError("Invalid bbox: south must be smaller than north")
    if west >= east:
        raise ValueError("Invalid bbox: west must be smaller than east")
    return values


def resolve_bbox(region: str | None = None, bbox: str | None = None) -> tuple[str, list[float]]:
    if bbox:
        return (region or "custom").strip().lower(), parse_bbox_string(bbox)

    key = (region or "himalayan_west").strip().lower()
    if key not in REGION_BBOXES:
        available = ", ".join(list_regions())
        raise ValueError(f"Unknown region '{region}'. Available regions: {available}")
    return key, REGION_BBOXES[key]


def normalize_region_list(regions: Iterable[str]) -> list[str]:
    output: list[str] = []
    for region in regions:
        key = region.strip().lower()
        if key not in REGION_BBOXES:
            available = ", ".join(list_regions())
            raise ValueError(f"Unknown region '{region}'. Available regions: {available}")
        output.append(key)
    return output
