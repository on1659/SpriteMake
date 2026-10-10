#!/usr/bin/env python3
"""Read-only PNG measurements for a SpriteMake candidate (Pillow + stdlib).

Measurements do not approve contact placement, style, or the meaning of motion.
An optional status is a fresh, unapproved candidate status, never a promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile

from PIL import Image, UnidentifiedImageError


class ContractError(ValueError):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_path(root: Path, value: str, prefixes: tuple[str, ...] = ()) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ContractError("Expected a nonempty path")
    path = Path(value.replace("\\", "/"))
    if ".." in path.parts:
        raise ContractError(f"Traversal is not allowed: {value}")

    def under_root(candidate: Path):
        # macOS /var -> /private/var is an ancestor alias, not a batch input
        # symlink. Retain lexical descendants so in-batch aliases still fail.
        if candidate.is_relative_to(root):
            return candidate.relative_to(root)
        relative = None
        for ancestor in candidate.parents:
            if ancestor.resolve() == root:
                relative = candidate.relative_to(ancestor)
        return relative

    if not path.is_absolute():
        cwd_path = Path.cwd() / path
        path = cwd_path if under_root(cwd_path) is not None else root / path
    relative = under_root(path)
    if relative is None:
        raise ContractError(f"Path escapes batch root: {value}")
    if prefixes and (not relative.parts or relative.parts[0] not in prefixes):
        raise ContractError(f"Path must be under {'/'.join(prefixes)}: {value}")
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ContractError(f"Symlink paths are not allowed: {value}")
    return (root / relative).resolve()


def integer(value, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ContractError(f"{label} must be an integer >= {minimum}")
    return value


def load_contract(path: Path) -> dict:
    try:
        contract = json.loads(path.read_text(encoding="utf-8-sig").strip())
        if not isinstance(contract, dict):
            raise ContractError("Contract must be an object")
        if type(contract.get("schemaVersion")) is not int or contract.get("schemaVersion") != 1:
            raise ContractError("schemaVersion must be 1")
        if not isinstance(contract.get("assetId"), str) or not contract["assetId"].strip():
            raise ContractError("assetId is required")
        integer(contract["version"], "version", 1)
        atlas = contract["atlas"]
        canvas, grid = atlas["canvas"], atlas["grid"]
        for key in ("width", "height"):
            integer(canvas[key], f"canvas.{key}", 1)
        for key in ("columns", "rows", "cellWidth", "cellHeight"):
            integer(grid[key], f"grid.{key}", 1)
        qa = contract.get("qa", {})
        if not isinstance(qa, dict) or not isinstance(qa.get("required", []), list):
            raise ContractError("qa.required must be a list")
        if not all(isinstance(name, str) and name for name in qa.get("required", [])):
            raise ContractError("qa.required entries must be names")
        if not isinstance(qa.get("thresholds", {}), dict):
            raise ContractError("qa.thresholds must be an object")
        anchor = atlas.get("anchor")
        if anchor is not None:
            if not isinstance(anchor, dict):
                raise ContractError("atlas.anchor must be an object")
            for key in ("x", "y"):
                val = anchor.get(key)
                if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val):
                    raise ContractError(f"anchor.{key} must be finite")
        for key in ("sourcePlaneY", "baselineY"):
            if key in atlas and (isinstance(atlas[key], bool) or not isinstance(atlas[key], (int, float)) or not math.isfinite(atlas[key])):
                raise ContractError(f"atlas.{key} must be finite")
        if "expectedBottomY" in atlas:
            integer(atlas["expectedBottomY"], "expectedBottomY")
        grounded = atlas.get("groundedFrames", [])
        if not isinstance(grounded, list):
            raise ContractError("groundedFrames must be a list of {row, column} objects")
        for entry in grounded:
            r, c = integer(entry["row"], "grounded row"), integer(entry["column"], "grounded column")
            if r >= grid["rows"] or c >= grid["columns"]:
                raise ContractError("grounded frame outside grid")
        animations = atlas.get("animations", {})
        if not isinstance(animations, dict):
            raise ContractError("atlas.animations must be an object")
        for name, anim in animations.items():
            if not isinstance(anim, dict):
                raise ContractError(f"Animation {name} must be an object")
            row = integer(anim["row"], "animation row")
            if row >= grid["rows"]:
                raise ContractError(f"Animation {name} row outside grid")
            if not isinstance(anim["frames"], list) or not anim["frames"]:
                raise ContractError(f"Animation {name} needs frame columns")
            if any(integer(c, "animation column") >= grid["columns"] for c in anim["frames"]):
                raise ContractError(f"Animation {name} column outside grid")
            fps = anim.get("fps")
            if isinstance(fps, bool) or not isinstance(fps, (int, float)) or not math.isfinite(fps) or fps <= 0:
                raise ContractError(f"Animation {name} fps must be positive")
            if not isinstance(anim.get("loop"), bool):
                raise ContractError(f"Animation {name} loop must be boolean")
        limit = qa.get("thresholds", {}).get("maximumAlpha1To7Pixels")
        if limit is not None:
            integer(limit, "maximumAlpha1To7Pixels")
        return contract
    except (KeyError, TypeError, AttributeError, json.JSONDecodeError) as error:
        raise ContractError(f"Malformed contract: {error}") from error


def required_inputs(contract: dict) -> list[str]:
    paths: list[str] = []

    def add(value):
        if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
            raise ContractError("Input paths must be batch-relative POSIX paths")
        if any(part in ("", ".", "..") for part in value.split("/")) or not value.startswith(("source/", "generated/", "manifests/", "qa/", "contracts/")):
            raise ContractError(f"Unsafe input path: {value}")
        paths.append(value)

    references = contract.get("references", [])
    if not isinstance(references, list):
        raise ContractError("references must be a list of {path, role} objects")
    for reference in references:
        if not isinstance(reference, dict) or not isinstance(reference.get("role"), str) or not reference["role"].strip():
            raise ContractError("Each reference requires a path and nonempty role")
        if set(reference).difference({"path", "role", "direction"}) or ("direction" in reference and (not isinstance(reference["direction"], str) or not reference["direction"].strip())):
            raise ContractError("Reference has invalid fields")
        add(reference.get("path"))
    required = contract.get("qa", {}).get("requiredInputs", [])
    if not isinstance(required, list):
        raise ContractError("qa.requiredInputs must be a list of paths")
    for value in required:
        add(value)
    reviews = contract.get("reviews", {})
    if not isinstance(reviews, dict):
        raise ContractError("reviews must be an object")
    for review in reviews.values():
        if not isinstance(review, dict):
            raise ContractError("Review entries must be objects")
        for key in ("required", "comparisonRequired"):
            if key in review and not isinstance(review[key], bool):
                raise ContractError(f"Review {key} must be boolean")
        for key in ("referencePath", "comparisonPath"):
            if review.get(key) is not None:
                add(review[key])
    return sorted(set(paths))


def alpha_measure(image: Image.Image) -> dict:
    alpha = image.getchannel("A")
    histogram = alpha.histogram()
    w, h = image.size
    return {"alphaBBox": list(alpha.getbbox()) if alpha.getbbox() else None,
            "cornerAlpha": [alpha.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))],
            "alpha1To7Pixels": sum(histogram[1:8]), "transparentPixels": histogram[0],
            "partialAlphaPixels": sum(histogram[1:255])}


def diff_pixels(first: bytes, second: bytes) -> int:
    return sum(first[i:i + 4] != second[i:i + 4] for i in range(0, len(first), 4))


def inspect(root: Path, contract_path: Path, image_path: Path, contract: dict, inputs: list[Path]) -> dict:
    checks: dict[str, dict] = {}
    manual: list[str] = []
    blockers: list[str] = []

    def check(name: str, passed: bool, details):
        checks[name] = {"status": "pass" if passed else "fail", "details": details}

    def unverified(name: str, details: str, blocks: bool = False):
        checks[name] = {"status": "manual", "details": details}
        manual.append(name)
        if blocks:
            blockers.append(name)

    checksums = [{"path": str(path.relative_to(root)), "sha256": digest(path) if path.is_file() else None} for path in inputs]
    check("inputs", all(record["sha256"] is not None for record in checksums), checksums)
    report = {"schemaVersion": 1, "kind": "spritemake-png-inspection", "assetId": contract["assetId"],
              "contractVersion": contract["version"], "contractSha256": digest(contract_path),
              "image": str(image_path.relative_to(root)), "candidateSha256": digest(image_path) if image_path.is_file() else None,
              "inputChecksums": checksums, "checks": checks, "requiredChecks": contract.get("qa", {}).get("required", []),
              "manualChecks": manual, "unverifiedRequiredChecks": blockers, "cells": [], "animations": {},
              "placementContract": {key: contract["atlas"].get(key) for key in ("anchor", "sourcePlaneY", "baselineY", "expectedBottomY", "groundedFrames")},
              "placementValidation": "unverified: pixels do not identify the intended contact anchor or source plane",
              "motionValidation": "unverified: frame differences do not establish correct gait or action"}
    atlas, qa = contract["atlas"], contract.get("qa", {})
    try:
        with Image.open(image_path) as source:
            source.load()
            check("png", source.format == "PNG", {"format": source.format})
            check("rgba", source.mode == "RGBA", {"mode": source.mode})
            image = source.convert("RGBA")
            w, h = image.size
            report["size"] = [w, h]
            canvas, grid = atlas["canvas"], atlas["grid"]
            cols, rows, cw, ch = (grid[k] for k in ("columns", "rows", "cellWidth", "cellHeight"))
            check("canvas", (w, h) == (canvas["width"], canvas["height"]), {"actual": [w, h], "expected": canvas})
            fits = (w, h) == (cols * cw, rows * ch)
            check("grid", fits and (canvas["width"], canvas["height"]) == (cols * cw, rows * ch),
                  {"grid": grid, "divisible": w % cols == 0 and h % rows == 0})
            report["alpha"] = alpha_measure(image)
            check("alpha", source.mode == "RGBA" and report["alpha"]["transparentPixels"] > 0 and not any(report["alpha"]["cornerAlpha"]),
                  {"meaning": "RGBA with transparent full-image corners and measurable transparency", **report["alpha"]})
            cell_images = {}
            if fits:
                for row in range(rows):
                    for col in range(cols):
                        cell = image.crop((col * cw, row * ch, (col + 1) * cw, (row + 1) * ch))
                        metrics = alpha_measure(cell)
                        box = metrics["alphaBBox"]
                        sides = [side for side, touch in zip(("left", "top", "right", "bottom"),
                                 (box and box[0] == 0, box and box[1] == 0, box and box[2] == cw, box and box[3] == ch)) if touch]
                        report["cells"].append({"row": row, "column": col, **metrics, "boundaryTouchSides": sides,
                                               "rgbaSha256": hashlib.sha256(cell.tobytes()).hexdigest()})
                        cell_images[row, col] = cell.tobytes()
            check("bbox", bool(report["alpha"]["alphaBBox"]) and fits and all(c["alphaBBox"] for c in report["cells"]),
                  "Full alpha bbox and a nonempty bbox for each declared cell; empty cells require a different contract")
            if fits:
                check("cellCornerAlpha", not any(any(cell["cornerAlpha"]) for cell in report["cells"]),
                      "All four corners of every declared cell must be transparent")
            report["boundaryEvidence"] = "Cell boundary touches are evidence only; absence does not prove one intended frame or no semantic bleed."
            for name, anim in atlas.get("animations", {}).items():
                if not fits:
                    report["animations"][name] = {"status": "unavailable", "reason": "grid mismatch"}
                    continue
                frames = [cell_images[anim["row"], col] for col in anim["frames"]]
                hashes = [hashlib.sha256(frame).hexdigest() for frame in frames]
                report["animations"][name] = {**anim, "frameHashes": hashes,
                    "duplicatePairs": [[i, j] for i in range(len(frames)) for j in range(i + 1, len(frames)) if hashes[i] == hashes[j]],
                    "adjacentDiffPixels": [diff_pixels(a, b) for a, b in zip(frames, frames[1:])],
                    "lastFirstDiffPixels": diff_pixels(frames[-1], frames[0]),
                    "interpretation": "Measurements only; repeated poses may be intentional holds and seam similarity is not a motion approval."}
            grounded, bottom = atlas.get("groundedFrames", []), atlas.get("expectedBottomY")
            if grounded and bottom is not None and fits:
                by_cell = {(c["row"], c["column"]): c for c in report["cells"]}
                measurements = [{**entry, "actualBottomY": (by_cell[entry["row"], entry["column"]]["alphaBBox"] or [0, 0, 0, 0])[3] - 1}
                                for entry in grounded]
                check("baseline", all(m["actualBottomY"] == bottom for m in measurements),
                      {"expectedBottomY": bottom, "coordinateMeaning": "inclusive lowest pixel with alpha > 0", "frames": measurements,
                       "limit": "Only explicitly grounded frames measured; this is not semantic contact validation"})
            else:
                unverified("baseline", "Requires placement review; no grounded frames were inferred. Optional atlas.groundedFrames [{row,column}] and expectedBottomY measure alpha bottoms only.")
            unverified("anchor", "Declared contact anchor preserved; human placement review must verify its meaning.")
            limit = qa.get("thresholds", {}).get("maximumAlpha1To7Pixels")
            if limit is not None:
                check("maximumAlpha1To7Pixels", report["alpha"]["alpha1To7Pixels"] <= limit,
                      {"actual": report["alpha"]["alpha1To7Pixels"], "maximum": limit})
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        check("imageReadable", False, str(error))
    for name in qa.get("required", []):
        if name not in checks:
            unverified(name, "Required check has no measurement implementation; needs a separate QA tool or review.", True)
    for name, value in qa.get("thresholds", {}).items():
        if value is not None and value != {} and name != "maximumAlpha1To7Pixels":
            unverified(name, "Threshold is not measured by this inspector; no halo or game-specific result is inferred.", True)
    failures = [name for name, value in checks.items() if value["status"] == "fail"]
    report["status"] = "fail" if failures else "pending" if blockers else "pass"
    report["pass"] = report["status"] == "pass"
    report["failedChecks"] = failures
    return report


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-root", required=True, type=Path)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", help="Batch-relative or absolute qa/ report path; defaults to qa/<assetId>-inspection.json")
    parser.add_argument("--status", help="Optional fresh unapproved status under qa/")
    args = parser.parse_args(argv)
    try:
        root = args.batch_root.resolve()
        contract_path = local_path(root, args.contract)
        contract = load_contract(contract_path)
        image_path = local_path(root, args.image, ("generated",))
        asset_slug = re.sub(r"[^A-Za-z0-9._-]+", "-", contract["assetId"]).strip(".-") or "asset"
        output = local_path(root, args.output or f"qa/{asset_slug}-inspection.json", ("qa",))
        status_path = local_path(root, args.status, ("qa",)) if args.status else None
        inputs = [local_path(root, str(root / value), ("source", "generated", "manifests", "qa", "contracts")) for value in required_inputs(contract)]
        immutable = {contract_path, image_path, *inputs}
        if output in immutable or status_path in immutable or status_path == output:
            raise ContractError("Report/status paths must not overwrite inputs or each other")
        report = inspect(root, contract_path, image_path, contract, inputs)
        status = None
        if status_path:
            status = {"schemaVersion": 1, "assetId": contract["assetId"], "contractVersion": contract["version"],
                "candidate": {"path": report["image"], "sha256": report["candidateSha256"], "provenance": "unverified"},
                "qa": {"status": report["status"], "reportPath": str(output.relative_to(root)),
                       "contractSha256": report["contractSha256"], "inputChecksums": report["inputChecksums"]},
                "reviews": {name: {"status": "pending", "required": bool(contract.get("reviews", {}).get(name, {}).get("required", False))}
                            for name in ("filenameContent", "style", "motion", "placement")},
                "promotion": {"eligible": False, "status": "candidate" if report["pass"] else "blocked"}}
            status["reviews"]["motion"]["required"] |= bool(contract["atlas"].get("animations"))
            status["reviews"]["placement"]["required"] |= bool({"anchor", "baseline"}.intersection(contract.get("qa", {}).get("required", [])))
        atomic_json(output, report)
        if status is not None:
            status["qa"]["reportSha256"] = digest(output)
            atomic_json(status_path, status)
        print(json.dumps({"status": report["status"], "report": str(output.relative_to(root)),
                          "failedChecks": report["failedChecks"], "manualChecks": report["manualChecks"]}, ensure_ascii=False))
        return 0 if report["pass"] else 1
    except (ContractError, OSError) as error:
        print(f"inspect_sprite: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
