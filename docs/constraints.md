# Constraints (Locked)

C1. Repo-as-memory: locked constraints live here; undocumented constraints are not binding.
C2. All paths must come from `config/config.yaml` (no hardcoded absolute paths in scripts).
C3. No silent failures: logging + validation + fail-fast assertions are mandatory.
C4. No speculative science: uncertain algorithms/metrics must go through Tier-2 gate.
C5. Python→R bridge: any handover file must be created via `save_for_r()` in `src/avcp_template/io/bridge.py`.
C6. Runtime state must be externalized under `artifacts/runs/<run_id>/`; chat context is not a durable source of truth.
C7. High-risk research mutations (`new_metric`, `outcome_switch`, `post_hoc_subgroup`, `statistical_interpretation`, `manuscript_main_conclusion`) require explicit approval gates before execution or publication.
C8. Manuscript-facing claims require evidence refs, uncertainty, and threats-to-validity annotations.

# Versioning Model (Lock one)
# - Model A: single repo SemVer
# - Model B: component SemVer
# - Model C: single repo SemVer + API_VERSION
