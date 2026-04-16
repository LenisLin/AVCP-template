from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import ClaimRecord, RunManifest


@dataclass(slots=True)
class LoadedRunState:
    run_dir: Path
    manifest: RunManifest
    events: list[dict[str, Any]]
    claims: list[ClaimRecord]


def _run_dir(run_root: str | Path, run_id: str) -> Path:
    return Path(run_root) / run_id


def initialize_run_storage(run_root: str | Path, run_id: str) -> Path:
    run_dir = _run_dir(run_root, run_id)
    (run_dir / "outputs").mkdir(parents=True, exist_ok=True)
    (run_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    return run_dir


def write_manifest(run_root: str | Path, manifest: RunManifest) -> Path:
    run_dir = initialize_run_storage(run_root=run_root, run_id=manifest.run_id)
    path = run_dir / "manifest.json"
    path.write_text(json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def append_run_event(run_root: str | Path, run_id: str, event: dict[str, Any]) -> Path:
    run_dir = initialize_run_storage(run_root=run_root, run_id=run_id)
    path = run_dir / "events.jsonl"
    with path.open("a", encoding="utf-8") as file_obj:
        file_obj.write(json.dumps(event, ensure_ascii=False) + "\n")
    return path


def write_claim_ledger(run_root: str | Path, run_id: str, claims: list[ClaimRecord]) -> Path:
    run_dir = initialize_run_storage(run_root=run_root, run_id=run_id)
    path = run_dir / "claims.json"
    payload = [claim.to_dict() for claim in claims]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_run_state(run_root: str | Path, run_id: str) -> LoadedRunState:
    run_dir = _run_dir(run_root, run_id)
    manifest = RunManifest.from_dict(
        json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    )

    events_path = run_dir / "events.jsonl"
    if events_path.exists():
        events = [
            json.loads(line)
            for line in events_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    else:
        events = []

    claims_path = run_dir / "claims.json"
    if claims_path.exists():
        claim_payload = json.loads(claims_path.read_text(encoding="utf-8"))
        claims = [ClaimRecord.from_dict(item) for item in claim_payload]
    else:
        claims = manifest.claims

    return LoadedRunState(run_dir=run_dir, manifest=manifest, events=events, claims=claims)
