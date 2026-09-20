from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "tools/runner/asset_gate.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AssetGateTests(unittest.TestCase):
    def write_fixture(self, directory: Path, approved: bool) -> tuple[Path, Path, Path]:
        (directory / "generated").mkdir(); (directory / "qa").mkdir()
        candidate = directory / "generated/example.png"; candidate.write_bytes(b"candidate")
        report = directory / "qa/example-report.json"; report.write_text('{"pass":true}\n')
        contract = directory / "contract.json"
        contract.write_text(json.dumps({"schemaVersion": 1, "assetId": "example", "version": 1,
            "target": {"finalPath": "final/example.png"}, "atlas": {}, "qa": {"required": [], "thresholds": {}},
            "reviews": {"filenameContent": {"required": True}, "style": {"required": True, "comparisonRequired": True}}}))
        comparison = directory / "qa/compare.png"; comparison.write_bytes(b"comparison")
        status = directory / "qa/asset-status.json"
        review = "approved" if approved else "pending"
        status.write_text(json.dumps({"schemaVersion": 1, "assetId": "example", "contractVersion": 1,
            "candidate": {"path": "generated/example.png", "sha256": sha(candidate), "provenance": "unverified"},
            "qa": {"status": "pass", "reportPath": "qa/example-report.json", "reportSha256": sha(report)},
            "reviews": {"filenameContent": {"status": review}, "style": {"status": review, "comparisonPath": "qa/compare.png"}},
            "promotion": {"eligible": False, "status": "candidate"}}))
        return candidate, contract, status

    def run_gate(self, command: str, directory: Path, contract: Path, status: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["python3", str(GATE), command, "--batch-root", str(directory), "--contract", str(contract), "--status", str(status)], text=True, capture_output=True)

    def test_promotion_requires_approvals_and_preserves_final_on_block(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp); candidate, contract, status = self.write_fixture(directory, approved=False)
            existing_final = directory / "final/example.png"; existing_final.parent.mkdir(); existing_final.write_bytes(b"old-final")
            result = self.run_gate("promote", directory, contract, status)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(existing_final.read_bytes(), b"old-final")
            self.assertEqual(json.loads(status.read_text())["promotion"]["status"], "blocked")

    def test_promotion_is_checksum_bound_and_atomic(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp); candidate, contract, status = self.write_fixture(directory, approved=True)
            result = self.run_gate("promote", directory, contract, status)
            self.assertEqual(result.returncode, 0, result.stderr)
            final = directory / "final/example.png"
            self.assertEqual(final.read_bytes(), candidate.read_bytes())
            self.assertEqual(json.loads(status.read_text())["promotion"]["status"], "promoted")


if __name__ == "__main__":
    unittest.main()
