from __future__ import annotations

import hashlib
import json
import subprocess
import sys
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
        (directory / "source").mkdir(); (directory / "manifests").mkdir()
        reference = directory / "source/reference.png"; reference.write_bytes(b"reference")
        curation = directory / "manifests/curation.json"; curation.write_text('{"selected": [0, 1]}\n')
        candidate = directory / "generated/example.png"; candidate.write_bytes(b"candidate")
        report = directory / "qa/example-report.json"; report.write_text('{"pass":true}\n')
        contract = directory / "contract.json"
        contract.write_text(json.dumps({"schemaVersion": 1, "assetId": "example", "version": 1,
            "target": {"finalPath": "final/example.png"}, "atlas": {}, "qa": {"required": [], "thresholds": {}, "requiredInputs": ["manifests/curation.json"]},
            "references": [{"path": "source/reference.png", "role": "style", "direction": "right"}],
            "reviews": {"filenameContent": {"required": True}, "style": {"required": True, "comparisonRequired": True, "referencePath": "source/reference.png"}}}))
        comparison = directory / "qa/compare.png"; comparison.write_bytes(b"comparison")
        status = directory / "qa/asset-status.json"
        review = "approved" if approved else "pending"
        status.write_text(json.dumps({"schemaVersion": 1, "assetId": "example", "contractVersion": 1,
            "candidate": {"path": "generated/example.png", "sha256": sha(candidate), "provenance": "unverified"},
            "qa": {"status": "pass", "reportPath": "qa/example-report.json", "reportSha256": sha(report), "contractSha256": sha(contract),
                   "inputChecksums": [{"path": "source/reference.png", "sha256": sha(reference), "role": "style"},
                                      {"path": "manifests/curation.json", "sha256": sha(curation), "role": "curation"}]},
            "reviews": {"filenameContent": {"status": review}, "style": {"status": review, "comparisonPath": "qa/compare.png",
                "comparisonSha256": sha(comparison), "referenceSha256": sha(reference)}},
            "promotion": {"eligible": False, "status": "candidate"}}))
        return candidate, contract, status

    def run_gate(self, command: str, directory: Path, contract: Path, status: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(GATE), command, "--batch-root", str(directory), "--contract", str(contract), "--status", str(status)], text=True, capture_output=True)

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

    def assert_blocked_preserving_final(self, directory, contract, status, message=None):
        final = directory / "final/example.png"
        final.parent.mkdir(exist_ok=True)
        final.write_bytes(b"prior-final")
        result = self.run_gate("promote", directory, contract, status)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(final.read_bytes(), b"prior-final")
        if message:
            self.assertIn(message, result.stdout + result.stderr)

    def update_contract(self, contract, status, change):
        data = json.loads(contract.read_text()); change(data)
        contract.write_text(json.dumps(data))
        state = json.loads(status.read_text()); state['qa']['contractSha256'] = sha(contract)
        status.write_text(json.dumps(state))

    def test_contract_bytes_bound_even_without_version_bump(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp); _, contract, status = self.write_fixture(directory, True)
            data = json.loads(contract.read_text()); data['atlas']['anchor'] = {'x': 90, 'y': 100}
            contract.write_text(json.dumps(data))
            self.assert_blocked_preserving_final(directory, contract, status, 'contract checksum changed')

    def test_changed_artifact_and_qa_inputs_block(self):
        for name in ('source/reference.png', 'manifests/curation.json', 'qa/compare.png',
                     'qa/example-report.json', 'generated/example.png'):
            with self.subTest(path=name), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp); _, contract, status = self.write_fixture(directory, True)
                (directory / name).write_bytes(b'changed')
                self.assert_blocked_preserving_final(directory, contract, status, 'checksum changed')

    def test_missing_checksums_block_legacy_approvals(self):
        for area, key in (('qa', 'contractSha256'), ('qa', 'inputChecksums'),
                          ('style', 'comparisonSha256'), ('style', 'referenceSha256')):
            with self.subTest(field=key), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp); _, contract, status = self.write_fixture(directory, True)
                data = json.loads(status.read_text())
                section = data['qa'] if area == 'qa' else data['reviews']['style']
                section.pop(key); status.write_text(json.dumps(data))
                self.assert_blocked_preserving_final(directory, contract, status)

    def test_missing_required_input_fingerprints_block(self):
        for name in ('source/reference.png', 'manifests/curation.json'):
            with self.subTest(path=name), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp); _, contract, status = self.write_fixture(directory, True)
                data = json.loads(status.read_text())
                data['qa']['inputChecksums'] = [r for r in data['qa']['inputChecksums'] if r['path'] != name]
                status.write_text(json.dumps(data))
                self.assert_blocked_preserving_final(directory, contract, status, 'required QA input fingerprint is missing')

    def test_malformed_and_duplicate_input_records_block(self):
        values = (None, {}, ['bad'], [{}], [{'path': [], 'sha256': 'a' * 64}],
                  [{'path': 'source/reference.png', 'sha256': None}],
                  [{'path': 'source/reference.png', 'sha256': 'Z' * 64}],
                  [{'path': 'source/reference.png', 'sha256': 'a' * 64, 'role': 10}])
        for records in values:
            with self.subTest(records=records), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp); _, contract, status = self.write_fixture(directory, True)
                data = json.loads(status.read_text()); data['qa']['inputChecksums'] = records
                status.write_text(json.dumps(data))
                self.assert_blocked_preserving_final(directory, contract, status)
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp); _, contract, status = self.write_fixture(directory, True)
            data = json.loads(status.read_text()); data['qa']['inputChecksums'].append(data['qa']['inputChecksums'][0])
            status.write_text(json.dumps(data))
            self.assert_blocked_preserving_final(directory, contract, status, 'duplicate QA input')

    def test_unsafe_input_paths_block(self):
        for name in ('source/../generated/example.png', 'source/./reference.png',
                     'source//reference.png', '/source/reference.png',
                     'source\\reference.png', 'final/example.png', 'source/\x00.png'):
            with self.subTest(path=name), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp); _, contract, status = self.write_fixture(directory, True)
                data = json.loads(status.read_text())
                data['qa']['inputChecksums'].append({'path': name, 'sha256': 'a' * 64})
                status.write_text(json.dumps(data))
                self.assert_blocked_preserving_final(directory, contract, status)

    def test_symlink_inputs_and_style_comparison_block(self):
        for name in ('source/reference.png', 'qa/compare.png', 'generated/example.png'):
            for outside in (False, True):
                with self.subTest(path=name, outside=outside), tempfile.TemporaryDirectory() as temp:
                    directory = Path(temp) / 'batch'; directory.mkdir()
                    _, contract, status = self.write_fixture(directory, True)
                    file = directory / name
                    destination = (Path(temp) if outside else directory / 'source') / 'alias.png'
                    destination.write_bytes(file.read_bytes()); file.unlink(); file.symlink_to(destination)
                    self.assert_blocked_preserving_final(directory, contract, status, 'symlink')

    def test_missing_input_file_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp); _, contract, status = self.write_fixture(directory, True)
            (directory / 'manifests/curation.json').unlink()
            self.assert_blocked_preserving_final(directory, contract, status, 'file is missing')

    def test_motion_review_required_only_when_declared(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp); _, contract, status = self.write_fixture(directory, True)
            self.update_contract(contract, status, lambda c: c['reviews'].update({'motion': {'required': True}}))
            self.assert_blocked_preserving_final(directory, contract, status, 'motion review is not approved')
            data = json.loads(status.read_text()); data['reviews']['motion'] = {'status': 'approved'}
            status.write_text(json.dumps(data))
            result = self.run_gate('promote', directory, contract, status)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_animation_requires_motion_review_without_explicit_flag(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp); _, contract, status = self.write_fixture(directory, True)
            self.update_contract(contract, status, lambda c: c['atlas'].update(
                {'animations': {'idle': {'row': 0, 'frames': [0, 1], 'fps': 6}}}))
            self.assert_blocked_preserving_final(directory, contract, status, 'motion review is not approved')
            data = json.loads(status.read_text()); data['reviews']['motion'] = {'status': 'approved'}
            status.write_text(json.dumps(data))
            result = self.run_gate('promote', directory, contract, status)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_semantic_placement_requires_review(self):
        for name in ('anchor', 'baseline', 'explicit'):
            with self.subTest(rule=name), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp); _, contract, status = self.write_fixture(directory, True)
                def require(c):
                    if name == 'explicit': c['reviews']['placement'] = {'required': True}
                    else: c['qa']['required'] = [name]
                self.update_contract(contract, status, require)
                self.assert_blocked_preserving_final(directory, contract, status, 'placement review is not approved')
                data = json.loads(status.read_text()); data['reviews']['placement'] = {'status': 'approved'}
                status.write_text(json.dumps(data))
                result = self.run_gate('promote', directory, contract, status)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_style_reference_needs_its_review_checksum_even_with_input_fingerprint(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp); _, contract, status = self.write_fixture(directory, True)
            data = json.loads(status.read_text()); data['reviews']['style']['referenceSha256'] = 'a' * 64
            status.write_text(json.dumps(data))
            self.assert_blocked_preserving_final(directory, contract, status, 'style reference checksum changed')

    def test_unsafe_required_contract_inputs_block(self):
        for key in ('references', 'requiredInputs', 'referencePath'):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as temp:
                directory = Path(temp); _, contract, status = self.write_fixture(directory, True)
                def mutate(c):
                    if key == 'references': c['references'][0]['path'] = 'source/../outside.png'
                    elif key == 'requiredInputs': c['qa'][key] = ['source/../outside.png']
                    else: c['reviews']['style'][key] = 'source/../outside.png'
                self.update_contract(contract, status, mutate)
                self.assert_blocked_preserving_final(directory, contract, status, 'unsafe components')


if __name__ == "__main__":
    unittest.main()
