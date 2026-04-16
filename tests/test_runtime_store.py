from __future__ import annotations

from pathlib import Path

from avcp_template.runtime.models import (
    ApprovalGate,
    CheckpointRef,
    ClaimRecord,
    RunManifest,
    TaskRecord,
)
from avcp_template.runtime.store import (
    append_run_event,
    initialize_run_storage,
    load_run_state,
    write_claim_ledger,
    write_manifest,
)


def test_run_storage_persists_and_recovers_checkpoint_history(tmp_path: Path) -> None:
    run_root = tmp_path / "artifacts" / "runs"
    manifest = RunManifest(
        run_id="run-001",
        research_stage="execution",
        permission_mode="workspace-write",
        autonomy_mode="balanced",
        max_parallel_subagents=2,
        compute_budget={"max_steps": 50},
        checkpoint_backend="filesystem",
        allowed_adapters=["local"],
        tasks=[
            TaskRecord(
                task_id="task-001",
                title="Run association model",
                stage="execution",
                status="completed",
                evidence_refs=["artifacts/runs/run-001/outputs/model.csv"],
            )
        ],
        approval_gates=[
            ApprovalGate(
                gate_id="gate-001",
                gate_type="interpretation_claim",
                status="approved",
                rationale="Supervisor approved interpretation checkpoint.",
            )
        ],
        claims=[],
        checkpoints=[
            CheckpointRef(
                checkpoint_id="cp-001",
                path="artifacts/runs/run-001/checkpoints/cp-001.json",
                created_at="2026-04-16T10:00:00Z",
                note="Model inputs frozen.",
            )
        ],
    )

    run_dir = initialize_run_storage(run_root=run_root, run_id="run-001")
    assert (run_dir / "outputs").exists()

    write_manifest(run_root=run_root, manifest=manifest)
    append_run_event(run_root=run_root, run_id="run-001", event={"seq": 1, "type": "run_started"})
    append_run_event(
        run_root=run_root,
        run_id="run-001",
        event={"seq": 2, "type": "checkpoint_saved", "checkpoint_id": "cp-001"},
    )
    write_claim_ledger(
        run_root=run_root,
        run_id="run-001",
        claims=[
            ClaimRecord(
                claim_id="claim-001",
                claim_class="interpretation",
                statement="Signal strength remained directionally consistent.",
                evidence_refs=["artifacts/runs/run-001/outputs/model.csv"],
                uncertainty="Confidence interval remains wide.",
                approval_status="approved",
                threats_to_validity=["sample size"],
            )
        ],
    )

    state = load_run_state(run_root=run_root, run_id="run-001")
    assert state.manifest.run_id == "run-001"
    assert state.manifest.checkpoints[0].checkpoint_id == "cp-001"
    assert state.events[-1]["checkpoint_id"] == "cp-001"
    assert state.claims[0].claim_id == "claim-001"

    append_run_event(
        run_root=run_root,
        run_id="run-001",
        event={"seq": 3, "type": "resumed_from_checkpoint", "checkpoint_id": "cp-001"},
    )
    resumed = load_run_state(run_root=run_root, run_id="run-001")
    assert [event["seq"] for event in resumed.events] == [1, 2, 3]
