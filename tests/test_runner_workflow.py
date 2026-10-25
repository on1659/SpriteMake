"""Exercise the shared inspector and promotion gate together on real PNGs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RunnerWorkflowTests(unittest.TestCase):
    def test_inspection_review_promotion_and_reference_invalidation(self):
        with tempfile.TemporaryDirectory() as temporary:
            batch = Path(temporary)
            for directory in ("generated", "source", "qa", "contracts"):
                (batch / directory).mkdir()
            candidate = batch / "generated/hero.png"
            image = Image.new("RGBA", (16, 8))
            for x_offset in (0, 8):
                for x in range(x_offset + 2, x_offset + 6):
                    for y in range(2, 6):
                        image.putpixel((x, y), (220, 120, 80, 255))
            image.save(candidate)
            reference = batch / "source/right.png"
            image.save(reference)
            comparison = batch / "qa/comparison.png"
            image.save(comparison)
            contract = batch / "contracts/hero.json"
            contract.write_text(json.dumps({
                "schemaVersion": 1, "assetId": "hero", "version": 1,
                "target": {"finalPath": "final/hero.png"},
                "references": [{"path": "source/right.png", "role": "identity", "direction": "right"}],
                "atlas": {"canvas": {"width": 16, "height": 8},
                    "grid": {"columns": 2, "rows": 1, "cellWidth": 8, "cellHeight": 8},
                    "anchor": {"x": 4, "y": 6, "meaning": "ground contact"}, "sourcePlaneY": 6,
                    "animations": {"idle": {"row": 0, "frames": [0, 1], "fps": 8, "loop": True}}},
                "qa": {"required": ["canvas", "grid", "alpha", "bbox", "anchor", "baseline"],
                    "requiredInputs": ["qa/comparison.png"], "thresholds": {"maximumAlpha1To7Pixels": 0}},
                "reviews": {"filenameContent": {"required": True},
                    "style": {"required": True, "referencePath": "source/right.png", "comparisonRequired": True},
                    "motion": {"required": True}, "placement": {"required": True}},
            }), encoding="utf-8-sig")
            report, status_path = batch / "qa/report.json", batch / "qa/status.json"

            def inspect():
                return subprocess.run([sys.executable, str(ROOT / "tools/runner/inspect_sprite.py"),
                    "--batch-root", str(batch), "--contract", str(contract), "--image", str(candidate),
                    "--output", str(report), "--status", str(status_path)], capture_output=True, text=True)

            def gate(command):
                return subprocess.run([sys.executable, str(ROOT / "tools/runner/asset_gate.py"), command,
                    "--batch-root", str(batch), "--contract", str(contract), "--status", str(status_path)],
                    capture_output=True, text=True)

            original = sha(candidate)
            result = inspect()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotEqual(gate("promote").returncode, 0)
            self.assertFalse((batch / "final/hero.png").exists())
            status = json.loads(status_path.read_text())
            for review in status["reviews"].values():
                review["status"] = "approved"
            status["reviews"]["style"].update(comparisonPath="qa/comparison.png",
                comparisonSha256=sha(comparison), referenceSha256=sha(reference))
            status_path.write_text(json.dumps(status))
            result = gate("promote")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(sha(batch / "final/hero.png"), original)
            image.putpixel((2, 2), (20, 20, 20, 255))
            image.save(reference)
            self.assertNotEqual(gate("promote").returncode, 0)
            self.assertEqual(sha(batch / "final/hero.png"), original)
            self.assertEqual(inspect().returncode, 0)
            fresh = json.loads(status_path.read_text())
            self.assertTrue(all(r["status"] == "pending" for r in fresh["reviews"].values()))
            self.assertFalse(fresh["promotion"]["eligible"])
            self.assertEqual(sha(candidate), original)


if __name__ == "__main__":
    unittest.main()
