from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("inspect_sprite", ROOT / "tools/runner/inspect_sprite.py")
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)


class InspectSpriteTests(unittest.TestCase):
    def fixture(self, root, mode="RGBA", size=(16, 8)):
        (root / "generated").mkdir()
        (root / "qa").mkdir()
        (root / "source").mkdir()
        reference = root / "source/reference.txt"
        reference.write_text("reference")
        image = Image.new(mode, size)
        for offset in (0, 8):
            for x in range(offset + 2, min(offset + 5, size[0])):
                for y in range(2, min(6, size[1])):
                    image.putpixel((x, y), (255, 0, 0, 255) if mode == "RGBA" else (255, 0, 0))
        image_path = root / "generated/candidate.png"
        image.save(image_path)
        contract = {"schemaVersion": 1, "assetId": "example", "version": 1,
            "atlas": {"canvas": {"width": 16, "height": 8},
                      "grid": {"columns": 2, "rows": 1, "cellWidth": 8, "cellHeight": 8},
                      "anchor": {"x": 4, "y": 6, "meaning": "foot"}, "sourcePlaneY": 6,
                      "animations": {"idle": {"row": 0, "frames": [0, 1], "fps": 8, "loop": True}}},
            "qa": {"required": ["canvas", "grid", "alpha", "bbox", "anchor", "baseline"],
                   "thresholds": {"maximumAlpha1To7Pixels": 0}, "requiredInputs": ["source/reference.txt"]},
            "reviews": {"filenameContent": {"required": True}, "style": {"required": False}}}
        contract_path = root / "contract.json"
        contract_path.write_text(json.dumps(contract))
        return contract, image_path, contract_path

    def run_inspect(self, root):
        code = inspector.main(["--batch-root", str(root), "--contract", "contract.json", "--image", "generated/candidate.png",
                               "--output", "qa/report.json", "--status", "qa/status.json"])
        return code, json.loads((root / "qa/report.json").read_text()), json.loads((root / "qa/status.json").read_text())

    def test_measurements_duplicates_and_unapproved_status_preserve_input(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, image, _ = self.fixture(root)
            before, mtime = image.read_bytes(), image.stat().st_mtime_ns
            code, report, status = self.run_inspect(root)
            self.assertEqual(code, 0)
            self.assertEqual(report["cells"][0]["alphaBBox"], [2, 2, 5, 6])
            self.assertEqual(report["animations"]["idle"]["duplicatePairs"], [[0, 1]])
            self.assertEqual(report["animations"]["idle"]["lastFirstDiffPixels"], 0)
            self.assertEqual(report["checks"]["anchor"]["status"], "manual")
            self.assertEqual(report["checks"]["baseline"]["status"], "manual")
            self.assertFalse(status["promotion"]["eligible"])
            self.assertTrue(all(review["status"] == "pending" for review in status["reviews"].values()))
            self.assertEqual(status["qa"]["reportSha256"], hashlib.sha256((root / "qa/report.json").read_bytes()).hexdigest())
            self.assertEqual(status["qa"]["inputChecksums"], [{"path": "source/reference.txt", "sha256": hashlib.sha256(b"reference").hexdigest()}])
            self.assertTrue(status["reviews"]["motion"]["required"])
            self.assertTrue(status["reviews"]["placement"]["required"])
            self.assertEqual(image.read_bytes(), before)
            self.assertEqual(image.stat().st_mtime_ns, mtime)

    def test_structural_failure_rgb_and_alpha_threshold(self):
        for mode, size, expected in [("RGBA", (17, 8), "canvas"), ("RGB", (16, 8), "rgba")]:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                self.fixture(root, mode, size)
                code, report, _ = self.run_inspect(root)
                self.assertEqual(code, 1)
                self.assertIn(expected, report["failedChecks"])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, path, _ = self.fixture(root)
            with Image.open(path) as source:
                image = source.copy()
            image.putpixel((6, 6), (250, 0, 250, 4))
            image.save(path)
            code, report, _ = self.run_inspect(root)
            self.assertEqual(code, 1)
            self.assertEqual(report["alpha"]["alpha1To7Pixels"], 1)

    def test_jump_not_automatically_grounded_and_explicit_subset_measured(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contract, path, contract_path = self.fixture(root)
            with Image.open(path) as source:
                image = source.copy()
            image.paste(Image.new("RGBA", (8, 8)), (8, 0))
            image.paste(Image.new("RGBA", (3, 2), (255, 0, 0, 255)), (10, 1))
            image.save(path)
            code, report, _ = self.run_inspect(root)
            self.assertEqual(code, 0)
            self.assertEqual(report["checks"]["baseline"]["status"], "manual")
            contract["atlas"].update(expectedBottomY=5, groundedFrames=[{"row": 0, "column": 0}])
            contract_path.write_text(json.dumps(contract))
            code, report, _ = self.run_inspect(root)
            self.assertEqual(code, 0)
            self.assertEqual(report["checks"]["baseline"]["status"], "pass")
            contract["atlas"]["groundedFrames"].append({"row": 0, "column": 1})
            contract_path.write_text(json.dumps(contract))
            code, report, _ = self.run_inspect(root)
            self.assertEqual(code, 1)
            self.assertIn("baseline", report["failedChecks"])

    def test_unknown_required_check_and_halo_threshold_never_fabricated(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contract, _, path = self.fixture(root)
            contract["qa"]["required"].append("gaitAlternation")
            contract["qa"]["thresholds"]["maximumHaloPixels"] = 0
            path.write_text(json.dumps(contract))
            code, report, _ = self.run_inspect(root)
            self.assertEqual(code, 1)
            self.assertEqual(report["status"], "pending")
            self.assertEqual(report["checks"]["maximumHaloPixels"]["status"], "manual")
            self.assertIn("gaitAlternation", report["unverifiedRequiredChecks"])

    def test_bom_whitespace_and_contract_change_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contract, _, path = self.fixture(root)
            path.write_text("\ufeff \r\n" + json.dumps(contract), encoding="utf-8")
            code, report, _ = self.run_inspect(root)
            self.assertEqual(code, 0)
            self.assertEqual(report["contractSha256"], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_malformed_contract_and_unsafe_paths_preserve_prior_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contract, _, path = self.fixture(root)
            self.run_inspect(root)
            report = (root / "qa/report.json").read_bytes()
            status = (root / "qa/status.json").read_bytes()
            for mutate in (lambda c: c["atlas"]["grid"].update(columns=0),
                           lambda c: c["qa"].update(requiredInputs=["../escaped.txt"])):
                broken = json.loads(json.dumps(contract))
                mutate(broken)
                path.write_text(json.dumps(broken))
                self.assertEqual(inspector.main(["--batch-root", str(root), "--contract", "contract.json", "--image", "generated/candidate.png",
                                                 "--output", "qa/report.json", "--status", "qa/status.json"]), 2)
                self.assertEqual((root / "qa/report.json").read_bytes(), report)
                self.assertEqual((root / "qa/status.json").read_bytes(), status)

    def test_reference_digest_changes_and_symlinks_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contract, _, path = self.fixture(root)
            contract["references"] = [{"path": "source/reference.txt", "role": "identity", "direction": "south"}]
            path.write_text(json.dumps(contract))
            _, first, _ = self.run_inspect(root)
            (root / "source/reference.txt").write_text("changed reference")
            _, second, _ = self.run_inspect(root)
            self.assertNotEqual(first["inputChecksums"], second["inputChecksums"])
            report_bytes = (root / "qa/report.json").read_bytes()
            (root / "source/alias.txt").symlink_to(root / "source/reference.txt")
            contract["references"][0]["path"] = "source/alias.txt"
            path.write_text(json.dumps(contract))
            self.assertEqual(inspector.main(["--batch-root", str(root), "--contract", "contract.json", "--image", "generated/candidate.png", "--output", "qa/report.json"]), 2)
            self.assertEqual((root / "qa/report.json").read_bytes(), report_bytes)

    def test_cwd_relative_cli_paths_inside_batch(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            root = project / "output/example"
            root.mkdir(parents=True)
            self.fixture(root)
            previous = Path.cwd()
            try:
                os.chdir(project)
                self.assertEqual(inspector.main(["--batch-root", "output/example", "--contract", "output/example/contract.json",
                    "--image", "output/example/generated/candidate.png", "--output", "output/example/qa/report.json"]), 0)
            finally:
                os.chdir(previous)
            self.assertTrue((root / "qa/report.json").is_file())

    def test_absolute_root_alias_preserves_descendant_symlink_rejection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            self.assertEqual(inspector.local_path(root.resolve(), str(root / "generated/candidate.png"), ("generated",)),
                             (root / "generated/candidate.png").resolve())
            (root / "source/backlink").symlink_to(root, target_is_directory=True)
            with self.assertRaises(inspector.ContractError):
                inspector.local_path(root.resolve(), str(root / "source/backlink/generated/candidate.png"))


if __name__ == "__main__":
    unittest.main()
