from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from ..validation.contracts import validate_research_stage

TASK_STATUSES = {"pending", "running", "completed", "blocked", "failed"}
SUBAGENT_STATUSES = {"planned", "running", "completed", "blocked", "failed"}
GATE_STATUSES = {"pending", "approved", "rejected"}
CLAIM_APPROVAL_STATUSES = {"not_required", "pending", "approved", "rejected"}
CLAIM_CLASSES = {
    "observation",
    "interpretation",
    "recommendation",
    "manuscript_main_conclusion",
}
HIGH_RISK_APPROVAL_TAGS = {
    "new_metric",
    "outcome_switch",
    "post_hoc_subgroup",
    "exclusion_criteria_drift",
    "statistical_interpretation",
    "interpretation_claim",
    "manuscript_main_conclusion",
}
CAUSAL_WORDING_PATTERN = re.compile(
    r"\b(cause|causes|caused|causal|drive|drives|drove|result(?:s|ed)? in|led to|proof|prove|proves)\b",
    re.IGNORECASE,
)


class RuntimeContractError(ValueError):
    """Raised when runtime-level scientific or orchestration contracts are violated."""


def _ensure_non_empty_str(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeContractError(f"{name} must be a non-empty string.")
    return value.strip()


def _ensure_mapping(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeContractError(f"{name} must be a mapping.")
    return value


def _ensure_string_list(name: str, value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise RuntimeContractError(f"{name} must be a list of strings.")
    cleaned = []
    for item in value:
        cleaned.append(_ensure_non_empty_str(name, item))
    return cleaned


@dataclass(slots=True)
class EvidenceItem:
    evidence_id: str
    kind: str
    ref: str
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "kind": self.kind,
            "ref": self.ref,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvidenceItem:
        return cls(
            evidence_id=_ensure_non_empty_str("evidence_id", data.get("evidence_id")),
            kind=_ensure_non_empty_str("kind", data.get("kind")),
            ref=_ensure_non_empty_str("ref", data.get("ref")),
            note=str(data.get("note", "")),
        )


@dataclass(slots=True)
class ApprovalGate:
    gate_id: str
    gate_type: str
    status: str
    rationale: str

    def __post_init__(self) -> None:
        self.gate_id = _ensure_non_empty_str("gate_id", self.gate_id)
        self.gate_type = _ensure_non_empty_str("gate_type", self.gate_type)
        self.rationale = _ensure_non_empty_str("rationale", self.rationale)
        if self.status not in GATE_STATUSES:
            raise RuntimeContractError(f"Unknown approval gate status '{self.status}'.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "gate_type": self.gate_type,
            "status": self.status,
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ApprovalGate:
        return cls(
            gate_id=data.get("gate_id", ""),
            gate_type=data.get("gate_type", ""),
            status=data.get("status", ""),
            rationale=data.get("rationale", ""),
        )


@dataclass(slots=True)
class CheckpointRef:
    checkpoint_id: str
    path: str
    created_at: str
    note: str = ""

    def __post_init__(self) -> None:
        self.checkpoint_id = _ensure_non_empty_str("checkpoint_id", self.checkpoint_id)
        self.path = _ensure_non_empty_str("path", self.path)
        self.created_at = _ensure_non_empty_str("created_at", self.created_at)

    def to_dict(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "path": self.path,
            "created_at": self.created_at,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CheckpointRef:
        return cls(
            checkpoint_id=data.get("checkpoint_id", ""),
            path=data.get("path", ""),
            created_at=data.get("created_at", ""),
            note=str(data.get("note", "")),
        )


@dataclass(slots=True)
class TaskRecord:
    task_id: str
    title: str
    stage: str
    status: str
    evidence_refs: list[str] = field(default_factory=list)
    risk_tags: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    summary: str = ""

    def __post_init__(self) -> None:
        self.task_id = _ensure_non_empty_str("task_id", self.task_id)
        self.title = _ensure_non_empty_str("title", self.title)
        validate_research_stage(self.stage)
        if self.status not in TASK_STATUSES:
            raise RuntimeContractError(f"Unknown task status '{self.status}'.")
        self.evidence_refs = _ensure_string_list("evidence_refs", self.evidence_refs)
        self.risk_tags = _ensure_string_list("risk_tags", self.risk_tags)
        self.artifacts = _ensure_string_list("artifacts", self.artifacts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "stage": self.stage,
            "status": self.status,
            "evidence_refs": self.evidence_refs,
            "risk_tags": self.risk_tags,
            "artifacts": self.artifacts,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskRecord:
        return cls(
            task_id=data.get("task_id", ""),
            title=data.get("title", ""),
            stage=data.get("stage", ""),
            status=data.get("status", ""),
            evidence_refs=data.get("evidence_refs", []),
            risk_tags=data.get("risk_tags", []),
            artifacts=data.get("artifacts", []),
            summary=str(data.get("summary", "")),
        )


@dataclass(slots=True)
class SubagentRecord:
    subagent_id: str
    name: str
    stage: str
    status: str
    summary: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    risk_tags: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    checkpoint_id: str | None = None

    def __post_init__(self) -> None:
        self.subagent_id = _ensure_non_empty_str("subagent_id", self.subagent_id)
        self.name = _ensure_non_empty_str("name", self.name)
        validate_research_stage(self.stage)
        if self.status not in SUBAGENT_STATUSES:
            raise RuntimeContractError(f"Unknown subagent status '{self.status}'.")
        self.evidence_refs = _ensure_string_list("evidence_refs", self.evidence_refs)
        self.risk_tags = _ensure_string_list("risk_tags", self.risk_tags)
        self.artifacts = _ensure_string_list("artifacts", self.artifacts)
        if self.checkpoint_id is not None:
            self.checkpoint_id = _ensure_non_empty_str("checkpoint_id", self.checkpoint_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "subagent_id": self.subagent_id,
            "name": self.name,
            "stage": self.stage,
            "status": self.status,
            "summary": self.summary,
            "evidence_refs": self.evidence_refs,
            "risk_tags": self.risk_tags,
            "artifacts": self.artifacts,
            "checkpoint_id": self.checkpoint_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SubagentRecord:
        return cls(
            subagent_id=data.get("subagent_id", ""),
            name=data.get("name", ""),
            stage=data.get("stage", ""),
            status=data.get("status", ""),
            summary=str(data.get("summary", "")),
            evidence_refs=data.get("evidence_refs", []),
            risk_tags=data.get("risk_tags", []),
            artifacts=data.get("artifacts", []),
            checkpoint_id=data.get("checkpoint_id"),
        )


@dataclass(slots=True)
class ClaimRecord:
    claim_id: str
    claim_class: str
    statement: str
    evidence_refs: list[str]
    uncertainty: str
    approval_status: str
    threats_to_validity: list[str]

    def __post_init__(self) -> None:
        self.claim_id = _ensure_non_empty_str("claim_id", self.claim_id)
        self.statement = _ensure_non_empty_str("statement", self.statement)
        self.uncertainty = _ensure_non_empty_str("uncertainty", self.uncertainty)
        if self.claim_class not in CLAIM_CLASSES:
            raise RuntimeContractError(f"Unknown claim_class '{self.claim_class}'.")
        if self.approval_status not in CLAIM_APPROVAL_STATUSES:
            raise RuntimeContractError(f"Unknown approval_status '{self.approval_status}'.")
        self.evidence_refs = _ensure_string_list("evidence_refs", self.evidence_refs)
        self.threats_to_validity = _ensure_string_list(
            "threats_to_validity", self.threats_to_validity
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "claim_class": self.claim_class,
            "statement": self.statement,
            "evidence_refs": self.evidence_refs,
            "uncertainty": self.uncertainty,
            "approval_status": self.approval_status,
            "threats_to_validity": self.threats_to_validity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ClaimRecord:
        return cls(
            claim_id=data.get("claim_id", ""),
            claim_class=data.get("claim_class", ""),
            statement=data.get("statement", ""),
            evidence_refs=data.get("evidence_refs", []),
            uncertainty=data.get("uncertainty", ""),
            approval_status=data.get("approval_status", ""),
            threats_to_validity=data.get("threats_to_validity", []),
        )


@dataclass(slots=True)
class RunManifest:
    run_id: str
    research_stage: str
    permission_mode: str
    autonomy_mode: str
    max_parallel_subagents: int
    compute_budget: dict[str, Any]
    checkpoint_backend: str
    allowed_adapters: list[str]
    tasks: list[TaskRecord] = field(default_factory=list)
    approval_gates: list[ApprovalGate] = field(default_factory=list)
    claims: list[ClaimRecord] = field(default_factory=list)
    checkpoints: list[CheckpointRef] = field(default_factory=list)
    subagents: list[SubagentRecord] = field(default_factory=list)
    evidence_catalog: list[EvidenceItem] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.run_id = _ensure_non_empty_str("run_id", self.run_id)
        validate_research_stage(self.research_stage)
        self.permission_mode = _ensure_non_empty_str("permission_mode", self.permission_mode)
        self.autonomy_mode = _ensure_non_empty_str("autonomy_mode", self.autonomy_mode)
        if self.max_parallel_subagents < 1:
            raise RuntimeContractError("max_parallel_subagents must be >= 1.")
        self.compute_budget = _ensure_mapping("compute_budget", self.compute_budget)
        self.checkpoint_backend = _ensure_non_empty_str(
            "checkpoint_backend", self.checkpoint_backend
        )
        self.allowed_adapters = _ensure_string_list("allowed_adapters", self.allowed_adapters)
        if not self.allowed_adapters:
            raise RuntimeContractError("allowed_adapters must not be empty.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "research_stage": self.research_stage,
            "permission_mode": self.permission_mode,
            "autonomy_mode": self.autonomy_mode,
            "max_parallel_subagents": self.max_parallel_subagents,
            "compute_budget": self.compute_budget,
            "checkpoint_backend": self.checkpoint_backend,
            "allowed_adapters": self.allowed_adapters,
            "tasks": [task.to_dict() for task in self.tasks],
            "approval_gates": [gate.to_dict() for gate in self.approval_gates],
            "claims": [claim.to_dict() for claim in self.claims],
            "checkpoints": [checkpoint.to_dict() for checkpoint in self.checkpoints],
            "subagents": [subagent.to_dict() for subagent in self.subagents],
            "evidence_catalog": [item.to_dict() for item in self.evidence_catalog],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunManifest:
        return cls(
            run_id=data.get("run_id", ""),
            research_stage=data.get("research_stage", ""),
            permission_mode=data.get("permission_mode", ""),
            autonomy_mode=data.get("autonomy_mode", ""),
            max_parallel_subagents=int(data.get("max_parallel_subagents", 0)),
            compute_budget=data.get("compute_budget", {}),
            checkpoint_backend=data.get("checkpoint_backend", ""),
            allowed_adapters=data.get("allowed_adapters", []),
            tasks=[TaskRecord.from_dict(item) for item in data.get("tasks", [])],
            approval_gates=[ApprovalGate.from_dict(item) for item in data.get("approval_gates", [])],
            claims=[ClaimRecord.from_dict(item) for item in data.get("claims", [])],
            checkpoints=[CheckpointRef.from_dict(item) for item in data.get("checkpoints", [])],
            subagents=[SubagentRecord.from_dict(item) for item in data.get("subagents", [])],
            evidence_catalog=[
                EvidenceItem.from_dict(item) for item in data.get("evidence_catalog", [])
            ],
        )

    def latest_approved_gate(self, gate_type: str) -> ApprovalGate | None:
        for gate in reversed(self.approval_gates):
            if gate.gate_type == gate_type and gate.status == "approved":
                return gate
        return None

    def ensure_task_allowed(self, task: TaskRecord) -> None:
        for risk_tag in task.risk_tags:
            if risk_tag in HIGH_RISK_APPROVAL_TAGS and self.latest_approved_gate(risk_tag) is None:
                raise RuntimeContractError(
                    f"Task requires an approved approval gate for risk tag '{risk_tag}'."
                )

    def validate_claim(self, claim: ClaimRecord, require_evidence: bool) -> None:
        if require_evidence and not claim.evidence_refs:
            raise RuntimeContractError(
                f"Claim '{claim.claim_id}' is missing required evidence_refs."
            )

        if claim.claim_class == "observation" and CAUSAL_WORDING_PATTERN.search(claim.statement):
            raise RuntimeContractError(
                f"Claim '{claim.claim_id}' uses causal wording despite claim_class='observation'."
            )

        if (
            claim.claim_class == "manuscript_main_conclusion"
            and claim.approval_status != "approved"
        ):
            raise RuntimeContractError(
                f"Claim '{claim.claim_id}' requires approval before becoming a manuscript conclusion."
            )

    def validate(self, require_evidence: bool) -> None:
        for task in self.tasks:
            self.ensure_task_allowed(task)
        for claim in self.claims:
            self.validate_claim(claim, require_evidence=require_evidence)
