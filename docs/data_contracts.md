# Data Contracts

## Analysis Dataset Contract

- Every analysis-ready dataset must document:
  - row identity / primary key
  - column names and units
  - missingness expectations
  - filtering / exclusion logic
  - seed policy for any stochastic step
  - upstream artifact lineage
- Preferred storage:
  - `.parquet` for large tables
  - `.csv` for small tables or handoff-friendly exports

## `save_for_r()` Sidecar Contract

Each export must create `<stem>_meta.json` alongside the data file.

Required fields:
- `file`
- `primary_key`
- `columns`
- `provenance.script`
- `provenance.git_commit`
- `provenance.config`
- `provenance.stage`
- `provenance.upstream_artifacts`
- `provenance.evidence_metadata`

Optional fields:
- `provenance.run_id`

Rules:
- `primary_key` must exist, contain no nulls, and be unique.
- `stage` must be one of:
  - `question_definition`
  - `background_review`
  - `protocol_lock`
  - `execution`
  - `evaluation_visualization`
  - `interpretation`
  - `manuscript_evidence_pack`
- `upstream_artifacts` must contain only non-empty strings.
- `evidence_metadata` must be a mapping when present.

## Research Artifact Provenance

Recommended `evidence_metadata` keys:
- `figure_ids`
- `table_ids`
- `metric_ids`
- `analysis_note`
- `external_citations`

Recommended dataset annotations:
- `units`: per-column units or `"unitless"`
- `missingness_rule`: e.g. `not_allowed`, `allowed_if_documented`
- `selection_criteria`: plain-language inclusion/exclusion summary
- `random_seed`: explicit integer seed or `"not_applicable"`

## Validation Functions

- `validate_for_r_export()`
  - validates DataFrame shape and primary-key integrity
- `validate_research_stage()`
  - validates stage labels against the research lifecycle
- `validate_research_export_metadata()`
  - validates research-sidecar provenance payloads
