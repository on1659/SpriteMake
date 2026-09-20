#!/usr/bin/env python3
"""Validate a SpriteMake candidate and atomically promote only approved assets.

The gate is intentionally local and keyless.  It consumes artifact paths and
checksums written by a generator/QA runner; it never calls an image API.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read JSON: {path}: {error}") from error


def relative_path(root: Path, relative: str, expected_prefix: str) -> Path:
    if not relative.startswith(expected_prefix):
        raise ValueError(f"Path must start with {expected_prefix}: {relative}")
    resolved_root = root.resolve()
    resolved = (root / relative).resolve()
    if resolved_root not in (resolved, *resolved.parents):
        raise ValueError(f"Path escapes batch root: {relative}")
    return resolved


def review_is_approved(review: object, required: bool) -> bool:
    if not required:
        return True
    return isinstance(review, dict) and review.get("status") == "approved"


def validate(root: Path, contract_path: Path, status_path: Path) -> tuple[dict[str, Any], list[str]]:
    contract = load_json(contract_path)
    status = load_json(status_path)
    errors: list[str] = []
    if contract.get("schemaVersion") != 1 or status.get("schemaVersion") != 1:
        errors.append("Unsupported schema version")
    if status.get("assetId") != contract.get("assetId"):
        errors.append("assetId does not match contract")
    if status.get("contractVersion") != contract.get("version"):
        errors.append("contractVersion does not match contract")

    candidate = status.get("candidate", {})
    if not isinstance(candidate, dict):
        errors.append("candidate is missing")
    else:
        try:
            candidate_path = relative_path(root, str(candidate.get("path", "")), "generated/")
            if not candidate_path.is_file():
                errors.append("candidate file is missing")
            elif candidate.get("sha256") != digest(candidate_path):
                errors.append("candidate checksum changed after QA")
        except ValueError as error:
            errors.append(str(error))

    qa = status.get("qa", {})
    if not isinstance(qa, dict) or qa.get("status") != "pass":
        errors.append("automated QA is not pass")
    else:
        try:
            report_path = relative_path(root, str(qa.get("reportPath", "")), "qa/")
            if not report_path.is_file():
                errors.append("QA report is missing")
            elif qa.get("reportSha256") != digest(report_path):
                errors.append("QA report checksum changed")
        except ValueError as error:
            errors.append(str(error))

    reviews = status.get("reviews", {})
    if not isinstance(reviews, dict):
        errors.append("reviews are missing")
    else:
        contract_reviews = contract.get("reviews", {})
        filename_required = bool(contract_reviews.get("filenameContent", {}).get("required", False))
        if not review_is_approved(reviews.get("filenameContent"), filename_required):
            errors.append("filename/content review is not approved")
        style = contract_reviews.get("style", {})
        style_required = bool(style.get("required", False))
        style_review = reviews.get("style")
        if not review_is_approved(style_review, style_required):
            errors.append("style review is not approved")
        if style_required and bool(style.get("comparisonRequired", False)):
            comparison = style_review.get("comparisonPath") if isinstance(style_review, dict) else None
            try:
                if not comparison or not relative_path(root, str(comparison), "qa/").is_file():
                    errors.append("required style comparison is missing")
            except ValueError as error:
                errors.append(str(error))
    return status, errors


def write_status(path: Path, status: dict[str, Any], errors: list[str], promoted: bool = False) -> None:
    promotion = status.setdefault("promotion", {})
    promotion["eligible"] = not errors
    promotion["status"] = "promoted" if promoted else ("candidate" if not errors else "blocked")
    promotion["blockers"] = errors
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def promote(root: Path, contract_path: Path, status_path: Path) -> int:
    status, errors = validate(root, contract_path, status_path)
    if errors:
        write_status(status_path, status, errors)
        print(json.dumps({"eligible": False, "blockers": errors}, ensure_ascii=False))
        return 1
    contract = load_json(contract_path)
    candidate_path = relative_path(root, status["candidate"]["path"], "generated/")
    final_path = relative_path(root, contract["target"]["finalPath"], "final/")
    final_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=final_path.parent, prefix=f".{final_path.name}.", delete=False) as staging:
        staged_path = Path(staging.name)
    try:
        shutil.copyfile(candidate_path, staged_path)
        if digest(staged_path) != status["candidate"]["sha256"]:
            raise RuntimeError("staged candidate checksum mismatch")
        os.replace(staged_path, final_path)
    finally:
        staged_path.unlink(missing_ok=True)
    status["promotion"]["finalPath"] = str(final_path.relative_to(root))
    status["promotion"]["finalSha256"] = digest(final_path)
    write_status(status_path, status, [], promoted=True)
    print(json.dumps({"eligible": True, "promoted": str(final_path)}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate", "promote"))
    parser.add_argument("--batch-root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--status", type=Path, required=True)
    args = parser.parse_args()
    root = args.batch_root.resolve()
    status_path = args.status.resolve()
    try:
        if args.command == "promote":
            return promote(root, args.contract.resolve(), status_path)
        status, errors = validate(root, args.contract.resolve(), status_path)
        write_status(status_path, status, errors)
        print(json.dumps({"eligible": not errors, "blockers": errors}, ensure_ascii=False))
        return 0 if not errors else 1
    except (ValueError, OSError, RuntimeError) as error:
        print(f"asset gate error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
