# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Alex Kim
# MODIFIED by SpriteMake on 2026-10-10: extracted only the pure in-memory
# recolor helpers from sprite_gen/effects/recolor.py; replaced sprite_gen._deps
# with direct NumPy import, removed CLI, path I/O, and engine dependencies.
# Function bodies are unchanged from upstream commit
# 3dc080aa8faa8b5a6dfe865b1247c047761f8fd1 (v2.44.0).
"""Pinned offline palette transformations; see PROVENANCE.json and NOTICE."""
from __future__ import annotations
import numpy as np

PASSTHROUGH_REPORT_CAP = 64

def format_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _packed_rgb(arr: np.ndarray) -> np.ndarray:
    """Pack the RGB channels of an ``(H, W, 4)`` array into ``(H, W)`` uint32."""
    rgb = arr[:, :, :3].astype(np.uint32)
    return (rgb[:, :, 0] << 16) | (rgb[:, :, 1] << 8) | rgb[:, :, 2]


def _pack_color(rgb: tuple[int, int, int]) -> int:
    return (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]


def _color_histogram(
    arr: np.ndarray, opaque: np.ndarray
) -> list[tuple[tuple[int, int, int], int]]:
    """Distinct opaque colours as ``[(rgb, pixels), ...]``, sorted by count desc
    then hex asc — a total order, so the draft is deterministic."""
    packed = _packed_rgb(arr)[opaque]
    if packed.size == 0:
        return []
    values, counts = np.unique(packed, return_counts=True)
    out = []
    for value, count in zip(values.tolist(), counts.tolist()):
        rgb = ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)
        out.append((rgb, int(count)))
    out.sort(key=lambda item: (-item[1], item[0]))
    return out


def _bake_variant_exact(
    arr: np.ndarray, opaque: np.ndarray, pairs
) -> tuple[np.ndarray, list[dict], np.ndarray]:
    """Exact-match bake. Returns (recoloured array, per-source hit records,
    covered mask)."""
    packed = _packed_rgb(arr)
    out = arr.copy()
    covered = np.zeros(arr.shape[:2], dtype=bool)
    records = []
    for src, tgt in pairs:
        mask = (packed == _pack_color(src)) & opaque & ~covered
        hits = int(mask.sum())
        if hits:
            out[mask, 0] = tgt[0]
            out[mask, 1] = tgt[1]
            out[mask, 2] = tgt[2]
            covered |= mask
        records.append({"from": format_hex(src), "to": format_hex(tgt), "pixels": hits})
    return out, records, covered


def _bake_variant_tolerance(
    arr: np.ndarray, opaque: np.ndarray, pairs, tolerance: int
) -> tuple[np.ndarray, list[dict], np.ndarray]:
    """Tolerance bake: an opaque pixel within Chebyshev ``tolerance`` of a
    source is recoloured to that source's target; nearest source (L2) wins,
    ties broken by map order. Deterministic — pure integer arithmetic."""
    rgb = arr[:, :, :3].astype(np.int32)
    out = arr.copy()
    best_dist = np.full(arr.shape[:2], np.iinfo(np.int32).max, dtype=np.int32)
    best_idx = np.full(arr.shape[:2], -1, dtype=np.int32)
    for idx, (src, _tgt) in enumerate(pairs):
        delta = np.abs(rgb - np.array(src, dtype=np.int32))
        cheb = delta.max(axis=2)
        l2 = (delta * delta).sum(axis=2)
        within = opaque & (cheb <= tolerance)
        # Strict-less keeps the earlier map entry on a tie (stable, deterministic).
        take = within & (l2 < best_dist)
        best_dist = np.where(take, l2, best_dist)
        best_idx = np.where(take, idx, best_idx)
    covered = best_idx >= 0
    records = []
    for idx, (src, tgt) in enumerate(pairs):
        mask = best_idx == idx
        hits = int(mask.sum())
        if hits:
            out[mask, 0] = tgt[0]
            out[mask, 1] = tgt[1]
            out[mask, 2] = tgt[2]
        records.append({"from": format_hex(src), "to": format_hex(tgt), "pixels": hits})
    return out, records, covered


def _passthrough_report(
    arr: np.ndarray, opaque: np.ndarray, covered: np.ndarray
) -> tuple[list[dict], int, int]:
    """Opaque colours the map did not cover: passed through unchanged, but named
    and counted. Returns (top colours, total distinct count, total pixels)."""
    leftover = opaque & ~covered
    histogram = _color_histogram(arr, leftover)
    total_colors = len(histogram)
    total_pixels = sum(count for _rgb, count in histogram)
    top = [
        {"hex": format_hex(rgb), "pixels": count}
        for rgb, count in histogram[:PASSTHROUGH_REPORT_CAP]
    ]
    return top, total_colors, total_pixels
