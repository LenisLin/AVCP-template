# API Specifications

## Runtime Records

### `RunManifest`
- Purpose: durable top-level state for one research run.
- Required fields:
  - `run_id: str`
  - `research_stage: question_definition | background_review | protocol_lock | execution | evaluation_visualization | interpretation | manuscript_evidence_pack`
  - `permission_mode: str`
  - `autonomy_mode: str`
  - `max_parallel_subagents: int >= 1`
  - `compute_budget: mapping`
  - `checkpoint_backend: str`
  - `allowed_adapters: list[str]`
  - `tasks: list[TaskRecord]`
  - `approval_gates: list[ApprovalGate]`
  - `claims: list[ClaimRecord]`
  - `checkpoints: list[CheckpointRef]`
  - `subagents: list[SubagentRecord]`
  - `evidence_catalog: list[EvidenceItem]`
- Invariants:
  - high-risk task `risk_tags` require a matching approved gate
  - manuscript main conclusions require approval
  - `allowed_adapters` must not be empty

### `TaskRecord`
- Fields:
  - `task_id`, `title`, `stage`, `status`
  - `evidence_refs`, `risk_tags`, `artifacts`, `summary`
- Notes:
  - `risk_tags` drive approval gating
  - `status` is one of `pending | running | completed | blocked | failed`

### `SubagentRecord`
- Fields:
  - `subagent_id`, `name`, `stage`, `status`
  - `summary`, `evidence_refs`, `risk_tags`, `artifacts`, `checkpoint_id`
- Contract:
  - subagents must return machine-readable state, not only free text

### `CheckpointRef`
- Fields:
  - `checkpoint_id`, `path`, `created_at`, `note`
- Contract:
  - checkpoint IDs are stable references for replay or resume

### `ApprovalGate`
- Fields:
  - `gate_id`, `gate_type`, `status`, `rationale`
- `gate_type` examples:
  - `new_metric`
  - `outcome_switch`
  - `post_hoc_subgroup`
  - `statistical_interpretation`
  - `interpretation_claim`
  - `manuscript_main_conclusion`

### `EvidenceItem`
- Fields:
  - `evidence_id`, `kind`, `ref`, `note`
- Intended `kind` values:
  - `file`
  - `table`
  - `figure`
  - `metric`
  - `command_output`
  - `external_citation`

### `ClaimRecord`
- Fields:
  - `claim_id`
  - `claim_class: observation | interpretation | recommendation | manuscript_main_conclusion`
  - `statement`
  - `evidence_refs`
  - `uncertainty`
  - `approval_status: not_required | pending | approved | rejected`
  - `threats_to_validity`
- Invariants:
  - no empty `evidence_refs` when audit requires evidence
  - `claim_class=observation` cannot use causal wording
  - `claim_class=manuscript_main_conclusion` requires `approval_status=approved`

## Storage Layout

- `artifacts/runs/<run_id>/manifest.json`
  - canonical serialized `RunManifest`
- `artifacts/runs/<run_id>/events.jsonl`
  - append-only runtime event stream
- `artifacts/runs/<run_id>/claims.json`
  - explicit claim ledger for downstream manuscript assembly
- `artifacts/runs/<run_id>/outputs/`
  - analysis outputs, tables, plots, summaries
- `artifacts/runs/<run_id>/checkpoints/`
  - provider-neutral resume artifacts

## Adapter Boundary

Provider-specific adapters are intentionally out of tree for v1. Any adapter must respect:
- config-driven permission mode and budget limits
- run manifest persistence before and after execution
- approval-gate enforcement before high-risk actions
- machine-readable subagent/task outputs
