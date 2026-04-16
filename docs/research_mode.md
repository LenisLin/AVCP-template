# Research Mode

`research_mode.md` is the stage-aware companion to the minimal AVCP system prompt. Load it progressively based on the current lifecycle stage instead of bloating the base prompt.

## Lifecycle

### 1. `question_definition`
- Clarify the scientific question, target population, and intended decision.
- Record hypotheses and what would count as disconfirming evidence.
- Do not invent methods or datasets that are not yet locked.

### 2. `background_review`
- Gather literature, prior runs, and domain constraints.
- Distinguish directly observed facts from inferred relevance.
- Capture open uncertainties that still affect protocol design.

### 3. `protocol_lock`
- Freeze metrics, exclusions, subgroup strategy, and statistical plan.
- Any change to primary metrics, exclusions, or subgroup plans requires an approval gate.
- This is the last stage where major design changes should happen cheaply.

### 4. `execution`
- Run analysis tasks under explicit config, budget, and output paths.
- Persist task summaries, artifacts, and checkpoints into the run ledger.
- Avoid speculative interpretation while execution is still underway.

### 5. `evaluation_visualization`
- Summarize results with figures, tables, diagnostics, and error checks.
- Mark exploratory outputs as exploratory.
- Ensure every plot/table is traceable to upstream artifacts.

### 6. `interpretation`
- Translate results into bounded scientific meaning.
- Record threats to validity and plausible alternative explanations.
- Treat strong language as a risk factor that may trigger approval.

### 7. `manuscript_evidence_pack`
- Assemble claim-ready evidence for writing or review.
- Every manuscript-facing claim must link to evidence refs, uncertainty, and threats to validity.
- The template should prefer claim ledgers over prose-only summaries.

## Progressive Loading Rule

- Always load:
  - `docs/state.md`
  - `docs/constraints.md`
  - `docs/decisions.md`
  - `docs/api_specs.md`
  - `docs/data_contracts.md`
  - `docs/avcp_guidelines.md`
- Load `docs/research_mode.md` sections matching the active stage before non-trivial work.
- If a task crosses stages, update `docs/state.md` and the run manifest before continuing.
