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
import re
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
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read JSON: {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"JSON must be an object: {path}")
    return value


INPUT_PREFIXES = ("source/", "generated/", "manifests/", "qa/", "contracts/")


def relative_path(root: Path, relative: str, expected_prefix: str | tuple[str, ...]) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or "\x00" in relative:
        raise ValueError("Path must be a batch-relative POSIX path")
    if any(part in ("", ".", "..") for part in relative.split("/")):
        raise ValueError(f"Path contains unsafe components: {relative}")
    if not relative.startswith(expected_prefix):
        raise ValueError(f"Path must start with {expected_prefix}: {relative}")
    resolved_root = root.resolve()
    unresolved = resolved_root
    for part in relative.split("/"):
        unresolved = unresolved / part
        if unresolved.is_symlink():
            raise ValueError(f"Path contains a symlink: {relative}")
    resolved = unresolved.resolve()
    if resolved_root not in (resolved, *resolved.parents):
        raise ValueError(f"Path escapes batch root: {relative}")
    return resolved


def check_file(root: Path, path: object, checksum: object, prefixes: str | tuple[str, ...], label: str, errors: list[str]) -> None:
    try:
        file_path = relative_path(root, path, prefixes)
        if not file_path.is_file():
            errors.append(f"{label} file is missing")
        elif not isinstance(checksum, str) or not re.fullmatch(r"[a-f0-9]{64}", checksum):
            errors.append(f"{label} checksum is missing or malformed")
        elif checksum != digest(file_path):
            errors.append(f"{label} checksum changed after QA")
    except (ValueError, OSError) as error:
        errors.append(f"{label}: {error}")


