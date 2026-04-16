## {{ title }}

{{ one_liner }}

> [!TIP]
> AVCP keeps research truth in versioned files and run ledgers, not in chat memory.

This template turns AVCP into a provider-neutral research runtime: docs lock policy, config locks execution boundaries, and `artifacts/runs/<run_id>/` keeps durable state for replay, audit, and manuscript evidence assembly.

### Why This Template Exists

| Research risk | Typical failure mode | Template control |
|---|---|---|
| Drifted protocol | metrics or exclusions change mid-analysis | approval gates + decision log |
| Hidden runtime state | context disappears between agent sessions | `manifest.json` + `events.jsonl` + `claims.json` |
| Overstated conclusions | observation is written as causation | claim classes + evidence requirements |
| Fragile handoffs | plots/tables lose provenance | bridge sidecars with stage + upstream artifacts |

### Repository Layout

```text
prompts/                 # pinned research-runtime prompt
config/                  # runtime and audit source-of-truth
docs/                    # memory, constraints, lifecycle, contracts
src/avcp_template/       # bridge + runtime models/storage
scripts/dev/             # doctor, README, changelog tooling
tests/                   # runtime, bridge, and tooling verification
artifacts/runs/          # durable run ledgers (created during use)
```

## Operating Contracts

### 1) Research cognition contract
- Start sessions by loading:
  - `docs/state.md`
  - `docs/constraints.md`
  - `docs/decisions.md`
  - `docs/api_specs.md`
  - `docs/data_contracts.md`
  - `docs/avcp_guidelines.md`
  - `docs/research_mode.md`
- Use `prompts/AVCP_SYSTEM_PROMPT_MIN.md` as the pinned operating protocol.

### 2) Runtime contract
- All execution limits and paths come from `config/config.yaml`.
- Serious runs should persist:
  - `artifacts/runs/<run_id>/manifest.json`
  - `artifacts/runs/<run_id>/events.jsonl`
  - `artifacts/runs/<run_id>/claims.json`
  - `artifacts/runs/<run_id>/outputs/`

### 3) Research claim contract
- Non-trivial claims must declare:
  - `claim_class`
  - `evidence_refs`
  - `uncertainty`
  - `approval_status`
  - `threats_to_validity`
- Observational claims may not use causal wording.

### 4) Data handoff contract
- Use `src/avcp_template/io/bridge.py::save_for_r()` for Python->R handoffs.
- Sidecars must include schema plus research provenance where available.

### 5) Tooling contract
- `README.md` is generated from `project.yaml` + `docs/readme.template.md`.
- Changelog updates go through `scripts/dev/update_changelog.py`.
- Preflight checks go through `python scripts/dev/doctor.py`.

## Quick Start

```bash
python -m pip install -e ".[dev]"
PYTHONPATH=src pytest -q
python scripts/dev/doctor.py
python scripts/dev/generate_readme.py --check
```

## Research Lifecycle

The default lifecycle is:
1. `question_definition`
2. `background_review`
3. `protocol_lock`
4. `execution`
5. `evaluation_visualization`
6. `interpretation`
7. `manuscript_evidence_pack`

Load the matching section in `docs/research_mode.md` before non-trivial work.

## Example Prompt

```text
Read and enforce prompts/AVCP_SYSTEM_PROMPT_MIN.md.
Load docs/state.md, docs/constraints.md, docs/decisions.md, docs/api_specs.md,
docs/data_contracts.md, docs/avcp_guidelines.md, docs/research_mode.md.
If the task affects protocol, metrics, statistics, or manuscript conclusions,
check approval gates before proposing code or claims.
```

## Recommended Workflow

1. Lock or update the current stage in `docs/state.md`.
2. Run `python scripts/dev/doctor.py` before long or publication-facing work.
3. Persist run state under `artifacts/runs/<run_id>/`.
4. Export analysis outputs with `save_for_r()` so sidecars capture provenance.
5. Record safe repo changes with `python scripts/dev/update_changelog.py --entry "feat(scope): ..."`
6. Regenerate the README after metadata/template changes.

## Default Public Interfaces

- Config keys:
  - `paths.run_root`
  - `runtime.permission_mode`
  - `runtime.autonomy_mode`
  - `runtime.max_parallel_subagents`
  - `runtime.compute_budget`
  - `runtime.checkpoint_backend`
  - `runtime.allowed_adapters`
  - `audit.require_evidence_for_claims`
  - `research.default_stage`
- Runtime records:
  - `RunManifest`
  - `TaskRecord`
  - `SubagentRecord`
  - `CheckpointRef`
  - `ApprovalGate`
  - `EvidenceItem`
  - `ClaimRecord`

## Maintenance Notes

- Keep docs and runtime schemas in sync in the same patch.
- Prefer local-first adapters in the template; provider-specific executors should remain replaceable.
- If `doctor.py` fails on pending approval gates, resolve the gate before continuing.

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy .
pytest -q
python scripts/dev/generate_readme.py --check
python scripts/dev/update_changelog.py --entry "chore(docs): update guide"
```

## 📌 Project At A Glance

- **Name:** `{{ name }}`
- **Domain:** {{ domain }}
- **Stage:** {{ stage }}
- **Owner:** {{ owner }}
- **License:** {{ license }}

## ⚙️ Entrypoints

{% for command in entrypoints %}- `{{ command }}`
{% endfor %}
{% if datasets %}
## 🧪 Datasets

{% for dataset in datasets %}- `{{ dataset }}`
{% endfor %}
{% endif %}
{% if outputs %}
## 📦 Outputs

{% for output in outputs %}- `{{ output }}`
{% endfor %}
{% endif %}
## 🔗 AVCP References

- Pinned system prompt: `prompts/AVCP_SYSTEM_PROMPT_MIN.md`
- Guidelines and gates: `docs/avcp_guidelines.md`
