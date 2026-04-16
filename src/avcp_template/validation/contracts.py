from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd


class DataContractError(ValueError):
    """Raised when a data contract is violated."""


def validate_for_r_export(df: pd.DataFrame, primary_key: str) -> None:
    if not isinstance(df, pd.DataFrame):
        raise DataContractError("Input must be a pandas DataFrame.")
    if df.shape[0] == 0:
        raise DataContractError("DataFrame is empty; refusing to export.")
    if primary_key not in df.columns:
        raise DataContractError(f"Primary key column '{primary_key}' missing.")
    if df[primary_key].isna().any():
        raise DataContractError(f"Primary key column '{primary_key}' contains NaN.")
    if not df[primary_key].is_unique:
        raise DataContractError(f"Primary key column '{primary_key}' is not unique.")


RESEARCH_STAGES = (
    "question_definition",
    "background_review",
    "protocol_lock",
    "execution",
    "evaluation_visualization",
    "interpretation",
    "manuscript_evidence_pack",
)


def validate_research_stage(stage: str) -> None:
    if stage not in RESEARCH_STAGES:
        allowed = ", ".join(RESEARCH_STAGES)
        raise DataContractError(f"Unknown research stage '{stage}'. Expected one of: {allowed}.")


def validate_research_export_metadata(
    stage: str | None,
    upstream_artifacts: Sequence[str] | None,
    evidence_metadata: Mapping[str, Any] | None,
) -> None:
    if stage is not None:
        validate_research_stage(stage)

    if upstream_artifacts is not None:
        if not isinstance(upstream_artifacts, Sequence) or isinstance(upstream_artifacts, str):
            raise DataContractError("upstream_artifacts must be a sequence of strings.")
        if not all(isinstance(item, str) and item for item in upstream_artifacts):
            raise DataContractError("upstream_artifacts must contain non-empty strings only.")

    if evidence_metadata is not None and not isinstance(evidence_metadata, Mapping):
        raise DataContractError("evidence_metadata must be a mapping.")
