# Decisions

## D001 — Template Initialization
- Context: The repository started as a compact AVCP skeleton focused on docs, bridge contracts, and generated README updates.
- Decision: Keep AVCP's repo-as-memory core while expanding it into a research-runtime template instead of a generic coding-agent template.
- Alternatives:
  - Stay docs-only and leave runtime state in chat context.
  - Bind the template directly to one provider runtime.
- Consequences:
  - Docs remain the long-term policy layer.
  - Runtime state becomes machine-readable and replayable.
- Review Trigger:
  - If provider-specific adapters become the dominant use case.

## D002 — Runtime Externalization
- Context: Research workflows need durable run state across long analyses and staged approvals.
- Decision: Persist every run under `artifacts/runs/<run_id>/` with `manifest.json`, `events.jsonl`, `claims.json`, and `outputs/`.
- Alternatives:
  - Keep state only in docs.
  - Persist only final artifacts without event history.
- Consequences:
  - Recovery, replay, and post-hoc auditing become possible.
  - Run schemas now count as public contracts and need tests.
- Review Trigger:
  - If storage needs exceed local filesystem assumptions.

## D003 — Balanced Research Autonomy
- Context: Full autonomy is attractive for throughput but risky for metrics, statistics, and manuscript claims.
- Decision: Default to `autonomy_mode: balanced`, allowing low/medium-risk execution to proceed automatically while routing protocol, statistics, and manuscript conclusions through approval gates.
- Alternatives:
  - Conservative approval-first for all non-trivial steps.
  - High-autonomy exploration by default.
- Consequences:
  - Most execution work stays fast.
  - High-risk scientific reasoning remains human-accountable.
- Review Trigger:
  - If teams need stricter governance or sandboxed autonomous exploration.

## D004 — Claim Discipline
- Context: Scientific outputs often blur observation, interpretation, and recommendation.
- Decision: Claims must declare `claim_class`, `evidence_refs`, `uncertainty`, `approval_status`, and `threats_to_validity`. Observational claims may not use causal wording.
- Alternatives:
  - Leave claim style to prose conventions only.
  - Enforce evidence refs only for manuscript text.
- Consequences:
  - The template can reject unsupported or causally overstated conclusions early.
  - Prompt and runtime validations stay aligned.
- Review Trigger:
  - If downstream writing tools need more granular claim classes.