def check_inputs(root: Path, contract: dict[str, Any], qa: dict[str, Any], errors: list[str]) -> None:
    records = qa.get("inputChecksums")
    if not isinstance(records, list):
        errors.append("QA inputChecksums must be an array (legacy QA must be rerun)")
        records = []
    recorded: set[str] = set()
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            errors.append("QA input checksum record is malformed")
            continue
        path = record["path"]
        if path in recorded:
            errors.append(f"duplicate QA input checksum path: {path}")
        recorded.add(path)
        if "role" in record and (not isinstance(record["role"], str) or not record["role"]):
            errors.append(f"QA input role is malformed: {path}")
        check_file(root, path, record.get("sha256"), INPUT_PREFIXES, f"QA input {path}", errors)

    required: list[object] = []
    references = contract.get("references", [])
    if not isinstance(references, list):
        errors.append("contract references must be an array")
    else:
        for ref in references:
            if not isinstance(ref, dict) or not isinstance(ref.get("role"), str) or not ref["role"]:
                errors.append("contract reference is malformed")
                continue
            if "direction" in ref and (not isinstance(ref["direction"], str) or not ref["direction"]):
                errors.append("contract reference direction is malformed")
            required.append(ref.get("path"))
    contract_qa = contract.get("qa", {})
    if not isinstance(contract_qa, dict):
        errors.append("contract qa must be an object")
    else:
        required_inputs = contract_qa.get("requiredInputs", [])
        if not isinstance(required_inputs, list):
            errors.append("contract qa.requiredInputs must be an array")
        else:
            if len([p for p in required_inputs if isinstance(p, str)]) != len(set(p for p in required_inputs if isinstance(p, str))):
                errors.append("contract qa.requiredInputs contains duplicate paths")
            required.extend(required_inputs)
    for path in required:
        try:
            relative_path(root, path, INPUT_PREFIXES)
            if path not in recorded:
                errors.append(f"required QA input fingerprint is missing: {path}")
        except ValueError as error:
            errors.append(f"required QA input: {error}")


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
    target = contract.get("target", {})
    try:
        relative_path(root, target.get("finalPath") if isinstance(target, dict) else None, "final/")
    except ValueError as error:
        errors.append(f"final target: {error}")

    candidate = status.get("candidate", {})
    if not isinstance(candidate, dict):
        errors.append("candidate is missing")
    else:
        check_file(root, candidate.get("path"), candidate.get("sha256"), "generated/", "candidate", errors)

    qa = status.get("qa", {})
    if not isinstance(qa, dict) or qa.get("status") != "pass":
        errors.append("automated QA is not pass")
    else:
        contract_hash = qa.get("contractSha256")
        if not isinstance(contract_hash, str) or not re.fullmatch(r"[a-f0-9]{64}", contract_hash):
            errors.append("QA contractSha256 is missing or malformed (legacy QA must be rerun)")
        elif contract_hash != digest(contract_path):
            errors.append("contract checksum changed after QA")
        check_file(root, qa.get("reportPath"), qa.get("reportSha256"), "qa/", "QA report", errors)
        check_inputs(root, contract, qa, errors)

    reviews = status.get("reviews", {})
    if not isinstance(reviews, dict):
        errors.append("reviews are missing")
    else:
        contract_reviews = contract.get("reviews", {})
        if not isinstance(contract_reviews, dict):
            errors.append("contract reviews must be an object")
            return status, errors
        for name in ("filenameContent", "style", "motion", "placement"):
            rule = contract_reviews.get(name, {})
            if not isinstance(rule, dict) or ("required" in rule and not isinstance(rule["required"], bool)):
                errors.append(f"contract {name} review rule is malformed")
                return status, errors
        filename_required = bool(contract_reviews.get("filenameContent", {}).get("required", False))
        if not review_is_approved(reviews.get("filenameContent"), filename_required):
            errors.append("filename/content review is not approved")
        style = contract_reviews.get("style", {})
        if "comparisonRequired" in style and not isinstance(style["comparisonRequired"], bool):
            errors.append("contract style comparisonRequired must be boolean")
        style_required = bool(style.get("required", False))
        style_review = reviews.get("style")
        if not review_is_approved(style_review, style_required):
            errors.append("style review is not approved")
        if style_required and bool(style.get("comparisonRequired", False)):
            comparison = style_review.get("comparisonPath") if isinstance(style_review, dict) else None
            comparison_hash = style_review.get("comparisonSha256") if isinstance(style_review, dict) else None
            check_file(root, comparison, comparison_hash, "qa/", "required style comparison", errors)
        if style_required and style.get("referencePath") is not None:
            reference_hash = style_review.get("referenceSha256") if isinstance(style_review, dict) else None
            check_file(root, style["referencePath"], reference_hash, INPUT_PREFIXES, "style reference", errors)
        atlas = contract.get("atlas", {})
        animations = atlas.get("animations", {}) if isinstance(atlas, dict) else {}
        if not isinstance(animations, (dict, list)):
            errors.append("contract atlas.animations must be an object or array")
        motion_required = contract_reviews.get("motion", {}).get("required", False) or bool(animations)
        if not review_is_approved(reviews.get("motion"), motion_required):
            errors.append("motion review is not approved")
        required_checks = contract.get("qa", {}).get("required", []) if isinstance(contract.get("qa"), dict) else []
        if not isinstance(required_checks, list) or any(not isinstance(name, str) for name in required_checks):
            errors.append("contract qa.required must be an array of check names")
            required_checks = []
        placement_required = contract_reviews.get("placement", {}).get("required", False) or any(
            check in required_checks for check in ("anchor", "baseline")
        )
        if not review_is_approved(reviews.get("placement"), placement_required):
            errors.append("placement review is not approved")
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
    if digest(contract_path) != status["qa"]["contractSha256"]:
        raise RuntimeError("contract changed during promotion")
    candidate_path = relative_path(root, status["candidate"]["path"], "generated/")
    final_path = relative_path(root, contract["target"]["finalPath"], "final/")
    final_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=final_path.parent, prefix=f".{final_path.name}.", delete=False) as staging:
        staged_path = Path(staging.name)
    try:
        shutil.copyfile(candidate_path, staged_path)
        if digest(staged_path) != status["candidate"]["sha256"]:
            raise RuntimeError("staged candidate checksum mismatch")
        # Recheck the approval evidence after copying, before replacing final bytes.
        current_status, errors = validate(root, contract_path, status_path)
        if current_status.get("candidate") != status["candidate"] or current_status.get("qa") != status["qa"]:
            errors.append("candidate or QA evidence changed during promotion")
        if errors:
            write_status(status_path, current_status, errors)
            print(json.dumps({"eligible": False, "blockers": errors}, ensure_ascii=False))
            return 1
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
