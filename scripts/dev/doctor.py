#!/usr/bin/env python3
# SCRIPT_HEADER_CONTRACT
# Script: scripts/dev/doctor.py
# Purpose: Validate that an AVCP repository is ready for research-runtime execution.
# Inputs:
#   - repo_root: repository root to inspect
#   - config/config.yaml: runtime configuration source-of-truth
# Outputs:
#   - stdout/stderr: doctor report for pass/fail checks
# Side Effects:
#   - N/A
# Config Dependencies:
#   - config/config.yaml::paths.run_root
#   - config/config.yaml::runtime
#   - config/config.yaml::audit
#   - config/config.yaml::research
# Execution:
#   - python scripts/dev/doctor.py [--repo-root PATH] [--config-file PATH]
# Failure Modes:
#   - missing config/docs/approval compliance -> exit code 1
# Last Updated: 2026-04-16
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(REPO_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_SRC_ROOT))

REQUIRED_DOCS = (
    "docs/state.md",
    "docs/constraints.md",
    "docs/decisions.md",
    "docs/api_specs.md",
    "docs/data_contracts.md",
    "docs/avcp_guidelines.md",
    "docs/research_mode.md",
)
REQUIRED_CONFIG_KEYS = (
    "paths.interim_viz_dir",
    "paths.run_root",
    "runtime.permission_mode",
    "runtime.autonomy_mode",
    "runtime.max_parallel_subagents",
    "runtime.compute_budget",
    "runtime.checkpoint_backend",
    "runtime.allowed_adapters",
    "audit.require_evidence_for_claims",
    "research.default_stage",
)
PLACEHOLDER_SNIPPETS = ("TODO", "(Define schemas", "(Define public interfaces", "- Current Sprint Goal:")


class DoctorError(ValueError):
    """Raised when repository preflight checks fail."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--config-file", default="config/config.yaml")
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise DoctorError(f"Missing config file: {path}")
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise DoctorError(f"Config file must parse to a mapping: {path}")
    return parsed


def _resolve_key(config: dict[str, Any], dotted_key: str) -> Any:
    current: Any = config
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            raise DoctorError(f"Missing config key: {dotted_key}")
        current = current[part]
    return current


def _check_required_docs(repo_root: Path) -> None:
    for relative_path in REQUIRED_DOCS:
        path = repo_root / relative_path
        if not path.exists():
            raise DoctorError(f"Missing required doc: {relative_path}")
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            raise DoctorError(f"Required doc is empty: {relative_path}")
        if any(snippet in text for snippet in PLACEHOLDER_SNIPPETS):
            raise DoctorError(f"Required doc still contains placeholder content: {relative_path}")


def _check_config(config: dict[str, Any]) -> None:
    for dotted_key in REQUIRED_CONFIG_KEYS:
        value = _resolve_key(config, dotted_key)
        if value in ("", [], {}, None):
            raise DoctorError(f"Config key is empty: {dotted_key}")


def _check_run_manifests(repo_root: Path, config: dict[str, Any]) -> None:
    from avcp_template.runtime.models import (
        HIGH_RISK_APPROVAL_TAGS,
        RunManifest,
        RuntimeContractError,
    )

    run_root = repo_root / Path(str(_resolve_key(config, "paths.run_root")))
    if not run_root.exists():
        return

    require_evidence = bool(_resolve_key(config, "audit.require_evidence_for_claims"))
    for manifest_path in sorted(run_root.glob("*/manifest.json")):
        manifest = RunManifest.from_dict(json.loads(manifest_path.read_text(encoding="utf-8")))
        try:
            manifest.validate(require_evidence=require_evidence)
        except RuntimeContractError as exc:
            raise DoctorError(str(exc)) from exc
        for gate in manifest.approval_gates:
            if gate.status == "pending" and gate.gate_type in HIGH_RISK_APPROVAL_TAGS:
                raise DoctorError(
                    f"Run '{manifest.run_id}' has pending approval gate '{gate.gate_type}'."
                )


def main() -> None:
    args = _parse_args()
    repo_root = Path(args.repo_root).resolve()
    config_path = Path(args.config_file).resolve()

    try:
        config = _load_yaml(config_path)
        _check_config(config)
        _check_required_docs(repo_root)
        _check_run_manifests(repo_root, config)
    except DoctorError as exc:
        print(f"Doctor check failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print("Doctor checks passed.")


if __name__ == "__main__":
    main()
