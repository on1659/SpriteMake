"""Offline sprite operations. All outputs are in memory; source files are read only.

Reports describe measurements and transformations, never semantic QA approval.
Recolor uses pinned Apache-2.0 sprite-gen helpers (see vendor/sprite_gen).
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path, PurePosixPath
import re

import numpy as np
from PIL import Image

if __package__:
    from .vendor.sprite_gen.recolor import (
        _bake_variant_exact, _bake_variant_tolerance, _passthrough_report,
    )
else:
    # Also support loading this single module for local QA without sys.path edits.
    import importlib.util
    _vendor_spec = importlib.util.spec_from_file_location(
        "spritemake_vendored_recolor", Path(__file__).parent / "vendor/sprite_gen/recolor.py"
    )
    _vendor = importlib.util.module_from_spec(_vendor_spec)
    _vendor_spec.loader.exec_module(_vendor)
    _bake_variant_exact = _vendor._bake_variant_exact
    _bake_variant_tolerance = _vendor._bake_variant_tolerance
    _passthrough_report = _vendor._passthrough_report

UPSTREAM_REVISION = "3dc080aa8faa8b5a6dfe865b1247c047761f8fd1"
MAX_PIXELS = 64 * 1024 * 1024


def _int(value, name, minimum=None, maximum=None):
    if type(value) is not int:
        raise ValueError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be <= {maximum}")
    return value


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    if abs(value) > 1000000 or not math.isfinite(value):
        raise ValueError(f"{name} must be finite and within +/-1000000")
    return value


def _pair(value, name, integers=False):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{name} must contain two coordinates")
    check = _int if integers else _number
    return [check(item, name) for item in value]


def _hex(value):
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError("colors must use #RRGGBB")
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def _bbox(image):
    bbox = image.getchannel("A").getbbox()
    return list(bbox) if bbox is not None else None


def recolor(image: Image.Image, spec: dict) -> tuple[Image.Image, dict]:
    """Simultaneous RGB replacement, preserving canvas geometry and every alpha.

    Tolerance uses Chebyshev radius, nearest squared L2 source, and input map
    order for ties. Pixels with alpha <= alphaThreshold are untouched.
    """
    if not isinstance(spec, dict):
        raise ValueError("recolor spec must be an object")
    unknown = set(spec) - {"map", "match", "tolerance", "alphaThreshold"}
    if unknown:
        raise ValueError(f"unknown recolor fields: {sorted(unknown)}")
    mapping = spec.get("map")
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError("recolor map must be a nonempty object")
    pairs = [(_hex(source), _hex(target)) for source, target in mapping.items()]
    if len({source for source, _ in pairs}) != len(pairs):
        raise ValueError("duplicate source color (case-insensitive)")
    match = spec.get("match", "exact")
    tolerance = _int(spec.get("tolerance", 0), "tolerance", 0, 255)
    threshold = _int(spec.get("alphaThreshold", 8), "alphaThreshold", 0, 255)
    if match not in ("exact", "tolerance"):
        raise ValueError("match must be exact or tolerance")
    if match == "exact" and tolerance != 0:
        raise ValueError("exact matching requires tolerance 0")
    arr = np.asarray(image.convert("RGBA"), dtype=np.uint8)
    opaque = arr[:, :, 3] > threshold
    if match == "exact":
        result, records, covered = _bake_variant_exact(arr, opaque, pairs)
    else:
        result, records, covered = _bake_variant_tolerance(arr, opaque, pairs, tolerance)
    colors, color_count, pixel_count = _passthrough_report(arr, opaque, covered)
    output = Image.fromarray(result)
    return output, {
        "operation": "recolor", "implementation": "sprite-gen vendored pure helpers",
        "upstreamRevision": UPSTREAM_REVISION, "match": match, "tolerance": tolerance,
        "alphaThreshold": threshold, "alphaPreserved": True, "geometryPreserved": True,
        "substitutedPixels": int(covered.sum()), "substitutions": records,
        "unusedSources": [record["from"] for record in records if not record["pixels"]],
        "passthroughPixels": pixel_count, "passthroughColorCount": color_count,
        "passthroughColors": colors, "passthroughColorsTruncated": color_count - len(colors),
    }


def extract_components(image: Image.Image, minimum_pixels: int = 1) -> list[list[int]]:
    """Return [x,y,width,height] for 8-connected nonzero-alpha components.

    Regions are suggestions, not automatic animation-frame classification.
    Sorting is top-to-bottom then left-to-right; minimum_pixels counts actual
    alpha pixels rather than the component's rectangle area.
    """
    _int(minimum_pixels, "minimum_pixels", 1)
    alpha = np.asarray(image.convert("RGBA"), dtype=np.uint8)[:, :, 3]
    if alpha.size > MAX_PIXELS:
        raise ValueError("component image exceeds pixel limit")
    remaining = alpha > 0
    height, width = remaining.shape
    rectangles = []
    for y in range(height):
        for x in np.flatnonzero(remaining[y]).tolist():
            if not remaining[y, x]:
                continue
            remaining[y, x] = False
            stack = [(x, y)]
            x0 = x1 = x
            y0 = y1 = y
            count = 0
            while stack:
                px, py = stack.pop()
                count += 1
                x0, x1 = min(x0, px), max(x1, px)
                y0, y1 = min(y0, py), max(y1, py)
                for ny in range(max(0, py - 1), min(height, py + 2)):
                    for nx in range(max(0, px - 1), min(width, px + 2)):
                        if remaining[ny, nx]:
                            remaining[ny, nx] = False
                            stack.append((nx, ny))
            if count >= minimum_pixels:
                rectangles.append([x0, y0, x1 - x0 + 1, y1 - y0 + 1])
    return sorted(rectangles, key=lambda rect: (rect[1], rect[0]))


def _source(root: Path, value):
    if not isinstance(value, str) or "\\" in value or ":" in value:
        raise ValueError("frame path must be a relative POSIX PNG path")
    relative = PurePosixPath(value)
    if (relative.is_absolute() or len(relative.parts) < 2
            or relative.parts[0] not in ("source", "generated")
            or any(part in (".", "..") for part in value.split("/"))
            or any(not part for part in value.split("/"))):
        raise ValueError("frame path must be inside source/ or generated/ without traversal")
    if relative.suffix.lower() != ".png":
        raise ValueError("frame input must be PNG")
    candidate = root
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ValueError("symlink frame paths are not allowed")
    if not candidate.is_file() or not candidate.resolve().is_relative_to(root):
        raise ValueError("frame input must be an existing regular batch PNG")
    return candidate


def _chroma(image, spec):
    if not isinstance(spec, dict) or set(spec) - {"key", "tolerance", "despill"}:
        raise ValueError("chroma must contain key, optional tolerance and despill only")
    key = _hex(spec.get("key"))
    tolerance = _int(spec.get("tolerance", 0), "chroma tolerance", 0, 255)
    despill = spec.get("despill", False)
    if type(despill) is not bool:
        raise ValueError("chroma despill must be boolean")
    arr = np.array(image, dtype=np.uint8)
    rgb = arr[:, :, :3].astype(np.int32)
    keyed = np.max(np.abs(rgb - np.array(key)), axis=2) <= tolerance
    removed = int(np.count_nonzero(keyed & (arr[:, :, 3] > 0)))
    arr[keyed, 3] = 0
    despilled = 0
    # Explicit conservative dominant-channel suppression, never alpha synthesis.
    # Only near-key surviving pixels are candidates; color detail elsewhere stays.
    if despill and len(set(key)) > 1:
        channels = [index for index, value in enumerate(key) if value == max(key)]
        others = [index for index in range(3) if index not in channels]
        if others:
            near = (np.max(np.abs(rgb - np.array(key)), axis=2) <= min(255, tolerance + 32))
            near &= arr[:, :, 3] > 0
            cap = rgb[:, :, others].max(axis=2)
            changed = np.zeros(arr.shape[:2], dtype=bool)
            for channel in channels:
                mask = near & (rgb[:, :, channel] > cap)
                arr[:, :, channel][mask] = cap[mask]
                changed |= mask
            despilled = int(changed.sum())
    return Image.fromarray(arr), {"operation": "explicit-chroma", "key": spec["key"],
        "tolerance": tolerance, "removedAlphaPixels": removed, "despilledPixels": despilled,
        "alphaNeverIncreased": True, "despillAlgorithm": "near-key dominant-channel clamp"}


def process_frames(root: Path, recipe: dict, contract: dict) -> tuple[Image.Image, dict]:
    """Extract fixed rects and place them by explicit reference anchors.

    One shared scale uses nearest-neighbor. Placement is target anchor minus
    sourceAnchor*scale plus explicit offset, rounded with floor(value+0.5).
    Anchors may lie beyond the crop, preserving an airborne reference plane.
    Only transparent padding may fall outside a cell; visible clipping fails.
    """
    if not isinstance(recipe, dict) or recipe.get("schemaVersion") != 1 or type(recipe.get("schemaVersion")) is not int:
        raise ValueError("recipe schemaVersion must be integer 1")
    unknown = set(recipe) - {"schemaVersion", "frames", "scale", "chroma", "recolor", "pixelGrid",
                             "contract", "inputs", "provenance"}
    if unknown:
        raise ValueError(f"unsupported recipe fields: {sorted(unknown)}")
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root must be a batch directory")
    try:
        atlas = contract["atlas"]
        canvas, grid, anchor = atlas["canvas"], atlas["grid"], atlas["anchor"]
        width = _int(canvas["width"], "canvas width", 1)
        height = _int(canvas["height"], "canvas height", 1)
        columns = _int(grid["columns"], "columns", 1)
        rows = _int(grid["rows"], "rows", 1)
        cw = _int(grid["cellWidth"], "cellWidth", 1)
        ch = _int(grid["cellHeight"], "cellHeight", 1)
        ax, ay = _int(anchor["x"], "anchor x", 0, cw), _int(anchor["y"], "anchor y", 0, ch)
        plane = _number(atlas["sourcePlaneY"], "sourcePlaneY")
    except (KeyError, TypeError) as exc:
        raise ValueError("contract requires explicit canvas, grid, anchor and sourcePlaneY") from exc
    if width != columns * cw or height != rows * ch or width * height > MAX_PIXELS:
        raise ValueError("contract must be an exact fixed grid within pixel limit")
    if not 0 <= plane <= ch:
        raise ValueError("sourcePlaneY must be inside or on the cell boundary")
    if anchor.get("mode", "pixel") != "pixel":
        raise ValueError("processing requires pixel anchors")
    scale = _number(recipe.get("scale", 1), "scale")
    if scale <= 0:
        raise ValueError("scale must be positive")
    pixel_grid = _int(recipe.get("pixelGrid", 1), "pixelGrid", 1)
    frames = recipe.get("frames")
    if not isinstance(frames, list) or len(frames) != columns * rows:
        raise ValueError("recipe must provide exactly one frame per target cell")
    validated, slots = [], set()
    for index, frame in enumerate(frames):
        if not isinstance(frame, dict) or set(frame) - {"path", "rect", "row", "column", "sourceAnchor", "offset"}:
            raise ValueError(f"frame {index} has unsupported fields")
        path = _source(root, frame.get("path"))
        row = _int(frame.get("row"), "row", 0, rows - 1)
        column = _int(frame.get("column"), "column", 0, columns - 1)
        if (row, column) in slots:
            raise ValueError("duplicate target cell")
        slots.add((row, column))
        source_anchor = _pair(frame.get("sourceAnchor"), "sourceAnchor")
        offset = _pair(frame.get("offset", [0, 0]), "offset", integers=True)
        rect = frame.get("rect")
        if rect is not None:
            if not isinstance(rect, list) or len(rect) != 4:
                raise ValueError("rect must be [x,y,width,height]")
            rect = [_int(value, "rect", 0 if position < 2 else 1) for position, value in enumerate(rect)]
        validated.append((frame, path, row, column, source_anchor, offset, rect))
    output = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    records = []
    for frame, path, row, column, source_anchor, offset, rect in validated:
        with Image.open(path) as source:
            if source.format != "PNG" or source.width * source.height > MAX_PIXELS:
                raise ValueError("frame must be a PNG within pixel limit")
            source_size = list(source.size)
            image = source.convert("RGBA")
        x, y, fw, fh = rect or [0, 0, *image.size]
        if x + fw > image.width or y + fh > image.height:
            raise ValueError("frame rect exceeds source canvas")
        image = image.crop((x, y, x + fw, y + fh))
        source_bbox = _bbox(image)
        transforms = []
        if recipe.get("chroma") is not None:
            image, measurement = _chroma(image, recipe["chroma"])
            transforms.append(measurement)
        if recipe.get("recolor") is not None:
            image, measurement = recolor(image, recipe["recolor"])
            transforms.append(measurement)
        if fw % pixel_grid or fh % pixel_grid:
            raise ValueError("pixelGrid must divide every source frame width and height")
        if pixel_grid > 1:
            image = image.resize((fw // pixel_grid, fh // pixel_grid), Image.Resampling.NEAREST).resize((fw, fh), Image.Resampling.NEAREST)
            transforms.append({"operation": "pixelGrid", "grid": pixel_grid, "canvasPreserved": True})
        size = (math.floor(fw * scale + 0.5), math.floor(fh * scale + 0.5))
        if min(size) < 1 or size[0] * size[1] > MAX_PIXELS:
            raise ValueError("scaled frame dimensions invalid or exceed pixel limit")
        if size != image.size:
            image = image.resize(size, Image.Resampling.NEAREST)
        left = math.floor(ax - source_anchor[0] * scale + offset[0] + 0.5)
        top = math.floor(ay - source_anchor[1] * scale + offset[1] + 0.5)
        bbox = _bbox(image)
        if bbox is None:
            raise ValueError(f"target cell ({column},{row}) would be blank")
        translated = [bbox[0] + left, bbox[1] + top, bbox[2] + left, bbox[3] + top]
        if translated[0] < 0 or translated[1] < 0 or translated[2] > cw or translated[3] > ch:
            raise ValueError(f"frame clips or bleeds outside target cell ({column},{row})")
        # Crop transparent overflow explicitly; copy pixels without alpha masking,
        # which would square semitransparent alpha on a transparent destination.
        cell = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        cell.paste(image, (left, top))
        output.paste(cell, (column * cw, row * ch))
        records.append({"path": frame["path"], "sourceSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "sourceSize": source_size, "rect": [x, y, fw, fh], "sourceAlphaBBox": source_bbox,
            "row": row, "column": column, "sourceAnchor": source_anchor, "offset": offset,
            "scale": scale, "scaledSize": list(size), "destinationTopLeft": [left, top],
            "alphaBBox": _bbox(cell), "transforms": transforms})
    return output, {"schemaVersion": 1, "operation": "fixed-grid-processing", "canvas": [width, height],
        "grid": {"columns": columns, "rows": rows, "cellWidth": cw, "cellHeight": ch},
        "anchor": {"x": ax, "y": ay}, "sourcePlaneY": plane, "sharedScale": scale,
        "rounding": "floor(value + 0.5)", "alphaBBox": _bbox(output), "frames": records,
        "qaStatus": "measurements-only; visual placement and motion review required"}
