from __future__ import annotations

import json
from pathlib import Path

from .types import JsonDict


def ensure_parent_directory(path: str | Path) -> Path:
    resolved_path = Path(path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path


def write_json(payload: JsonDict, output_path: str | Path) -> None:
    path = ensure_parent_directory(output_path)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
