"""JSONL audit logging for decision recommendations.

This module records decision outputs as append-only JSON lines so local API
usage leaves a lightweight audit trail without introducing a database or queue.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DECISION_HISTORY_PATH = Path("logs/decision_history.jsonl")


def build_decision_audit_record(
    decision: dict[str, Any],
    *,
    timestamp: datetime | None = None,
) -> dict[str, Any]:
    """Build the JSON-serializable audit record for a decision response.

    Args:
        decision: Decision payload containing company, decision,
            highest severity, signal count, key drivers, and rationale.
        timestamp: Optional timestamp used by tests or deterministic callers.

    Returns:
        dict[str, Any]: Audit record with an ISO timestamp and decision fields.

    Raises:
        KeyError: If the decision payload is missing a required audit field.
    """
    recorded_at = timestamp or datetime.now(timezone.utc)
    return {
        "timestamp": recorded_at.isoformat(),
        "company": decision["company"],
        "decision": decision["decision"],
        "highest_severity": decision["highest_severity"],
        "signal_count": decision["signal_count"],
        "key_drivers": decision["key_drivers"],
        "rationale": decision["rationale"],
    }


def write_decision_audit_record(
    decision: dict[str, Any],
    *,
    output_path: str | Path = DEFAULT_DECISION_HISTORY_PATH,
    timestamp: datetime | None = None,
) -> dict[str, Any]:
    """Append one decision audit record to a JSONL file.

    Args:
        decision: Decision payload returned by the decision service.
        output_path: JSONL destination path. Parent directories are created
            automatically.
        timestamp: Optional timestamp used by tests or deterministic callers.

    Returns:
        dict[str, Any]: The record written to disk.

    Raises:
        KeyError: If the decision payload is missing a required audit field.
        OSError: If the destination cannot be created or written.

    Side Effects:
        Creates the output directory when missing and appends one JSON object
        followed by a newline.
    """
    record = build_decision_audit_record(decision, timestamp=timestamp)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True))
        handle.write("\n")
    return record
