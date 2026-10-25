#!/usr/bin/env python3
"""Offline sprite transforms, fixed-grid import, preview, and pending QA."""
from __future__ import annotations

import argparse
import base64
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))
from PIL import Image
from tools.runner import inspect_sprite as inspector
from tools.runner import asset_gate
from tools.sprite_pipeline import image_ops

PREFIXES = ("source", "generated", "manifests", "qa", "contracts")


def parse_json(raw, path):
    value = json.loads(raw.decode("utf-8-sig"), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"Invalid number {x}")))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path.name}")
    return value


def load(path):
    return parse_json(path.read_bytes(), path)


def local(root, value, prefixes=PREFIXES):
    if not isinstance(value, str) or "\\" in value or "\x00" in value or any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("Expected a batch-relative POSIX path without empty or traversal components")
    return inspector.local_path(root, value, prefixes)


def rel(root, path):
    return path.relative_to(root).as_posix()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    inspector.atomic_json(path, value)


def slug(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", value):
        raise ValueError(f"{label} must be 1-80 ASCII letters, digits, _ or -")
    return value


def data_url(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def recipe_inputs(root, recipe, recipe_path):
    if type(recipe.get("schemaVersion")) is not int or recipe["schemaVersion"] != 1:
        raise ValueError("Recipe schemaVersion must be 1")
    allowed = {"schemaVersion", "contract", "frames", "scale", "chroma", "recolor", "pixelGrid", "inputs", "provenance"}
    if set(recipe) - allowed:
        raise ValueError(f"Unsupported recipe fields: {sorted(set(recipe) - allowed)}")
    contract_path = local(root, recipe.get("contract"), ("contracts",))
    contract_bytes = contract_path.read_bytes()
    contract = inspector.load_contract(contract_path)
    if contract_path.read_bytes() != contract_bytes or contract != parse_json(contract_bytes, contract_path):
        raise ValueError("Contract changed while it was read; retry with unchanged inputs")
    asset_gate.relative_path(root, contract.get("target", {}).get("finalPath"), "final/")
    frames = recipe.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("Recipe frames must be a nonempty array")
    extra = recipe.get("inputs", [])
    if not isinstance(extra, list) or any(not isinstance(x, str) for x in extra):
        raise ValueError("Recipe inputs must be an array of paths")
    paths = {recipe_path, contract_path}
    for frame in frames:
        if not isinstance(frame, dict):
            raise ValueError("Frame must be an object")
        paths.add(local(root, frame.get("path"), ("source", "generated")))
    for value in extra + inspector.required_inputs(contract):
        paths.add(local(root, value))
    for path in paths:
        if not path.is_file():
            raise ValueError(f"Missing input: {rel(root, path)}")
    return contract_path, contract, sorted(paths), hashlib.sha256(contract_bytes).hexdigest()


def bake(root, recipe_value, attempt):
    root = root.resolve()
    attempt = slug(attempt, "attempt")
    recipe_path = local(root, recipe_value, ("manifests",))
    recipe_bytes = recipe_path.read_bytes()
    recipe = parse_json(recipe_bytes, recipe_path)
    contract_path, contract, inputs, loaded_contract_sha = recipe_inputs(root, recipe, recipe_path)
    asset = slug(contract["assetId"], "assetId")
    before = {path: sha(path) for path in inputs}
    if before[recipe_path] != hashlib.sha256(recipe_bytes).hexdigest() or before[contract_path] != loaded_contract_sha:
        raise ValueError("Recipe or contract changed during validation; retry with unchanged inputs")
    directories = {name: local(root, f"{name}/{attempt}", (name,))
                   for name in ("generated", "manifests", "contracts", "qa", "tools")}
    for directory in directories.values():
        if directory.exists():
            raise ValueError(f"Attempt already exists: {rel(root, directory)}; choose a new attempt")
    atlas, transform = image_ops.process_frames(root, recipe, contract)
    if not isinstance(atlas, Image.Image) or atlas.mode != "RGBA":
        raise ValueError("Processor must return an RGBA image")
    derived = deepcopy(contract)
    output_paths = {
        "image": f"generated/{attempt}/{asset}.png",
        "manifest": f"manifests/{attempt}/{asset}.json",
        "contract": f"contracts/{attempt}/{asset}.json",
        "transform": f"qa/{attempt}/transform.json",
        "report": f"qa/{attempt}/{asset}-report.json",
        "status": f"qa/{attempt}/asset-status.json",
    }
    required = {rel(root, path) for path in inputs}
    required.update((output_paths["manifest"], output_paths["transform"]))
    derived.setdefault("qa", {})["requiredInputs"] = sorted(required)
    derived["processing"] = {"recipe": rel(root, recipe_path), "attempt": attempt,
                             "originalContractSha256": before[contract_path],
                             "provenance": "local deterministic processing; source generation model unverified"}
    placement = derived.setdefault("reviews", {})
    placement.setdefault("placement", {})["required"] = True
    placement.setdefault("filenameContent", {})["required"] = True
    motion_review = placement.setdefault("motion", {})
    motion_review["required"] = bool(motion_review.get("required")) or bool(derived["atlas"].get("animations"))
    layout = derived["atlas"]
    manifest = {"sheets": {"main": {
        "label": asset, "image": f"../../{output_paths['image']}",
        "canvas": layout["canvas"], "cell": {"width": layout["grid"]["cellWidth"], "height": layout["grid"]["cellHeight"]},
        "grid": {"columns": layout["grid"]["columns"], "rows": layout["grid"]["rows"]},
        "anchor": {**layout["anchor"], "mode": "pixel"},
        "baselineY": layout.get("sourcePlaneY", layout.get("baselineY")),
        "animations": layout.get("animations") or {"still": {"row": 0, "frames": [0], "fps": 1, "loop": False}},
        "defaultScale": 2, "reviewNotes": {"placement": "pending", "motion": "pending"}
    }}}
    transform.update({"kind": "spritemake-transform", "schemaVersion": 1,
                      "inputs": [{"path": rel(root, p), "sha256": before[p]} for p in inputs],
                      "sourceGeneration": "unverified; processing does not select or verify a generation model"})
    published = []
    try:
        with tempfile.TemporaryDirectory(prefix=".sprite-pipeline-", dir=root) as temporary:
            staging = Path(temporary)
            for name in directories:
                (staging / name / attempt).mkdir(parents=True)
            atlas.save(staging / output_paths["image"], format="PNG")
            write_json(staging / output_paths["manifest"], manifest)
            write_json(staging / output_paths["contract"], derived)
            write_json(staging / output_paths["transform"], transform)
            from tools.sprite_pipeline.preview import build_tools
            images = {manifest["sheets"]["main"]["image"]: data_url(staging / output_paths["image"])}
            for frame in recipe["frames"]:
                images[frame["path"]] = data_url(local(root, frame["path"], ("source", "generated")))
            build_tools(root, recipe, derived, manifest, images, staging / "tools" / attempt)
            # Every input must still be the exact version that was processed.
            if any(not p.is_file() or sha(p) != value for p, value in before.items()):
                raise ValueError("Input changed during processing; retry with unchanged inputs")
            for name, directory in directories.items():
                directory.parent.mkdir(parents=True, exist_ok=True)
                if directory.exists():
                    raise ValueError("Attempt was created concurrently")
                os.rename(staging / name / attempt, directory)
                published.append(directory)
            result = inspector.main(["--batch-root", str(root), "--contract", output_paths["contract"],
                "--image", output_paths["image"], "--output", output_paths["report"], "--status", output_paths["status"]])
            if result == 2:
                raise ValueError("Inspector could not validate the exported candidate")
            status = load(root / output_paths["status"])
            measured_inputs = {record["path"]: record["sha256"] for record in status["qa"]["inputChecksums"]}
            if any(not p.is_file() or sha(p) != value or measured_inputs.get(rel(root, p)) != value for p, value in before.items()):
                raise ValueError("Input changed during inspection; attempt rolled back, retry with unchanged inputs")
            status["candidate"]["provenance"] = "local deterministic processing; source generation unverified"
            write_json(root / output_paths["status"], status)
        return {"attempt": attempt, **output_paths, "qaStatus": status["qa"]["status"],
                "preview": f"tools/{attempt}/animation-preview.html", "curation": f"tools/{attempt}/curation.html",
                "promotion": "pending human review"}
    except BaseException:
        for directory in reversed(published):
            shutil.rmtree(directory)
        raise


def import_upstream(root, atlas_value, manifest_value, contract_value, output_value):
    root = root.resolve()
    atlas_path = local(root, atlas_value, ("source", "generated"))
    source_manifest = local(root, manifest_value, ("source", "manifests", "generated"))
    contract_path = local(root, contract_value, ("contracts",))
    output = local(root, output_value, ("manifests",))
    if output.exists() or output in (atlas_path, source_manifest, contract_path):
        raise ValueError("Import output must be a new manifest recipe")
    upstream = load(source_manifest)
    contract = inspector.load_contract(contract_path)
    rows = upstream.get("frame_layout", {}).get("rows")
    timing = upstream.get("animation", {}).get("rows")
    animations = contract["atlas"].get("animations", {})
    if not isinstance(rows, dict) or not isinstance(timing, dict) or set(rows) != set(animations):
        raise ValueError("Upstream states must exactly match contract animations")
    frames, used = [], set()
    cw, ch = (contract["atlas"]["grid"][key] for key in ("cellWidth", "cellHeight"))
    anchor = contract["atlas"]["anchor"]
    with Image.open(atlas_path) as image:
        width, height = image.size
        for name, animation in animations.items():
            rects, source_timing = rows[name], timing.get(name)
            if not isinstance(rects, list) or len(rects) != len(animation["frames"]) or not isinstance(source_timing, dict):
                raise ValueError(f"State frame count/timing mismatch: {name}")
            fps = source_timing.get("fps")
            if isinstance(fps, bool) or not isinstance(fps, (float, int)) or not math.isfinite(fps) or fps <= 0:
                raise ValueError(f"Invalid upstream fps: {name}")
            if fps != animation["fps"] or source_timing.get("loop") is not animation["loop"]:
                raise ValueError(f"Timing differs from contract: {name}")
            durations = source_timing.get("durations_ms")
            if durations is not None:
                if not isinstance(durations, list) or len(durations) != len(rects) or any(type(d) not in (int, float) or not math.isfinite(d) or d <= 0 for d in durations):
                    raise ValueError(f"Invalid upstream durations: {name}")
                if len(set(durations)) != 1 or abs(durations[0] - 1000 / fps) > 1:
                    raise ValueError("Variable or inconsistent durations need an explicit timing contract")
            for rect, column in zip(rects, animation["frames"]):
                if not isinstance(rect, dict) or any(type(rect.get(key)) is not int for key in ("x", "y", "w", "h")):
                    raise ValueError("Invalid frame rectangle")
                x, y, w, h = (rect[key] for key in ("x", "y", "w", "h"))
                if (w, h) != (cw, ch) or x < 0 or y < 0 or x + w > width or y + h > height:
                    raise ValueError("Import requires complete source cells matching the target cell size")
                cell = (animation["row"], column)
                if cell in used:
                    raise ValueError("Animations must not assign the same target cell twice")
                used.add(cell)
                frames.append({"path": rel(root, atlas_path), "rect": [x, y, w, h],
                    "row": cell[0], "column": cell[1], "sourceAnchor": [anchor["x"], anchor["y"]], "offset": [0, 0]})
    grid = contract["atlas"]["grid"]
    if len(used) != grid["columns"] * grid["rows"]:
        raise ValueError("Contract must assign every fixed cell; supply an explicit recipe for padding holds")
    recipe = {"schemaVersion": 1, "contract": rel(root, contract_path), "scale": 1,
              "frames": frames, "inputs": [rel(root, source_manifest)],
              "provenance": {"kind": "sprite-gen-frame-layout-import", "source": rel(root, source_manifest)}}
    write_json(output, recipe)
    return {"recipe": rel(root, output), "frames": len(frames), "status": "ready to bake; unverified"}


def utility(root, command, image_value, output_value, minimum_pixels=1):
    root = root.resolve()
    path = local(root, image_value, ("source", "generated"))
    output = local(root, output_value, ("qa",))
    if output.exists():
        raise ValueError("Report output must be a new qa/ file")
    with Image.open(path) as source:
        image = source.convert("RGBA")
    if command == "components":
        if minimum_pixels < 1:
            raise ValueError("minimum-pixels must be positive")
        report = {"kind": "spritemake-components", "rects": image_ops.extract_components(image, minimum_pixels),
                  "warning": "Components are pixel regions; review grouping and detached accessories before slicing"}
    else:
        counts = {}
        for r, g, b, a in image.getdata():
            if a > 8:
                color = f"#{r:02x}{g:02x}{b:02x}"
                counts[color] = counts.get(color, 0) + 1
        ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        report = {"kind": "spritemake-palette", "alphaThreshold": 8, "colorCount": len(counts),
                  "colors": [{"hex": color, "pixels": count} for color, count in ordered[:256]],
                  "omittedColors": max(0, len(ordered) - 256),
                  "map": {color: color for color, count in ordered[:256]}}
    report.update({"source": rel(root, path), "sha256": sha(path)})
    write_json(output, report)
    return {"report": rel(root, output)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    bake_parser = commands.add_parser("bake", help="Create a new candidate attempt with QA and offline tools")
    bake_parser.add_argument("--recipe", required=True)
    bake_parser.add_argument("--attempt", required=True)
    upstream = commands.add_parser("import-upstream", help="Expand sprite-gen absolute rects into fixed cells")
    upstream.add_argument("--atlas", required=True)
    upstream.add_argument("--manifest", required=True)
    upstream.add_argument("--contract", required=True)
    upstream.add_argument("--output", required=True)
    for name in ("palette", "components"):
        p = commands.add_parser(name)
        p.add_argument("--image", required=True)
        p.add_argument("--output", required=True)
        if name == "components":
            p.add_argument("--minimum-pixels", type=int, default=1)
    for sub in (bake_parser, upstream, *[commands.choices[name] for name in ("palette", "components")]):
        sub.add_argument("--batch-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "bake":
            result = bake(args.batch_root, args.recipe, args.attempt)
        elif args.command == "import-upstream":
            result = import_upstream(args.batch_root, args.atlas, args.manifest, args.contract, args.output)
        else:
            result = utility(args.batch_root, args.command, args.image, args.output, getattr(args, "minimum_pixels", 1))
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, Image.DecompressionBombError) as error:
        print(f"sprite_pipeline: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
