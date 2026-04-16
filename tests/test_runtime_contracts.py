from __future__ import annotations

import pytest

from avcp_template.runtime.models import (
    ApprovalGate,
    ClaimRecord,
    RunManifest,
    RuntimeContractError,
    TaskRecord,
)


def _base_manifest() -> RunManifest:
    return RunManifest(
        run_id="run-001",
        research_stage="protocol_lock",
        permission_mode="workspace-write",
        autonomy_mode="balanced",
        max_parallel_subagents=3,
        compute_budget={"max_steps": 100, "max_runtime_minutes": 30},
        checkpoint_backend="filesystem",
        allowed_adapters=["local", "openai"],
        tasks=[],
        approval_gates=[],
        claims=[],
    )


def test_run_manifest_round_trip_preserves_gate_state() -> None:
    manifest = _base_manifest()
    gate = ApprovalGate(
        gate_id="gate-001",
        gate_type="new_metric",
        status="approved",
        rationale="PI approved the metric change before execution.",
    )
    task = TaskRecord(
        task_id="task-001",
        title="Adopt adjusted primary endpoint",
        stage="protocol_lock",
        status="blocked",
        risk_tags=["new_metric"],
        evidence_refs=["docs/decisions.md#D002"],
    )
    manifest.approval_gates.append(gate)
    manifest.tasks.append(task)

    manifest.ensure_task_allowed(task)

    restored = RunManifest.from_dict(manifest.to_dict())
    approved_gate = restored.latest_approved_gate("new_metric")
    assert restored.to_dict() == manifest.to_dict()
    assert approved_gate is not None
    assert approved_gate.gate_id == "gate-001"


def test_high_risk_task_without_approval_is_blocked() -> None:
    manifest = _base_manifest()
    task = TaskRecord(
        task_id="task-002",
        title="Switch primary outcome after interim look",
        stage="protocol_lock",
        status="blocked",
        risk_tags=["outcome_switch"],
        evidence_refs=["docs/decisions.md#D003"],
    )

    with pytest.raises(RuntimeContractError, match="outcome_switch"):
        manifest.ensure_task_allowed(task)


def test_observational_claim_cannot_use_causal_wording() -> None:
    manifest = _base_manifest()
    claim = ClaimRecord(
        claim_id="claim-001",
        claim_class="observation",
        statement="The biomarker causes the improvement observed in the cohort.",
        evidence_refs=["artifacts/runs/run-001/outputs/table-1.csv"],
        uncertainty="Associational evidence only.",
        approval_status="not_required",
        threats_to_validity=["unmeasured confounding"],
    )

    with pytest.raises(RuntimeContractError, match="causal wording"):
        manifest.validate_claim(claim, require_evidence=True)


def test_manuscript_main_conclusion_requires_evidence_and_approval() -> None:
    manifest = _base_manifest()
    claim = ClaimRecord(
        claim_id="claim-002",
        claim_class="manuscript_main_conclusion",
        statement="The intervention improved the primary endpoint.",
        evidence_refs=[],
        uncertainty="Needs final adjudication.",
        approval_status="pending",
        threats_to_validity=["small sample size"],
    )

    with pytest.raises(RuntimeContractError, match="evidence_refs"):
        manifest.validate_claim(claim, require_evidence=True)
