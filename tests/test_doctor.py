from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "dev" / "doctor.py"


def _write_minimal_repo(root: Path) -> Path:
    config_dir = root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "paths:",
                "  interim_viz_dir: data/interim_viz",
                "  run_root: artifacts/runs",
                "runtime:",
                "  permission_mode: workspace-write",
                "  autonomy_mode: balanced",
                "  max_parallel_subagents: 3",
                "  compute_budget:",
                "    max_steps: 100",
                "    max_runtime_minutes: 30",
                "  checkpoint_backend: filesystem",
                "  allowed_adapters:",
                "    - local",
                "audit:",
                "  require_evidence_for_claims: true",
                "research:",
                "  default_stage: question_definition",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    for name, text in {
        "state.md": "# Project State\n\n- Current Research Question: Is the signal reproducible?\n",
        "constraints.md": "# Constraints\n\n- No speculative science.\n",
        "decisions.md": "# Decisions\n\n## D001\n- Decision: Freeze protocol before execution.\n",
        "api_specs.md": "# API Specifications\n\nRuntime schemas locked.\n",
        "data_contracts.md": "# Data Contracts\n\nResearch export sidecars locked.\n",
        "avcp_guidelines.md": "# AVCP Guidelines\n\nEvidence-first and approval-gated.\n",
        "research_mode.md": "# Research Mode\n\nStages are defined and active.\n",
    }.items():
        (docs_dir / name).write_text(text, encoding="utf-8")

    return config_path


def _run_doctor(repo_root: Path, config_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo-root",
            str(repo_root),
            "--config-file",
            str(config_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def test_doctor_passes_for_minimal_research_ready_repo(tmp_path: Path) -> None:
    config_path = _write_minimal_repo(tmp_path)
    result = _run_doctor(tmp_path, config_path)
    assert result.returncode == 0, result.stderr
    assert "Doctor checks passed" in result.stdout


def test_doctor_fails_when_pending_high_risk_gate_exists(tmp_path: Path) -> None:
    config_path = _write_minimal_repo(tmp_path)
    run_dir = tmp_path / "artifacts" / "runs" / "run-001"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "outputs").mkdir(exist_ok=True)
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": "run-001",
                "research_stage": "interpretation",
                "permission_mode": "workspace-write",
                "autonomy_mode": "balanced",
                "max_parallel_subagents": 2,
                "compute_budget": {"max_steps": 20},
                "checkpoint_backend": "filesystem",
                "allowed_adapters": ["local"],
                "tasks": [],
                "claims": [],
                "approval_gates": [
                    {
                        "gate_id": "gate-001",
                        "gate_type": "manuscript_main_conclusion",
                        "status": "pending",
                        "rationale": "Awaiting PI review.",
                    }
                ],
                "checkpoints": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = _run_doctor(tmp_path, config_path)
    assert result.returncode != 0
    assert "pending approval gate" in result.stderr
