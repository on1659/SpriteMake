"""Observable contracts for safe, deterministic sprite post-processing."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "tools/sprite_pipeline/run.py"
GATE = ROOT / "tools/runner/asset_gate.py"


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


class SpritePipelineTests(unittest.TestCase):
    def fixture(self, root: Path, scale=1):
        for name in ("source", "manifests", "contracts", "final"):
            (root / name).mkdir(parents=True)
        (root / "final/prior.png").write_bytes(b"existing production asset")
        for name, top, color in (("ground", 1, (255, 0, 0, 255)),
                                 ("air", 0, (0, 255, 0, 255))):
            image = Image.new("RGBA", (4, 4))
            image.paste(color, (1, top, 3, top + 2))
            image.save(root / f"source/{name}.png")
        cell = 8 * scale
        contract = {"schemaVersion": 1, "assetId": "hero", "version": 1,
            "target": {"finalPath": "final/hero.png"}, "references": [],
            "atlas": {"canvas": {"width": 2 * cell, "height": cell},
                "grid": {"columns": 2, "rows": 1, "cellWidth": cell, "cellHeight": cell},
                "anchor": {"x": 4 * scale, "y": 6 * scale, "meaning": "foot contact"},
                "sourcePlaneY": 6 * scale,
                "animations": {"idle": {"row": 0, "frames": [0, 1], "fps": 8, "loop": True}}},
            "qa": {"required": ["canvas", "grid", "alpha", "bbox", "anchor", "baseline"],
                "requiredInputs": [], "thresholds": {"maximumAlpha1To7Pixels": 0}},
            "reviews": {"filenameContent": {"required": True}, "placement": {"required": True},
                "motion": {"required": True}, "style": {"required": False}}}
        recipe = {"schemaVersion": 1, "contract": "contracts/hero.json", "scale": scale,
            "frames": [{"path": f"source/{name}.png", "row": 0, "column": column,
                        "sourceAnchor": [2, 3], "offset": [0, 0]}
                       for column, name in enumerate(("ground", "air"))]}
        write_json(root / "contracts/hero.json", contract)
        write_json(root / "manifests/hero.recipe.json", recipe)
        return contract, recipe

    def cli(self, root, command, *args):
        return subprocess.run([sys.executable, str(PIPELINE), command, "--batch-root", str(root), *map(str, args)],
                              text=True, capture_output=True, timeout=30)

    def bake(self, root, attempt="one", recipe="manifests/hero.recipe.json"):
        return self.cli(root, "bake", "--recipe", recipe, "--attempt", attempt)

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_failed_without_writes(self, root, result, before):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(snapshot(root), before, "Rejected input published or changed an artifact")

    def ops(self):
        spec = importlib.util.spec_from_file_location("sprite_pipeline_image_ops", PIPELINE.with_name("image_ops.py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def runner(self):
        spec = importlib.util.spec_from_file_location("sprite_pipeline_orchestration_tests", PIPELINE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_exact_recolor_preserves_alpha_and_does_not_cascade(self):
        image = Image.new("RGBA", (5, 1))
        image.putdata([(255, 0, 0, 255), (0, 255, 0, 128), (255, 0, 0, 7),
                       (255, 0, 0, 0), (254, 0, 0, 255)])
        before = image.tobytes()
        changed, _ = self.ops().recolor(image, {"map": {"#ff0000": "#00ff00", "#00ff00": "#0000ff"},
            "match": "exact", "tolerance": 0, "alphaThreshold": 8})
        self.assertEqual([changed.getpixel((x, 0)) for x in range(5)], [(0, 255, 0, 255), (0, 0, 255, 128),
            (255, 0, 0, 7), (255, 0, 0, 0), (254, 0, 0, 255)])
        self.assertEqual(image.tobytes(), before)

    def test_components_filter_noise_and_do_not_merge_separate_frames(self):
        image = Image.new("RGBA", (12, 8))
        image.paste((255, 0, 0, 255), (1, 1, 3, 4))
        image.paste((0, 255, 0, 255), (7, 2, 10, 5))
        image.putpixel((11, 7), (0, 0, 255, 255))
        rects = self.ops().extract_components(image, minimum_pixels=2)
        self.assertEqual(sorted(map(tuple, rects)), [(1, 1, 2, 3), (7, 2, 3, 3)])

    def test_palette_and_components_cli_report_pixels_without_mutating_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            source = root / "source/ground.png"
            before = source.read_bytes()
            self.assert_success(self.cli(root, "palette", "--image", "source/ground.png", "--output", "qa/palette.json"))
            palette = read_json(root / "qa/palette.json")
            self.assertEqual(palette["kind"], "spritemake-palette")
            self.assertEqual(palette["colorCount"], 1)
            self.assertEqual(palette["colors"], [{"hex": "#ff0000", "pixels": 4}])
            self.assert_success(self.cli(root, "components", "--image", "source/ground.png", "--output", "qa/components.json",
                                         "--minimum-pixels", "2"))
            components = read_json(root / "qa/components.json")
            self.assertEqual(components["kind"], "spritemake-components")
            self.assertEqual(components["rects"], [[1, 1, 2, 2]])
            self.assertEqual(components["sha256"], sha(source))
            self.assertEqual(source.read_bytes(), before)

    def test_analysis_commands_reject_final_outputs_and_source_overwrite(self):
        for command in ("palette", "components"):
            for output in ("final/prior.png", "source/ground.png", "qa/../../escaped.json"):
                with self.subTest(command=command, output=output), tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    self.fixture(root)
                    before = snapshot(root)
                    self.assert_failed_without_writes(root, self.cli(root, command, "--image", "source/ground.png",
                                                                     "--output", output), before)

    def test_bake_preserves_shared_scale_air_height_and_input_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root, scale=2)
            before = snapshot(root)
            self.assert_success(self.bake(root))
            with Image.open(root / "generated/one/hero.png") as image:
                self.assertEqual(image.mode, "RGBA")
                self.assertEqual(image.size, (32, 16))
                ground = image.crop((0, 0, 16, 16))
                air = image.crop((16, 0, 32, 16))
                self.assertEqual(ground.getbbox(), (6, 8, 10, 12))
                self.assertEqual(air.getbbox(), (6, 6, 10, 10))
                self.assertEqual(ground.getpixel((6, 8)), (255, 0, 0, 255))
                self.assertEqual(air.getpixel((6, 6)), (0, 255, 0, 255))
                self.assertEqual(image.getpixel((0, 0))[3], 0)
            for name, data in before.items():
                self.assertEqual((root / name).read_bytes(), data, name)
            self.assertFalse((root / "final/hero.png").exists())

    def test_repeated_bakes_have_identical_pixels_and_png_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            self.assert_success(self.bake(root, "first"))
            self.assert_success(self.bake(root, "second"))
            self.assertEqual((root / "generated/first/hero.png").read_bytes(),
                             (root / "generated/second/hero.png").read_bytes())

    def test_explicit_source_anchor_outside_crop_preserves_airborne_height(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, recipe = self.fixture(root)
            for frame in recipe["frames"]:
                frame["sourceAnchor"] = [2, 5]
            write_json(root / "manifests/hero.recipe.json", recipe)
            self.assert_success(self.bake(root))
            with Image.open(root / "generated/one/hero.png") as image:
                self.assertEqual(image.crop((0, 0, 8, 8)).getbbox(), (3, 2, 5, 4))
                self.assertEqual(image.crop((8, 0, 16, 8)).getbbox(), (3, 1, 5, 3))

    def test_chroma_then_recolor_keeps_transparency_and_source_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, recipe = self.fixture(root)
            image = Image.new("RGBA", (4, 4), (255, 0, 255, 255))
            image.paste((255, 0, 0, 128), (1, 1, 3, 3))
            image.save(root / "source/ground.png")
            recipe["chroma"] = {"key": "#ff00ff", "tolerance": 0, "despill": False}
            recipe["recolor"] = {"map": {"#ff0000": "#0000ff"}, "match": "exact", "alphaThreshold": 8}
            write_json(root / "manifests/hero.recipe.json", recipe)
            before = (root / "source/ground.png").read_bytes()
            self.assert_success(self.bake(root))
            with Image.open(root / "generated/one/hero.png") as result:
                self.assertEqual(result.crop((0, 0, 8, 8)).getbbox(), (3, 4, 5, 6))
                self.assertEqual(result.getpixel((3, 4)), (0, 0, 255, 128))
                self.assertEqual(result.getpixel((2, 3))[3], 0)
            self.assertEqual((root / "source/ground.png").read_bytes(), before)

    def test_bake_publishes_bound_contract_pending_reviews_and_offline_tools(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            self.assert_success(self.bake(root))
            derived = root / "contracts/one/hero.json"
            status = read_json(root / "qa/one/asset-status.json")
            self.assertEqual(status["qa"]["contractSha256"], sha(derived))
            self.assertEqual(status["candidate"]["sha256"], sha(root / "generated/one/hero.png"))
            self.assertEqual(status["candidate"]["path"], "generated/one/hero.png")
            self.assertFalse(status["promotion"]["eligible"])
            self.assertTrue(status["reviews"])
            self.assertTrue(all(r["status"] == "pending" for r in status["reviews"].values()))
            bound = {r["path"]: r["sha256"] for r in status["qa"]["inputChecksums"]}
            for path in ("source/ground.png", "source/air.png", "manifests/hero.recipe.json",
                         "contracts/hero.json", "manifests/one/hero.json"):
                self.assertEqual(bound.get(path), sha(root / path), path)
            for name in ("animation-preview.html", "curation.html"):
                html = (root / "tools/one" / name).read_text(encoding="utf-8")
                self.assertIn("data:image/png;base64,", html)
                self.assertNotIn("https://cdn.", html)

    def test_existing_attempt_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            self.assert_success(self.bake(root))
            before = snapshot(root)
            self.assert_failed_without_writes(root, self.bake(root), before)

    def test_invalid_frames_and_contract_fail_without_partial_artifacts(self):
        changes = {
            "clipped": lambda c, r: r["frames"][0].update(offset=[-100, 0]),
            "duplicate cell": lambda c, r: r["frames"][1].update(column=0),
            "missing cell": lambda c, r: r["frames"].pop(),
            "outside cell": lambda c, r: r["frames"][1].update(column=2),
            "bad rect": lambda c, r: r["frames"][0].update(rect=[0, 0, 0, 4]),
            "outside rect": lambda c, r: r["frames"][0].update(rect=[3, 0, 4, 4]),
            "bad scale": lambda c, r: r.update(scale=0),
            "per frame scale": lambda c, r: r["frames"][1].update(scale=2),
            "nan offset": lambda c, r: r["frames"][0].update(offset=[float("nan"), 0]),
            "fractional column": lambda c, r: r["frames"][0].update(column=0.5),
            "mismatched canvas": lambda c, r: c["atlas"]["canvas"].update(width=17),
            "unsafe final target": lambda c, r: c["target"].update(finalPath="../escaped.png"),
        }
        for label, change in changes.items():
            with self.subTest(case=label), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                contract, recipe = self.fixture(root)
                change(contract, recipe)
                write_json(root / "contracts/hero.json", contract)
                write_json(root / "manifests/hero.recipe.json", recipe)
                before = snapshot(root)
                self.assert_failed_without_writes(root, self.bake(root), before)

    def test_blank_frame_and_malformed_json_fail_without_writes(self):
        for kind in ("blank", "malformed", "array"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                self.fixture(root)
                if kind == "blank":
                    Image.new("RGBA", (4, 4)).save(root / "source/air.png")
                elif kind == "malformed":
                    (root / "manifests/hero.recipe.json").write_text("{ broken")
                else:
                    write_json(root / "manifests/hero.recipe.json", [])
                before = snapshot(root)
                self.assert_failed_without_writes(root, self.bake(root), before)

    def test_source_path_traversal_and_final_inputs_are_rejected(self):
        for name in ("source/../source/ground.png", "../outside.png", "/tmp/outside.png",
                     "source//ground.png", "source\\ground.png", "final/prior.png"):
            with self.subTest(path=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                _, recipe = self.fixture(root)
                recipe["frames"][0]["path"] = name
                write_json(root / "manifests/hero.recipe.json", recipe)
                before = snapshot(root)
                self.assert_failed_without_writes(root, self.bake(root), before)

    def test_symlink_source_and_output_directories_are_rejected(self):
        for kind in ("source file", "source parent", "generated parent"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / "batch"
                root.mkdir()
                _, recipe = self.fixture(root)
                outside = Path(temp) / "outside"
                outside.mkdir()
                if kind == "source file":
                    (outside / "ground.png").write_bytes((root / "source/ground.png").read_bytes())
                    (root / "source/ground.png").unlink()
                    (root / "source/ground.png").symlink_to(outside / "ground.png")
                elif kind == "source parent":
                    (outside / "ground.png").write_bytes((root / "source/ground.png").read_bytes())
                    (root / "source/link").symlink_to(outside, target_is_directory=True)
                    recipe["frames"][0]["path"] = "source/link/ground.png"
                    write_json(root / "manifests/hero.recipe.json", recipe)
                else:
                    (root / "generated").symlink_to(outside, target_is_directory=True)
                before, external_before = snapshot(root), snapshot(outside)
                self.assert_failed_without_writes(root, self.bake(root), before)
                self.assertEqual(snapshot(outside), external_before)

    def test_attempt_names_cannot_escape_into_final_or_parent(self):
        for attempt in ("../final", "x/y", "..", "/tmp/escaped", "final/hero"):
            with self.subTest(attempt=attempt), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                self.fixture(root)
                before = snapshot(root)
                self.assert_failed_without_writes(root, self.bake(root, attempt), before)

    def test_approved_status_is_invalidated_by_changed_source_recipe_manifest_or_contract(self):
        for path in ("source/ground.png", "manifests/hero.recipe.json", "manifests/one/hero.json", "contracts/hero.json"):
            with self.subTest(changed=path), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                self.fixture(root)
                self.assert_success(self.bake(root))
                status_path = root / "qa/one/asset-status.json"
                status = read_json(status_path)
                self.assertEqual(status["qa"]["status"], "pass")
                for review in status["reviews"].values():
                    review["status"] = "approved"
                write_json(status_path, status)
                changed = root / path
                changed.write_bytes(changed.read_bytes() + b"\nchanged")
                result = subprocess.run([sys.executable, str(GATE), "promote", "--batch-root", str(root),
                    "--contract", str(root / "contracts/one/hero.json"), "--status", str(status_path)],
                    text=True, capture_output=True, timeout=30)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("checksum changed", result.stdout + result.stderr)
                self.assertFalse((root / "final/hero.png").exists())
                self.assertEqual((root / "final/prior.png").read_bytes(), b"existing production asset")

    def test_source_change_during_inspection_rolls_back_every_attempt_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            before = snapshot(root)
            runner = self.runner()
            original_inspect = runner.inspector.main
            seen_candidate = []

            def change_source_then_inspect(argv):
                with Image.open(root / "generated/one/hero.png") as candidate:
                    seen_candidate.append(candidate.getpixel((3, 4)))
                source_path = root / "source/ground.png"
                with Image.open(source_path) as source:
                    changed = source.convert("RGBA")
                changed.paste((0, 0, 255, 255), (1, 1, 3, 3))
                changed.save(source_path)
                before["source/ground.png"] = source_path.read_bytes()
                return original_inspect(argv)

            with mock.patch.object(runner.inspector, "main", side_effect=change_source_then_inspect):
                with self.assertRaisesRegex(ValueError, "Input changed"):
                    runner.bake(root, "manifests/hero.recipe.json", "one")
            self.assertEqual(seen_candidate, [(255, 0, 0, 255)])
            self.assertEqual(snapshot(root), before)
            for folder in ("generated", "manifests", "contracts", "qa", "tools"):
                self.assertFalse((root / folder / "one").exists(), folder)
            self.assertFalse((root / "final/hero.png").exists())

    def test_recipe_and_contract_changes_after_parsing_are_rejected_before_publication(self):
        for name in ("manifests/hero.recipe.json", "contracts/hero.json"):
            with self.subTest(path=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                self.fixture(root)
                before = snapshot(root)
                runner = self.runner()
                original_inputs = runner.recipe_inputs

                def change_parsed_input(*args):
                    result = original_inputs(*args)
                    path = root / name
                    data = read_json(path)
                    if name.startswith("manifests/"):
                        data["scale"] = 0.5
                    else:
                        data["atlas"]["anchor"]["x"] = 5
                    write_json(path, data)
                    before[name] = path.read_bytes()
                    return result

                with mock.patch.object(runner, "recipe_inputs", side_effect=change_parsed_input):
                    with self.assertRaisesRegex(ValueError, "changed"):
                        runner.bake(root, "manifests/hero.recipe.json", "one")
                self.assertEqual(snapshot(root), before)

    def test_bake_preserves_explicit_motion_review_for_contract_without_animations(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contract, _ = self.fixture(root)
            contract["atlas"]["animations"] = {}
            contract["reviews"]["motion"]["required"] = True
            write_json(root / "contracts/hero.json", contract)
            self.assert_success(self.bake(root))
            derived_path = root / "contracts/one/hero.json"
            self.assertTrue(read_json(derived_path)["reviews"]["motion"]["required"])
            status_path = root / "qa/one/asset-status.json"
            status = read_json(status_path)
            for name in ("filenameContent", "placement"):
                status["reviews"][name]["status"] = "approved"
            self.assertEqual(status["reviews"]["motion"]["status"], "pending")
            write_json(status_path, status)
            result = subprocess.run([sys.executable, str(GATE), "promote", "--batch-root", str(root),
                "--contract", str(derived_path), "--status", str(status_path)],
                text=True, capture_output=True, timeout=30)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("motion review is not approved", result.stdout + result.stderr)
            self.assertFalse((root / "final/hero.png").exists())
            self.assertEqual((root / "final/prior.png").read_bytes(), b"existing production asset")

    def upstream_fixture(self, root):
        contract, _ = self.fixture(root)
        sheet = Image.new("RGBA", (24, 16))
        sheet.paste((40, 80, 120, 255), (11, 5, 13, 8))
        sheet.save(root / "source/upstream.png")
        upstream = {"frame_layout": {"rows": {"idle": [
            {"x": 8, "y": 2, "w": 8, "h": 8}, {"x": 8, "y": 2, "w": 8, "h": 8}]}},
            "animation": {"rows": {"idle": {"fps": 8, "loop": True, "durations_ms": [125, 125]}}}}
        write_json(root / "source/upstream.json", upstream)
        return upstream

    def import_upstream(self, root, output="manifests/imported.recipe.json"):
        return self.cli(root, "import-upstream", "--atlas", "source/upstream.png", "--manifest", "source/upstream.json",
                        "--contract", "contracts/hero.json", "--output", output)

    def test_import_absolute_rects_repack_duplicate_entries_into_separate_cells(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.upstream_fixture(root)
            before = (root / "source/upstream.png").read_bytes()
            self.assert_success(self.import_upstream(root))
            recipe = read_json(root / "manifests/imported.recipe.json")
            self.assertEqual([f["rect"] for f in recipe["frames"]], [[8, 2, 8, 8], [8, 2, 8, 8]])
            self.assertEqual({(f["row"], f["column"]) for f in recipe["frames"]}, {(0, 0), (0, 1)})
            self.assert_success(self.bake(root, recipe="manifests/imported.recipe.json"))
            with Image.open(root / "generated/one/hero.png") as image:
                first, second = image.crop((0, 0, 8, 8)), image.crop((8, 0, 16, 8))
                self.assertEqual(first.tobytes(), second.tobytes())
                self.assertEqual(first.getbbox(), (3, 3, 5, 6))
            status = read_json(root / "qa/one/asset-status.json")
            bound = {record["path"]: record["sha256"] for record in status["qa"]["inputChecksums"]}
            for path in ("source/upstream.png", "source/upstream.json"):
                self.assertEqual(bound.get(path), sha(root / path), path)
            self.assertEqual((root / "source/upstream.png").read_bytes(), before)

    def test_import_rejects_nonuniform_timing_and_final_output_without_writes(self):
        for kind in ("timing", "final output", "rect outside", "missing state"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                upstream = self.upstream_fixture(root)
                output = "manifests/imported.recipe.json"
                if kind == "timing":
                    upstream["animation"]["rows"]["idle"]["durations_ms"] = [100, 150]
                elif kind == "final output":
                    output = "final/imported.recipe.json"
                elif kind == "rect outside":
                    upstream["frame_layout"]["rows"]["idle"][0]["x"] = 100
                else:
                    upstream["frame_layout"]["rows"] = {"walk": upstream["frame_layout"]["rows"]["idle"]}
                write_json(root / "source/upstream.json", upstream)
                before = snapshot(root)
                self.assert_failed_without_writes(root, self.import_upstream(root, output), before)


if __name__ == "__main__":
    unittest.main()
