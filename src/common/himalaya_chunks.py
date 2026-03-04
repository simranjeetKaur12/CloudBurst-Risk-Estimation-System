from __future__ import annotations

from typing import Iterable

CHUNK_ORDER = ["western", "central", "eastern"]

# [north, west, south, east]
CHUNK_BBOXES: dict[str, list[float]] = {
    # Western Himalaya: Jammu & Kashmir, Ladakh, Himachal Pradesh
    "western": [37.5, 72.0, 29.0, 79.0],
    # Central Himalaya: Uttarakhand
    "central": [31.5, 77.0, 28.0, 81.5],
    # Eastern Himalaya: Sikkim, Arunachal Pradesh
    "eastern": [30.5, 87.5, 24.0, 97.5],
}


def list_chunks() -> list[str]:
    return list(CHUNK_ORDER)


def normalize_chunks(chunks: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    for chunk in chunks:
        key = chunk.strip().lower()
        if key not in CHUNK_BBOXES:
            raise ValueError(f"Unknown chunk '{chunk}'. Available: {list_chunks()}")
        normalized.append(key)
    return normalized


def contains_lat_lon(chunk: str, lat: float, lon: float) -> bool:
    north, west, south, east = CHUNK_BBOXES[chunk]
    return south <= lat <= north and west <= lon <= east


def assign_chunk(lat: float, lon: float) -> str | None:
    for chunk in CHUNK_ORDER:
        if contains_lat_lon(chunk, lat, lon):
            return chunk
    return None
